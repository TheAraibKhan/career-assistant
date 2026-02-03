"""User authentication routes."""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from services.auth_service import create_user, authenticate_user, get_user_by_id, update_user_profile
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not all([email, password, full_name, confirm_password]):
            error = 'All fields are required'
        elif password != confirm_password:
            error = 'Passwords do not match'
        elif len(password) < 8:
            error = 'Password must be at least 8 characters'
        else:
            result = create_user(email, password, full_name)
            if 'error' not in result:
                session['user_id'] = result['id']
                return redirect(url_for('user.home'))
            else:
                error = result['error']
    
    return render_template('auth/register.html', error=error)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            error = 'Email and password are required'
        else:
            user = authenticate_user(email, password)
            if user:
                session['user_id'] = user['id']
                session['email'] = user['email']
                session['full_name'] = user['full_name']
                return redirect(url_for('user.home'))
            else:
                error = 'Invalid email or password'
    
    return render_template('auth/login.html', error=error)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.home'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session.get('user_id')
    user = get_user_by_id(user_id)
    error = None
    success = None
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        
        if full_name:
            update_user_profile(user_id, full_name=full_name)
            session['full_name'] = full_name
            success = 'Saved'
            user = get_user_by_id(user_id)
    
    return render_template('auth/profile.html', user=user, error=error, success=success)