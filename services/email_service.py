"""Email notification service for user engagement and milestones."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from database.db import get_db


class EmailNotificationService:
    """Send personalized, human-centered email notifications."""
    
    @staticmethod
    def send_welcome_email(user_name, user_email, next_steps):
        """Send welcome email to new users."""
        
        subject = f"Welcome to Smart Career Assistant, {user_name}! 🎯"
        
        body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
        <h2>Welcome, {user_name}!</h2>
        
        <p>We're excited to have you join our community of career explorers and builders.</p>
        
        <h3>Here's What You Can Do Next:</h3>
        <ul>
            <li><strong>Complete Your Profile</strong> - Tell us about your career interests and current level</li>
            <li><strong>Upload Your Resume</strong> - We'll analyze your skills and experience</li>
            <li><strong>Get Personalized Insights</strong> - Discover your career path and learning roadmap</li>
            <li><strong>Chat with Your Mentor</strong> - Get guidance on any career question</li>
        </ul>
        
        <p><a href="https://smartcareer.app/dashboard" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Get Started →</a></p>
        
        <hr>
        <p style="font-size: 12px; color: #666;">
            Questions? We're here to help. Reply to this email or visit our <a href="https://smartcareer.app/help">Help Center</a>.
        </p>
    </div>
</body>
</html>
        """
        
        return {
            'subject': subject,
            'body': body,
            'recipient': user_email,
            'template': 'welcome',
            'scheduled_for': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def send_progress_update(user_name, user_email, metrics):
        """Send progress update email."""
        
        readiness = metrics.get('readiness_score', 0)
        confidence = metrics.get('confidence_score', 0)
        recent_goals = metrics.get('recent_goals', [])
        
        if readiness >= 75:
            progress_message = "🚀 You're almost there! You're in the home stretch."
        elif readiness >= 50:
            progress_message = "📈 Great progress! You're building real momentum."
        else:
            progress_message = "🌱 You're off to a solid start. Keep going!"
        
        subject = f"{progress_message} - Your Career Progress"
        
        body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
        <h2>Your Career Progress</h2>
        
        <p>{progress_message}</p>
        
        <div style="background-color: white; padding: 15px; border-radius: 4px; margin: 20px 0;">
            <h3>Current Metrics</h3>
            <ul>
                <li>Career Readiness: {readiness}%</li>
                <li>Confidence Level: {confidence}%</li>
            </ul>
        </div>
        
        <h3>What to Focus On Next</h3>
        <p>Based on your profile, we recommend:</p>
        <ul>
            <li>Continue building core competencies</li>
            <li>Work on skill gaps that matter most</li>
            <li>Document your learning progress</li>
        </ul>
        
        <p><a href="https://smartcareer.app/dashboard" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">View Your Dashboard →</a></p>
        
        <hr>
        <p style="font-size: 12px; color: #666;">
            This email was sent based on your notification preferences. <a href="https://smartcareer.app/settings">Manage your preferences</a>.
        </p>
    </div>
</body>
</html>
        """
        
        return {
            'subject': subject,
            'body': body,
            'recipient': user_email,
            'template': 'progress_update',
            'metrics': metrics
        }
    
    @staticmethod
    def send_achievement_email(user_name, user_email, achievement):
        """Send congratulations email for achievements."""
        
        subject = f"🎉 Achievement Unlocked: {achievement['name']}!"
        
        body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
        <h2>🎉 Congratulations, {user_name}!</h2>
        
        <div style="background-color: white; padding: 20px; border-radius: 4px; text-align: center; margin: 20px 0;">
            <h3 style="font-size: 48px; margin: 0;">{achievement.get('icon', '⭐')}</h3>
            <h3>{achievement['name']}</h3>
            <p>{achievement['description']}</p>
        </div>
        
        <p>This is a huge milestone! You're making real progress on your career journey.</p>
        
        <h3>What's Next?</h3>
        <p>Keep the momentum going by:</p>
        <ul>
            <li>Setting your next goal</li>
            <li>Deepening your skills further</li>
            <li>Sharing your journey with others</li>
        </ul>
        
        <p><a href="https://smartcareer.app/dashboard" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Keep Going →</a></p>
        
        <hr>
        <p style="font-size: 12px; color: #666;">
            Keep up the great work! Your dedication is paying off.
        </p>
    </div>
</body>
</html>
        """
        
        return {
            'subject': subject,
            'body': body,
            'recipient': user_email,
            'template': 'achievement',
            'achievement': achievement
        }
    
    @staticmethod
    def send_milestone_celebration(user_name, user_email, milestone_type, value):
        """Send celebration email for reaching milestones."""
        
        milestones = {
            'readiness_50': {
                'subject': '🎯 50% Career Ready!',
                'message': 'You\'ve reached the halfway mark on your career readiness journey!'
            },
            'readiness_75': {
                'subject': '⚡ 75% Career Ready!',
                'message': 'You\'re in the home stretch! Just a bit more to go.'
            },
            'readiness_100': {
                'subject': '🏆 100% Career Ready!',
                'message': 'Congratulations! You\'re ready for your next career move!'
            },
            'login_streak_7': {
                'subject': '🔥 7-Day Streak!',
                'message': 'You\'ve logged in 7 days in a row. Your consistency is inspiring!'
            },
            'skills_10': {
                'subject': '📚 10 Skills Mastered!',
                'message': 'You now have 10 skills to showcase. Impressive!'
            }
        }
        
        milestone_info = milestones.get(milestone_type, {
            'subject': '🎉 Milestone Reached!',
            'message': f'You\'ve reached an important milestone in your journey!'
        })
        
        body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
        <h2>{milestone_info['subject']}</h2>
        
        <p>{milestone_info['message']}</p>
        
        <div style="background-color: #fff3cd; padding: 15px; border-radius: 4px; margin: 20px 0;">
            <p style="margin: 0; font-weight: bold;">Your success is no accident. You've put in the work.</p>
        </div>
        
        <p>Keep building on this momentum. Your career is in motion.</p>
        
        <p><a href="https://smartcareer.app/dashboard" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">View Your Progress →</a></p>
        
        <hr>
        <p style="font-size: 12px; color: #666;">
            You're doing amazing! Keep it up.
        </p>
    </div>
</body>
</html>
        """
        
        return {
            'subject': milestone_info['subject'],
            'body': body,
            'recipient': user_email,
            'template': 'milestone',
            'milestone_type': milestone_type
        }
    
    @staticmethod
    def send_inactivity_nudge(user_name, user_email, last_activity):
        """Send friendly reminder for inactive users."""
        
        subject = f"We miss you, {user_name}! Come back and continue your journey 👋"
        
        body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
        <h2>We Miss You!</h2>
        
        <p>It's been a while since we last saw you, {user_name}. We'd love to help you continue your career journey.</p>
        
        <div style="background-color: white; padding: 15px; border-radius: 4px; margin: 20px 0;">
            <h3>What You Can Do Now:</h3>
            <ul>
                <li>Check your updated career readiness score</li>
                <li>Chat with your mentor about next steps</li>
                <li>Review new opportunities in your field</li>
                <li>Track your progress on your goals</li>
            </ul>
        </div>
        
        <p><a href="https://smartcareer.app/dashboard" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Welcome Back →</a></p>
        
        <hr>
        <p style="font-size: 12px; color: #666;">
            Your career journey is important. We're here when you're ready to continue.
        </p>
    </div>
</body>
</html>
        """
        
        return {
            'subject': subject,
            'body': body,
            'recipient': user_email,
            'template': 'inactivity_nudge'
        }
    
    @staticmethod
    def send_digest_email(user_name, user_email, digest_data):
        """Send weekly or monthly digest email."""
        
        period = digest_data.get('period', 'weekly')
        interactions = digest_data.get('interaction_count', 0)
        achievements = digest_data.get('new_achievements', [])
        progress = digest_data.get('progress_change', 0)
        
        subject = f"Your {period.capitalize()} Career Update ✨"
        
        achievements_html = ""
        if achievements:
            achievements_html = f"""
            <h3>🎉 New Achievements</h3>
            <ul>
                {''.join([f'<li>{a["name"]}: {a["description"]}</li>' for a in achievements])}
            </ul>
            """
        
        body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
        <h2>Your {period.capitalize()} Update, {user_name}</h2>
        
        <div style="background-color: white; padding: 15px; border-radius: 4px; margin: 20px 0;">
            <h3>📊 This {period.capitalize()}</h3>
            <ul>
                <li><strong>{interactions}</strong> interactions with career mentor</li>
                <li><strong>{progress:+.0f}%</strong> change in career readiness</li>
            </ul>
        </div>
        
        {achievements_html}
        
        <h3>💡 Recommended for Next {period.capitalize()}</h3>
        <ul>
            <li>Focus on one key skill area</li>
            <li>Document your progress</li>
            <li>Reflect on your growth</li>
        </ul>
        
        <p><a href="https://smartcareer.app/dashboard" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">View Full Report →</a></p>
        
        <hr>
        <p style="font-size: 12px; color: #666;">
            You're building a great foundation. Keep going!
        </p>
    </div>
</body>
</html>
        """
        
        return {
            'subject': subject,
            'body': body,
            'recipient': user_email,
            'template': 'digest',
            'period': period
        }


class NotificationScheduler:
    """Schedule and manage notifications."""
    
    @staticmethod
    def queue_notification(user_id, notification_type, data, scheduled_for=None):
        """Queue a notification for sending."""
        db = get_db()
        
        scheduled_for = scheduled_for or datetime.utcnow().isoformat()
        
        db.execute('''
            INSERT INTO notification_queue (user_id, notification_type, data, scheduled_for, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, notification_type, str(data), scheduled_for, 'pending'))
        
        db.commit()
    
    @staticmethod
    def get_pending_notifications(limit=100):
        """Get pending notifications to send."""
        db = get_db()
        
        notifications = db.execute('''
            SELECT * FROM notification_queue
            WHERE status = 'pending'
            AND scheduled_for <= datetime('now')
            ORDER BY scheduled_for ASC
            LIMIT ?
        ''', (limit,)).fetchall()
        
        return [dict(n) for n in notifications]
    
    @staticmethod
    def mark_sent(notification_id):
        """Mark notification as sent."""
        db = get_db()
        
        db.execute('''
            UPDATE notification_queue
            SET status = 'sent', sent_at = ?
            WHERE id = ?
        ''', (datetime.utcnow().isoformat(), notification_id))
        
        db.commit()
