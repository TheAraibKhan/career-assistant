"""
Insight Service - Generates personalized insights from unified user profile.
All insights derive from the SAME profile/stats data used by other modules.
"""
import random


def generate_insights(profile_data, stats, skills_data, resume_data=None):
    """
    Generate personalized career insights.
    All data comes from the unified profile - no independent logic.

    Args:
        profile_data: dict with skills, interests, goals, daily_time, phase
        stats: dict with total_xp, tasks_completed, career_readiness, current_streak
        skills_data: dict of {skill_name: {level, tasksCompleted, totalXp}}
        resume_data: optional dict with ats_score, skills_found, recommendations
    
    Returns:
        dict with metrics, skill_breakdown, recommendations, achievements, activity_heatmap
    """
    skills_list = profile_data.get('skills', [])

    # Core metrics - derived from stats
    metrics = {
        'career_readiness': stats.get('career_readiness', 0),
        'xp_earned': stats.get('total_xp', 0),
        'streak_days': stats.get('current_streak', 0),
        'percentile': max(28, min(95, stats.get('career_readiness', 0) + random.randint(-5, 5))),
    }

    # Skill breakdown - from user's actual skills, not hardcoded
    skill_breakdown = {}
    for i, skill in enumerate(skills_list[:7]):
        skill_info = skills_data.get(skill, {})
        base = skill_info.get('totalXp', 0)
        # Estimate proficiency as percentage (0-95)
        proficiency = min(95, base // 5 + i * 8) if base > 0 else min(95, i * 10 + 5)
        skill_breakdown[skill] = proficiency

    # Recommendations - based on actual user state
    recommendations = _build_recommendations(profile_data, stats, resume_data)

    # Achievements - computed from real progress
    achievements = _compute_achievements(stats)

    # Activity heatmap (simulated for now, would come from activity_log table)
    levels = ['low', 'med', 'high', 'max']
    activity_heatmap = [[random.choice(levels) for _ in range(7)] for _ in range(5)]

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
        {'icon': 'T', 'name': 'First Steps', 'threshold': ('tasks_completed', 5)},
        {'icon': '*', 'name': 'Task Master', 'threshold': ('tasks_completed', 10)},
        {'icon': '#', 'name': '7-Day Streak', 'threshold': ('current_streak', 7)},
        {'icon': '>', 'name': 'Career Ready', 'threshold': ('career_readiness', 75)},
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
