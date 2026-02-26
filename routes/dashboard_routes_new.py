from flask import Blueprint, render_template, session, redirect, url_for, request
from functools import wraps
from database.db import get_db
import json
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# LOGIN REQUIRED DECORATOR
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# MAIN DASHBOARD ROUTE
@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard view."""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    
    # Force commit any pending transactions to ensure fresh data
    try:
        db.commit()
    except:
        pass
    
    # Get user profile
    user = db.execute(
        'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    
    if not user:
        return redirect(url_for('auth.login'))
    
    # Get user's resumes (from submissions table)
    resumes = db.execute('''
        SELECT id, name, created_at, readiness_score, resume_file_path
        FROM submissions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 10
    ''', (user_id,)).fetchall()
    
    resume_count = len(resumes) if resumes else 0
    
    # Calculate average readiness score
    avg_readiness = 0
    if resumes:
        scores = [r['readiness_score'] or 0 for r in resumes]
        avg_readiness = sum(scores) / len(scores) if scores else 0
    
    # Get recent analyses
    recent_analyses = db.execute('''
        SELECT id, name, recommendation, created_at, readiness_score
        FROM submissions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 5
    ''', (user_id,)).fetchall()
    
    # Get usage stats (this month)
    today = datetime.now().strftime('%Y-%m-%d')
    year_month = datetime.now().strftime('%Y-%m')
    
    monthly_usage = db.execute('''
        SELECT career_analyses_used, resume_uploads_used, chatbot_messages_used
        FROM usage_tracking_monthly
        WHERE user_id = ? AND year_month = ?
    ''', (user_id, year_month)).fetchone()
    
    analyses_used = monthly_usage['career_analyses_used'] if monthly_usage else 0
    
    # Get user tier
    user_tier = user['tier'] if user else 'free'
    
    # Get limits based on tier
    tier_config = db.execute('''
        SELECT career_analyses_limit, resume_uploads_limit
        FROM tier_config
        WHERE tier = ?
    ''', (user_tier,)).fetchone()
    
    analyses_limit = tier_config['career_analyses_limit'] if tier_config else 3
    
    dashboard_data = {
        'user': user,
        'resume_count': resume_count,
        'avg_readiness_score': round(avg_readiness),
        'analyses_used': analyses_used,
        'analyses_limit': analyses_limit,
        'analyses_remaining': max(0, analyses_limit - analyses_used),
        'resumes': resumes,
        'recent_analyses': recent_analyses,
    }
    
    return render_template('dashboard/real_dashboard.html', **dashboard_data)

# USER PROFILE PAGE
@dashboard_bp.route('/profile')
@login_required
def profile():
    """User profile edit page."""
    user_id = session.get('user_id')
    db = get_db()
    
    user = db.execute(
        'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    
    if not user:
        return redirect(url_for('auth.login'))
    
    profile_data = {
        'user': user,
    }
    
    return render_template('auth/profile.html', user=user)

@dashboard_bp.route('/api/track-time', methods=['POST'])
@login_required
def track_time():
    """Track user session time on pages."""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        page = data.get('page', 'unknown')
        duration = data.get('duration', 0)
        
        db = get_db()
        now = datetime.now(UTC).isoformat()
        
        # Track as user interaction
        db.execute('''
            INSERT INTO user_interactions (user_id, interaction_type, metadata, timestamp)
            VALUES (?, 'page_view', ?, ?)
        ''', (user_id, json.dumps({'page': page, 'duration': duration}), now))
        db.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Time tracking error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# UPDATE PROFILE
@dashboard_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile."""
    user_id = session.get('user_id')
    db = get_db()
    
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    
    db.execute('''
        UPDATE users
        SET full_name = ?, updated_at = ?
        WHERE id = ?
    ''', (full_name, datetime.now().isoformat(), user_id))
    
    db.commit()
    
    # Update session
    session['user_name'] = full_name
    
    from flask import flash
    flash('Profile updated successfully!', 'success')
    
    return redirect(url_for('dashboard.profile'))

# RESUME HISTORY
@dashboard_bp.route('/resumes')
@login_required
def resume_history():
    """View all user's resumes."""
    user_id = session.get('user_id')
    db = get_db()
    
    resumes = db.execute('''
        SELECT id, name, created_at, readiness_score, resume_file_path
        FROM submissions
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,)).fetchall()
    
    resume_data = {
        'resumes': resumes,
        'resume_count': len(resumes),
    }
    
    return render_template('dashboard/resume_history.html', **resume_data)

# ANALYSIS HISTORY
@dashboard_bp.route('/analyses')
@login_required
def analysis_history():
    """View all user's analyses."""
    user_id = session.get('user_id')
    db = get_db()
    
    analyses = db.execute('''
        SELECT id, name, interest, level, recommendation, readiness_score, confidence_score, created_at
        FROM submissions
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,)).fetchall()
    
    analysis_data = {
        'analyses': analyses,
        'analysis_count': len(analyses),
    }
    
    return render_template('dashboard/analysis_history.html', **analysis_data)

# SKILL TRACKING
@dashboard_bp.route('/skills')
@login_required
def skill_tracking():
    """View tracked skills and progress."""
    user_id = session.get('user_id')
    db = get_db()
    
    # Get all skills from submissions
    submissions = db.execute('''
        SELECT id, resume_parsed_skills, created_at
        FROM submissions
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,)).fetchall()
    
    # Parse and aggregate skills
    all_skills = {}
    for submission in submissions:
        if submission['resume_parsed_skills']:
            try:
                skills = json.loads(submission['resume_parsed_skills'])
                for skill in skills if isinstance(skills, list) else []:
                    if skill not in all_skills:
                        all_skills[skill] = {'count': 0, 'first_seen': submission['created_at']}
                    all_skills[skill]['count'] += 1
            except:
                pass
    
    # Sort by count
    sorted_skills = sorted(all_skills.items(), key=lambda x: x[1]['count'], reverse=True)
    
    skill_data = {
        'skills': sorted_skills,
        'unique_skill_count': len(all_skills),
    }
    
    return render_template('dashboard/skills.html', **skill_data)

# CAREER ROADMAP
@dashboard_bp.route('/career-roadmap')
@login_required
def career_roadmap():
    """Career progression roadmap."""
    user_id = session.get('user_id')
    db = get_db()
    
    # Get user's latest analysis
    latest = db.execute('''
        SELECT interest, level, recommendation, gaps
        FROM submissions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    ''', (user_id,)).fetchone()
    
    roadmap_data = {
        'latest_analysis': latest,
    }
    
    return render_template('dashboard/career_roadmap.html', **roadmap_data)

# SKILL GAP ANALYSIS
@dashboard_bp.route('/skill-gap')
@login_required
def skill_gap():
    """Skill gap analysis page."""
    user_id = session.get('user_id')
    db = get_db()
    
    # Get latest analysis
    latest = db.execute('''
        SELECT gaps, recommendation, resume_parsed_skills
        FROM submissions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    ''', (user_id,)).fetchone()
    
    gap_data = {
        'latest_analysis': latest,
    }
    
    return render_template('dashboard/skill_gap.html', **gap_data)

# REPORTS
@dashboard_bp.route('/reports')
@login_required
def reports():
    """Career reports and insights."""
    user_id = session.get('user_id')
    db = get_db()
    
    # Get all analyses
    analyses = db.execute('''
        SELECT id, name, interest, level, recommendation, readiness_score, created_at
        FROM submissions
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,)).fetchall()
    
    # Calculate statistics
    if analyses:
        scores = [a['readiness_score'] or 0 for a in analyses]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
    else:
        avg_score = max_score = min_score = 0
    
    report_data = {
        'analyses': analyses,
        'total_analyses': len(analyses),
        'avg_score': round(avg_score),
        'max_score': max_score,
        'min_score': min_score,
    }
    
    return render_template('dashboard/reports.html', **report_data)
