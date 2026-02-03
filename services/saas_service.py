"""SaaS tier management, usage tracking, and feature flags."""
import json
from datetime import datetime, timedelta
from database.db import get_db


# ==================== TIER CONFIGURATION ====================

DEFAULT_TIER_CONFIG = {
    'free': {
        'name': 'Free',
        'career_analyses_limit': 3,
        'resume_uploads_limit': 1,
        'chatbot_messages_limit': 15,
        'features': {
            'career_analysis': True,
            'resume_upload': False,
            'chatbot': True,
            'skill_roadmap': False,
            'export_results': False,
            'priority_support': False
        }
    },
    'pro': {
        'name': 'Pro',
        'career_analyses_limit': 30,
        'resume_uploads_limit': 10,
        'chatbot_messages_limit': 300,
        'features': {
            'career_analysis': True,
            'resume_upload': True,
            'chatbot': True,
            'skill_roadmap': True,
            'export_results': True,
            'priority_support': True
        }
    },
    'business': {
        'name': 'Business',
        'career_analyses_limit': 999999,
        'resume_uploads_limit': 999999,
        'chatbot_messages_limit': 999999,
        'features': {
            'career_analysis': True,
            'resume_upload': True,
            'chatbot': True,
            'skill_roadmap': True,
            'export_results': True,
            'priority_support': True,
            'team_management': True,
            'api_access': True
        }
    }
}


# ==================== USER TIER MANAGEMENT ====================

def get_user_tier(user_id):
    """Get user's current tier."""
    db = get_db()
    user = db.execute('SELECT tier, is_premium FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        return None
    return {
        'tier': user['tier'] or 'free',
        'is_premium': bool(user['is_premium']),
        'tier_config': DEFAULT_TIER_CONFIG.get(user['tier'] or 'free')
    }


def upgrade_user_tier(user_id, new_tier):
    """Upgrade user to a new tier."""
    db = get_db()
    if new_tier not in DEFAULT_TIER_CONFIG:
        return {'error': 'Invalid tier'}
    
    is_premium = 1 if new_tier != 'free' else 0
    now = datetime.utcnow().isoformat()
    
    try:
        db.execute(
            'UPDATE users SET tier = ?, is_premium = ?, updated_at = ? WHERE id = ?',
            (new_tier, is_premium, now, user_id)
        )
        db.commit()
        return {'success': True, 'tier': new_tier}
    except Exception as e:
        db.rollback()
        return {'error': str(e)}


def get_tier_config(tier_name):
    """Get configuration for a specific tier."""
    return DEFAULT_TIER_CONFIG.get(tier_name, DEFAULT_TIER_CONFIG['free'])


# ==================== USAGE TRACKING ====================

def get_today_usage(user_id):
    """Get user's usage today."""
    db = get_db()
    today = datetime.utcnow().date().isoformat()
    
    usage = db.execute(
        'SELECT * FROM usage_tracking_daily WHERE user_id = ? AND date = ?',
        (user_id, today)
    ).fetchone()
    
    if not usage:
        return {
            'career_analyses_used': 0,
            'resume_uploads_used': 0,
            'chatbot_messages_used': 0
        }
    
    return {
        'career_analyses_used': usage['career_analyses_used'],
        'resume_uploads_used': usage['resume_uploads_used'],
        'chatbot_messages_used': usage['chatbot_messages_used']
    }


def get_month_usage(user_id):
    """Get user's usage this month."""
    db = get_db()
    today = datetime.utcnow().date()
    year_month = today.strftime('%Y-%m')
    
    usage = db.execute(
        'SELECT * FROM usage_tracking_monthly WHERE user_id = ? AND year_month = ?',
        (user_id, year_month)
    ).fetchone()
    
    if not usage:
        return {
            'career_analyses_used': 0,
            'resume_uploads_used': 0,
            'chatbot_messages_used': 0
        }
    
    return {
        'career_analyses_used': usage['career_analyses_used'],
        'resume_uploads_used': usage['resume_uploads_used'],
        'chatbot_messages_used': usage['chatbot_messages_used']
    }


def increment_usage(user_id, usage_type):
    """Increment a usage counter (daily & monthly)."""
    db = get_db()
    today = datetime.utcnow().date().isoformat()
    year_month = datetime.utcnow().date().strftime('%Y-%m')
    now = datetime.utcnow().isoformat()
    
    if usage_type not in ['career_analyses_used', 'resume_uploads_used', 'chatbot_messages_used']:
        return {'error': 'Invalid usage type'}
    
    try:
        # Update or insert daily tracking
        existing_daily = db.execute(
            'SELECT id FROM usage_tracking_daily WHERE user_id = ? AND date = ?',
            (user_id, today)
        ).fetchone()
        
        if existing_daily:
            db.execute(
                f'UPDATE usage_tracking_daily SET {usage_type} = {usage_type} + 1 WHERE user_id = ? AND date = ?',
                (user_id, today)
            )
        else:
            cols = ', '.join([f'{usage_type}'] if usage_type else [])
            vals = ', '.join(['?'] if usage_type else [])
            db.execute(
                f'INSERT INTO usage_tracking_daily (user_id, date, {usage_type}, created_at) VALUES (?, ?, 1, ?)',
                (user_id, today, now)
            )
        
        # Update or insert monthly tracking
        existing_monthly = db.execute(
            'SELECT id FROM usage_tracking_monthly WHERE user_id = ? AND year_month = ?',
            (user_id, year_month)
        ).fetchone()
        
        if existing_monthly:
            db.execute(
                f'UPDATE usage_tracking_monthly SET {usage_type} = {usage_type} + 1 WHERE user_id = ? AND year_month = ?',
                (user_id, year_month)
            )
        else:
            db.execute(
                f'INSERT INTO usage_tracking_monthly (user_id, year_month, {usage_type}, created_at) VALUES (?, ?, 1, ?)',
                (user_id, year_month, now)
            )
        
        db.commit()
        return {'success': True}
    except Exception as e:
        db.rollback()
        return {'error': str(e)}


# ==================== USAGE LIMITS & ENFORCEMENT ====================

def check_usage_limit(user_id, usage_type):
    """
    Check if user has exceeded their usage limit.
    Returns: {'allowed': True/False, 'remaining': int, 'limit': int, 'message': str}
    """
    user_tier = get_user_tier(user_id)
    if not user_tier:
        return {'allowed': False, 'message': 'User not found'}
    
    tier_config = user_tier['tier_config']
    limit_key = usage_type
    
    limit = tier_config.get(limit_key, 0)
    
    # Premium/enterprise users have no hard limit
    if user_tier['is_premium']:
        return {'allowed': True, 'remaining': limit, 'limit': limit, 'message': 'Unlimited'}
    
    # Check usage
    today_usage = get_today_usage(user_id)
    used = today_usage.get(usage_type, 0)
    remaining = max(0, limit - used)
    
    allowed = used < limit
    
    message = ''
    if not allowed:
        message = f"You've reached your daily limit of {limit} {usage_type.replace('_', ' ')}. Upgrade to Pro for unlimited access."
    elif remaining <= 1 and limit > 0:
        message = f"Only 1 {usage_type.split('_')[0]} remaining today. Upgrade to Pro for unlimited access."
    
    return {
        'allowed': allowed,
        'remaining': remaining,
        'limit': limit,
        'used': used,
        'message': message,
        'tier': user_tier['tier']
    }


def get_usage_context(user_id):
    """Get complete usage context for a user (for displaying in UI)."""
    user_tier = get_user_tier(user_id)
    if not user_tier:
        return None
    
    tier_config = user_tier['tier_config']
    today_usage = get_today_usage(user_id)
    month_usage = get_month_usage(user_id)
    
    return {
        'tier': user_tier['tier'],
        'is_premium': user_tier['is_premium'],
        'features': tier_config['features'],
        'today': {
            'career_analyses': {
                'used': today_usage['career_analyses_used'],
                'limit': tier_config['career_analyses_limit'],
                'remaining': max(0, tier_config['career_analyses_limit'] - today_usage['career_analyses_used'])
            },
            'resume_uploads': {
                'used': today_usage['resume_uploads_used'],
                'limit': tier_config['resume_uploads_limit'],
                'remaining': max(0, tier_config['resume_uploads_limit'] - today_usage['resume_uploads_used'])
            },
            'chatbot_messages': {
                'used': today_usage['chatbot_messages_used'],
                'limit': tier_config['chatbot_messages_limit'],
                'remaining': max(0, tier_config['chatbot_messages_limit'] - today_usage['chatbot_messages_used'])
            }
        },
        'month': {
            'career_analyses': {
                'used': month_usage['career_analyses_used'],
                'limit': tier_config['career_analyses_limit'] * 30,
            },
            'resume_uploads': {
                'used': month_usage['resume_uploads_used'],
                'limit': tier_config['resume_uploads_limit'] * 30,
            },
            'chatbot_messages': {
                'used': month_usage['chatbot_messages_used'],
                'limit': tier_config['chatbot_messages_limit'] * 30,
            }
        }
    }


# ==================== FEATURE FLAGS ====================

def has_feature(user_id, feature_name):
    """Check if user has access to a specific feature."""
    user_tier = get_user_tier(user_id)
    if not user_tier:
        return False
    
    features = user_tier['tier_config'].get('features', {})
    return features.get(feature_name, False)


def get_user_features(user_id):
    """Get all enabled features for user."""
    user_tier = get_user_tier(user_id)
    if not user_tier:
        return {}
    
    return user_tier['tier_config'].get('features', {})
