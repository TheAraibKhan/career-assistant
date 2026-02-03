"""SaaS subscription and trial management system."""
from datetime import datetime, timedelta
from database.db import get_db


class SubscriptionManager:
    """Manage user subscriptions and trials."""
    
    TIERS = {
        'free': {
            'name': 'Free',
            'price': 0,
            'limits': {
                'career_analyses': 5,
                'resume_uploads': 2,
                'chatbot_messages': 20,
                'monthly_storage_mb': 10
            },
            'features': [
                'Basic career analysis',
                'Resume upload (limited)',
                'AI chatbot (limited messages)',
                'Basic dashboard'
            ]
        },
        'pro': {
            'name': 'Pro',
            'price': 9.99,
            'limits': {
                'career_analyses': 100,
                'resume_uploads': 50,
                'chatbot_messages': 1000,
                'monthly_storage_mb': 500
            },
            'features': [
                'Unlimited career analysis',
                'Unlimited resume uploads',
                'Unlimited career mentoring',
                'Analytics dashboard',
                'Export reports',
                'Priority support',
                'API access'
            ]
        },
        'business': {
            'name': 'Business',
            'price': 49.99,
            'limits': {
                'career_analyses': 999999,
                'resume_uploads': 999999,
                'chatbot_messages': 999999,
                'monthly_storage_mb': 5000,
                'team_members': 10
            },
            'features': [
                'Everything in Pro',
                'Team management',
                'Custom branding',
                'Dedicated support',
                'SLA guarantee',
                'Custom integrations',
                'Custom workflows'
            ]
        }
    }
    
    @staticmethod
    def create_subscription(user_id, tier='free', trial_days=14):
        """Create new subscription for user."""
        db = get_db()
        
        now = datetime.utcnow()
        trial_end = now + timedelta(days=trial_days)
        
        # Check if subscription exists
        existing = db.execute(
            'SELECT id FROM subscriptions WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        
        if existing:
            return False
        
        db.execute('''
            INSERT INTO subscriptions 
            (user_id, tier, status, trial_started_at, trial_ends_at, current_period_start, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            tier,
            'active',
            now.isoformat(),
            trial_end.isoformat(),
            now.isoformat(),
            now.isoformat()
        ))
        
        db.commit()
        return True
    
    @staticmethod
    def get_subscription(user_id):
        """Get user's subscription info."""
        db = get_db()
        
        sub = db.execute(
            'SELECT * FROM subscriptions WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        
        if not sub:
            return None
        
        sub_dict = dict(sub)
        sub_dict['tier_info'] = SubscriptionManager.TIERS.get(sub['tier'], {})
        
        # Check trial status
        if sub['trial_ends_at']:
            trial_end = datetime.fromisoformat(sub['trial_ends_at'])
            now = datetime.utcnow()
            sub_dict['trial_active'] = now < trial_end
            sub_dict['trial_days_remaining'] = (trial_end - now).days
        
        return sub_dict
    
    @staticmethod
    def upgrade_subscription(user_id, new_tier):
        """Upgrade user to new tier."""
        db = get_db()
        
        if new_tier not in SubscriptionManager.TIERS:
            return False
        
        now = datetime.utcnow()
        
        db.execute('''
            UPDATE subscriptions
            SET tier = ?, updated_at = ?
            WHERE user_id = ?
        ''', (new_tier, now.isoformat(), user_id))
        
        db.commit()
        return True
    
    @staticmethod
    def check_usage_limit(user_id, feature_type):
        """Check if user has hit usage limit for feature."""
        db = get_db()
        
        sub = SubscriptionManager.get_subscription(user_id)
        if not sub:
            return True  # Block if no subscription
        
        tier = sub['tier']
        limits = SubscriptionManager.TIERS[tier]['limits']
        
        # Map feature types to limit keys
        feature_map = {
            'career_analysis': 'career_analyses',
            'resume_upload': 'resume_uploads',
            'chatbot_message': 'chatbot_messages'
        }
        
        limit_key = feature_map.get(feature_type)
        if not limit_key:
            return False  # Unknown feature, allow
        
        limit = limits.get(limit_key, 0)
        
        # Get usage this month
        now = datetime.utcnow()
        year_month = now.strftime('%Y-%m')
        
        usage = db.execute('''
            SELECT SUM(CASE WHEN ? THEN 1 ELSE 0 END) as count
            FROM usage_tracking_monthly
            WHERE user_id = ? AND year_month = ?
        ''', (f'{feature_type}_used', user_id, year_month)).fetchone()
        
        current_usage = usage['count'] or 0
        
        return current_usage < limit
    
    @staticmethod
    def track_usage(user_id, feature_type, quantity=1):
        """Track feature usage."""
        db = get_db()
        
        now = datetime.utcnow()
        year_month = now.strftime('%Y-%m')
        
        # Map feature types
        feature_map = {
            'career_analysis': 'career_analyses_used',
            'resume_upload': 'resume_uploads_used',
            'chatbot_message': 'chatbot_messages_used'
        }
        
        usage_col = feature_map.get(feature_type)
        if not usage_col:
            return False
        
        # Update or insert daily
        date_str = now.strftime('%Y-%m-%d')
        db.execute(f'''
            INSERT INTO usage_tracking_daily (user_id, date, {usage_col}, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, date) DO UPDATE SET {usage_col} = {usage_col} + ?
        ''', (user_id, date_str, quantity, now.isoformat(), quantity))
        
        # Update or insert monthly
        db.execute(f'''
            INSERT INTO usage_tracking_monthly (user_id, year_month, {usage_col}, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, year_month) DO UPDATE SET {usage_col} = {usage_col} + ?
        ''', (user_id, year_month, quantity, now.isoformat(), quantity))
        
        db.commit()
        return True
    
    @staticmethod
    def get_usage_summary(user_id):
        """Get user's usage summary."""
        db = get_db()
        
        sub = SubscriptionManager.get_subscription(user_id)
        if not sub:
            return None
        
        tier = sub['tier']
        limits = SubscriptionManager.TIERS[tier]['limits']
        
        now = datetime.utcnow()
        year_month = now.strftime('%Y-%m')
        
        usage = db.execute('''
            SELECT 
                COALESCE(career_analyses_used, 0) as career_analyses,
                COALESCE(resume_uploads_used, 0) as resume_uploads,
                COALESCE(chatbot_messages_used, 0) as chatbot_messages
            FROM usage_tracking_monthly
            WHERE user_id = ? AND year_month = ?
        ''', (user_id, year_month)).fetchone()
        
        if not usage:
            usage = {
                'career_analyses': 0,
                'resume_uploads': 0,
                'chatbot_messages': 0
            }
        else:
            usage = dict(usage)
        
        return {
            'tier': tier,
            'current_usage': usage,
            'limits': limits,
            'usage_percentage': {
                'career_analyses': (usage['career_analyses'] / limits['career_analyses'] * 100) if limits['career_analyses'] else 0,
                'resume_uploads': (usage['resume_uploads'] / limits['resume_uploads'] * 100) if limits['resume_uploads'] else 0,
                'chatbot_messages': (usage['chatbot_messages'] / limits['chatbot_messages'] * 100) if limits['chatbot_messages'] else 0
            },
            'limits_exceeded': any([
                usage['career_analyses'] >= limits['career_analyses'],
                usage['resume_uploads'] >= limits['resume_uploads'],
                usage['chatbot_messages'] >= limits['chatbot_messages']
            ])
        }


class TrialManager:
    """Manage trial periods."""
    
    @staticmethod
    def start_trial(user_id, trial_days=14):
        """Start trial for user."""
        db = get_db()
        
        now = datetime.utcnow()
        trial_end = now + timedelta(days=trial_days)
        
        db.execute('''
            UPDATE subscriptions
            SET trial_started_at = ?, trial_ends_at = ?
            WHERE user_id = ?
        ''', (now.isoformat(), trial_end.isoformat(), user_id))
        
        db.commit()
    
    @staticmethod
    def is_trial_active(user_id):
        """Check if user's trial is still active."""
        db = get_db()
        
        sub = db.execute(
            'SELECT trial_ends_at FROM subscriptions WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        
        if not sub or not sub['trial_ends_at']:
            return False
        
        trial_end = datetime.fromisoformat(sub['trial_ends_at'])
        return datetime.utcnow() < trial_end
    
    @staticmethod
    def get_trial_status(user_id):
        """Get detailed trial status."""
        db = get_db()
        
        sub = db.execute('''
            SELECT trial_started_at, trial_ends_at FROM subscriptions WHERE user_id = ?
        ''', (user_id,)).fetchone()
        
        if not sub:
            return None
        
        now = datetime.utcnow()
        
        if not sub['trial_ends_at']:
            return {
                'active': False,
                'message': 'No trial period'
            }
        
        trial_end = datetime.fromisoformat(sub['trial_ends_at'])
        days_remaining = (trial_end - now).days
        
        if days_remaining < 0:
            return {
                'active': False,
                'message': 'Trial has ended',
                'ended_at': sub['trial_ends_at']
            }
        
        return {
            'active': True,
            'days_remaining': days_remaining,
            'ends_at': sub['trial_ends_at'],
            'message': f'Trial ends in {days_remaining} day{"s" if days_remaining != 1 else ""}'
        }


class BillingManager:
    """Manage billing and invoices."""
    
    @staticmethod
    def generate_invoice(subscription_id):
        """Generate invoice for subscription."""
        db = get_db()
        
        sub = db.execute(
            'SELECT * FROM subscriptions WHERE id = ?',
            (subscription_id,)
        ).fetchone()
        
        if not sub:
            return None
        
        tier_info = SubscriptionManager.TIERS.get(sub['tier'], {})
        
        invoice = {
            'invoice_id': f"INV-{sub['id']}-{datetime.utcnow().strftime('%Y%m%d')}",
            'user_id': sub['user_id'],
            'tier': sub['tier'],
            'amount': tier_info.get('price', 0),
            'currency': 'USD',
            'period_start': sub['current_period_start'],
            'period_end': datetime.utcnow().isoformat(),
            'generated_at': datetime.utcnow().isoformat(),
            'status': 'unpaid',
            'items': [
                {
                    'description': f"{tier_info.get('name', 'Unknown')} Tier Subscription",
                    'quantity': 1,
                    'unit_price': tier_info.get('price', 0),
                    'total': tier_info.get('price', 0)
                }
            ]
        }
        
        return invoice
