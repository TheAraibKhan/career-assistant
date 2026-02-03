# services/roles.py
"""
Role progression engine - Maps interests and levels to realistic career roles.
Supports 5 experience levels: beginner, junior, intermediate, senior, lead
"""

# Role mapping: interest -> level -> role title
ROLE_ENGINE = {
    "backend": {
        "beginner": "Junior Backend Engineer",
        "junior": "Backend Engineer",
        "intermediate": "Senior Backend Engineer",
        "senior": "Staff Backend Engineer",
        "lead": "Backend Engineering Manager"
    },
    "frontend": {
        "beginner": "Junior Frontend Engineer",
        "junior": "Frontend Engineer",
        "intermediate": "Senior Frontend Engineer",
        "senior": "Staff Frontend Engineer",
        "lead": "Frontend Engineering Manager"
    },
    "fullstack": {
        "beginner": "Junior Full-Stack Engineer",
        "junior": "Full-Stack Engineer",
        "intermediate": "Senior Full-Stack Engineer",
        "senior": "Staff Full-Stack Engineer",
        "lead": "Engineering Manager"
    },
    "ml": {
        "beginner": "ML Engineer Intern",
        "junior": "ML Engineer",
        "intermediate": "Senior ML Engineer",
        "senior": "Staff ML Engineer",
        "lead": "ML Engineering Manager"
    },
    "nlp": {
        "beginner": "NLP Engineer Intern",
        "junior": "NLP Engineer",
        "intermediate": "Senior NLP Engineer",
        "senior": "Staff NLP Engineer",
        "lead": "NLP Engineering Manager"
    },
    "data": {
        "beginner": "Data Analyst",
        "junior": "Junior Data Scientist",
        "intermediate": "Data Scientist",
        "senior": "Senior Data Scientist",
        "lead": "Data Science Manager"
    },
    "ai": {
        "beginner": "AI Engineer Intern",
        "junior": "AI Engineer",
        "intermediate": "Senior AI Engineer",
        "senior": "Staff AI Engineer",
        "lead": "AI Engineering Manager"
    },
    "mlops": {
        "beginner": "MLOps Engineer Intern",
        "junior": "MLOps Engineer",
        "intermediate": "Senior MLOps Engineer",
        "senior": "Staff MLOps Engineer",
        "lead": "MLOps Engineering Manager"
    },
    "data_engineering": {
        "beginner": "Data Engineering Intern",
        "junior": "Data Engineer",
        "intermediate": "Senior Data Engineer",
        "senior": "Staff Data Engineer",
        "lead": "Data Engineering Manager"
    },
    "design": {
        "beginner": "Junior Product Designer",
        "junior": "Product Designer",
        "intermediate": "Senior Product Designer",
        "senior": "Lead Designer",
        "lead": "Design Manager"
    },
    "product": {
        "beginner": "Associate Product Manager",
        "junior": "Product Manager",
        "intermediate": "Senior Product Manager",
        "senior": "Principal Product Manager",
        "lead": "Director of Product"
    }
}


def get_role_for_profile(interest, level):
    """
    Get the recommended role based on interest and level.
    
    Args:
        interest (str): Career interest (backend, frontend, fullstack, ml, nlp, data, ai, mlops, data_engineering, design, product)
        level (str): Experience level (beginner, junior, intermediate, senior, lead)
    
    Returns:
        dict: {
            "role": str,
            "tier": str (the level),
            "next_role": str (what comes after this role)
        }
    """
    interest = interest.lower()
    level = level.lower()
    
    # Validate inputs
    if interest not in ROLE_ENGINE:
        return {
            "role": "Career Assistant",
            "tier": level,
            "next_role": None
        }
    
    if level not in ROLE_ENGINE[interest]:
        return {
            "role": "Career Assistant",
            "tier": level,
            "next_role": None
        }
    
    role = ROLE_ENGINE[interest][level]
    
    # Determine next role in progression
    levels = ["beginner", "junior", "intermediate", "senior", "lead"]
    current_idx = levels.index(level)
    next_role = None
    
    if current_idx < len(levels) - 1:
        next_level = levels[current_idx + 1]
        next_role = ROLE_ENGINE[interest][next_level]
    
    return {
        "role": role,
        "tier": level,
        "next_role": next_role
    }


# Valid levels for the system
EXPERIENCE_LEVELS = [
    ("beginner", "Beginner (0–1 years)"),
    ("junior", "Junior (1–2 years)"),
    ("intermediate", "Intermediate (2–4 years)"),
    ("senior", "Senior (4–7 years)"),
    ("lead", "Lead (7+ years)")
]

INTERESTS = [
    ("backend", "Backend Engineering"),
    ("frontend", "Frontend Engineering"),
    ("fullstack", "Full-Stack Engineering"),
    ("ml", "Machine Learning"),
    ("nlp", "Natural Language Processing"),
    ("data", "Data Science"),
    ("ai", "AI Engineering"),
    ("mlops", "MLOps Engineering"),
    ("data_engineering", "Data Engineering"),
    ("design", "Product Design"),
    ("product", "Product Management")
]
