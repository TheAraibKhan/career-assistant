# services/analytics.py
"""
SaaS-grade analytics for admin dashboard
Real-time submission analytics and insights
"""

from database.db import get_db
import json


def get_dashboard_analytics():
    """
    Get comprehensive dashboard analytics.
    
    Returns:
        dict: {
            "summary": {...},
            "by_level": {...},
            "by_interest": {...},
            "skills_analysis": {...},
            "recent_activity": [...]
        }
    """
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get all submissions
            cursor.execute("""
                SELECT interest, level, recommendation, readiness_score, created_at, name, confidence_score
                FROM submissions
                ORDER BY created_at DESC
            """)
            submissions = cursor.fetchall()
            
            if not submissions:
                return _empty_analytics()
            
            # Calculate summary stats
            summary = _calculate_summary(submissions)
            
            # Group by level
            by_level = _group_by_level(submissions)
            
            # Group by interest
            by_interest = _group_by_interest(submissions)
            
            # Most recommended roles
            most_recommended = _get_most_recommended_roles(submissions)
            
            # Most common missing skills (if available)
            missing_skills = _get_most_common_missing_skills(submissions)
            
            # Recent activity
            recent = _get_recent_activity(submissions)
            
            return {
                "summary": summary,
                "by_level": by_level,
                "by_interest": by_interest,
                "most_recommended_roles": most_recommended,
                "most_common_missing_skills": missing_skills,
                "recent_activity": recent,
                "total_submissions": len(submissions)
            }
    
    except Exception as e:
        print(f"Error getting analytics: {e}")
        return _empty_analytics()


def _empty_analytics():
    """Return empty analytics structure."""
    return {
        "summary": {
            "total_submissions": 0,
            "avg_readiness": 0,
            "high_confidence_pct": 0,
            "medium_confidence_pct": 0,
            "low_confidence_pct": 0
        },
        "by_level": {},
        "by_interest": {},
        "most_recommended_roles": [],
        "most_common_missing_skills": [],
        "recent_activity": []
    }


def _calculate_summary(submissions):
    """Calculate summary statistics."""
    
    if not submissions:
        return _empty_analytics()["summary"]
    
    total = len(submissions)
    
    # Average readiness
def _calculate_summary(submissions):
    """Calculate summary statistics."""
    total = len(submissions)
    
    readiness_scores = [s[3] for s in submissions if s[3] is not None]  # readiness_score is index 3
    avg_readiness = int(sum(readiness_scores) / len(readiness_scores)) if readiness_scores else 0
    
    # Confidence scores from index 6
    confidence_scores = [s[6] for s in submissions if s[6] is not None]  
    high = sum(1 for c in confidence_scores if c >= 80)
    medium = sum(1 for c in confidence_scores if 60 <= c < 80)
    low = sum(1 for c in confidence_scores if c < 60)
    
    high_pct = (high * 100 // total) if total > 0 else 0
    med_pct = (medium * 100 // total) if total > 0 else 0
    low_pct = (low * 100 // total) if total > 0 else 0
    
    return {
        "total_submissions": total,
        "avg_readiness": avg_readiness,
        "avg_confidence": int(sum(confidence_scores) / len(confidence_scores)) if confidence_scores else 0,
        "high_confidence_pct": high_pct,
        "medium_confidence_pct": med_pct,
        "low_confidence_pct": low_pct,
        "avg_readiness_status": _readiness_status(avg_readiness)
    }


def _readiness_status(score):
    """Convert readiness score to status."""
    if score >= 75:
        return "Very Ready"
    elif score >= 60:
        return "Ready with gaps"
    elif score >= 40:
        return "Building foundation"
    else:
        return "Early stage"


def _group_by_level(submissions):
    """Group submissions by experience level."""
    
    grouped = {}
    for sub in submissions:
        level = sub[1]  # level is index 1
        if level not in grouped:
            grouped[level] = {
                "count": 0,
                "avg_readiness": 0,
                "avg_confidence": 0,
                "readiness_scores": [],
                "confidence_scores": []
            }
        
        grouped[level]["count"] += 1
        if sub[3] is not None:  # readiness_score is index 3
            grouped[level]["readiness_scores"].append(sub[3])
        if sub[6] is not None:  # confidence_score is index 6
            grouped[level]["confidence_scores"].append(sub[6])
    
    # Calculate averages
    for level in grouped:
        readiness = grouped[level]["readiness_scores"]
        confidence = grouped[level]["confidence_scores"]
        grouped[level]["avg_readiness"] = int(sum(readiness) / len(readiness)) if readiness else 0
        grouped[level]["avg_confidence"] = int(sum(confidence) / len(confidence)) if confidence else 0
        del grouped[level]["readiness_scores"]
        del grouped[level]["confidence_scores"]
    
    return grouped


def _group_by_interest(submissions):
    """Group submissions by interest area."""
    
    grouped = {}
    for sub in submissions:
        interest = sub[0]  # interest is index 0
        if interest not in grouped:
            grouped[interest] = {
                "count": 0,
                "avg_readiness": 0,
                "avg_confidence": 0,
                "readiness_scores": [],
                "confidence_scores": []
            }
        
        grouped[interest]["count"] += 1
        if sub[3] is not None:  # readiness_score is index 3
            grouped[interest]["readiness_scores"].append(sub[3])
        if sub[6] is not None:  # confidence_score is index 6
            grouped[interest]["confidence_scores"].append(sub[6])
    
    # Calculate averages
    for interest in grouped:
        readiness = grouped[interest]["readiness_scores"]
        confidence = grouped[interest]["confidence_scores"]
        grouped[interest]["avg_readiness"] = int(sum(readiness) / len(readiness)) if readiness else 0
        grouped[interest]["avg_confidence"] = int(sum(confidence) / len(confidence)) if confidence else 0
        del grouped[interest]["readiness_scores"]
        del grouped[interest]["confidence_scores"]
    
    return grouped


def _get_most_recommended_roles(submissions):
    """Get most recommended roles."""
    
    role_counts = {}
    for sub in submissions:
        role = sub[2]  # recommendation is index 2
        role_counts[role] = role_counts.get(role, 0) + 1
    
    # Sort by count
    sorted_roles = sorted(role_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [
        {
            "role": role,
            "count": count,
            "percentage": int(count * 100 / len(submissions))
        }
        for role, count in sorted_roles[:10]
    ]


def _get_most_common_missing_skills(submissions):
    """Get most commonly missing skills from gaps data."""
    
    skill_counts = {}
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT gaps FROM submissions WHERE gaps IS NOT NULL")
            rows = cursor.fetchall()
            
            for row in rows:
                if row["gaps"]:
                    try:
                        gaps = json.loads(row["gaps"])
                        for skill in gaps:
                            skill_name = skill if isinstance(skill, str) else skill
                            skill_counts[skill_name] = skill_counts.get(skill_name, 0) + 1
                    except:
                        pass
    except:
        pass
    
    # Sort by count
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [
        {
            "skill": skill,
            "frequency": count,
            "impact": "Common gap" if count > 3 else "Notable gap"
        }
        for skill, count in sorted_skills[:10]
    ]


def _get_recent_activity(submissions):
    """Get recent submissions for activity feed."""
    
    recent_subs = sorted(submissions, key=lambda x: x[4], reverse=True)[:10]  # created_at is index 4
    
    return [
        {
            "name": sub[5],  # name is index 5
            "interest": sub[0],
            "level": sub[1],
            "role": sub[2],
            "readiness": sub[3],
            "confidence": sub[6],  # confidence_score is index 6
            "timestamp": sub[4]
        }
        for sub in recent_subs
    ]
