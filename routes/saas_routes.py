"""SaaS Dashboard routes for user insights and engagement."""
from flask import Blueprint, render_template, request, jsonify, session
from services.user_experience import UserExperienceTracker, OnboardingManager, PersonalizationEngine, AchievementManager
from services.subscription_service import SubscriptionManager, TrialManager
from services.empathy_mentor import MentorshipJourney
from services.accessibility import GDPRCompliance, ConsentManager
from database.db import get_db
from functools import wraps
from datetime import datetime, timedelta

saas_bp = Blueprint('saas', __name__, url_prefix='/api/saas')


def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


@saas_bp.route('/user/health', methods=['GET'])
@login_required
def get_user_health():
    """Get user engagement health score."""
    user_id = session.get('user_id')
    health = UserExperienceTracker.get_user_health_score(user_id)
    
    return jsonify({
        'success': True,
        'health': health
    })


@saas_bp.route('/onboarding/status', methods=['GET'])
@login_required
def get_onboarding_status():
    """Get user's onboarding progress."""
    user_id = session.get('user_id')
    status = OnboardingManager.get_onboarding_status(user_id)
    next_step = OnboardingManager.get_next_onboarding_step(user_id)
    
    return jsonify({
        'success': True,
        'status': status,
        'next_step': next_step
    })


@saas_bp.route('/onboarding/complete-step', methods=['POST'])
@login_required
def complete_onboarding_step():
    """Mark onboarding step as complete."""
    user_id = session.get('user_id')
    step = request.json.get('step')
    
    if not step:
        return jsonify({'error': 'Step required'}), 400
    
    success = OnboardingManager.mark_step_complete(user_id, step)
    
    if success:
        UserExperienceTracker.track_interaction(user_id, f'onboarding_{step}_completed')
    
    return jsonify({'success': success})


@saas_bp.route('/preferences/get', methods=['GET'])
@login_required
def get_preferences():
    """Get user preferences."""
    user_id = session.get('user_id')
    prefs = PersonalizationEngine.get_user_preferences(user_id)
    
    return jsonify({
        'success': True,
        'preferences': prefs
    })


@saas_bp.route('/preferences/update', methods=['POST'])
@login_required
def update_preferences():
    """Update user preferences."""
    user_id = session.get('user_id')
    preferences = request.json
    
    PersonalizationEngine.update_preferences(user_id, preferences)
    UserExperienceTracker.track_interaction(user_id, 'preferences_updated', preferences)
    
    return jsonify({'success': True})


@saas_bp.route('/achievements', methods=['GET'])
@login_required
def get_achievements():
    """Get user's achievements."""
    user_id = session.get('user_id')
    achievements = AchievementManager.get_user_achievements(user_id)
    
    return jsonify({
        'success': True,
        'achievements': achievements,
        'total': len(achievements)
    })


@saas_bp.route('/journey/status', methods=['GET'])
@login_required
def get_journey_status():
    """Get user's mentorship journey status."""
    user_id = session.get('user_id')
    journey = MentorshipJourney.get_journey_status(user_id)
    
    if not journey:
        return jsonify({'error': 'No submission found'}), 404
    
    motivational = MentorshipJourney.get_motivational_message(
        journey['stage'],
        journey['readiness_score'],
        journey['confidence_score']
    )
    
    return jsonify({
        'success': True,
        'journey': journey,
        'motivational_message': motivational
    })


@saas_bp.route('/subscription/info', methods=['GET'])
@login_required
def get_subscription_info():
    """Get user's subscription info."""
    user_id = session.get('user_id')
    subscription = SubscriptionManager.get_subscription(user_id)
    usage = SubscriptionManager.get_usage_summary(user_id)
    trial = TrialManager.get_trial_status(user_id) if subscription else None
    
    return jsonify({
        'success': True,
        'subscription': subscription,
        'usage': usage,
        'trial': trial
    })


@saas_bp.route('/subscription/upgrade', methods=['POST'])
@login_required
def upgrade_subscription():
    """Upgrade to a new tier."""
    user_id = session.get('user_id')
    new_tier = request.json.get('tier')
    
    if not new_tier:
        return jsonify({'error': 'Tier required'}), 400
    
    success = SubscriptionManager.upgrade_subscription(user_id, new_tier)
    
    if success:
        UserExperienceTracker.track_interaction(user_id, 'subscription_upgraded', {'new_tier': new_tier})
    
    return jsonify({'success': success})


@saas_bp.route('/feedback/submit', methods=['POST'])
@login_required
def submit_feedback():
    """Submit user feedback."""
    user_id = session.get('user_id')
    feedback_text = request.json.get('feedback', '').strip()
    rating = request.json.get('rating', 0)
    feature = request.json.get('feature', 'general')
    
    if not feedback_text or not rating:
        return jsonify({'error': 'Feedback and rating required'}), 400
    
    UserExperienceTracker.submit_feedback(user_id, feedback_text, rating, feature)
    UserExperienceTracker.track_interaction(user_id, 'feedback_submitted', {'feature': feature})
    
    return jsonify({'success': True, 'message': 'Thank you for your feedback!'})


@saas_bp.route('/data/export', methods=['GET'])
@login_required
def export_data():
    """Export user's data (GDPR)."""
    user_id = session.get('user_id')
    data_json = GDPRCompliance.export_user_data(user_id)
    
    return jsonify({
        'success': True,
        'data': data_json,
        'export_date': datetime.utcnow().isoformat()
    })


@saas_bp.route('/data/delete', methods=['POST'])
@login_required
def delete_data():
    """Delete user's data (right to be forgotten)."""
    user_id = session.get('user_id')
    
    # Require confirmation
    confirm = request.json.get('confirm', False)
    if not confirm:
        return jsonify({'error': 'Deletion must be confirmed'}), 400
    
    success = GDPRCompliance.delete_user_data(user_id)
    
    if success:
        session.clear()
    
    return jsonify({
        'success': success,
        'message': 'Your data has been deleted. Session cleared.'
    })


@saas_bp.route('/consent/status', methods=['GET'])
@login_required
def get_consent_status():
    """Get user's consent status."""
    user_id = session.get('user_id')
    consents = ConsentManager.get_user_consent_status(user_id)
    
    return jsonify({
        'success': True,
        'consents': consents,
        'consent_types': ConsentManager.CONSENT_TYPES
    })


@saas_bp.route('/consent/update', methods=['POST'])
@login_required
def update_consents():
    """Update user consent preferences."""
    user_id = session.get('user_id')
    consents_dict = request.json.get('consents', {})
    
    ConsentManager.update_consents(user_id, consents_dict)
    UserExperienceTracker.track_interaction(user_id, 'consents_updated', consents_dict)
    
    return jsonify({'success': True})


@saas_bp.route('/dashboard/summary', methods=['GET'])
@login_required
def get_dashboard_summary():
    """Get comprehensive dashboard summary."""
    user_id = session.get('user_id')
    db = get_db()
    
    # Get user info
    user = db.execute(
        'SELECT * FROM users WHERE email = ?',
        (session.get('email'),)
    ).fetchone()
    
    # Get submission data
    latest_submission = db.execute(
        'SELECT * FROM submissions WHERE user_id = ? ORDER BY created_at DESC LIMIT 1',
        (user_id,)
    ).fetchone()
    
    # Get various stats
    health = UserExperienceTracker.get_user_health_score(user_id)
    journey = MentorshipJourney.get_journey_status(user_id)
    subscription = SubscriptionManager.get_subscription(user_id)
    achievements = AchievementManager.get_user_achievements(user_id)
    onboarding = OnboardingManager.get_onboarding_status(user_id)
    
    return jsonify({
        'success': True,
        'summary': {
            'user_info': dict(user) if user else None,
            'latest_submission': dict(latest_submission) if latest_submission else None,
            'health_score': health['score'] if health else 0,
            'journey_stage': journey['stage'] if journey else None,
            'readiness_score': journey['readiness_score'] if journey else 0,
            'confidence_score': journey['confidence_score'] if journey else 0,
            'subscription_tier': subscription['tier'] if subscription else 'free',
            'achievements_count': len(achievements),
            'onboarding_complete': onboarding['completion_percentage'] if onboarding else 0
        }
    })
