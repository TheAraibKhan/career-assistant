"""User authentication and session management."""
import bcrypt
import re
from datetime import datetime
from database.db import get_db


def hash_password(password):
    """Hash password with bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, pwd_hash):
    """Verify password against hash. Supports both bcrypt and legacy pbkdf2."""
    try:
        # Try bcrypt first (new format)
        if pwd_hash.startswith('$2'):
            return bcrypt.checkpw(password.encode('utf-8'), pwd_hash.encode('utf-8'))
        
        # Legacy pbkdf2 format (salt$hash) — for backward compatibility
        import hashlib
        salt, hash_val = pwd_hash.split('$', 1)
        pwd_verify = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return pwd_verify.hex() == hash_val
    except Exception:
        return False


def _validate_email(email):
    """Basic email format validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def create_user(email, password, full_name):
    """Create a new user account with default free tier."""
    # Input validation
    email = email.strip().lower()
    full_name = full_name.strip()
    
    if not _validate_email(email):
        return {'error': 'Invalid email format'}
    
    if len(password) < 8:
        return {'error': 'Password must be at least 8 characters'}
    
    if len(full_name) < 2 or len(full_name) > 100:
        return {'error': 'Name must be between 2 and 100 characters'}
    
    db = get_db()
    now = datetime.utcnow().isoformat()
    
    # Check if user exists
    existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
    if existing:
        return {'error': 'Email already registered'}
    
    pwd_hash = hash_password(password)
    
    try:
        cursor = db.execute(
            '''INSERT INTO users (email, password_hash, full_name, tier, is_premium, created_at, updated_at)
               VALUES (?, ?, ?, 'free', 0, ?, ?)''',
            (email, pwd_hash, full_name, now, now)
        )
        db.commit()
        return {'id': cursor.lastrowid, 'email': email, 'tier': 'free'}
    except Exception as e:
        db.rollback()
        return {'error': 'Account creation failed. Please try again.'}


def authenticate_user(email, password):
    """Authenticate user by email and password."""
    if not email or not password:
        return None
    
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE email = ? AND is_active = 1',
        (email.strip().lower(),)
    ).fetchone()
    
    if not user:
        # Constant-time comparison to prevent timing attacks
        verify_password('dummy', hash_password('dummy'))
        return None
    
    if verify_password(password, user['password_hash']):
        # Update last login
        db.execute(
            'UPDATE users SET last_login = ? WHERE id = ?',
            (datetime.utcnow().isoformat(), user['id'])
        )
        db.commit()
        
        # Upgrade legacy password hash to bcrypt on successful login
        if not user['password_hash'].startswith('$2'):
            new_hash = hash_password(password)
            db.execute(
                'UPDATE users SET password_hash = ? WHERE id = ?',
                (new_hash, user['id'])
            )
            db.commit()
        
        return user
    
    return None


def get_user_by_id(user_id):
    """Get user by ID."""
    if not user_id:
        return None
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    return user


def update_user_profile(user_id, full_name=None, profile_image_path=None):
    """Update user profile information."""
    db = get_db()
    now = datetime.utcnow().isoformat()
    
    if full_name:
        full_name = full_name.strip()[:100]  # sanitize
        db.execute(
            'UPDATE users SET full_name = ?, updated_at = ? WHERE id = ?',
            (full_name, now, user_id)
        )
    
    if profile_image_path:
        db.execute(
            'UPDATE users SET profile_image_path = ?, updated_at = ? WHERE id = ?',
            (profile_image_path, now, user_id)
        )
    
    db.commit()