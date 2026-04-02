"""Action Guidance Service - Provide clear, actionable next steps."""
from database.db import get_db
from datetime import datetime, timedelta
import json


class ActionGuidanceService:
    """Provide clear daily, weekly, and monthly action guidance."""
    
    @staticmethod
    def generate_action_plan(user_id, profile, skill_gaps, learning_path):
        """Generate immediate, clear action items."""
        
        actions = {
            'today': ActionGuidanceService._generate_today_actions(profile, skill_gaps),
            'this_week': ActionGuidanceService._generate_week_actions(profile, learning_path),
            'this_month': ActionGuidanceService._generate_month_actions(profile, learning_path),
            'summary': ActionGuidanceService._generate_action_summary(profile, skill_gaps)
        }
        
        ActionGuidanceService._save_action_plan(user_id, actions)
        
        return actions
    
    @staticmethod
    def _generate_today_actions(profile, skill_gaps):
        """Generate actions for today (next few hours)."""
        actions = []
        
        # Everyone should understand their goal
        actions.append({
            'action': 'Define Your Goal Clearly',
            'description': 'Write down in 1-2 sentences: What role do you want? What will you be doing?',
            'time_needed': '15 minutes',
            'why': 'Clarity is the first step. Everything else builds from this.',
            'is_critical': True
        })
        
        # Based on gaps
        if skill_gaps.get('core_gaps'):
            first_gap = skill_gaps['core_gaps'][0]['skill']
            actions.append({
                'action': f'Learn One Core Topic: {first_gap}',
                'description': f'Find ONE good resource about {first_gap}. Spend 1-2 hours learning basics.',
                'time_needed': '1-2 hours',
                'why': f'{first_gap} is essential. Start with fundamentals today.',
                'is_critical': True
            })
        
        # Proof building starts with portfolio
        actions.append({
            'action': 'Open Your GitHub / Portfolio',
            'description': 'Create or review your GitHub profile. Make sure username is professional.',
            'time_needed': '20 minutes',
            'why': 'This is where people will see your actual work.',
            'is_critical': False
        })
        
        return actions
    
    @staticmethod
    def _generate_week_actions(profile, learning_path):
        """Generate actions for this week."""
        actions = []
        
        weeks_available = profile.get('available_hours_per_week', 10)
        
        if weeks_available >= 15:
            intensity = 'aggressive'
            target_hours = 2
        elif weeks_available >= 10:
            intensity = 'moderate'
            target_hours = 1.5
        else:
            intensity = 'minimal'
            target_hours = 1
        
        actions.append({
            'action': 'Complete First Learning Module',
            'description': f'Spend {target_hours} hours on your first priority skill. Focus on one concept.',
            'time_needed': f'{target_hours} hours per day, 4-5 days',
            'why': 'Consistent learning builds momentum. Small, regular effort beats cramming.',
            'is_critical': True
        })
        
        actions.append({
            'action': 'Start Your First Project',
            'description': 'Choose a small project that demonstrates the skill you\'re learning. Get it started.',
            'time_needed': '2-3 hours for planning',
            'why': 'Learning by doing sticks. Projects are your proof.',
            'is_critical': True
        })
        
        actions.append({
            'action': 'Set Up Learning Tracking',
            'description': 'Create a simple log or habit tracker. Record what you learn each day.',
            'time_needed': '20 minutes',
            'why': 'What gets measured gets managed. You\'ll see progress.',
            'is_critical': False
        })
        
        actions.append({
            'action': 'Reach Out for Feedback',
            'description': 'Find someone who knows the field. Ask them 3 questions about your learning path.',
            'time_needed': '1 hour',
            'why': 'Outside perspective saves months of wasted effort.',
            'is_critical': False
        })
        
        return actions
    
    @staticmethod
    def _generate_month_actions(profile, learning_path):
        """Generate actions for this month."""
        actions = []
        
        actions.append({
            'action': 'Complete First Core Skill',
            'description': 'Master your first priority skill from the learning path. Build something with it.',
            'time_needed': '20-30 hours total',
            'why': 'One completed skill is worth more than 5 half-learned skills.',
            'is_critical': True
        })
        
        actions.append({
            'action': 'Launch First Portfolio Project',
            'description': 'Finish your first portfolio project. Deploy it, document it, share it.',
            'time_needed': '20-40 hours total',
            'why': 'You need proof. Projects are proof.',
            'is_critical': True
        })
        
        actions.append({
            'action': 'Build Your Professional Presence',
            'description': 'Update your resume/CV. Add your new project. Improve LinkedIn. Create portfolio site.',
            'time_needed': '5-10 hours total',
            'why': 'Your work is invisible if no one sees it.',
            'is_critical': True
        })
        
        actions.append({
            'action': 'Connect With People in Your Field',
            'description': 'Find and connect with 5-10 people in your target role. Reach out genuinely.',
            'time_needed': '3-5 hours total',
            'why': 'Most opportunities come through people, not job boards.',
            'is_critical': False
        })
        
        actions.append({
            'action': 'Review & Adjust Your Plan',
            'description': 'Look back at your learning. What\'s working? What needs to change?',
            'time_needed': '1-2 hours',
            'why': 'Plans are guides, not law. Adjust based on reality.',
            'is_critical': False
        })
        
        return actions
    
    @staticmethod
    def _generate_action_summary(profile, skill_gaps):
        """Generate an executive summary of the action plan."""
        core_gaps = len(skill_gaps.get('core_gaps', []) or [])
        timeline = profile.get('target_timeline_months', 6)
        
        if timeline <= 2:
            urgency = 'High - Your timeline is tight. Focus on essentials only.'
        elif timeline <= 4:
            urgency = 'Medium - Balance learning and building. You have some runway.'
        else:
            urgency = 'Manageable - You have time. Build depth, not speed.'
        
        return {
            'urgency': urgency,
            'headline': f'Learn {core_gaps} skills, build 2-3 projects, and prove capability in {timeline} months.',
            'key_principle': 'Build as you learn. Theory without practice is forgotten. Practice without theory is inefficient.',
            'success_metrics': [
                f'{core_gaps} skills demonstrably completed',
                '2-3 portfolio projects with documentation',
                'Professional resume and portfolio site',
                'Network of people who can vouch for your work'
            ],
            'biggest_risk': 'Spreading yourself too thin. Do fewer things better.',
            'biggest_opportunity': 'Consistent daily action. 30 minutes/day compounds to incredible growth.'
        }
    
    @staticmethod
    def _save_action_plan(user_id, actions):
        """Save action plan to database."""
        db = get_db()
        now = datetime.utcnow().isoformat()
        
        try:
            # Clear existing action plans
            db.execute('DELETE FROM action_plans WHERE user_id = ?', (user_id,))
            
            # Today's actions
            for action in actions.get('today', []):
                db.execute('''
                    INSERT INTO action_plans
                    (user_id, action_category, action_title, action_description,
                     time_commitment, priority, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    'Today',
                    action.get('action'),
                    action.get('description'),
                    action.get('time_needed'),
                    'high' if action.get('is_critical') else 'medium',
                    now,
                    now
                ))
            
            # This week
            for action in actions.get('this_week', []):
                db.execute('''
                    INSERT INTO action_plans
                    (user_id, action_category, action_title, action_description,
                     time_commitment, priority, target_date, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    'This Week',
                    action.get('action'),
                    action.get('description'),
                    action.get('time_needed'),
                    'high' if action.get('is_critical') else 'medium',
                    (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d'),
                    now,
                    now
                ))
            
            # This month
            for action in actions.get('this_month', []):
                db.execute('''
                    INSERT INTO action_plans
                    (user_id, action_category, action_title, action_description,
                     time_commitment, priority, target_date, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    'This Month',
                    action.get('action'),
                    action.get('description'),
                    action.get('time_needed'),
                    'high' if action.get('is_critical') else 'medium',
                    (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d'),
                    now,
                    now
                ))
            
            db.commit()
        except Exception as e:
            print(f"Error saving action plan: {e}")
            db.rollback()
    
    @staticmethod
    def get_action_plan(user_id):
        """Retrieve action plan for user."""
        db = get_db()
        try:
            actions = db.execute(
                '''SELECT * FROM action_plans 
                   WHERE user_id = ? 
                   ORDER BY action_category, priority DESC, action_title''',
                (user_id,)
            ).fetchall()
            
            if actions:
                plan = {
                    'today': [],
                    'this_week': [],
                    'this_month': []
                }
                
                for action in actions:
                    item = {
                        'id': action['id'],
                        'title': action['action_title'],
                        'description': action['action_description'],
                        'time': action['time_commitment'],
                        'priority': action['priority'],
                        'status': action['status'],
                        'target_date': action['target_date']
                    }
                    
                    if action['action_category'] == 'Today':
                        plan['today'].append(item)
                    elif action['action_category'] == 'This Week':
                        plan['this_week'].append(item)
                    elif action['action_category'] == 'This Month':
                        plan['this_month'].append(item)
                
                return plan
            return None
        except:
            return None
    
    @staticmethod
    def mark_action_complete(user_id, action_id):
        """Mark an action as completed."""
        db = get_db()
        now = datetime.utcnow().isoformat()
        
        try:
            db.execute('''
                UPDATE action_plans
                SET status = 'completed', completed_date = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
            ''', (now, now, action_id, user_id))
            
            db.commit()
            return True
        except:
            return False
