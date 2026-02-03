from flask import Blueprint, render_template, request, redirect, url_for, session
from database.models import fetch_all_logs, get_database_stats
from services.analytics import get_dashboard_analytics
from config import ADMIN_USERNAME, ADMIN_PASSWORD
import traceback

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    force_login = request.args.get('force', 'false').lower() == 'true'
    
    if force_login:
        session.clear()
    
    if session.get("admin") is True and not force_login:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session.clear()
            session["admin"] = True
            session.permanent = False
            session.modified = True
            return redirect(url_for("admin.dashboard"))

        print(f"Admin login failed for user: {username}")
        return render_template(
            "admin_login.html",
            error="Invalid username or password"
        )

    return render_template("admin_login.html")


@admin_bp.route("/", methods=["GET"])
@admin_bp.route("/dashboard", methods=["GET"])
def dashboard():
    if session.get("admin") is not True:
        return redirect(url_for("admin.login"))

    try:
        logs = fetch_all_logs()
        stats = get_database_stats()
        analytics = get_dashboard_analytics()

        return render_template(
            "admin.html",
            logs=logs,
            stats=stats,
            analytics=analytics
        )

    except Exception as e:
        traceback.print_exc()
        return render_template(
            "admin.html",
            logs=[],
            stats={"total": 0, "by_interest": [], "by_level": []},
            analytics={
                "summary": {},
                "by_level": {},
                "by_interest": {},
                "most_recommended_roles": [],
                "most_common_missing_skills": [],
                "recent_activity": []
            },
            error="Failed to load admin data"
        )


# =========================
# Admin Logout
# =========================
@admin_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))
