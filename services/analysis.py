def analyze_profile(interest, level):
    """
    Core analysis engine that decides best career + confidence score
    """

    career_map = {
        "tech": "Software Engineer",
        "ai": "AI Engineer",
        "data": "Data Scientist",
        "design": "UI/UX Designer",
        "business": "Business Analyst"
    }

    confidence_map = {
        "beginner": 50,
        "intermediate": 70
    }

    career = career_map.get(interest, "Invalid")
    confidence = confidence_map.get(level, 40)

    return {
        "career": career,
        "confidence": confidence
    }
