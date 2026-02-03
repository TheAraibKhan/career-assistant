# services/action_plan.py
"""
Dynamic 30-60-90 day career action plans
Generates structured learning and progression plans based on role and gaps
"""


def generate_action_plan(role, level, acquired_skills, missing_skills):
    """
    Generate a 30-60-90 day action plan.
    
    Args:
        role (str): Target role
        level (str): Current experience level
        acquired_skills (list): Skills user has
        missing_skills (list): Critical skills to develop
    
    Returns:
        dict: {
            "month_1": {
                "focus": str,
                "actions": list of specific actions,
                "success_metrics": list
            },
            "month_2": {...},
            "month_3": {...},
            "quick_wins": list of achievable skills in <2 weeks
        }
    """
    
    # Identify quick wins (most achievable skills)
    quick_wins = _identify_quick_wins(missing_skills)
    
    # Generate progressive monthly plans
    month_1 = _generate_month_1_plan(role, level, quick_wins)
    month_2 = _generate_month_2_plan(role, level, missing_skills)
    month_3 = _generate_month_3_plan(role, level)
    
    return {
        "month_1": month_1,
        "month_2": month_2,
        "month_3": month_3,
        "quick_wins": quick_wins,
        "overall_timeline": _estimate_timeline(level, len(missing_skills))
    }


def _identify_quick_wins(missing_skills):
    """Identify skills that can be learned quickly (< 2 weeks)."""
    
    quick_win_topics = {
        "Git": "Can learn basics in 1-2 weeks",
        "REST API": "Concepts learnable in 1-2 weeks",
        "SQL Basics": "Fundamentals in 1-2 weeks",
        "HTML/CSS": "Basics in 1-2 weeks",
        "Excel": "Intermediate skills in 1-2 weeks",
        "JSON": "Can master in 1-2 weeks",
        "Command Line": "Basics in 1-2 weeks",
        "Docker Basics": "Introduction in 1-2 weeks",
    }
    
    quick_wins = []
    for skill in missing_skills:
        skill_name = skill if isinstance(skill, str) else skill.get("name", "")
        for topic, desc in quick_win_topics.items():
            if topic.lower() in skill_name.lower():
                quick_wins.append({
                    "skill": skill_name,
                    "timeline": "1-2 weeks",
                    "effort": "Low",
                    "impact": "Foundation for other skills"
                })
                break
    
    return quick_wins[:3]  # Top 3 quick wins


def _generate_month_1_plan(role, level, quick_wins):
    """Generate Month 1 focused plan on foundations and quick wins."""
    
    return {
        "focus": "Build Foundations & Quick Wins",
        "theme": "Week 1-2: Learn quick wins. Week 3-4: Deepen understanding.",
        "actions": [
            f"Complete 2 quick-win skill modules ({quick_wins[0]['skill'] if quick_wins else 'fundamentals'})",
            "Take 1-2 foundational courses (YouTube, Udemy, or free platforms)",
            "Set up development environment for your target role",
            "Join relevant online communities (Discord, Reddit, Slack groups)",
            "Complete 1 small personal project using new skills",
        ] if quick_wins else [
            "Establish learning routine (5-10 hours/week)",
            "Identify top 3 foundational skills to learn",
            "Set up development environment",
            "Start 1 foundational course",
            "Join industry communities",
        ],
        "success_metrics": [
            "Completed 2 foundational courses",
            "Set up working development environment",
            f"Built 1 small project using new skills",
            "Joined 1+ industry communities",
            "Established consistent learning habits",
        ]
    }


def _generate_month_2_plan(role, level, missing_skills):
    """Generate Month 2 focused plan on intermediate skills."""
    
    return {
        "focus": "Develop Core Skills & Build Portfolio",
        "theme": "Week 5-8: Deep dive into 2-3 core skills. Start portfolio projects.",
        "actions": [
            "Complete 2 intermediate-level courses in core skills",
            "Build 2 portfolio projects demonstrating skills",
            "Get feedback from mentors or communities on your work",
            "Start contributing to open-source (if tech/data)",
            "Document your learning journey (blog or GitHub)",
        ],
        "success_metrics": [
            "Completed intermediate courses (2+)",
            "Built 2 portfolio projects",
            "Got feedback from 2+ sources",
            "Made 1 open-source contribution",
            "Documented learning publicly",
        ]
    }


def _generate_month_3_plan(role, level):
    """Generate Month 3 focused plan on application and advancement."""
    
    return {
        "focus": "Apply Skills & Progress to Next Level",
        "theme": "Week 9-12: Apply skills in real context. Position for opportunities.",
        "actions": [
            "Complete final capstone or advanced project",
            "Polish portfolio and resume with new projects",
            "Network with professionals in target role (LinkedIn, events)",
            "Practice interviews or case studies for role",
            "Apply for internships, jobs, or take on freelance projects",
        ],
        "success_metrics": [
            "Completed 1 capstone project",
            "Updated resume/portfolio with new work",
            "Made 5+ meaningful professional connections",
            "Practiced 5+ interview/case questions",
            "Applied to 3+ opportunities or completed 1 project",
        ]
    }


def _estimate_timeline(level, skill_gap_count):
    """Estimate total time to reach role readiness."""
    
    level_months = {
        "beginner": 6,
        "junior": 4,
        "intermediate": 3,
        "advanced": 2,
        "expert": 1
    }
    
    base_months = level_months.get(level, 3)
    gap_months = min(skill_gap_count * 0.5, 4)  # Cap at 4 additional months
    
    total = int(base_months + gap_months)
    
    if total <= 3:
        timeline_desc = "Fast Track (3 months)"
    elif total <= 6:
        timeline_desc = "Standard Track (3-6 months)"
    elif total <= 12:
        timeline_desc = "Extended Track (6-12 months)"
    else:
        timeline_desc = "Long-Term Journey (12+ months)"
    
    return {
        "estimated_months": total,
        "description": timeline_desc,
        "note": f"Assuming 5-10 hours/week consistent learning effort"
    }
