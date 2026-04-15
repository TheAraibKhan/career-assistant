"""
Feature page routes — Phase 2.
Each feature page is now wired to the user's live data from the database.
Unauthenticated users see the public version (static content).
Authenticated users see their own data overlaid on the same page.
"""

from flask import Blueprint, render_template, session, jsonify, request
from functools import wraps
from database.db import get_db
import json
from datetime import datetime, timedelta

features_bp = Blueprint("features", __name__, url_prefix="/features")


# helpers 

def _uid():
    return session.get("user_id")


def _get_user_resume_snapshot(db, user_id):
    """Return the most recent resume analysis snapshot for a user."""
    row = db.execute(
        """
        SELECT id, name, readiness_score, confidence_score,
               resume_parsed_skills, strengths, gaps,
               recommendation, created_at
        FROM submissions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (user_id,),
    ).fetchone()
    return dict(row) if row else None


def _get_resume_history(db, user_id, limit=10):
    """Return a user's resume submission history (score over time)."""
    rows = db.execute(
        """
        SELECT id, name, readiness_score, confidence_score, created_at
        FROM submissions
        WHERE user_id = ?
        ORDER BY created_at ASC
        LIMIT ?
        """,
        (user_id, limit),
    ).fetchall()
    return [dict(r) for r in rows]


def _parse_json_field(raw, default=None):
    if default is None:
        default = []
    if not raw:
        return default
    try:
        val = json.loads(raw)
        return val if isinstance(val, (list, dict)) else default
    except Exception:
        # Fall back: treat as comma-separated string
        if isinstance(raw, str):
            return [s.strip() for s in raw.split(",") if s.strip()]
        return default


def _get_skill_gap(db, user_id):
    """Return skill gap record if it exists."""
    row = db.execute(
        "SELECT * FROM skill_gap_analysis WHERE user_id = ?", (user_id,)
    ).fetchone()
    return dict(row) if row else None


def _get_resume_health(db, user_id):
    row = db.execute(
        "SELECT * FROM resume_health WHERE user_id = ?", (user_id,)
    ).fetchone()
    return dict(row) if row else None


def _get_quick_analysis(db, user_id):
    """Return most recent quick (text-paste) analysis."""
    try:
        # Ensure the table exists (created lazily by the analyze endpoint)
        db.execute(
            """CREATE TABLE IF NOT EXISTS quick_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                resume_text TEXT,
                target_role TEXT,
                ats_score INTEGER,
                overall_score INTEGER,
                skills_found TEXT,
                recommendations TEXT,
                created_at TEXT NOT NULL
            )"""
        )
        row = db.execute(
            """
            SELECT ats_score, overall_score, skills_found, recommendations,
                   target_role, created_at
            FROM quick_analyses
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()
        return dict(row) if row else None
    except Exception:
        return None


# ATS Detection 

@features_bp.route("/ats-detection")
def ats_detection():
    uid = _uid()
    user_data = None

    if uid:
        db = get_db()
        snapshot = _get_user_resume_snapshot(db, uid)
        health = _get_resume_health(db, uid)
        quick = _get_quick_analysis(db, uid)

        if snapshot or health or quick:
            ats_score = None
            skills = []
            blockers = []
            strengths = []
            analyzed_at = None

            if health:
                ats_score = health.get("ats_score")
                analyzed_at = health.get("last_analyzed_at")
                blockers = _parse_json_field(health.get("suggestions"))

            if snapshot:
                if ats_score is None:
                    ats_score = snapshot.get("confidence_score")
                skills = _parse_json_field(snapshot.get("resume_parsed_skills"))
                strengths = _parse_json_field(snapshot.get("strengths"))
                if not blockers:
                    blockers = _parse_json_field(snapshot.get("gaps"))
                if not analyzed_at:
                    analyzed_at = snapshot.get("created_at")

            if quick and ats_score is None:
                ats_score = quick.get("ats_score")
                if not skills:
                    skills = _parse_json_field(quick.get("skills_found"))

            # Human-readable level
            if ats_score is not None:
                if ats_score >= 75:
                    level = "readable"
                    level_label = "Systems can read this clearly"
                elif ats_score >= 50:
                    level = "partial"
                    level_label = "Some sections may not parse correctly"
                else:
                    level = "needs_work"
                    level_label = "Structural changes will help readability"
            else:
                level = None
                level_label = None

            user_data = {
                "ats_score": ats_score,
                "level": level,
                "level_label": level_label,
                "skills": skills[:12],
                "skill_count": len(skills),
                "blockers": blockers[:4],
                "strengths": strengths[:4],
                "analyzed_at": analyzed_at,
                "has_data": True,
            }

    return render_template("features/ats_detection.html", user_data=user_data)


# Gap Analysis 

@features_bp.route("/gap-analysis")
def gap_analysis():
    uid = _uid()
    user_data = None

    if uid:
        db = get_db()
        gap_row = _get_skill_gap(db, uid)
        snapshot = _get_user_resume_snapshot(db, uid)

        if gap_row or snapshot:
            current_skills = []
            gap_skills = []
            priority_gaps = []
            target_role = None
            estimated_weeks = None

            if gap_row:
                current_skills = _parse_json_field(gap_row.get("current_skills"))
                gap_skills = _parse_json_field(gap_row.get("required_skills"))
                priority_gaps = _parse_json_field(gap_row.get("priority_gaps"))
                estimated_weeks = gap_row.get("estimated_learning_weeks")

            if snapshot:
                if not current_skills:
                    current_skills = _parse_json_field(snapshot.get("resume_parsed_skills"))
                if not gap_skills:
                    gap_skills = _parse_json_field(snapshot.get("gaps"))
                target_role = snapshot.get("recommendation")

            gap_count = len(priority_gaps) if priority_gaps else len(gap_skills)
            coverage = 0
            total = len(current_skills) + gap_count
            if total > 0:
                coverage = round(len(current_skills) / total * 100)

            user_data = {
                "current_skills": current_skills[:10],
                "gap_skills": gap_skills[:8],
                "priority_gaps": priority_gaps[:5] if priority_gaps else gap_skills[:5],
                "target_role": target_role,
                "gap_count": gap_count,
                "skill_coverage": coverage,
                "estimated_weeks": estimated_weeks,
                "has_data": True,
            }

    return render_template("features/gap_analysis.html", user_data=user_data)


# Recruiter Perspective 

@features_bp.route("/recruiter-perspective")
def recruiter_perspective():
    uid = _uid()
    user_data = None

    if uid:
        db = get_db()
        snapshot = _get_user_resume_snapshot(db, uid)
        health = _get_resume_health(db, uid)

        if snapshot or health:
            formatting_score = None
            keyword_score = None
            content_score = None
            overall = None
            strengths = []
            gaps = []
            name = None
            analyzed_at = None

            if health:
                formatting_score = health.get("formatting_score")
                keyword_score = health.get("keyword_score")
                content_score = health.get("content_completeness")
                overall = health.get("overall_health")
                analyzed_at = health.get("last_analyzed_at")

            if snapshot:
                name = snapshot.get("name") or snapshot.get("recommendation", "your profile")
                strengths = _parse_json_field(snapshot.get("strengths"))
                gaps = _parse_json_field(snapshot.get("gaps"))
                if overall is None:
                    overall = snapshot.get("readiness_score")
                if not analyzed_at:
                    analyzed_at = snapshot.get("created_at")

            # Derive sections clarity status from scores
            sections = []
            if formatting_score is not None:
                sections.append({
                    "label": "Layout & Spacing",
                    "score": formatting_score,
                    "status": "clear" if formatting_score >= 70 else "needs_attention",
                })
            if keyword_score is not None:
                sections.append({
                    "label": "Keyword Density",
                    "score": keyword_score,
                    "status": "clear" if keyword_score >= 60 else "needs_attention",
                })
            if content_score is not None:
                sections.append({
                    "label": "Section Completeness",
                    "score": content_score,
                    "status": "clear" if content_score >= 65 else "needs_attention",
                })

            user_data = {
                "overall_score": overall,
                "formatting_score": formatting_score,
                "keyword_score": keyword_score,
                "content_score": content_score,
                "sections": sections,
                "strengths": strengths[:4],
                "gaps": gaps[:4],
                "profile_label": name,
                "analyzed_at": analyzed_at,
                "has_data": bool(health or snapshot),
            }

    return render_template("features/recruiter_perspective.html", user_data=user_data)


# Bullet Impact 

@features_bp.route("/bullet-impact")
def bullet_impact():
    uid = _uid()
    user_data = None

    if uid:
        db = get_db()
        # Use resume history to show evolution
        history = _get_resume_history(db, uid, limit=6)
        snapshot = _get_user_resume_snapshot(db, uid)

        if history or snapshot:
            # Score progression (readiness_score over time as proxy for bullet quality trend)
            score_timeline = [
                {"date": r["created_at"][:10], "score": r["readiness_score"] or 0}
                for r in history
                if r.get("readiness_score") is not None
            ]

            current_score = None
            skills = []
            gaps = []
            version_count = len(history)

            if snapshot:
                current_score = snapshot.get("readiness_score")
                skills = _parse_json_field(snapshot.get("resume_parsed_skills"))
                gaps = _parse_json_field(snapshot.get("gaps"))

            # Derive improvement since first version
            improvement = None
            if len(score_timeline) >= 2:
                first = score_timeline[0]["score"]
                latest = score_timeline[-1]["score"]
                improvement = latest - first

            # Classify current bullet quality stage
            stage = None
            stage_label = None
            if current_score is not None:
                if current_score >= 75:
                    stage = "outcome"
                    stage_label = "Your descriptions are outcome-focused"
                elif current_score >= 50:
                    stage = "developing"
                    stage_label = "Moving from responsibility to outcome language"
                else:
                    stage = "responsibility"
                    stage_label = "Currently describing responsibilities — ready to evolve"

            user_data = {
                "current_score": current_score,
                "version_count": version_count,
                "score_timeline": score_timeline,
                "improvement": improvement,
                "stage": stage,
                "stage_label": stage_label,
                "skills": skills[:8],
                "gaps_to_address": gaps[:4],
                "has_data": bool(history or snapshot),
            }

    return render_template("features/bullet_impact.html", user_data=user_data)


# Formatting Guidance 

@features_bp.route("/formatting-guidance")
def formatting_guidance():
    uid = _uid()
    user_data = None

    if uid:
        db = get_db()
        health = _get_resume_health(db, uid)
        snapshot = _get_user_resume_snapshot(db, uid)

        if health or snapshot:
            formatting_score = None
            checklist = {}
            analyzed_at = None
            suggestions = []

            if health:
                formatting_score = health.get("formatting_score")
                analyzed_at = health.get("last_analyzed_at")
                suggestions = _parse_json_field(health.get("suggestions"))

            if snapshot and not analyzed_at:
                analyzed_at = snapshot.get("created_at")

            # Derive checklist from score bands
            if formatting_score is not None:
                checklist = {
                    "font_consistency": formatting_score >= 70,
                    "spacing": formatting_score >= 60,
                    "margins": formatting_score >= 55,
                    "no_tables_images": formatting_score >= 65,
                    "section_clarity": formatting_score >= 50,
                }

            grade = None
            grade_label = None
            if formatting_score is not None:
                if formatting_score >= 80:
                    grade = "A"
                    grade_label = "Presentation is clean and clear"
                elif formatting_score >= 65:
                    grade = "B"
                    grade_label = "Good structure, a few things to tighten"
                elif formatting_score >= 50:
                    grade = "C"
                    grade_label = "Readable but some friction for the reader"
                else:
                    grade = "D"
                    grade_label = "Formatting is creating friction — worth fixing"

            user_data = {
                "formatting_score": formatting_score,
                "grade": grade,
                "grade_label": grade_label,
                "checklist": checklist,
                "suggestions": suggestions[:5],
                "analyzed_at": analyzed_at,
                "has_data": bool(health or snapshot),
            }

    return render_template("features/formatting_guidance.html", user_data=user_data)


# Career Readiness 

@features_bp.route("/career-readiness")
def career_readiness():
    uid = _uid()
    user_data = None

    if uid:
        db = get_db()
        history = _get_resume_history(db, uid, limit=12)
        snapshot = _get_user_resume_snapshot(db, uid)
        confidence = db.execute(
            "SELECT * FROM confidence_index WHERE user_id = ?", (uid,)
        ).fetchone()
        confidence = dict(confidence) if confidence else None

        if history or snapshot or confidence:
            score_timeline = [
                {"date": r["created_at"][:10], "score": r["readiness_score"] or 0}
                for r in history
                if r.get("readiness_score") is not None
            ]

            current_score = None
            trend = "stable"
            improvement_total = None
            resume_strength = None
            skill_readiness = None
            market_alignment = None
            version_count = len(history)

            if confidence:
                current_score = confidence.get("overall_score")
                trend = confidence.get("trend", "stable")
                resume_strength = confidence.get("resume_strength")
                skill_readiness = confidence.get("skill_readiness")
                market_alignment = confidence.get("market_alignment")

            if snapshot and current_score is None:
                current_score = snapshot.get("readiness_score")

            if len(score_timeline) >= 2:
                improvement_total = (
                    score_timeline[-1]["score"] - score_timeline[0]["score"]
                )
                if improvement_total > 3:
                    trend = "improving"
                elif improvement_total < -3:
                    trend = "declining"
                else:
                    trend = "stable"

            # Determine tier label (no emojis, no pressure)
            tier = None
            tier_label = None
            next_step = None
            if current_score is not None:
                if current_score >= 76:
                    tier = "well_developed"
                    tier_label = "Well-Developed"
                    next_step = "Keep submitting updated versions as you grow."
                elif current_score >= 61:
                    tier = "solid"
                    tier_label = "Solid"
                    next_step = "Focus on bullet clarity and role alignment."
                elif current_score >= 41:
                    tier = "building"
                    tier_label = "Building"
                    next_step = "Work on skill alignment and content structure."
                else:
                    tier = "early_stage"
                    tier_label = "Early Stage"
                    next_step = "Start with structure and readability first."

            user_data = {
                "current_score": current_score,
                "tier": tier,
                "tier_label": tier_label,
                "next_step": next_step,
                "trend": trend,
                "improvement_total": improvement_total,
                "version_count": version_count,
                "score_timeline": score_timeline,
                "resume_strength": resume_strength,
                "skill_readiness": skill_readiness,
                "market_alignment": market_alignment,
                "has_data": bool(score_timeline or current_score),
            }

    return render_template("features/career_readiness.html", user_data=user_data)


# JSON API endpoints (for AJAX data refresh on feature pages) 

@features_bp.route("/api/user-snapshot")
def api_user_snapshot():
    """Returns all key user metrics as JSON for JS-powered data panels."""
    uid = _uid()
    if not uid:
        return jsonify({"authenticated": False})

    db = get_db()
    snapshot = _get_user_resume_snapshot(db, uid)
    health = _get_resume_health(db, uid)
    gap = _get_skill_gap(db, uid)
    history = _get_resume_history(db, uid, limit=10)
    confidence = db.execute(
        "SELECT * FROM confidence_index WHERE user_id = ?", (uid,)
    ).fetchone()

    return jsonify({
        "authenticated": True,
        "snapshot": snapshot,
        "health": dict(health) if health else None,
        "gap": dict(gap) if gap else None,
        "confidence": dict(confidence) if confidence else None,
        "history_count": len(history),
        "score_timeline": [
            {"date": r["created_at"][:10], "score": r["readiness_score"] or 0}
            for r in history
            if r.get("readiness_score") is not None
        ],
    })
