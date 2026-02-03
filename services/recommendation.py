from services.roles import get_role_for_profile


def analyze_profile(interest, level):
    """
    Analyze profile and recommend a career role.
    Maps interest + level -> specific job role.
    
    Args:
        interest (str): Career interest
        level (str): Experience level (beginner, junior, intermediate, senior, lead)
    
    Returns:
        dict: {
            "career": str (job role title),
            "tier": str (level),
            "confidence": int (0-100),
            "next_role": str (what comes next)
        }
    """
    
    interest = interest.lower().strip()
    level = level.lower().strip()
    
    # Use the advanced role engine
    role_info = get_role_for_profile(interest, level)
    
    # Determine confidence score based on level progression
    confidence_mapping = {
        "beginner": 65,
        "junior": 75,
        "intermediate": 80,
        "senior": 85,
        "lead": 90
    }
    
    confidence = confidence_mapping.get(level, 60)
    
    # Adjust confidence based on whether the interest is valid
    if interest not in ["backend", "frontend", "fullstack", "ml", "nlp", "data", "ai", "mlops", "data_engineering", "design", "product"]:
        confidence = 40
    
    return {
        "career": role_info["role"],
        "tier": role_info["tier"],
        "confidence": confidence,
        "next_role": role_info["next_role"],
        "interest": interest
    }
