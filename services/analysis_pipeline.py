"""
services/analysis_pipeline.py — Phase 4

The central data pipeline that runs after every resume upload.
Computes, normalises, and persists all derived metrics to the
satellite tables that Phases 2 & 3 depend on:

  • resume_health          (formatting, keyword, content, ATS scores)
  • skill_gap_analysis     (current skills, required skills, priority gaps)
  • confidence_index       (overall readiness + per-dimension scores + trend)
  • user_goals             (created on first upload if missing; kept up-to-date)

Usage (in resume_routes.py, after a successful parse):

    from services.analysis_pipeline import run_full_pipeline
    run_full_pipeline(db, user_id, parse_result, ats_result, quality_score)
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any

# helpers 

def _now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def _jdump(v: Any) -> str:
    if isinstance(v, (list, dict)):
        return json.dumps(v)
    return str(v) if v else ""


def _clamp(v, lo=0, hi=100):
    if v is None:
        return None
    return max(lo, min(hi, int(v)))


# scoring helpers 

# Common resume sections that a good resume should have
_SECTION_RE = re.compile(
    r"\b(summary|objective|experience|education|skills|projects|"
    r"certifications|achievements|publications|awards|languages|"
    r"interests|volunteer|references)\b",
    re.IGNORECASE,
)

# Action verbs signal strong bullet writing
_ACTION_VERBS = [
    "led", "built", "designed", "developed", "implemented", "launched",
    "improved", "reduced", "increased", "managed", "delivered", "created",
    "architected", "optimised", "scaled", "owned", "drove", "collaborated",
]

_METRIC_RE = re.compile(r"\d+\s*[%x×]|\$\s*\d+|[0-9]+\s*(users|customers|clients|engineers|people|members)", re.IGNORECASE)


def _compute_formatting_score(parse_result: dict, ats_result: dict) -> int:
    """Estimate resume formatting quality (0-100) from parsed data."""
    score = 0
    text: str = parse_result.get("text", "") or ""
    text_lower = text.lower()

    # Section count (max 30)
    sections = set(_SECTION_RE.findall(text_lower))
    score += min(30, len(sections) * 5)

    # Length (max 20)
    length = len(text)
    if 1500 <= length <= 5000:
        score += 20
    elif 800 <= length < 8000:
        score += 12
    else:
        score += 4

    # ATS format sub-score carries 25 pts
    ats_format = ats_result.get("categories", {}).get("format", 0)
    score += _clamp(ats_format * 2.5, 0, 25)  # ats format/10 => /25

    # Contact info present (max 10)
    ats_contact = ats_result.get("categories", {}).get("contact_info", 0)
    score += _clamp(ats_contact, 0, 10)

    # No blockers (max 15)
    blockers = ats_result.get("blockers", [])
    score += max(0, 15 - len(blockers) * 5)

    return _clamp(score)


def _compute_keyword_score(parse_result: dict, ats_result: dict) -> int:
    """Estimate keyword density / relevance (0-100)."""
    score = 0
    skills = parse_result.get("skills", []) or []

    # Skill count (max 40)
    score += min(40, len(skills) * 3)

    # ATS keyword sub-score (max 40)
    ats_kw = ats_result.get("categories", {}).get("keywords", 0)
    score += _clamp(ats_kw * (40 / 15), 0, 40)

    # Action verbs present (max 20)
    text = (parse_result.get("text", "") or "").lower()
    verb_hits = sum(1 for v in _ACTION_VERBS if v in text)
    score += min(20, verb_hits * 3)

    return _clamp(score)


def _compute_content_completeness(parse_result: dict, ats_result: dict) -> int:
    """Estimate how complete the resume content is (0-100)."""
    score = 0
    text = (parse_result.get("text", "") or "").lower()

    has_experience = parse_result.get("experience") or parse_result.get("has_experience") or False
    education = parse_result.get("education", []) or []

    # Experience section (25 pts)
    if has_experience:
        score += 15
    ats_exp = ats_result.get("categories", {}).get("experience", 0)
    score += _clamp(ats_exp * 0.5, 0, 10)   # up to 10 bonus from ats

    # Education (15 pts)
    score += min(15, len(education) * 7)

    # Metrics (20 pts)
    metrics = _METRIC_RE.findall(text)
    score += min(20, len(metrics) * 4)

    # Summary (10 pts)
    ats_summ = ats_result.get("categories", {}).get("summary", 0)
    score += _clamp(ats_summ * 2, 0, 10)

    # Skills (20 pts)
    skills = parse_result.get("skills", []) or []
    score += min(20, len(skills) * 2)

    # Contact info (10 pts)
    ats_contact = ats_result.get("categories", {}).get("contact_info", 0)
    score += _clamp(ats_contact, 0, 10)

    return _clamp(score)


def _derive_priority_gaps(current_skills: list, ats_result: dict, parse_result: dict) -> list:
    """Derive a short list of priority skill gaps from context.
    
    Extracts technical/professional skills from recommendations & blockers,
    filtering out generic words like 'Create', 'Add', 'Improve'.
    """
    # Common skills and tech terms to look for - organized by category
    # Only single words or well-known multi-word terms to avoid partial matches
    SKILL_KEYWORDS = {
        # Languages (avoid single letters like 'R', 'C' that match in other words)
        "Python", "Java", "JavaScript", "TypeScript", "Ruby", "Go",
        "Rust", "PHP", "Kotlin", "Swift", "MATLAB", "SQL",
        # Web/Frontend
        "React", "Vue", "Angular", "HTML", "CSS", "Node", "Django",
        "Flask", "Spring", "Laravel", "Express", "Next",
        # Data/Cloud
        "AWS", "Azure", "GCP", "Kubernetes", "Docker", "Terraform", "Jenkins",
        "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Spark", "Hadoop",
        # Professional
        "Agile", "Scrum", "Git", "GitHub", "GitLab", "DevOps",
        "Microservices", "REST", "GraphQL", "API", "CI/CD",
        # Soft skills
        "Leadership", "Communication", "Management", "Analysis", "Project Management",
        # Others
        "Blockchain", "ML", "AI", "Kubernetes", "Terraform",
        "Machine Learning", "Deep Learning", "Data Science", "Analytics", "Statistics",
    }
    
    current_skills_lower = [s.lower() for s in current_skills]
    priority = []
    
    # Extract from recommendations using word-aware matching
    recs = ats_result.get("recommendations", []) or []
    for rec in recs:
        rec_lower = rec.lower()
        for skill_kw in SKILL_KEYWORDS:
            skill_lower = skill_kw.lower()
            # Use word boundaries: match as whole word or as part of phrase
            # For multi-word terms, just do substring match
            # For single-word terms, check word boundaries
            if " " in skill_kw:
                # Multi-word term: substring match is fine
                if skill_lower in rec_lower and skill_lower not in current_skills_lower:
                    priority.append(skill_kw)
            else:
                # Single-word term: use word boundary check with regex
                pattern = r"\b" + re.escape(skill_lower) + r"\b"
                if re.search(pattern, rec_lower) and skill_lower not in current_skills_lower:
                    priority.append(skill_kw)
    
    # Also check blockers for skills
    blockers = ats_result.get("blockers", []) or []
    for blocker in blockers:
        blocker_lower = blocker.lower()
        for skill_kw in SKILL_KEYWORDS:
            skill_lower = skill_kw.lower()
            if " " in skill_kw:
                if skill_lower in blocker_lower and skill_lower not in current_skills_lower:
                    priority.append(skill_kw)
            else:
                pattern = r"\b" + re.escape(skill_lower) + r"\b"
                if re.search(pattern, blocker_lower) and skill_lower not in current_skills_lower:
                    priority.append(skill_kw)
    
    # De-duplicate while preserving order and limiting to 8
    seen = set()
    out = []
    for p in priority:
        if p.lower() not in seen:
            seen.add(p.lower())
            out.append(p)
        if len(out) >= 8:
            break
    
    return out


def _compute_confidence_dimensions(
    overall: int,
    formatting: int,
    keyword: int,
    content: int,
) -> dict:
    """Return sub-scores for the three confidence dimensions."""
    # resume_strength comes largely from formatting + content
    resume_strength = _clamp((formatting * 0.5 + content * 0.5))
    # skill_readiness comes from keyword density
    skill_readiness = _clamp(keyword)
    # market_alignment is holistic (overall weighted towards keyword)
    market_alignment = _clamp(overall * 0.6 + keyword * 0.4)
    return {
        "resume_strength": resume_strength,
        "skill_readiness": skill_readiness,
        "market_alignment": market_alignment,
    }


# ── required-skills catalog (used for skill gap) ───────────────────────────────

_COMMON_REQUIRED_SKILLS = [
    "Python", "SQL", "Communication", "Problem Solving",
    "Git", "Data Analysis", "Critical Thinking", "Project Management",
    "Agile", "Documentation",
]


# main pipeline entry point 

def run_full_pipeline(
    db,
    user_id: Any,
    parse_result: dict,
    ats_result: dict,
    quality_score: int,
    target_role: str | None = None,
) -> dict:
    """
    Computes all derived metrics and writes them to:
      - resume_health
      - skill_gap_analysis
      - confidence_index
      - user_goals (upsert)

    Returns a summary dict of what was persisted.
    """

    now = _now()
    skills: list = parse_result.get("skills", []) or []
    ats_score: int = _clamp(ats_result.get("ats_score", quality_score))

    # 1. Derived scores 
    formatting_score = _compute_formatting_score(parse_result, ats_result)
    keyword_score    = _compute_keyword_score(parse_result, ats_result)
    content_score    = _compute_content_completeness(parse_result, ats_result)

    # Overall health = weighted average of the three dimensions + ATS
    overall_health = _clamp(
        formatting_score * 0.25 +
        keyword_score    * 0.30 +
        content_score    * 0.25 +
        ats_score        * 0.20
    )

    suggestions_raw = ats_result.get("recommendations", [])
    suggestions_json = _jdump(suggestions_raw[:6])

    # 2. Persist resume_health 
    existing_health = db.execute(
        "SELECT id FROM resume_health WHERE user_id = ?", (user_id,)
    ).fetchone()

    if existing_health:
        db.execute(
            """
            UPDATE resume_health
            SET ats_score          = ?,
                formatting_score   = ?,
                keyword_score      = ?,
                content_completeness = ?,
                overall_health     = ?,
                suggestions        = ?,
                last_analyzed_at   = ?,
                updated_at         = ?
            WHERE user_id = ?
            """,
            (
                ats_score, formatting_score, keyword_score,
                content_score, overall_health,
                suggestions_json, now, now,
                user_id,
            ),
        )
    else:
        db.execute(
            """
            INSERT INTO resume_health
              (user_id, ats_score, formatting_score, keyword_score,
               content_completeness, overall_health, suggestions, last_analyzed_at,
               created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, ats_score, formatting_score, keyword_score,
                content_score, overall_health,
                suggestions_json, now,
                now, now,
            ),
        )

    # 3. Persist skill_gap_analysis 
    priority_gaps    = _derive_priority_gaps(skills, ats_result, parse_result)
    current_skills_j = _jdump(skills)
    required_j       = _jdump(_COMMON_REQUIRED_SKILLS)
    gaps_j           = _jdump(priority_gaps)

    # Estimated weeks: 2 weeks per priority gap (rough but consistent)
    estimated_weeks = len(priority_gaps) * 2

    existing_gap = db.execute(
        "SELECT id FROM skill_gap_analysis WHERE user_id = ?", (user_id,)
    ).fetchone()

    if existing_gap:
        db.execute(
            """
            UPDATE skill_gap_analysis
            SET current_skills          = ?,
                required_skills         = ?,
                priority_gaps           = ?,
                estimated_learning_weeks = ?,
                target_role             = ?,
                updated_at              = ?
            WHERE user_id = ?
            """,
            (
                current_skills_j, required_j, gaps_j,
                estimated_weeks, target_role, now,
                user_id,
            ),
        )
    else:
        db.execute(
            """
            INSERT INTO skill_gap_analysis
              (user_id, current_skills, required_skills, priority_gaps,
               estimated_learning_weeks, target_role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, current_skills_j, required_j, gaps_j,
                estimated_weeks, target_role, now, now,
            ),
        )

    # 4. Persist confidence_index 
    dims = _compute_confidence_dimensions(
        overall_health, formatting_score, keyword_score, content_score
    )

    # Determine trend by comparing to previous score
    prev = db.execute(
        "SELECT overall_score FROM confidence_index WHERE user_id = ?", (user_id,)
    ).fetchone()

    trend = "stable"
    if prev and prev["overall_score"] is not None:
        delta = overall_health - int(prev["overall_score"])
        trend = "improving" if delta > 3 else "declining" if delta < -3 else "stable"

    if prev:
        db.execute(
            """
            UPDATE confidence_index
            SET overall_score    = ?,
                resume_strength  = ?,
                skill_readiness  = ?,
                market_alignment = ?,
                trend            = ?,
                updated_at       = ?
            WHERE user_id = ?
            """,
            (
                overall_health,
                dims["resume_strength"],
                dims["skill_readiness"],
                dims["market_alignment"],
                trend, now,
                user_id,
            ),
        )
    else:
        db.execute(
            """
            INSERT INTO confidence_index
              (user_id, overall_score, resume_strength, skill_readiness,
               market_alignment, trend, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, overall_health,
                dims["resume_strength"],
                dims["skill_readiness"],
                dims["market_alignment"],
                trend, now, now,
            ),
        )

    # 5. Upsert user_goals (first upload baseline) 
    try:
        existing_goal = db.execute(
            "SELECT id FROM user_goals WHERE user_id = ?", (user_id,)
        ).fetchone()
        goal_desc = f"Health: {overall_health}/100, Target: {target_role or 'TBD'}"
        
        if not existing_goal:
            db.execute(
                """
                INSERT INTO user_goals
                  (user_id, goal_title, goal_description, category, status,
                   completion_percentage, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    f"Improve career readiness for {target_role or 'target role'}",
                    goal_desc,
                    "career_development",
                    "active",
                    min(100, overall_health),  # use current health as completion %
                    now, now,
                ),
            )
        else:
            # Update completion_percentage based on current health score
            db.execute(
                """UPDATE user_goals 
                   SET goal_description = ?, completion_percentage = ?, updated_at = ? 
                   WHERE user_id = ?""",
                (goal_desc, min(100, overall_health), now, user_id),
            )
    except Exception as _goal_err:
        pass  # user_goals table may not exist in older DBs — non-fatal

    db.connection.commit() if hasattr(db, "connection") else None

    try:
        db.execute("SELECT 1")   # triggers implicit commit in sqlite3 Row
    except Exception:
        pass

    return {
        "ats_score": ats_score,
        "formatting_score": formatting_score,
        "keyword_score": keyword_score,
        "content_score": content_score,
        "overall_health": overall_health,
        "skill_count": len(skills),
        "priority_gaps": priority_gaps,
        "trend": trend,
        **dims,
    }
