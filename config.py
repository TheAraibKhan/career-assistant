import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta

# Load .env from project root
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Admin credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'career_data.db')

# API Keys
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GROQ_MODEL = os.environ.get('GROQ_MODEL', 'mixtral-8x7b-32768')

# Rate limiting
CHATBOT_RATE_LIMIT = int(os.environ.get('CHATBOT_RATE_LIMIT', '100'))
CHATBOT_MAX_HISTORY = int(os.environ.get('CHATBOT_MAX_HISTORY', '20'))

# Session configuration
PERMANENT_SESSION_LIFETIME = timedelta(days=30)
SESSION_REFRESH_EACH_REQUEST = True

# File upload
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_RESUME_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_RESUME_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Feature flags
FEATURE_FLAGS = {
    'resume_upload': True,
    'profile_image': True,
    'ai_mentor': True,
    'user_accounts': True,
    'skill_roadmap': True,
}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)