from flask import Blueprint, render_template, request, session, jsonify
from services.analysis import analyze_profile
from services.roadmap import get_roadmap
from services.readiness import calculate_readiness
from services.recommendations_engine import get_detailed_recommendation
from services.action_plan import generate_action_plan
from services.career_engine import (
    get_career_recommendation, get_role_skills, calculate_career_confidence,
    get_career_guidance
)
from services.saas_service import check_usage_limit, increment_usage, get_usage_context
from database.models import insert_submission, get_user_submissions
import traceback
import json
import uuid

user_bp = Blueprint("user", __name__)


@user_bp.route("/", methods=["GET", "POST"])
def home():
    user_id = session.get('user_id', str(uuid.uuid4()))
    session['user_id'] = user_id
    
    recommendation = None
    detailed_rec = None
    readiness_score = None
    confidence = None
    strengths = []
    gaps = []
    next_actions = []
    next_role = None
    error = None
    previous_submissions = []
    
    if 'user_id' in session and session['user_id'] != user_id:
        previous_submissions = get_user_submissions(session['user_id'], limit=5) or []
    
    if request.method == "POST":
        try:
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.form.get('_ajax') == '1'
            
            if 'user_id' in session:
                usage_check = check_usage_limit(session['user_id'], 'career_analyses_used')
                if not usage_check['allowed']:
                    error = usage_check['message']
                    if is_ajax:
                        return jsonify({'success': False, 'message': error}), 403
                    return render_template("index.html", error=error)
            
            name = request.form.get("name", "").strip()
            email = session.get('email', request.form.get("email", "")).strip()
            interest = request.form.get("interest", "").strip().lower()
            level = request.form.get("level", "").strip().lower()
            acquired_skills = request.form.getlist("known_skills")
            resume_skills = request.form.getlist("resume_skills")
            
            all_skills = list(set(acquired_skills + resume_skills))
            
            if not all([name, interest, level]):
                error = "Name, interest, and level are required"
                if is_ajax:
                    return jsonify({'success': False, 'message': error})
            else:
                career_rec = get_career_recommendation(interest, level)
                if not career_rec:
                    error = "Invalid interest or level selection"
                    if is_ajax:
                        return jsonify({'success': False, 'message': error})
                else:
                    role = career_rec['role']
                    tier = career_rec['tier']
                    next_role = career_rec.get('next_role')
                    
                    guidance = get_career_guidance(interest, level, all_skills)
                    
                    confidence = guidance['confidence'] if guidance else calculate_career_confidence(interest, level, all_skills)
                    
                    role_skills = get_role_skills(role)
                    
                    readiness_data = calculate_readiness(role, all_skills)
                    readiness_score = readiness_data.get('readiness_score', 0)
                    strengths = readiness_data.get('strengths', [])
                    gaps = readiness_data.get('gaps', [])
                    next_actions = readiness_data.get('next_actions', [])
                    
                    submission_id = None
                    if user_id:
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
                            recommended_role_tier=tier,
                            strengths=strengths,
                            gaps=gaps
                        )
                    
                    if submission_id or user_id:
                        # Increment usage after successful analysis
                        if user_id:
                            increment_usage(user_id, 'career_analyses_used')
                        recommendation = role
                        detailed_rec = guidance or career_rec
                        
                        if is_ajax:
                            return jsonify({
                                'success': True,
                                'data': {
                                    'role': role,
                                    'confidence': confidence,
                                    'readiness_score': readiness_score,
                                    'current_level': level,
                                    'strengths': strengths[:5],
                                    'gaps': gaps[:5],
                                    'next_actions': next_actions[:5],
                                    'next_role': next_role
                                }
                            })
                    else:
                        error = "Failed to process analysis"
                        if is_ajax:
                            return jsonify({'success': False, 'message': error})
        
        except Exception as e:
            error = f"Error processing request: {str(e)}"
            traceback.print_exc()
            if is_ajax:
                return jsonify({'success': False, 'message': error}), 500
    
    # Get usage context for display
    usage_context = None
    if 'user_id' in session:
        usage_context = get_usage_context(session['user_id'])
    
    return render_template(
        'index.html',
        recommendation=recommendation,
        detailed_recommendation=detailed_rec,
        readiness_score=readiness_score,
        confidence=confidence,
        strengths=strengths,
        gaps=gaps,
        next_actions=next_actions,
        next_role=next_role,
        error=error,
        previous_submissions=previous_submissions,
        usage_context=usage_context
    )


@user_bp.route("/api/usage-status", methods=["GET"])
def get_usage_status():
    """API endpoint for user's current usage status."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session.get('user_id')
    usage_context = get_usage_context(user_id)
    
    if not usage_context:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(usage_context)


@user_bp.route("/api/check-limit", methods=["POST"])
def check_limit():
    """API endpoint to check if user can perform an action."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    usage_type = data.get('usage_type', '')
    
    user_id = session.get('user_id')
    result = check_usage_limit(user_id, usage_type)
    
    return jsonify(result)


@user_bp.route("/api/career-options", methods=["GET"])
def get_career_options():
    """API endpoint for career options."""
    interest = request.args.get('interest', '').lower()
    
    if interest not in ['ai', 'tech', 'data', 'design', 'business']:
        return jsonify({'error': 'Invalid interest'}), 400
    
    from services.career_engine import CAREER_DATABASE
    
    options = []
    if interest in CAREER_DATABASE:
        for level, data in CAREER_DATABASE[interest].items():
            options.append({
                'level': level,
                'role': data['role'],
                'next_role': data['next_role'],
                'salary': data['avg_salary']
            })
    
    return jsonify(options)


@user_bp.route("/api/role-skills", methods=["GET"])
def get_role_skills_api():
    """API endpoint for role-specific skills."""
    role = request.args.get('role', '')
    
    skills = get_role_skills(role)
    if not skills:
        return jsonify({'error': 'Role not found'}), 404
    
    return jsonify(skills)
