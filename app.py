from flask import Flask, render_template, session
from config import SECRET_KEY, PERMANENT_SESSION_LIFETIME
from database.models import create_table
from database.db import init_db
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp
from routes.chatbot_routes import chatbot_bp
from routes.auth_routes import auth_bp
from routes.resume_routes import resume_bp
from routes.dashboard_routes import dashboard_bp
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

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(resume_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(saas_bp)
app.register_blueprint(contact_bp)

# Main routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard/index.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

# Create DB on startup
with app.app_context():
    init_db()
    create_table()
    print("Application initialized successfully")
    print("Database connection established")
    print("All blueprints registered")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)