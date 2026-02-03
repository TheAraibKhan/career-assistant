# services/recommendations_engine.py
"""
Enhanced Recommendations Engine with multiple variants and detailed reasoning
Provides structured recommendations with "Why?" explanations
"""

from services.roles import get_role_for_profile
from services.skill_gap import get_skill_gap


def get_detailed_recommendation(interest, level, acquired_skills):
    """
    Generate detailed recommendation with multiple variants and reasoning.
    
    Args:
        interest (str): Career interest
        level (str): Experience level
        acquired_skills (list): User's current skills
    
    Returns:
        dict: {
            "primary_role": str,
            "role_variants": list of alternative roles,
            "confidence": int (0-100),
            "confidence_level": str (Low/Medium/High),
            "why_this_role": {
                "skill_alignment": str,
                "experience_suitability": str,
                "industry_demand": str,
                "gap_feasibility": str
            },
            "tier": str,
            "next_role": str
        }
    """
    
    # Get primary role
    role_info = get_role_for_profile(interest, level)
    primary_role = role_info["role"]
    tier = role_info["tier"]
    next_role = role_info["next_role"]
    
    # Get skill requirements
    skill_gap = get_skill_gap(primary_role)
    core_skills = skill_gap["core_skills"]
    
    # Calculate confidence
    confidence = _calculate_confidence(interest, level, acquired_skills, core_skills)
    confidence_level = _interpret_confidence(confidence)
    
    # Get role variants
    variants = _get_role_variants(interest, level)
    
    # Generate "why" reasoning
    why_reasoning = _generate_why_reasoning(
        primary_role, 
        tier, 
        acquired_skills, 
        core_skills,
        interest
    )
    
    return {
        "primary_role": primary_role,
        "role_variants": variants,
        "confidence": confidence,
        "confidence_level": confidence_level,
        "why_this_role": why_reasoning,
        "tier": tier,
        "next_role": next_role
    }


def _calculate_confidence(interest, level, acquired_skills, core_skills):
    """Calculate confidence score based on multiple factors."""
    
    # Base confidence by level
    level_confidence = {
        "beginner": 60,
        "junior": 70,
        "intermediate": 80,
        "advanced": 85,
        "expert": 90
    }
    
    base = level_confidence.get(level, 65)
    
    # Adjust based on skill match
    if core_skills:
        core_skills_lower = [s["name"].lower() for s in core_skills]
        acquired_lower = [a.lower() for a in acquired_skills]
        
        matched = sum(1 for core in core_skills_lower 
                     if any(acq in core or core in acq for acq in acquired_lower))
        match_ratio = matched / len(core_skills) if core_skills else 0
        
        # Adjust confidence based on skill match
        if match_ratio > 0.8:
            base += 10
        elif match_ratio < 0.3:
            base -= 10
    
    # Cap confidence
    return min(max(base, 40), 95)


def _interpret_confidence(confidence):
    """Convert numeric confidence to human-readable level."""
    if confidence >= 80:
        return "High"
    elif confidence >= 60:
        return "Medium"
    else:
        return "Low"


def _get_role_variants(interest, level):
    """Get alternative role variants for the same interest-level combo."""
    
    variants_map = {
        ("ai", "beginner"): ["ML Intern", "Data Scientist Trainee", "AI Associate"],
        ("ai", "junior"): ["ML Engineer", "Data Engineer (AI focus)", "AI Specialist"],
        ("ai", "intermediate"): ["AI Engineer", "ML Architect", "Senior Data Scientist"],
        ("ai", "advanced"): ["Senior AI Engineer", "ML Lead", "Director of AI"],
        ("ai", "expert"): ["VP AI/ML", "AI Research Scientist", "Chief AI Officer"],
        
        ("tech", "beginner"): ["Junior Developer", "Frontend Developer", "Backend Developer Trainee"],
        ("tech", "junior"): ["Frontend Developer", "Backend Developer", "Full-Stack Developer"],
        ("tech", "intermediate"): ["Software Engineer", "Senior Developer", "Tech Lead"],
        ("tech", "advanced"): ["Senior Software Engineer", "Engineering Manager", "Architect"],
        ("tech", "expert"): ["Staff Engineer", "VP Engineering", "CTO"],
        
        ("data", "beginner"): ["Data Analyst", "Analytics Associate", "BI Developer Trainee"],
        ("data", "junior"): ["Data Analyst", "Junior Data Scientist", "Analytics Engineer"],
        ("data", "intermediate"): ["Data Scientist", "Analytics Engineer", "Data Engineer"],
        ("data", "advanced"): ["Senior Data Scientist", "Data Science Lead", "Analytics Director"],
        ("data", "expert"): ["VP Data Science", "Chief Data Officer", "Data Strategy Lead"],
        
        ("design", "beginner"): ["UI/UX Junior", "Graphic Designer", "Web Designer"],
        ("design", "junior"): ["Product Designer", "UX Designer", "UI Designer"],
        ("design", "intermediate"): ["Senior Product Designer", "Design Lead", "UX Strategist"],
        ("design", "advanced"): ["Design Manager", "Head of Design", "Chief Design Officer"],
        ("design", "expert"): ["VP Design", "Design Director", "Chief Creative Officer"],
        
        ("business", "beginner"): ["Business Analyst", "Product Associate", "Operations Analyst"],
        ("business", "junior"): ["Product Manager", "Business Analyst", "Strategy Analyst"],
        ("business", "intermediate"): ["Senior Product Manager", "Product Lead", "Strategy Manager"],
        ("business", "advanced"): ["Principal Product Manager", "Director of Product", "VP Product"],
        ("business", "expert"): ["Chief Product Officer", "SVP Product", "President/CEO"],
    }
    
    key = (interest.lower(), level.lower())
    return variants_map.get(key, [])


def _generate_why_reasoning(role, tier, acquired_skills, core_skills, interest):
    """Generate structured reasoning for the recommendation."""
    
    # Skill alignment reasoning
    if core_skills:
        core_skill_names = [s["name"] for s in core_skills]
        acquired_lower = [a.lower() for a in acquired_skills]
        
        matched = [s for s in core_skill_names 
                  if any(a in s.lower() or s.lower() in a for a in acquired_lower)]
        matched_count = len(matched)
        total = len(core_skills)
        
        if matched_count / total > 0.7:
            skill_alignment = f"You have {matched_count} of {total} core skills ({matched_count*100//total}%). Strong foundation for {role}."
        elif matched_count / total > 0.4:
            skill_alignment = f"You have {matched_count} of {total} core skills ({matched_count*100//total}%). Solid foundation, but some gaps remain."
        else:
            skill_alignment = f"You have {matched_count} of {total} core skills ({matched_count*100//total}%). You'll need to develop foundational skills."
    else:
        skill_alignment = "Your skills provide a foundation for this role. Specialized training will help."
    
    # Experience suitability
    level_suitability = {
        "beginner": "Perfect entry-level position to start your career in this field.",
        "junior": "Ideal for consolidating your skills and moving into more independent work.",
        "intermediate": "Natural progression that leverages your growing expertise.",
        "advanced": "Positions you as a senior contributor with leadership potential.",
        "expert": "Top-tier role for industry veterans and thought leaders."
    }
    experience_suitability = level_suitability.get(tier, "Well-matched for your experience level.")
    
    # Industry demand
    demand_insights = {
        "ai": "AI/ML roles are in extremely high demand. Companies are investing heavily in AI talent.",
        "tech": "Software engineering roles are consistently in high demand across all sectors.",
        "data": "Data science roles are critical as companies become more data-driven.",
        "design": "Product and UX design roles are increasingly valued in tech companies.",
        "business": "Product management is one of the most sought-after roles in tech."
    }
    industry_demand = demand_insights.get(interest, "This role has strong industry demand.")
    
    # Gap feasibility
    if core_skills:
        high_priority_gaps = [s for s in core_skills if s["priority"] == "High"]
        gap_count = len(high_priority_gaps)
        
        if gap_count <= 2:
            gap_feasibility = f"You need to master {gap_count} critical skill(s). This is very achievable with focused effort (3-6 months)."
        elif gap_count <= 4:
            gap_feasibility = f"You need to develop {gap_count} core skills. This is realistic with a 6-12 month learning plan."
        else:
            gap_feasibility = f"You need to develop {gap_count} core skills. This requires a structured 12+ month learning journey."
    else:
        gap_feasibility = "Clear learning path with manageable skill gaps."
    
    return {
        "skill_alignment": skill_alignment,
        "experience_suitability": experience_suitability,
        "industry_demand": industry_demand,
        "gap_feasibility": gap_feasibility
    }
