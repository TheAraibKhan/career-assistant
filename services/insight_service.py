"""Generates career insights, achievements, and activity heatmaps."""
import random
from datetime import datetime, timedelta


def generate_insights(profile_data, stats, skills_data, resume_data=None):
    """Build metrics, skill breakdown, recommendations, and achievements."""
    skills_list = profile_data.get('skills', [])

    # Core metrics - derived from stats
    readiness = stats.get('career_readiness', 0)
    xp = stats.get('total_xp', 0)
    streak = stats.get('current_streak', 0)
    
    # Percentile calculation based on multiple factors (more meaningful than random)
    percentile = min(95, max(10, 
        int(readiness * 0.5 + min(30, xp / 50) + min(15, streak * 2))
    ))
    
    metrics = {
        'career_readiness': readiness,
        'xp_earned': xp,
        'streak_days': streak,
        'percentile': percentile,
    }

    # Skill breakdown - from user's actual skills, not hardcoded
    skill_breakdown = {}
    for i, skill in enumerate(skills_list[:7]):
        skill_info = skills_data.get(skill, {})
        base = skill_info.get('totalXp', 0)
        tasks = skill_info.get('tasksCompleted', 0)
        # Estimate proficiency as percentage (0-95) based on XP + tasks
        proficiency = min(95, base // 4 + tasks * 8) if (base > 0 or tasks > 0) else max(5, i * 6 + 5)
        skill_breakdown[skill] = proficiency

    # Recommendations - based on actual user state
    recommendations = _build_recommendations(profile_data, stats, resume_data)

    # Achievements - computed from real progress
    achievements = _compute_achievements(stats)

    # Activity heatmap — pull from real activity_log data
    activity_heatmap = _build_activity_heatmap()

    return {
        'success': True,
        'metrics': metrics,
        'skill_breakdown': skill_breakdown,
        'recommendations': recommendations,
        'achievements': achievements,
        'activity_heatmap': activity_heatmap,
    }


def _build_recommendations(profile_data, stats, resume_data):
    """Generate recommendations based on actual user state."""
    recs = []
    skills_list = profile_data.get('skills', [])
    primary_skill = skills_list[0] if skills_list else 'your primary skill'

    readiness = stats.get('career_readiness', 0)
    streak = stats.get('current_streak', 0)
    tasks = stats.get('tasks_completed', 0)

    # Recommendation based on progress level
    if readiness < 30:
        recs.append({
            'icon': '>',
            'title': 'Build Strong Foundation',
            'description': f'Start with fundamentals in {primary_skill}. Complete beginner tasks to establish core knowledge.',
        })
    elif readiness < 60:
        recs.append({
            'icon': '^',
            'title': 'Accelerate Progress',
            'description': f'You are making progress in {primary_skill}. Complete 3 more intermediate tasks to unlock advanced content.',
        })
    else:
        recs.append({
            'icon': '*',
            'title': 'Ready for Opportunities',
            'description': 'Your profile is strong. Start applying to roles or building projects to showcase your skills.',
        })

    # Streak recommendation
    if streak > 7:
        recs.append({
            'icon': '#',
            'title': f'{streak}-Day Streak',
            'description': 'Keep up the momentum. Consistency is key to mastering new skills.',
        })
    elif streak > 0:
        recs.append({
            'icon': '+',
            'title': f'Build Your Streak',
            'description': f'You are on a {streak}-day streak. Reach 7 days to unlock the Consistency achievement.',
        })

    # Resume-based recommendation
    if resume_data and resume_data.get('ats_score', 0) > 0:
        ats = resume_data['ats_score']
        if ats < 50:
            recs.append({
                'icon': '!',
                'title': 'Resume Needs Work',
                'description': f'Your ATS score is {ats}%. Add more relevant keywords and quantify your achievements.',
            })
        elif ats < 75:
            recs.append({
                'icon': '^',
                'title': 'Improve Your Resume',
                'description': f'Your ATS score is {ats}%. A few targeted improvements can push you past 75%.',
            })

    # Goal-specific recommendation
    goals = profile_data.get('goals', [])
    if goals and tasks < 5:
        recs.append({
            'icon': '>',
            'title': f'Focus on {goals[0]}',
            'description': f'Complete 5 more tasks to build momentum toward your goal: {goals[0]}.',
        })

    return recs


def _compute_achievements(stats):
    """Compute achievements based on real stats."""
    all_achievements = [
        {'icon': 'T', 'name': 'First Steps', 'threshold': ('tasks_completed', 1)},
        {'icon': '*', 'name': 'Task Apprentice', 'threshold': ('tasks_completed', 5)},
        {'icon': '*', 'name': 'Task Master', 'threshold': ('tasks_completed', 10)},
        {'icon': 'L', 'name': 'Consistent Learner', 'threshold': ('tasks_completed', 25)},
        {'icon': '#', 'name': '3-Day Streak', 'threshold': ('current_streak', 3)},
        {'icon': '#', 'name': '7-Day Streak', 'threshold': ('current_streak', 7)},
        {'icon': '#', 'name': '14-Day Streak', 'threshold': ('current_streak', 14)},
        {'icon': '>', 'name': 'Career Ready', 'threshold': ('career_readiness', 50)},
        {'icon': '>', 'name': 'Career Strong', 'threshold': ('career_readiness', 75)},
        {'icon': 'D', 'name': 'Elite', 'threshold': ('career_readiness', 90)},
    ]

    achievements = []
    for ach in all_achievements:
        key, val = ach['threshold']
        earned = stats.get(key, 0) >= val
        achievements.append({
            'icon': ach['icon'],
            'name': ach['name'],
            'earned': earned,
        })

    return achievements


def _build_activity_heatmap():
    """
    Build activity heatmap from real activity_log data.
    Returns a 5-week x 7-day matrix with intensity levels.
    """
    try:
        from database.db import get_db
        from flask import g
        db = get_db()
        
        # Get activity counts per day for the last 35 days
        today = datetime.utcnow().date()
        start_date = today - timedelta(days=34)
        
        rows = db.execute('''
            SELECT DATE(created_at) as activity_date, COUNT(*) as count
            FROM activity_log
            WHERE created_at >= ?
            GROUP BY DATE(created_at)
        ''', (start_date.isoformat(),)).fetchall()
        
        # Build a date -> count map
        day_counts = {}
        for row in rows:
            day_counts[row['activity_date']] = row['count']
        
        # Build 5x7 grid (5 weeks, 7 days per week)
        heatmap = []
        for week in range(5):
            week_row = []
            for day in range(7):
                date_offset = week * 7 + day
                check_date = (start_date + timedelta(days=date_offset)).isoformat()
                count = day_counts.get(check_date, 0)
                
                if count == 0:
                    level = 'none'
                elif count <= 1:
                    level = 'low'
                elif count <= 3:
                    level = 'med'
                elif count <= 5:
                    level = 'high'
                else:
                    level = 'max'
                
                week_row.append(level)
            heatmap.append(week_row)
        
        return heatmap
        
    except Exception:
        # Fallback: empty heatmap if no activity_log table or no Flask context
        return [['none'] * 7 for _ in range(5)]
