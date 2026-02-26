from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from config import SECRET_KEY, PERMANENT_SESSION_LIFETIME
from database.models import create_table
from database.db import init_db
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp
from routes.chatbot_routes import chatbot_bp, api_bp as chatbot_api_bp
from routes.auth_routes import auth_bp
from routes.resume_routes import resume_bp
from routes.dashboard_routes_new import dashboard_bp
from routes.saas_routes import saas_bp
from routes.contact_routes import contact_bp
import sys
import io
from datetime import timedelta

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

app = Flask(__name__)

# Configuration
app.secret_key = SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = PERMANENT_SESSION_LIFETIME
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = PERMANENT_SESSION_LIFETIME

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.context_processor
def inject_user():
    """Make current_user available in all templates."""
    from database.db import get_db
    user = None
    if 'user_id' in session:
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE id = ?', (session['user_id'],)
        ).fetchone()
    
    # Create a simple user object for templates
    class CurrentUser:
        def __init__(self, user=None):
            self.user = user
        
        @property
        def is_authenticated(self):
            return self.user is not None
        
        @property
        def name(self):
            return self.user['full_name'] if self.user else None
        
        @property
        def email(self):
            return self.user['email'] if self.user else None
        
        def __getattr__(self, name):
            if self.user and name in self.user:
                return self.user[name]
            return None
    
    return {'current_user': CurrentUser(user)}

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(chatbot_api_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(resume_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(saas_bp)
app.register_blueprint(contact_bp)

# Main routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/features/target-role')
def target_role_feature():
    return render_template('features/target_role.html')


@app.route('/api/analyze-resume', methods=['POST'])
def api_analyze_resume():
    """Analyze resume text in-page without file upload, save to DB, return JSON."""
    from database.db import get_db
    from services.ats_scorer import get_ats_score
    import re, json
    from datetime import datetime

    data = request.get_json(silent=True) or {}
    resume_text = (data.get('resumeText') or '').strip()
    role_text   = (data.get('roleText')   or '').strip()

    if not resume_text and not role_text:
        return jsonify({'success': False, 'message': 'Please provide resume text or target role.'}), 400

    # ── Simple text-based skill extraction ──────────────────────────────────
    SKILL_KEYWORDS = [
        'python','java','javascript','typescript','react','angular','vue','node',
        'sql','mysql','postgresql','mongodb','redis','aws','azure','gcp','docker',
        'kubernetes','git','linux','machine learning','deep learning','tensorflow',
        'pytorch','data analysis','excel','power bi','tableau','html','css',
        'c++','c#','ruby','php','swift','kotlin','rust','go','scala',
        'communication','leadership','project management','agile','scrum',
        'problem solving','teamwork','analytical','critical thinking',
    ]
    text_lower = resume_text.lower() + ' ' + role_text.lower()
    found_skills = [s for s in SKILL_KEYWORDS if s in text_lower]

    # ── ATS scoring ─────────────────────────────────────────────────────────
    has_experience = any(kw in text_lower for kw in
                         ['work experience','professional experience','employment',
                          'position','role','internship','job'])
    education = ['degree'] if any(kw in text_lower for kw in
                                  ['bachelor','master','phd','degree','university','college']) else []

    ats_result = get_ats_score({
        'skills': found_skills,
        'has_experience': has_experience,
        'education': education,
        'text_length': len(resume_text),
        'text': resume_text,
    })

    ats_score = int(ats_result.get('ats_score', 0))

    # ── Feedback generation ──────────────────────────────────────────────────
    word_count = len(resume_text.split()) if resume_text else 0
    has_metrics = bool(re.search(r'\d+[%$]|\d+\s*(percent|million|billion|k\b)', resume_text, re.I))
    has_action_verbs = any(v in text_lower for v in
                           ['led','managed','built','designed','implemented','delivered',
                            'improved','increased','reduced','created','developed'])

    overall_score = min(100, max(10,
        ats_score * 0.6 +
        (20 if has_metrics else 0) +
        (10 if has_action_verbs else 0) +
        (10 if len(found_skills) >= 5 else len(found_skills) * 2)
    ))

    feedback = {
        'ats_score': ats_score,
        'overall_score': round(overall_score),
        'word_count': word_count,
        'skills_found': found_skills,
        'skills_count': len(found_skills),
        'has_metrics': has_metrics,
        'has_action_verbs': has_action_verbs,
        'has_experience': has_experience,
        'education_found': len(education) > 0,
        'target_role': role_text,
        'recommendations': ats_result.get('recommendations', []),
        'strengths': ats_result.get('strengths', []),
        'blockers': ats_result.get('blockers', []),
        'categories': ats_result.get('categories', {}),
    }

    # ── Persist to DB ────────────────────────────────────────────────────────
    try:
        db = get_db()
        now = datetime.utcnow().isoformat()
        user_id = session.get('user_id', 'anonymous')
        db.execute(
            '''CREATE TABLE IF NOT EXISTS quick_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                resume_text TEXT,
                target_role TEXT,
                ats_score INTEGER,
                overall_score INTEGER,
                skills_found TEXT,
                recommendations TEXT,
                created_at TEXT NOT NULL
            )'''
        )
        db.execute(
            '''INSERT INTO quick_analyses
               (user_id, resume_text, target_role, ats_score, overall_score,
                skills_found, recommendations, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id, resume_text[:5000], role_text, ats_score,
             round(overall_score), json.dumps(found_skills),
             json.dumps(feedback['recommendations']), now)
        )
        db.commit()
    except Exception as e:
        print(f'DB save error: {e}')

    return jsonify({'success': True, 'data': feedback})


@app.route('/login')
def login():
    return redirect(url_for('auth.login'))

@app.route('/signup')
def signup():
    return redirect(url_for('auth.register'))

@app.route('/resume')
def resume_page():
    return redirect(url_for('resume.upload'))

@app.route('/profile')
def profile():
    return redirect(url_for('auth.profile'))

@app.route('/career-guidance')
def career_guidance():
    return redirect(url_for('dashboard.index'))

@app.route('/chatbot')
def chatbot():
    return redirect(url_for('chatbot.index'))

# Feature detail routes
@app.route('/features/ats-detection')
def ats_detection():
    return render_template('features/ats_detection.html')

@app.route('/features/gap-analysis')
def gap_analysis():
    return render_template('features/gap_analysis.html')

@app.route('/features/recruiter-perspective')
def recruiter_perspective():
    return render_template('features/recruiter_perspective.html')

@app.route('/features/bullet-impact')
def bullet_impact():
    return render_template('features/bullet_impact.html')

@app.route('/features/formatting-guidance')
def formatting_guidance():
    return render_template('features/formatting_guidance.html')

@app.route('/features/career-readiness')
def career_readiness():
    return render_template('features/career_readiness.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

# Initialize database and models on startup
with app.app_context():
    init_db()
    create_table()
    print("✓ Application initialized successfully")
    print("✓ Database connection established")
    print("✓ All blueprints registered")
    print("→ Ready to serve requests")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)