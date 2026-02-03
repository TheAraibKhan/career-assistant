# Skill gap analysis module
"""Analyze skill gaps for career paths."""

SKILL_REQUIREMENTS = {
    # ==================== TECH / SOFTWARE ====================
    "Software Intern": {
        "core": [
            {
                "name": "Python",
                "priority": "High",
                "weight": 20,
                "reason": "Industry-standard language for learning",
                "impact": "Foundation for all development work"
            },
            {
                "name": "Git",
                "priority": "High",
                "weight": 15,
                "reason": "Essential for team collaboration",
                "impact": "Required for any professional role"
            },
            {
                "name": "Problem Solving",
                "priority": "High",
                "weight": 15,
                "reason": "Core competency for developers",
                "impact": "Ability to debug and solve issues"
            }
        ],
        "optional": [
            {
                "name": "JavaScript",
                "priority": "Medium",
                "weight": 10,
                "reason": "Useful for web development exposure"
            }
        ]
    },
    "Software Developer": {
        "core": [
            {
                "name": "Python",
                "priority": "High",
                "weight": 20,
                "reason": "Primary backend language",
                "impact": "Build production applications"
            },
            {
                "name": "Git",
                "priority": "High",
                "weight": 15,
                "reason": "Version control for teams",
                "impact": "Manage code across projects"
            },
            {
                "name": "Data Structures",
                "priority": "High",
                "weight": 18,
                "reason": "Foundation for efficient coding",
                "impact": "Write optimized code"
            },
            {
                "name": "APIs & Web Basics",
                "priority": "Medium",
                "weight": 12,
                "reason": "Communication between systems",
                "impact": "Build backend services"
            }
        ],
        "optional": [
            {
                "name": "Databases (SQL)",
                "priority": "Medium",
                "weight": 10,
                "reason": "Store and query data"
            }
        ]
    },
    "Software Engineer": {
        "core": [
            {
                "name": "Python",
                "priority": "High",
                "weight": 18,
                "reason": "Fluent programming language",
                "impact": "Write clean, maintainable code"
            },
            {
                "name": "Data Structures & Algorithms",
                "priority": "High",
                "weight": 20,
                "reason": "Efficient solution design",
                "impact": "Optimize performance at scale"
            },
            {
                "name": "System Design",
                "priority": "High",
                "weight": 18,
                "reason": "Design scalable systems",
                "impact": "Architect production systems"
            },
            {
                "name": "Databases & SQL",
                "priority": "High",
                "weight": 15,
                "reason": "Data persistence and queries",
                "impact": "Build data-driven applications"
            }
        ],
        "optional": [
            {
                "name": "Cloud Platforms (AWS/GCP)",
                "priority": "Medium",
                "weight": 10,
                "reason": "Deployment and scaling"
            }
        ]
    },
    "Senior Software Engineer": {
        "core": [
            {
                "name": "System Design & Architecture",
                "priority": "High",
                "weight": 25,
                "reason": "Design large-scale systems",
                "impact": "Lead technical decisions"
            },
            {
                "name": "Advanced Algorithms",
                "priority": "High",
                "weight": 15,
                "reason": "Optimize complex problems",
                "impact": "Build high-performance solutions"
            },
            {
                "name": "Leadership & Code Review",
                "priority": "High",
                "weight": 18,
                "reason": "Mentor junior developers",
                "impact": "Improve team code quality"
            },
            {
                "name": "Cloud Architecture",
                "priority": "High",
                "weight": 15,
                "reason": "Design cloud solutions",
                "impact": "Build reliable, scalable systems"
            }
        ],
        "optional": [
            {
                "name": "Open Source Contribution",
                "priority": "Medium",
                "weight": 8,
                "reason": "Community involvement"
            }
        ]
    },
    "Staff Engineer / Tech Lead": {
        "core": [
            {
                "name": "System Architecture & Design",
                "priority": "High",
                "weight": 25,
                "reason": "Enterprise-level systems",
                "impact": "Set technical direction"
            },
            {
                "name": "Technical Leadership",
                "priority": "High",
                "weight": 22,
                "reason": "Lead across teams",
                "impact": "Influence company tech strategy"
            },
            {
                "name": "Mentorship & Culture",
                "priority": "High",
                "weight": 18,
                "reason": "Develop team capabilities",
                "impact": "Build strong engineering teams"
            },
            {
                "name": "Business Acumen",
                "priority": "Medium",
                "weight": 15,
                "reason": "Understand business impact",
                "impact": "Make strategic technical decisions"
            }
        ],
        "optional": []
    },

    # ==================== AI / ML ====================
    "ML Intern": {
        "core": [
            {
                "name": "Python",
                "priority": "High",
                "weight": 25,
                "reason": "ML development language",
                "impact": "Build ML models"
            },
            {
                "name": "Statistics Basics",
                "priority": "High",
                "weight": 20,
                "reason": "Understand ML fundamentals",
                "impact": "Grasp ML concepts"
            },
            {
                "name": "Machine Learning Basics",
                "priority": "High",
                "weight": 20,
                "reason": "Learn ML algorithms",
                "impact": "Build simple models"
            }
        ],
        "optional": [
            {
                "name": "Linear Algebra",
                "priority": "Medium",
                "weight": 15,
                "reason": "Math foundation"
            }
        ]
    },
    "ML Engineer": {
        "core": [
            {
                "name": "Python",
                "priority": "High",
                "weight": 20,
                "reason": "Production ML development",
                "impact": "Write production code"
            },
            {
                "name": "Machine Learning",
                "priority": "High",
                "weight": 25,
                "reason": "Build ML systems",
                "impact": "Create predictive models"
            },
            {
                "name": "Data Processing (Pandas/NumPy)",
                "priority": "High",
                "weight": 18,
                "reason": "Prepare training data",
                "impact": "Feature engineering"
            },
            {
                "name": "Statistics",
                "priority": "High",
                "weight": 15,
                "reason": "Model evaluation",
                "impact": "Validate model quality"
            }
        ],
        "optional": [
            {
                "name": "MLOps",
                "priority": "Medium",
                "weight": 10,
                "reason": "Deploy ML models"
            }
        ]
    },
    "AI Engineer": {
        "core": [
            {
                "name": "Deep Learning",
                "priority": "High",
                "weight": 25,
                "reason": "Advanced AI models",
                "impact": "Build neural networks"
            },
            {
                "name": "Machine Learning",
                "priority": "High",
                "weight": 20,
                "reason": "ML fundamentals",
                "impact": "Understand algorithms"
            },
            {
                "name": "Python",
                "priority": "High",
                "weight": 15,
                "reason": "AI development",
                "impact": "Implement AI systems"
            },
            {
                "name": "Statistics & Math",
                "priority": "High",
                "weight": 18,
                "reason": "AI theory",
                "impact": "Understand algorithms deeply"
            }
        ],
        "optional": [
            {
                "name": "NLP / Computer Vision",
                "priority": "Medium",
                "weight": 12,
                "reason": "Specialized AI domains"
            }
        ]
    },
    "Senior AI Engineer": {
        "core": [
            {
                "name": "Advanced Deep Learning",
                "priority": "High",
                "weight": 25,
                "reason": "Newest models",
                "impact": "Build state-of-the-art AI"
            },
            {
                "name": "Research & Innovation",
                "priority": "High",
                "weight": 20,
                "reason": "Push AI boundaries",
                "impact": "Contribute to field"
            },
            {
                "name": "System Design for ML",
                "priority": "High",
                "weight": 18,
                "reason": "Scale AI systems",
                "impact": "Production AI systems"
            }
        ],
        "optional": []
    },
    "AI Architect / Research Scientist": {
        "core": [
            {
                "name": "AI Research",
                "priority": "High",
                "weight": 30,
                "reason": "Advance AI field",
                "impact": "Published research"
            },
            {
                "name": "System Architecture",
                "priority": "High",
                "weight": 20,
                "reason": "Design large AI systems",
                "impact": "Enterprise AI solutions"
            },
            {
                "name": "Leadership",
                "priority": "High",
                "weight": 18,
                "reason": "Guide AI strategy",
                "impact": "Shape company direction"
            }
        ],
        "optional": []
    },

    # ==================== DATA ====================
    "Data Analyst Trainee": {
        "core": [
            {
                "name": "SQL",
                "priority": "High",
                "weight": 25,
                "reason": "Query databases",
                "impact": "Extract data"
            },
            {
                "name": "Excel",
                "priority": "High",
                "weight": 20,
                "reason": "Analyze spreadsheets",
                "impact": "Perform analysis"
            },
            {
                "name": "Data Visualization",
                "priority": "High",
                "weight": 20,
                "reason": "Present findings",
                "impact": "Create dashboards"
            }
        ],
        "optional": [
            {
                "name": "Python",
                "priority": "Medium",
                "weight": 15,
                "reason": "Automate analysis"
            }
        ]
    },
    "Data Analyst": {
        "core": [
            {
                "name": "SQL",
                "priority": "High",
                "weight": 25,
                "reason": "Query large datasets",
                "impact": "Extract insights"
            },
            {
                "name": "Data Visualization",
                "priority": "High",
                "weight": 20,
                "reason": "Create reports",
                "impact": "Communicate findings"
            },
            {
                "name": "Statistical Analysis",
                "priority": "High",
                "weight": 18,
                "reason": "Analyze trends",
                "impact": "Drive decisions"
            },
            {
                "name": "Excel / Python",
                "priority": "High",
                "weight": 15,
                "reason": "Data manipulation",
                "impact": "Clean and prepare data"
            }
        ],
        "optional": []
    },
    "Data Scientist": {
        "core": [
            {
                "name": "Machine Learning",
                "priority": "High",
                "weight": 25,
                "reason": "Build predictive models",
                "impact": "Drive predictions"
            },
            {
                "name": "Python",
                "priority": "High",
                "weight": 22,
                "reason": "Data science development",
                "impact": "Implement models"
            },
            {
                "name": "Statistics",
                "priority": "High",
                "weight": 20,
                "reason": "Statistical modeling",
                "impact": "Validate results"
            },
            {
                "name": "SQL",
                "priority": "High",
                "weight": 15,
                "reason": "Query data",
                "impact": "Access data"
            }
        ],
        "optional": [
            {
                "name": "Deep Learning",
                "priority": "Medium",
                "weight": 12,
                "reason": "Advanced modeling"
            }
        ]
    },
    "Senior Data Scientist": {
        "core": [
            {
                "name": "Advanced ML & Deep Learning",
                "priority": "High",
                "weight": 25,
                "reason": "Build complex models",
                "impact": "Solve hard problems"
            },
            {
                "name": "MLOps & Deployment",
                "priority": "High",
                "weight": 20,
                "reason": "Productionize models",
                "impact": "Models in production"
            },
            {
                "name": "Leadership",
                "priority": "High",
                "weight": 18,
                "reason": "Mentor junior scientists",
                "impact": "Team growth"
            }
        ],
        "optional": []
    },
    "Principal Data Scientist / Head of Data": {
        "core": [
            {
                "name": "Data Strategy",
                "priority": "High",
                "weight": 25,
                "reason": "Define data vision",
                "impact": "Company data strategy"
            },
            {
                "name": "Leadership",
                "priority": "High",
                "weight": 25,
                "reason": "Manage teams",
                "impact": "Build data organization"
            },
            {
                "name": "Business Acumen",
                "priority": "High",
                "weight": 20,
                "reason": "Align to business",
                "impact": "Business impact"
            }
        ],
        "optional": []
    },

    # ==================== DESIGN ====================
    "Junior UI/UX Designer": {
        "core": [
            {
                "name": "Figma",
                "priority": "High",
                "weight": 30,
                "reason": "Design tool mastery",
                "impact": "Create designs"
            },
            {
                "name": "UI Design Principles",
                "priority": "High",
                "weight": 25,
                "reason": "Understand design fundamentals",
                "impact": "Create usable interfaces"
            },
            {
                "name": "Design Systems",
                "priority": "Medium",
                "weight": 20,
                "reason": "Consistent design",
                "impact": "Maintain brand"
            }
        ],
        "optional": []
    },
    "UI/UX Designer": {
        "core": [
            {
                "name": "UX Research",
                "priority": "High",
                "weight": 25,
                "reason": "User insights",
                "impact": "Design for users"
            },
            {
                "name": "Wireframing & Prototyping",
                "priority": "High",
                "weight": 25,
                "reason": "Design thinking",
                "impact": "Test ideas"
            },
            {
                "name": "Figma & Design Tools",
                "priority": "High",
                "weight": 20,
                "reason": "Create high-fidelity designs",
                "impact": "Professional designs"
            },
            {
                "name": "User Testing",
                "priority": "High",
                "weight": 15,
                "reason": "Validate designs",
                "impact": "Improve UX"
            }
        ],
        "optional": []
    },
    "Senior UI/UX Designer": {
        "core": [
            {
                "name": "Design Leadership",
                "priority": "High",
                "weight": 25,
                "reason": "Lead design vision",
                "impact": "Shape product design"
            },
            {
                "name": "User Research & Strategy",
                "priority": "High",
                "weight": 25,
                "reason": "Strategic thinking",
                "impact": "Impact product strategy"
            },
            {
                "name": "Design Systems & Scale",
                "priority": "High",
                "weight": 20,
                "reason": "Design at scale",
                "impact": "Consistency across products"
            }
        ],
        "optional": []
    },
    "Lead UX Designer": {
        "core": [
            {
                "name": "Design Strategy",
                "priority": "High",
                "weight": 30,
                "reason": "Long-term vision",
                "impact": "Shape product"
            },
            {
                "name": "Leadership & Mentorship",
                "priority": "High",
                "weight": 25,
                "reason": "Develop designers",
                "impact": "Team growth"
            },
            {
                "name": "Stakeholder Management",
                "priority": "High",
                "weight": 20,
                "reason": "Align with business",
                "impact": "Execute strategy"
            }
        ],
        "optional": []
    },
    "Design Director / Head of Design": {
        "core": [
            {
                "name": "Design Vision & Strategy",
                "priority": "High",
                "weight": 30,
                "reason": "Set company direction",
                "impact": "Brand & product"
            },
            {
                "name": "Leadership",
                "priority": "High",
                "weight": 25,
                "reason": "Lead design org",
                "impact": "Build team"
            },
            {
                "name": "Business Strategy",
                "priority": "High",
                "weight": 20,
                "reason": "Business outcomes",
                "impact": "ROI of design"
            }
        ],
        "optional": []
    },

    # ==================== BUSINESS ====================
    "Business Analyst Trainee": {
        "core": [
            {
                "name": "Data Analysis Basics",
                "priority": "High",
                "weight": 25,
                "reason": "Analyze business data",
                "impact": "Extract insights"
            },
            {
                "name": "SQL Basics",
                "priority": "High",
                "weight": 20,
                "reason": "Query databases",
                "impact": "Access data"
            },
            {
                "name": "Excel",
                "priority": "High",
                "weight": 20,
                "reason": "Data manipulation",
                "impact": "Create reports"
            },
            {
                "name": "Communication",
                "priority": "Medium",
                "weight": 15,
                "reason": "Present findings",
                "impact": "Influence decisions"
            }
        ],
        "optional": []
    },
    "Business Analyst": {
        "core": [
            {
                "name": "Requirements Gathering",
                "priority": "High",
                "weight": 25,
                "reason": "Understand needs",
                "impact": "Define solutions"
            },
            {
                "name": "Data Analysis",
                "priority": "High",
                "weight": 22,
                "reason": "Business insights",
                "impact": "Drive decisions"
            },
            {
                "name": "SQL",
                "priority": "High",
                "weight": 18,
                "reason": "Query business data",
                "impact": "Access insights"
            },
            {
                "name": "Communication & Reporting",
                "priority": "High",
                "weight": 15,
                "reason": "Stakeholder updates",
                "impact": "Alignment"
            }
        ],
        "optional": []
    },
    "Senior Business Analyst": {
        "core": [
            {
                "name": "Strategic Analysis",
                "priority": "High",
                "weight": 28,
                "reason": "Business strategy",
                "impact": "Guide business"
            },
            {
                "name": "Advanced SQL",
                "priority": "High",
                "weight": 20,
                "reason": "Complex analysis",
                "impact": "Deep insights"
            },
            {
                "name": "Stakeholder Management",
                "priority": "High",
                "weight": 18,
                "reason": "Lead initiatives",
                "impact": "Execute strategy"
            }
        ],
        "optional": []
    },
    "Product Manager": {
        "core": [
            {
                "name": "Product Strategy",
                "priority": "High",
                "weight": 30,
                "reason": "Product vision",
                "impact": "Shape product"
            },
            {
                "name": "Data-Driven Decision Making",
                "priority": "High",
                "weight": 22,
                "reason": "Metrics-focused",
                "impact": "Evidence-based"
            },
            {
                "name": "Leadership",
                "priority": "High",
                "weight": 20,
                "reason": "Lead cross-functional teams",
                "impact": "Execute vision"
            }
        ],
        "optional": []
    },
    "Director of Product / VP Product": {
        "core": [
            {
                "name": "Product Vision & Strategy",
                "priority": "High",
                "weight": 35,
                "reason": "Set direction",
                "impact": "Company strategy"
            },
            {
                "name": "Leadership",
                "priority": "High",
                "weight": 30,
                "reason": "Manage teams",
                "impact": "Org effectiveness"
            },
            {
                "name": "Business Acumen",
                "priority": "High",
                "weight": 20,
                "reason": "Financial impact",
                "impact": "Business outcomes"
            }
        ],
        "optional": []
    }
}


def get_skill_gap(role):
    """
    Get advanced skill gap information for a specific role.
    
    Args:
        role (str): Job role title
    
    Returns:
        dict: {
            "core_skills": list,
            "optional_skills": list,
            "total_weight": int
        }
    """
    if role not in SKILL_REQUIREMENTS:
        return {
            "core_skills": [],
            "optional_skills": [],
            "total_weight": 0
        }
    
    skills_data = SKILL_REQUIREMENTS[role]
    
    return {
        "core_skills": skills_data.get("core", []),
        "optional_skills": skills_data.get("optional", []),
        "total_weight": sum(
            s["weight"] for s in skills_data.get("core", [])
        ) + sum(
            s["weight"] for s in skills_data.get("optional", [])
        )
    }
