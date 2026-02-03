"""Human-centered UX tracking and feedback service."""
import json
from datetime import datetime, timedelta
from database.db import get_db


class UserExperienceTracker:
    """Track user interactions and experience metrics."""
    
    @staticmethod
    def track_interaction(user_id, interaction_type, metadata=None):
        """Log user interaction for UX analysis."""
        db = get_db()
        
        db.execute('''
            INSERT INTO user_interactions 
            (user_id, interaction_type, metadata, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (
            user_id,
            interaction_type,
            json.dumps(metadata or {}),
            datetime.utcnow().isoformat()
        ))
        db.commit()
    
    @staticmethod
    def submit_feedback(user_id, feedback_text, rating, feature=None):
        """Collect user feedback with sentiment."""
        db = get_db()
        
        db.execute('''
            INSERT INTO user_feedback 
            (user_id, feedback_text, rating, feature, submitted_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id,
            feedback_text,
            rating,
            feature,
            datetime.utcnow().isoformat()
        ))
        db.commit()
    
    @staticmethod
    def get_user_health_score(user_id):
        """Calculate user engagement health score (0-100)."""
        db = get_db()
        
        # Get interaction count in last 7 days
        interactions = db.execute('''
            SELECT COUNT(*) as count FROM user_interactions
            WHERE user_id = ? AND timestamp > datetime('now', '-7 days')
        ''', (user_id,)).fetchone()
        
        # Get average feedback rating
        feedback = db.execute('''
            SELECT AVG(rating) as avg_rating FROM user_feedback
            WHERE user_id = ?
        ''', (user_id,)).fetchone()
        
        # Get login frequency
        logins = db.execute('''
            SELECT COUNT(*) as count FROM user_interactions
            WHERE user_id = ? AND interaction_type = 'login'
            AND timestamp > datetime('now', '-7 days')
        ''', (user_id,)).fetchone()
        
        interaction_score = min(100, (interactions['count'] or 0) * 5)
        feedback_score = (feedback['avg_rating'] or 3) * 20
        login_score = min(100, (logins['count'] or 0) * 10)
        
        health_score = (interaction_score + feedback_score + login_score) / 3
        
        return {
            'score': int(health_score),
            'engagement_level': 'high' if health_score > 70 else 'medium' if health_score > 40 else 'low',
            'last_active': db.execute('''
                SELECT timestamp FROM user_interactions
                WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1
            ''', (user_id,)).fetchone()
        }


class OnboardingManager:
    """Structured onboarding flow for new users."""
    
    @staticmethod
    def get_onboarding_status(user_id):
        """Get user's onboarding completion status."""
        db = get_db()
        
        status = db.execute('''
            SELECT * FROM onboarding_progress WHERE user_id = ?
        ''', (user_id,)).fetchone()
        
        if not status:
            return {
                'profile_complete': False,
                'resume_uploaded': False,
                'preferences_set': False,
                'tutorial_watched': False,
                'first_recommendation': False,
                'completion_percentage': 0
            }
        
        return dict(status)
    
    @staticmethod
    def mark_step_complete(user_id, step):
        """Mark onboarding step as complete."""
        db = get_db()
        
        steps = [
            'profile_complete',
            'resume_uploaded',
            'preferences_set',
            'tutorial_watched',
            'first_recommendation'
        ]
        
        if step not in steps:
            return False
        
        db.execute(f'''
            UPDATE onboarding_progress SET {step} = 1
            WHERE user_id = ?
        ''', (user_id,))
        
        # Calculate completion
        progress = db.execute('''
            SELECT * FROM onboarding_progress WHERE user_id = ?
        ''', (user_id,)).fetchone()
        
        completed = sum([
            progress['profile_complete'],
            progress['resume_uploaded'],
            progress['preferences_set'],
            progress['tutorial_watched'],
            progress['first_recommendation']
        ])
        
        completion_percentage = (completed / len(steps)) * 100
        
        db.execute('''
            UPDATE onboarding_progress SET completion_percentage = ?
            WHERE user_id = ?
        ''', (int(completion_percentage), user_id))
        
        db.commit()
        return True
    
    @staticmethod
    def get_next_onboarding_step(user_id):
        """Get the next recommended onboarding step."""
        status = OnboardingManager.get_onboarding_status(user_id)
        
        steps_order = [
            ('profile_complete', 'Complete your profile'),
            ('resume_uploaded', 'Upload your resume'),
            ('preferences_set', 'Set your learning preferences'),
            ('tutorial_watched', 'Watch the quick tutorial'),
            ('first_recommendation', 'Get your first recommendation')
        ]
        
        for step_key, step_label in steps_order:
            if not status[step_key]:
                return {
                    'step': step_key,
                    'label': step_label,
                    'completion_before': int((steps_order.index((step_key, step_label)) / len(steps_order)) * 100)
                }
        
        return None  # All steps complete


class PersonalizationEngine:
    """Personalize experience based on user preferences and behavior."""
    
    @staticmethod
    def get_user_preferences(user_id):
        """Get user's personalization preferences."""
        db = get_db()
        
        prefs = db.execute('''
            SELECT * FROM user_preferences WHERE user_id = ?
        ''', (user_id,)).fetchone()
        
        if not prefs:
            return {
                'communication_style': 'friendly',  # friendly, professional, technical
                'learning_pace': 'balanced',  # slow, balanced, fast
                'goal_orientation': 'career',  # career, skill, confidence
                'notification_frequency': 'daily',  # never, daily, weekly
                'dark_mode': False,
                'email_updates': True,
                'show_tips': True
            }
        
        return dict(prefs)
    
    @staticmethod
    def update_preferences(user_id, preferences):
        """Update user preferences."""
        db = get_db()
        
        db.execute('''
            INSERT OR REPLACE INTO user_preferences
            (user_id, communication_style, learning_pace, goal_orientation,
             notification_frequency, dark_mode, email_updates, show_tips, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            preferences.get('communication_style', 'friendly'),
            preferences.get('learning_pace', 'balanced'),
            preferences.get('goal_orientation', 'career'),
            preferences.get('notification_frequency', 'daily'),
            preferences.get('dark_mode', False),
            preferences.get('email_updates', True),
            preferences.get('show_tips', True),
            datetime.utcnow().isoformat()
        ))
        
        db.commit()
    
    @staticmethod
    def get_personalized_chatbot_context(user_id):
        """Build personalized chatbot context based on user preferences."""
        prefs = PersonalizationEngine.get_user_preferences(user_id)
        
        context = {
            'tone': {
                'friendly': 'warm, encouraging, supportive',
                'professional': 'formal, structured, goal-oriented',
                'technical': 'detailed, precise, specification-focused'
            }[prefs['communication_style']],
            'pace_guidance': {
                'slow': 'Take time to master fundamentals',
                'balanced': 'Balanced approach with depth and breadth',
                'fast': 'Quick progression through concepts'
            }[prefs['learning_pace']],
            'goal_focus': {
                'career': 'focus on career advancement and job readiness',
                'skill': 'focus on skill acquisition and mastery',
                'confidence': 'focus on building confidence and overcoming imposter syndrome'
            }[prefs['goal_orientation']]
        }
        
        return context


class AchievementManager:
    """Track and celebrate user milestones and achievements."""
    
    ACHIEVEMENTS = {
        'first_steps': {
            'name': 'Getting Started',
            'description': 'Completed your profile setup',
            'icon': '🚀',
            'trigger': 'profile_complete'
        },
        'resume_upload': {
            'name': 'Document Ready',
            'description': 'Uploaded your first resume',
            'icon': '📄',
            'trigger': 'resume_uploaded'
        },
        'skill_explorer': {
            'name': 'Skill Explorer',
            'description': 'Identified 5+ skills in your profile',
            'icon': '🔍',
            'trigger': 'skill_count_5'
        },
        'goal_setter': {
            'name': 'Goal Setter',
            'description': 'Set learning preferences and goals',
            'icon': '🎯',
            'trigger': 'preferences_set'
        },
        'conversation_starter': {
            'name': 'Conversation Starter',
            'description': 'Had 10+ conversations with career mentor',
            'icon': '💬',
            'trigger': 'chat_count_10'
        },
        'learner': {
            'name': 'Lifelong Learner',
            'description': 'Completed a learning roadmap',
            'icon': '📚',
            'trigger': 'roadmap_progress_100'
        },
        'consistent': {
            'name': 'Consistent Performer',
            'description': 'Logged in 7 days in a row',
            'icon': '🔥',
            'trigger': 'consecutive_logins_7'
        },
        'milestone_master': {
            'name': 'Milestone Master',
            'description': 'Reached a 75% readiness score',
            'icon': '⭐',
            'trigger': 'readiness_score_75'
        }
    }
    
    @staticmethod
    def unlock_achievement(user_id, achievement_key):
        """Unlock an achievement for a user."""
        db = get_db()
        
        # Check if already unlocked
        existing = db.execute('''
            SELECT id FROM user_achievements
            WHERE user_id = ? AND achievement_key = ?
        ''', (user_id, achievement_key)).fetchone()
        
        if existing:
            return False
        
        if achievement_key not in AchievementManager.ACHIEVEMENTS:
            return False
        
        achievement = AchievementManager.ACHIEVEMENTS[achievement_key]
        
        db.execute('''
            INSERT INTO user_achievements
            (user_id, achievement_key, name, description, icon, unlocked_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            achievement_key,
            achievement['name'],
            achievement['description'],
            achievement['icon'],
            datetime.utcnow().isoformat()
        ))
        
        db.commit()
        return True
    
    @staticmethod
    def get_user_achievements(user_id):
        """Get all achievements for a user."""
        db = get_db()
        
        achievements = db.execute('''
            SELECT achievement_key, name, description, icon, unlocked_at
            FROM user_achievements
            WHERE user_id = ?
            ORDER BY unlocked_at DESC
        ''', (user_id,)).fetchall()
        
        return [dict(a) for a in achievements]
