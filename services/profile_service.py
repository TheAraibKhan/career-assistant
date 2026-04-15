"""Handles reading and writing user profile data."""
import json
from datetime import datetime


def get_user_profile(user_id):
    """Build a complete profile dict for the given user."""
    from database.db import get_db
    from services.auth_service import get_user_by_id

    db = get_db()
    user_row = get_user_by_id(user_id)
    user = dict(user_row) if user_row else {}

    # Get onboarding profile
    onboarding = _get_onboarding(db, user_id) or {}

    # Get user stats
    stats = _get_stats(db, user_id, onboarding)

    # Get skill progress
    skills_data = _get_skill_progress(db, user_id, onboarding)

    # Get resume analysis data (if available)
    resume_data = _get_resume_data(db, user_id)

    return {
        'user': {
            'id': user.get('id'),
            'name': user.get('full_name', 'Profile'),
            'email': user.get('email', ''),
            'phase': onboarding.get('phase', 'college'),
            'created_at': user.get('created_at') if isinstance(user, dict) else None,
        },
        'profile': {
            'skills': onboarding.get('skills', []),
            'interests': onboarding.get('interests', []),
            'goals': onboarding.get('goals', []),
            'daily_time': onboarding.get('daily_time', 1),
            'primary_skill': onboarding.get('skills', ['Python'])[0] if onboarding.get('skills') else 'Python',
            'completed': bool(onboarding),
        },
        'stats': stats,
        'skills': skills_data,
        'resume_data': resume_data,
    }


def update_user_profile(user_id, profile_data):
    """Save profile changes and refresh dependent modules."""
    from database.db import get_db
    
    db = get_db()
    now = datetime.utcnow().isoformat()
    
    # Update profile
    db.execute('''
        INSERT OR REPLACE INTO user_profiles 
        (user_id, skills, interests, phase, goals, daily_time, updated_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, COALESCE(
            (SELECT created_at FROM user_profiles WHERE user_id = ?),
            ?
        ))
    ''', (
        user_id,
        json.dumps(profile_data.get('skills', [])),
        json.dumps(profile_data.get('interests', [])),
        profile_data.get('phase', 'college'),
        json.dumps(profile_data.get('goals', [])),
        int(profile_data.get('daily_time', 1)),
        now,
        user_id,
        now
    ))
    
    # Ensure skill_progress records exist for all skills
    skills = profile_data.get('skills', [])
    for skill in skills:
        existing = db.execute(
            'SELECT id FROM skill_progress WHERE user_id = ? AND skill_name = ?',
            (user_id, skill)
        ).fetchone()
        
        if not existing:
            db.execute('''
                INSERT INTO skill_progress 
                (user_id, skill_name, proficiency_level, tasks_completed, total_xp)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, skill, 0, 0, 0))
    
    # Ensure stats record exists
    existing_stats = db.execute(
        'SELECT id FROM user_stats WHERE user_id = ?',
        (user_id,)
    ).fetchone()
    
    if not existing_stats:
        db.execute('''
            INSERT INTO user_stats 
            (user_id, total_xp, current_streak, longest_streak, 
             tasks_completed, career_readiness, skills_tracked, 
             last_activity_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, 0, 0, 0, 0, 0, len(skills), now, now, now))
    else:
        # Update skills_tracked count
        db.execute(
            'UPDATE user_stats SET skills_tracked = ? WHERE user_id = ?',
            (len(skills), user_id)
        )
    
    db.commit()
    
    # Refresh dependent modules
    from services.data_sync import refresh_user_data
    return refresh_user_data(user_id)


def _get_onboarding(db, user_id):
    """Get user's onboarding profile from database."""
    try:
        result = db.execute(
            "SELECT skills, interests, phase, goals, daily_time FROM user_profiles WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        if result:
            return {
                'skills': json.loads(result['skills'] or '[]'),
                'interests': json.loads(result['interests'] or '[]'),
                'phase': result['phase'] or 'college',
                'goals': json.loads(result['goals'] or '[]'),
                'daily_time': result['daily_time'] or 1,
                'completed': True,
            }
        return None
    except Exception as e:
        print(f"Error in _get_onboarding: {e}")
        return None


def _get_stats(db, user_id, onboarding):
    """Get user stats from database."""
    try:
        stats_row = db.execute(
            'SELECT total_xp, tasks_completed, career_readiness, current_streak, skills_tracked FROM user_stats WHERE user_id = ?',
            (user_id,)
        ).fetchone()

        skills_count = len(onboarding.get('skills', [])) if onboarding else 0

        return {
            'total_xp': stats_row['total_xp'] if stats_row else 0,
            'tasks_completed': stats_row['tasks_completed'] if stats_row else 0,
            'career_readiness': stats_row['career_readiness'] if stats_row else 0,
            'current_streak': stats_row['current_streak'] if stats_row else 0,
            'skills_tracked': max(stats_row['skills_tracked'] if stats_row else 0, skills_count),
        }
    except Exception:
        return {
            'total_xp': 0,
            'tasks_completed': 0,
            'career_readiness': 0,
            'current_streak': 0,
            'skills_tracked': 0,
        }


def _get_skill_progress(db, user_id, onboarding):
    """Get skill progress data for the user."""
    skills_list = onboarding.get('skills', []) if onboarding else []
    skills_data = {}

    for skill in skills_list:
        try:
            skill_row = db.execute(
                'SELECT proficiency_level, tasks_completed, total_xp FROM skill_progress WHERE user_id = ? AND skill_name = ?',
                (user_id, skill)
            ).fetchone()

            skills_data[skill] = {
                'level': skill_row['proficiency_level'] if skill_row else 0,
                'tasksCompleted': skill_row['tasks_completed'] if skill_row else 0,
                'totalXp': skill_row['total_xp'] if skill_row else 0,
            }
        except Exception:
            skills_data[skill] = {
                'level': 0,
                'tasksCompleted': 0,
                'totalXp': 0,
            }

    return skills_data


def _get_resume_data(db, user_id):
    """Get the latest resume analysis data for this user."""
    try:
        row = db.execute(
            '''SELECT ats_score, overall_score, skills_found, recommendations
               FROM quick_analyses WHERE user_id = ?
               ORDER BY created_at DESC LIMIT 1''',
            (str(user_id),)
        ).fetchone()

        if row:
            return {
                'ats_score': row['ats_score'] or 0,
                'overall_score': row['overall_score'] or 0,
                'skills_found': json.loads(row['skills_found'] or '[]'),
                'recommendations': json.loads(row['recommendations'] or '[]'),
            }
    except Exception:
        pass

    return {
        'ats_score': 0,
        'overall_score': 0,
        'skills_found': [],
        'recommendations': [],
    }


def get_phase_label(phase):
    """Convert phase key to display label."""
    labels = {
        'pre-college': 'Pre-College',
        'college': 'College',
        'post-college': 'Post-College',
    }
    return labels.get(phase, 'Member')
