"""Student Profile Service - Handle profile discovery and student intake."""
from database.db import get_db
from datetime import datetime
import json


class StudentProfileService:
    """Manage student profile creation and updates."""
    
    @staticmethod
    def create_profile(user_id, education_level, interests, current_skills, 
                      career_goals, experience_level, confusion_areas=None, 
                      learning_style=None, available_hours_per_week=None,
                      target_timeline_months=None):
        """Create or update student profile with discovery data."""
        db = get_db()
        now = datetime.utcnow().isoformat()
        
        try:
            existing = db.execute(
                'SELECT id FROM student_profiles WHERE user_id = ?',
                (user_id,)
            ).fetchone()
            
            if existing:
                # Update existing profile
                db.execute('''
                    UPDATE student_profiles
                    SET education_level = ?, interests = ?, current_skills = ?,
                        career_goals = ?, experience_level = ?,
                        confusion_areas = ?, learning_style = ?,
                        available_hours_per_week = ?, target_timeline_months = ?,
                        updated_at = ?
                    WHERE user_id = ?
                ''', (
                    education_level,
                    json.dumps(interests) if isinstance(interests, list) else interests,
                    json.dumps(current_skills) if isinstance(current_skills, list) else current_skills,
                    career_goals,
                    experience_level,
                    json.dumps(confusion_areas) if isinstance(confusion_areas, list) else confusion_areas,
                    learning_style,
                    available_hours_per_week,
                    target_timeline_months,
                    now,
                    user_id
                ))
            else:
                # Create new profile
                db.execute('''
                    INSERT INTO student_profiles
                    (user_id, education_level, interests, current_skills, career_goals,
                     experience_level, confusion_areas, learning_style,
                     available_hours_per_week, target_timeline_months, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    education_level,
                    json.dumps(interests) if isinstance(interests, list) else interests,
                    json.dumps(current_skills) if isinstance(current_skills, list) else current_skills,
                    career_goals,
                    experience_level,
                    json.dumps(confusion_areas) if isinstance(confusion_areas, list) else confusion_areas,
                    learning_style,
                    available_hours_per_week,
                    target_timeline_months,
                    now,
                    now
                ))
            
            db.commit()
            return True
        except Exception as e:
            print(f"Error creating/updating profile: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def get_profile(user_id):
        """Retrieve student profile."""
        db = get_db()
        try:
            profile = db.execute(
                'SELECT * FROM student_profiles WHERE user_id = ?',
                (user_id,)
            ).fetchone()
            
            if profile:
                return {
                    'user_id': profile['user_id'],
                    'education_level': profile['education_level'],
                    'interests': json.loads(profile['interests']) if profile['interests'] else [],
                    'current_skills': json.loads(profile['current_skills']) if profile['current_skills'] else [],
                    'career_goals': profile['career_goals'],
                    'experience_level': profile['experience_level'],
                    'confusion_areas': json.loads(profile['confusion_areas']) if profile['confusion_areas'] else [],
                    'learning_style': profile['learning_style'],
                    'available_hours_per_week': profile['available_hours_per_week'],
                    'target_timeline_months': profile['target_timeline_months'],
                    'created_at': profile['created_at'],
                    'updated_at': profile['updated_at'],
                }
            return None
        except Exception as e:
            print(f"Error retrieving profile: {e}")
            return None
    
    @staticmethod
    def has_profile(user_id):
        """Check if student has a profile."""
        db = get_db()
        try:
            result = db.execute(
                'SELECT id FROM student_profiles WHERE user_id = ?',
                (user_id,)
            ).fetchone()
            return result is not None
        except:
            return False
    
    @staticmethod
    def is_profile_complete(user_id):
        """Check if profile has all essential information."""
        profile = StudentProfileService.get_profile(user_id)
        if not profile:
            return False
        
        essential_fields = [
            'education_level',
            'interests',
            'current_skills',
            'experience_level'
        ]
        
        for field in essential_fields:
            value = profile.get(field)
            if not value:
                return False
        
        return True
    
    @staticmethod
    def get_profile_summary(user_id):
        """Get a human-readable summary of student profile."""
        profile = StudentProfileService.get_profile(user_id)
        if not profile:
            return None
        
        return {
            'education': profile.get('education_level', 'Not specified'),
            'interests': profile.get('interests', []),
            'current_strengths': profile.get('current_skills', []),
            'goals': profile.get('career_goals', 'Not specified'),
            'experience': profile.get('experience_level', 'Not specified'),
            'challenges': profile.get('confusion_areas', []),
            'learning_pace': profile.get('learning_style', 'Balanced'),
            'commitment': profile.get('available_hours_per_week', 'Flexible'),
        }
    
    @staticmethod
    def calculate_profile_completeness(user_id):
        """Calculate percentage of profile completion."""
        profile = StudentProfileService.get_profile(user_id)
        if not profile:
            return 0
        
        fields = [
            'education_level',
            'interests',
            'current_skills',
            'career_goals',
            'experience_level',
            'learning_style',
            'available_hours_per_week',
            'target_timeline_months'
        ]
        
        filled_fields = 0
        for field in fields:
            value = profile.get(field)
            if value and (isinstance(value, list) and len(value) > 0 or isinstance(value, str) and value or isinstance(value, int)):
                filled_fields += 1
        
        return int((filled_fields / len(fields)) * 100)


def suggest_next_steps(profile):
    """Suggest what the student should do next based on their profile."""
    suggestions = []
    
    # Based on experience level
    if profile.get('experience_level') == 'beginner':
        suggestions.append({
            'priority': 'high',
            'action': 'Learn fundamentals',
            'description': 'Start with core concepts in your field of interest'
        })
    
    # Based on career goals clarity
    if profile.get('career_goals') == 'unclear' or not profile.get('career_goals'):
        suggestions.append({
            'priority': 'high',
            'action': 'Clarify your career direction',
            'description': 'Explore roles and industries that match your interests'
        })
    
    # Based on skills gaps
    if not profile.get('current_skills') or len(profile.get('current_skills', [])) < 3:
        suggestions.append({
            'priority': 'high',
            'action': 'Build foundational skills',
            'description': 'Focus on skills most relevant to your goals'
        })
    
    # Always suggest resume if not mentioned
    if not profile.get('career_goals') or 'resume' not in str(profile.get('career_goals')).lower():
        suggestions.append({
            'priority': 'medium',
            'action': 'Review your resume',
            'description': 'Use our analyzer to get feedback on your current resume'
        })
    
    # Based on timeline  
    if profile.get('target_timeline_months'):
        months = profile.get('target_timeline_months')
        if months < 3:
            suggestions.append({
                'priority': 'high',
                'action': 'Create urgent action plan',
                'description': f'You have {months} months - focus on most impactful actions'
            })
    
    return suggestions
