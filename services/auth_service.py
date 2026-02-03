"""User authentication and session management."""
import hashlib
import secrets
from datetime import datetime
from database.db import get_db


def hash_password(password):
    """Hash password with salt."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"


def verify_password(password, pwd_hash):
    """Verify password against hash."""
    try:
        salt, hash_val = pwd_hash.split('$')
        pwd_verify = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return pwd_verify.hex() == hash_val
    except:
        return False


def create_user(email, password, full_name):
    """Create a new user account with default free tier."""
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
        return {'error': str(e)}


def authenticate_user(email, password):
    """Authenticate user by email and password."""
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE email = ? AND is_active = 1',
        (email,)
    ).fetchone()
    
    if not user:
        return None
    
    if verify_password(password, user['password_hash']):
        # Update last login
        db.execute(
            'UPDATE users SET last_login = ? WHERE id = ?',
            (datetime.utcnow().isoformat(), user['id'])
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