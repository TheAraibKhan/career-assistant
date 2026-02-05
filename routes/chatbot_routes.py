"""
AI Chatbot routes with SaaS-integrated free API.
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from services.ai_chatbot_service import CareerChatbot
from services.saas_service import check_usage_limit, increment_usage
from database.models import track_chatbot_analytics
from services.auth_service import get_user_by_id
from functools import wraps
import uuid
import json

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')


def login_required(f):
    """Decorator to require login for chatbot."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@chatbot_bp.route('/', methods=['GET'])
@login_required
def index():
    """Display chatbot interface."""
    user_id = session.get('user_id')
    user = get_user_by_id(user_id)
    
    if not user:
        return redirect(url_for('auth.login'))
    
    return render_template('chatbot/index.html', user=user)


# API routes
api_bp = Blueprint('chatbot_api', __name__, url_prefix='/api/chat')


def api_login_required(f):
    """Decorator to require login for chatbot API."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


@api_bp.route('/message', methods=['POST'])
@api_login_required
def chat_message():
    """Handle chatbot messages with SaaS usage limits."""
    try:
        user_id = session.get('user_id')
        message = request.json.get('message', '').strip()
        session_id = request.json.get('session_id', str(uuid.uuid4()))
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Check usage limits
        usage_check = check_usage_limit(user_id, 'chatbot_messages_used')
        if not usage_check['allowed']:
            return jsonify({
                'error': usage_check['message'],
                'remaining': usage_check['remaining']
            }), 429
        
        # Get user context
        user_context = {
            'interest': request.json.get('interest'),
            'level': request.json.get('level'),
            'skills': request.json.get('skills'),
            'goal': request.json.get('goal')
        }
        
        # Initialize chatbot
        chatbot = CareerChatbot(user_id=user_id, session_id=session_id)
        
        # Generate response
        response_data = chatbot.generate_response(message, user_context)
        bot_response = response_data.get('response', '')
        
        if not bot_response:
            return jsonify({'error': 'Failed to generate response'}), 500
        
        # Save to database
        chatbot.save_message(message, bot_response)
        
        # Increment usage
        increment_usage(user_id, 'chatbot_messages_used')
        track_chatbot_analytics(user_id, 'message_sent', {'topic': 'career_guidance'})
        
        return jsonify({
            'success': True,
            'message': message,
            'response': bot_response,
            'timestamp': request.json.get('timestamp'),
            'remaining': usage_check['remaining'] - 1
        })
    
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500


@api_bp.route('/history', methods=['GET'])
@login_required
def chat_history():
    """Get chat history."""
    user_id = session.get('user_id')
    session_id = request.args.get('session_id', '')
    
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400
    
    chatbot = CareerChatbot(user_id=user_id, session_id=session_id)
    history = chatbot.get_conversation_history(limit=20)
    
    messages = []
    for msg in history:
        messages.append({
            'message': msg['message'],
            'response': msg['response'],
            'timestamp': msg['created_at']
        })
    
    return jsonify({'messages': messages})


@api_bp.route('/start', methods=['POST'])
@login_required
def start_session():
    """Start new chat session."""
    user_id = session.get('user_id')
    session_id = str(uuid.uuid4())
    
    track_chatbot_analytics(user_id, 'session_started', {'action': 'new_session'})
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'user_id': user_id
    })


@api_bp.route('/context', methods=['POST'])
@login_required
def update_context():
    """Update chatbot context with user data."""
    user_id = session.get('user_id')
    
    context = {
        'interest': request.json.get('interest'),
        'level': request.json.get('level'),
        'skills': request.json.get('skills', []),
        'goal': request.json.get('goal')
    }
    
    session['chatbot_context'] = context
    track_chatbot_analytics(user_id, 'context_updated', context)
    
    return jsonify({'success': True, 'context': context})


@api_bp.route('/greeting', methods=['GET'])
def greeting():
    """Get greeting message without requiring login."""
    greeting_messages = [
        "Hi there! 👋 I'm your AI Career Mentor. What's on your mind today?",
        "Welcome! 🎓 Ready to explore your career path?",
        "Hey! 🚀 Let's work on your career goals together.",
        "Hello! 💼 What can I help you with regarding your career?",
        "Welcome back! 📈 How can I support your career journey today?"
    ]
    
    import random
    return jsonify({
        'success': True,
        'message': random.choice(greeting_messages),
        'tips': [
            'Ask me about career paths for your interests',
            'Tell me about your skills and I\'ll find suitable roles',
            'Need help with skill gaps? I\'m here for that!',
            'Want to know about your career readiness? Just ask!'
        ]
    })