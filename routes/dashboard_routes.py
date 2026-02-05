"""User dashboard and profile routes."""
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from services.auth_service import get_user_by_id, update_user_profile
from services.saas_service import get_usage_context, get_user_tier, check_usage_limit, increment_usage
from services.analysis import analyze_profile
from services.readiness import calculate_readiness
from services.recommendations_engine import get_detailed_recommendation
from services.career_engine import (
    get_career_recommendation, get_role_skills, calculate_career_confidence,
    get_career_guidance
)
from database.models import get_user_submissions, insert_submission
from functools import wraps
from datetime import datetime, timedelta
import json
import traceback
import uuid

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@dashboard_bp.route('/', methods=['GET'])
@login_required
def index():
    """User dashboard home."""
    user_id = session.get('user_id')
    user = get_user_by_id(user_id)
    
    if not user:
        return redirect(url_for('auth.login'))
    
    # Get usage context
    usage_context = get_usage_context(user_id)
    
    # Get past submissions (analytics)
    submissions = get_user_submissions(user_id, limit=50) or []
    
    # Calculate analytics
    analytics = {
        'total_analyses': len(submissions),
        'avg_readiness': 0,
        'top_recommendation': None,
        'timeline': []
    }
    
    if submissions:
        # Average readiness
        readiness_scores = [s.get('readiness_score', 0) for s in submissions if s.get('readiness_score')]
        if readiness_scores:
            analytics['avg_readiness'] = round(sum(readiness_scores) / len(readiness_scores), 1)
        
        # Top recommendation
        from collections import Counter
        recommendations = [s.get('recommendation') for s in submissions if s.get('recommendation')]
        if recommendations:
            analytics['top_recommendation'] = Counter(recommendations).most_common(1)[0][0]
        
        # Timeline - last 7 submissions
        analytics['timeline'] = submissions[:7]
    
    return render_template(
        'dashboard/real_dashboard.html',
        user=user,
        usage_context=usage_context,
        analytics=analytics,
        submissions=submissions
    )


@dashboard_bp.route('/progress', methods=['GET'])
@login_required
def progress():
    """User career progress tracking."""
    user_id = session.get('user_id')
    user = get_user_by_id(user_id)
    
    if not user:
        return redirect(url_for('auth.login'))
    
    # Get submissions
    submissions = get_user_submissions(user_id, limit=100) or []
    
    # Build progress data
    progress_data = {
        'total_analyses': len(submissions),
        'readiness_trend': [],
        'confidence_trend': [],
        'skill_improvements': {}
    }
    
    # Process submissions in chronological order
    sorted_submissions = sorted(submissions, key=lambda x: x['created_at'], reverse=True)
    
    for submission in sorted_submissions:
        progress_data['readiness_trend'].append({
            'date': submission['created_at'][:10],
            'score': submission.get('readiness_score', 0),
            'role': submission['recommendation']
        })
        
        progress_data['confidence_trend'].append({
            'date': submission['created_at'][:10],
            'score': submission.get('confidence_score', 0)
        })
    
    # Reverse to get chronological order
    progress_data['readiness_trend'] = list(reversed(progress_data['readiness_trend']))
    progress_data['confidence_trend'] = list(reversed(progress_data['confidence_trend']))
    
    usage_context = get_usage_context(user_id)
    
    return render_template(
        'dashboard/progress.html',
        user=user,
        progress_data=progress_data,
        usage_context=usage_context
    )


@dashboard_bp.route('/history', methods=['GET'])
@login_required
def history():
    """View all past analyses."""
    user_id = session.get('user_id')
    user = get_user_by_id(user_id)
    
    if not user:
        return redirect(url_for('auth.login'))
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    submissions = get_user_submissions(user_id, limit=per_page, offset=offset) or []
    total = len(get_user_submissions(user_id, limit=10000) or [])
    total_pages = (total + per_page - 1) // per_page
    
    usage_context = get_usage_context(user_id)
    
    return render_template(
        'dashboard/history.html',
        user=user,
        submissions=submissions,
        page=page,
        total_pages=total_pages,
        total=total,
        usage_context=usage_context
    )


@dashboard_bp.route('/analysis', methods=['GET', 'POST'])
@login_required
def analysis():
    """Career analysis form."""
    user_id = session.get('user_id')
    user = get_user_by_id(user_id)
    
    if not user:
        return redirect(url_for('auth.login'))
    
    recommendation = None
    detailed_rec = None
    readiness_score = None
    confidence = None
    strengths = []
    gaps = []
    next_actions = []
    error = None
    usage_context = get_usage_context(user_id)
    
    if request.method == "POST":
        try:
            # Check usage limit (only on form submission)
            usage_check = check_usage_limit(user_id, 'career_analyses_used')
            if not usage_check['allowed']:
                error = usage_check['message']
            else:
                name = request.form.get("name", "").strip()
                email = request.form.get("email", "").strip()
                interest = request.form.get("interest", "").strip().lower()
                level = request.form.get("level", "").strip().lower()
                acquired_skills = request.form.getlist("known_skills")
                resume_skills = request.form.getlist("resume_skills")
                
                all_skills = list(set(acquired_skills + resume_skills))
                
                if not all([name, interest, level]):
                    error = "Name, interest, and level are required"
                else:
                    # Analyze profile
                    analysis_result = analyze_profile(interest, level, all_skills)
                    
                    if analysis_result and not isinstance(analysis_result, str):
                        role = analysis_result.get('recommended_role')
                        career_rec = analysis_result.get('career_recommendation', {})
                        
                        # Get readiness
                        readiness_score = calculate_readiness(
                            role, level, all_skills
                        )
                        
                        # Get confidence
                        confidence = calculate_career_confidence(role, all_skills, level)
                        
                        # Get strengths and gaps
                        strengths = analysis_result.get('strengths', [])
                        gaps = analysis_result.get('gaps', [])
                        next_actions = analysis_result.get('next_steps', [])
                        
                        # Get detailed recommendation
                        detailed_rec = get_detailed_recommendation(role, level, all_skills)
                        
                        # Get guidance
                        guidance = get_career_guidance(role, level, all_skills)
                        if guidance:
                            detailed_rec = guidance
                        
                        # Save submission
                        submission_id = insert_submission(
                            user_id=user_id,
                            name=name,
                            email=email,
                            interest=interest,
                            level=level,
                            known_skills=", ".join(all_skills) if all_skills else None,
                            recommendation=role,
                            readiness_score=readiness_score,
                            confidence_score=confidence,
                            strengths=strengths,
                            gaps=gaps
                        )
                        
                        if submission_id:
                            increment_usage(user_id, 'career_analyses_used')
                            recommendation = role
                        else:
                            error = "Failed to save analysis results"
                    else:
                        error = "Failed to analyze profile. Please try again."
        
        except Exception as e:
            error = f"Error processing request: {str(e)}"
            traceback.print_exc()
    
    return render_template(
        'dashboard/analysis.html',
        user=user,
        recommendation=recommendation,
        detailed_recommendation=detailed_rec,
        readiness_score=readiness_score,
        confidence=confidence,
        strengths=strengths,
        gaps=gaps,
        next_actions=next_actions,
        error=error,
        usage_context=usage_context
    )


@dashboard_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User account settings."""
    user_id = session.get('user_id')
    user = get_user_by_id(user_id)
    
    if not user:
        return redirect(url_for('auth.login'))
    
    error = None
    success = None
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        
        if full_name:
            update_user_profile(user_id, full_name=full_name)
            session['full_name'] = full_name
            success = 'Profile updated successfully'
            user = get_user_by_id(user_id)
    
    usage_context = get_usage_context(user_id)
    user_tier = get_user_tier(user_id)
    
    return render_template(
        'dashboard/settings.html',
        user=user,
        usage_context=usage_context,
        user_tier=user_tier,
        error=error,
        success=success
    )


@dashboard_bp.route('/api/analytics', methods=['GET'])
@login_required
def api_analytics():
    """API endpoint for analytics data."""
    user_id = session.get('user_id')
    submissions = get_user_submissions(user_id, limit=100) or []
    
    if not submissions:
        return jsonify({
            'readiness': [],
            'confidence': [],
            'by_role': {}
        })
    
    # Process data
    data = {
        'readiness': [],
        'confidence': [],
        'by_role': {}
    }
    
    for submission in sorted(submissions, key=lambda x: x['created_at']):
        date = submission['created_at'][:10]
        data['readiness'].append({
            'date': date,
            'value': submission.get('readiness_score', 0)
        })
        data['confidence'].append({
            'date': date,
            'value': submission.get('confidence_score', 0)
        })
        
        role = submission['recommendation']
        if role not in data['by_role']:
            data['by_role'][role] = 0
        data['by_role'][role] += 1
    
    return jsonify(data)
