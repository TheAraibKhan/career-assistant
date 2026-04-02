"""Skill Gap Analysis Service - Identify missing skills and explain their importance."""
from database.db import get_db
from datetime import datetime
import json


class SkillGapAnalyzer:
    """Analyze skill gaps and provide learning prioritization."""
    
    # Skill importance mappings by field
    SKILL_IMPORTANCE_MAP = {
        'software-engineering': {
            'core': [
                {'skill': 'Programming Fundamentals', 'importance': 'critical', 'why': 'Foundation for all development work'},
                {'skill': 'Version Control (Git)', 'importance': 'critical', 'why': 'Essential for team collaboration and code management'},
                {'skill': 'Data Structures & Algorithms', 'importance': 'critical', 'why': 'Required for technical interviews and problem-solving'},
                {'skill': 'Problem Solving', 'importance': 'critical', 'why': 'Core of engineering work'},
            ],
            'supporting': [
                {'skill': 'Testing & Debugging', 'importance': 'high', 'why': 'Ensures code quality and reliability'},
                {'skill': 'System Design', 'importance': 'high', 'why': 'Needed for senior roles and scalable solutions'},
                {'skill': 'Database Design', 'importance': 'high', 'why': 'Required for data-driven applications'},
            ]
        },
        'data-science': {
            'core': [
                {'skill': 'Python Programming', 'importance': 'critical', 'why': 'Primary tool for data analysis and ML'},
                {'skill': 'Statistics & Math', 'importance': 'critical', 'why': 'Foundation for ML and data interpretation'},
                {'skill': 'SQL', 'importance': 'critical', 'why': 'Required for data extraction and manipulation'},
                {'skill': 'Data Visualization', 'importance': 'critical', 'why': 'Communicate insights effectively'},
            ],
            'supporting': [
                {'skill': 'Machine Learning', 'importance': 'high', 'why': 'Key for advanced data roles'},
                {'skill': 'Cloud Platforms', 'importance': 'high', 'why': 'Needed for production ML systems'},
            ]
        },
        'product-management': {
            'core': [
                {'skill': 'User Research', 'importance': 'critical', 'why': 'Understand what users actually need'},
                {'skill': 'Product Strategy', 'importance': 'critical', 'why': 'Drive product direction and decisions'},
                {'skill': 'Data Analysis', 'importance': 'critical', 'why': 'Make data-driven product decisions'},
                {'skill': 'Communication', 'importance': 'critical', 'why': 'Influence across teams'},
            ],
            'supporting': [
                {'skill': 'Design Thinking', 'importance': 'high', 'why': 'Solve problems creatively'},
                {'skill': 'Agile Methodologies', 'importance': 'high', 'why': 'Work in modern product teams'},
            ]
        },
        'design': {
            'core': [
                {'skill': 'Visual Design', 'importance': 'critical', 'why': 'Core of your craft'},
                {'skill': 'User Experience (UX)', 'importance': 'critical', 'why': 'Design for users, not aesthetics'},
                {'skill': 'Design Tools', 'importance': 'critical', 'why': 'Execute your ideas'},
                {'skill': 'Communication', 'importance': 'critical', 'why': 'Defend your design decisions'},
            ],
            'supporting': [
                {'skill': 'Prototyping', 'importance': 'high', 'why': 'Test ideas quickly'},
                {'skill': 'User Research', 'importance': 'high', 'why': 'Validate design decisions'},
            ]
        },
    }
    
    @staticmethod
    def analyze_gaps(user_id, profile=None):
        """Analyze skill gaps based on student profile."""
        from services.student_profile_service import StudentProfileService
        
        if not profile:
            profile = StudentProfileService.get_profile(user_id)
        
        if not profile:
            return None
        
        # Get relevant skills for their career goal
        career_goal = profile.get('career_goals', '').lower()
        current_skills = profile.get('current_skills', [])
        
        # Determine relevant skill category
        relevant_category = SkillGapAnalyzer._find_relevant_category(career_goal)
        
        gaps = {
            'core_gaps': [],
            'supporting_gaps': [],
            'strengths': current_skills,
            'summary': None
        }
        
        if relevant_category in SkillGapAnalyzer.SKILL_IMPORTANCE_MAP:
            skills_map = SkillGapAnalyzer.SKILL_IMPORTANCE_MAP[relevant_category]
            
            # Find core skill gaps
            for skill_item in skills_map.get('core', []):
                skill = skill_item['skill'].lower()
                if not any(skill in str(s).lower() for s in current_skills):
                    gaps['core_gaps'].append(skill_item)
            
            # Find supporting skill gaps
            for skill_item in skills_map.get('supporting', []):
                skill = skill_item['skill'].lower()
                if not any(skill in str(s).lower() for s in current_skills):
                    gaps['supporting_gaps'].append(skill_item)
        
        gaps['summary'] = SkillGapAnalyzer._generate_gap_summary(gaps, profile)
        
        # Save to database
        SkillGapAnalyzer._save_gap_analysis(user_id, gaps)
        
        return gaps
    
    @staticmethod
    def _find_relevant_category(career_goal):
        """Map career goal to skill importance category."""
        goal_lower = career_goal.lower()
        
        if any(word in goal_lower for word in ['software', 'engineer', 'developer', 'coding']):
            return 'software-engineering'
        elif any(word in goal_lower for word in ['data', 'science', 'analytics']):
            return 'data-science'
        elif any(word in goal_lower for word in ['product', 'management']):
            return 'product-management'
        elif any(word in goal_lower for word in ['design', 'designer', 'ux', 'ui']):
            return 'design'
        
        return 'software-engineering'  # Default
    
    @staticmethod
    def _generate_gap_summary(gaps, profile):
        """Generate human-readable summary of gaps."""
        core_gap_count = len(gaps['core_gaps'])
        supporting_gap_count = len(gaps['supporting_gaps'])
        experience = profile.get('experience_level', '')
        
        if core_gap_count == 0 and supporting_gap_count == 0:
            return "You have the foundational skills. Focus on deepening expertise."
        elif core_gap_count <= 2:
            return f"You're close. Master these {core_gap_count} core skills to be competitive."
        else:
            weeks = core_gap_count * 4
            return f"You need {core_gap_count} core skills. Plan for ~{weeks} weeks of focused learning."
    
    @staticmethod
    def _save_gap_analysis(user_id, gaps):
        """Save gap analysis to database."""
        db = get_db()
        now = datetime.utcnow().isoformat()
        
        try:
            existing = db.execute(
                'SELECT id FROM skill_gap_analysis WHERE user_id = ?',
                (user_id,)
            ).fetchone()
            
            gaps_json = json.dumps({
                'core_gaps': gaps['core_gaps'],
                'supporting_gaps': gaps['supporting_gaps'],
                'summary': gaps['summary']
            })
            
            if existing:
                db.execute('''
                    UPDATE skill_gap_analysis
                    SET priority_gaps = ?, estimated_learning_weeks = ?, updated_at = ?
                    WHERE user_id = ?
                ''', (gaps_json, len(gaps['core_gaps']) * 4, now, user_id))
            else:
                db.execute('''
                    INSERT INTO skill_gap_analysis
                    (user_id, priority_gaps, estimated_learning_weeks, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, gaps_json, len(gaps['core_gaps']) * 4, now, now))
            
            db.commit()
        except Exception as e:
            print(f"Error saving gap analysis: {e}")
            db.rollback()
    
    @staticmethod
    def get_gap_analysis(user_id):
        """Retrieve gap analysis for user."""
        db = get_db()
        try:
            result = db.execute(
                'SELECT * FROM skill_gap_analysis WHERE user_id = ?',
                (user_id,)
            ).fetchone()
            
            if result and result['priority_gaps']:
                return json.loads(result['priority_gaps'])
            return None
        except:
            return None
    
    @staticmethod
    def format_gap_explanation(gap_item):
        """Format a gap item for display."""
        return {
            'skill': gap_item.get('skill', ''),
            'importance': gap_item.get('importance', ''),
            'why_matters': gap_item.get('why', 'Important for career success'),
            'suggested_timeframe': SkillGapAnalyzer._estimate_learning_time(gap_item.get('skill', ''))
        }
    
    @staticmethod
    def _estimate_learning_time(skill):
        """Estimate learning time for a skill."""
        # Simplified estimation
        skill_lower = skill.lower()
        
        if any(word in skill_lower for word in ['fundamentals', 'basics', 'intro']):
            return '2-4 weeks'
        elif any(word in skill_lower for word in ['design', 'thinking', 'analysis']):
            return '4-8 weeks'
        elif any(word in skill_lower for word in ['machine learning', 'data science']):
            return '8-12 weeks'
        else:
            return '4-8 weeks'  # Default
