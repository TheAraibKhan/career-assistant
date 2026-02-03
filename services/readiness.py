# Readiness assessment module
"""Calculate role readiness scores."""

from services.career_engine import get_role_skills


def calculate_readiness(role, user_skills=None):
    """Calculate readiness for a specific role."""
    if not user_skills:
        user_skills = []
    
    role_skills = get_role_skills(role)
    
    if not role_skills:
        return {
            'readiness_score': 30,
            'strengths': [],
            'gaps': ['No role data found'],
            'next_actions': ['Research the role requirements']
        }
    
    # Skill matching
    user_skills_lower = [s.lower() for s in user_skills]
    core_skills = role_skills.get('core', [])
    technical_skills = role_skills.get('technical', [])
    tools = role_skills.get('tools', [])
    soft_skills = role_skills.get('soft', [])
    
    # Calculate match percentages
    core_match = sum(1 for skill in core_skills if any(
        skill.lower() in user_skill for user_skill in user_skills_lower
    )) / len(core_skills) if core_skills else 0
    
    technical_match = sum(1 for skill in technical_skills if any(
        skill.lower() in user_skill for user_skill in user_skills_lower
    )) / len(technical_skills) if technical_skills else 0
    
    tools_match = sum(1 for skill in tools if any(
        skill.lower() in user_skill for user_skill in user_skills_lower
    )) / len(tools) if tools else 0
    
    # Weighted score
    readiness_score = int(
        (core_match * 40) +  # Core skills weighted heavier
        (technical_match * 35) +
        (tools_match * 20) +
        (5)  # Base credit
    )
    
    # Identify strengths
    strengths = []
    if core_match >= 0.7:
        strengths.append('Strong core skills foundation')
    if technical_match >= 0.6:
        strengths.append('Good technical knowledge')
    if tools_match >= 0.5:
        strengths.append('Familiar with key tools')
    if user_skills:
        strengths.append(f'{len(user_skills)} skills identified')
    
    # Identify gaps
    gaps = []
    missing_core = [s for s in core_skills if not any(
        s.lower() in user_skill for user_skill in user_skills_lower
    )]
    if missing_core:
        gaps.append(f'Missing core: {", ".join(missing_core[:3])}')
    
    missing_technical = [s for s in technical_skills if not any(
        s.lower() in user_skill for user_skill in user_skills_lower
    )]
    if missing_technical:
        gaps.append(f'Need to learn: {", ".join(missing_technical[:3])}')
    
    missing_tools = [s for s in tools if not any(
        s.lower() in user_skill for user_skill in user_skills_lower
    )]
    if missing_tools:
        gaps.append(f'Tool experience: {", ".join(missing_tools[:2])}')
    
    # Next actions
    next_actions = []
    if readiness_score < 40:
        next_actions.append('Start with foundational courses')
        next_actions.append('Build beginner projects')
        next_actions.append('Join community groups')
    elif readiness_score < 70:
        next_actions.append('Deepen technical knowledge')
        next_actions.append('Build intermediate projects')
        next_actions.append('Get relevant certifications')
    else:
        next_actions.append('Specialize in niche areas')
        next_actions.append('Build advanced projects')
        next_actions.append('Contribute to open source')
    
    next_actions.append('Update resume with proof of skills')
    
    return {
        'readiness_score': min(readiness_score, 100),
        'core_match_pct': round(core_match * 100),
        'technical_match_pct': round(technical_match * 100),
        'tools_match_pct': round(tools_match * 100),
        'strengths': strengths,
        'gaps': gaps,
        'next_actions': next_actions,
        'detailed_report': {
            'core_skills_status': 'Mastered' if core_match >= 0.8 else 'Learning' if core_match >= 0.4 else 'Start here',
            'technical_depth': 'Advanced' if technical_match >= 0.8 else 'Intermediate' if technical_match >= 0.4 else 'Beginner',
            'tools_proficiency': 'Expert' if tools_match >= 0.8 else 'Proficient' if tools_match >= 0.4 else 'Novice'
        }
    }
