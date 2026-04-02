"""Learning Path Generator - Create prioritized learning directions."""
from database.db import get_db
from datetime import datetime, timedelta
import json


class LearningPathGenerator:
    """Generate structured learning paths based on student needs."""
    
    # Learning resources recommendations (no specific links to keep it framework-agnostic)
    LEARNING_RESOURCES = {
        'Programming Fundamentals': {
            'types': ['Interactive Course', 'Practice Problems', 'Documentation'],
            'description': 'Start with logic and syntax. Write simple programs daily.'
        },
        'Python Programming': {
            'types': ['Interactive Course', 'Practice Projects', 'Code Review'],
            'description': 'Master syntax, data structures, and built-in libraries.'
        },
        'Data Structures & Algorithms': {
            'types': ['Structured Course', 'Practice Problems', 'Interview Prep'],
            'description': 'Critical for interviews. Practice consistently.'
        },
        'SQL': {
            'types': ['Interactive Course', 'Practice Exercises', 'Real Data'],
            'description': 'Learn queries, joins, and optimization.'
        },
        'System Design': {
            'types': ['Study Group', 'Case Studies', 'Real Projects'],
            'description': 'Study real systems. Design your own.'
        },
        'Version Control (Git)': {
            'types': ['Tutorial', 'Practice Exercises', 'Real Projects'],
            'description': 'Essential for collaboration. Use daily.'
        },
        'Testing & Debugging': {
            'types': ['Practice Projects', 'Code Review', 'Best Practices'],
            'description': 'Learn testing strategies. Debug intentionally.'
        },
        'User Research': {
            'types': ['Case Studies', 'Real Practice', 'Mentorship'],
            'description': 'Talk to users. Document insights. Iterate.'
        },
        'Data Visualization': {
            'types': ['Tool Learning', 'Projects', 'Practice'],
            'description': 'Tell stories with data. Make insights clear.'
        },
        'UX Design': {
            'types': ['Portfolio Projects', 'Case Studies', 'User Testing'],
            'description': 'Learn by doing. Get user feedback early.'
        },
    }
    
    @staticmethod
    def generate_learning_path(user_id, profile, skill_gaps):
        """Generate a prioritized learning path."""
        learning_path = []
        
        # Combine core gaps (high priority) and supporting gaps (medium priority)
        all_gaps = []
        for gap in (skill_gaps.get('core_gaps', []) or []):
            gap['priority'] = 1  # Highest priority
            all_gaps.append(gap)
        
        for gap in (skill_gaps.get('supporting_gaps', []) or []):
            gap['priority'] = 2  # Medium priority
            all_gaps.append(gap)
        
        # Sort by priority
        all_gaps.sort(key=lambda x: (x.get('priority', 3), -len(str(x.get('why', '')))))
        
        # Generate learning path items
        cumulative_weeks = 0
        for idx, gap in enumerate(all_gaps):
            skill = gap.get('skill', '')
            estimated_weeks = LearningPathGenerator._estimate_weeks(skill)
            
            learning_item = {
                'skill_area': skill,
                'priority': idx + 1,
                'skill_category': 'Core' if gap.get('priority') == 1 else 'Supporting',
                'skill_description': gap.get('why', ''),
                'why_matters': gap.get('why', ''),
                'learning_order': idx + 1,
                'estimated_weeks': estimated_weeks,
                'target_completion_date': (datetime.utcnow() + timedelta(weeks=cumulative_weeks + estimated_weeks)).strftime('%Y-%m-%d'),
                'resources': LearningPathGenerator._get_resources_for_skill(skill),
            }
            
            learning_path.append(learning_item)
            cumulative_weeks += estimated_weeks
        
        # Save to database
        LearningPathGenerator._save_learning_path(user_id, learning_path)
        
        return {
            'path': learning_path,
            'total_weeks': cumulative_weeks,
            'learning_focus': LearningPathGenerator._determine_learning_focus(skill_gaps),
        }
    
    @staticmethod
    def _estimate_weeks(skill):
        """Estimate learning time for a skill."""
        skill_lower = skill.lower()
        
        basics = ['git', 'basics', 'fundamentals', 'intro']
        intermediate = ['design', 'analysis', 'testing', 'data']
        advanced = ['system design', 'machine learning', 'advanced']
        
        if any(word in skill_lower for word in basics):
            return 2
        elif any(word in skill_lower for word in intermediate):
            return 6
        elif any(word in skill_lower for word in advanced):
            return 12
        else:
            return 4
    
    @staticmethod
    def _get_resources_for_skill(skill):
        """Get resource recommendations for a skill."""
        if skill in LearningPathGenerator.LEARNING_RESOURCES:
            resource = LearningPathGenerator.LEARNING_RESOURCES[skill]
            return {
                'types': resource['types'],
                'approach': resource['description'],
            }
        
        # Generic fallback
        return {
            'types': ['Course', 'Practice', 'Project'],
            'approach': f'Learn {skill} through structured practice and real projects.',
        }
    
    @staticmethod
    def _determine_learning_focus(skill_gaps):
        """Determine the overall learning focus."""
        core_count = len(skill_gaps.get('core_gaps', []) or [])
        
        if core_count >= 4:
            return 'Comprehensive foundation building'
        elif core_count >= 2:
            return 'Core skill development'
        else:
            return 'Skill deepening and specialization'
    
    @staticmethod
    def _save_learning_path(user_id, learning_path):
        """Save learning path to database."""
        db = get_db()
        now = datetime.utcnow().isoformat()
        
        try:
            # Clear existing learning paths
            db.execute('DELETE FROM learning_paths WHERE user_id = ?', (user_id,))
            
            for item in learning_path:
                db.execute('''
                    INSERT INTO learning_paths
                    (user_id, skill_area, priority, skill_category, skill_description,
                     why_matters, learning_order, estimated_weeks, resources, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    item.get('skill_area'),
                    item.get('priority'),
                    item.get('skill_category'),
                    item.get('skill_description'),
                    item.get('why_matters'),
                    item.get('learning_order'),
                    item.get('estimated_weeks'),
                    json.dumps(item.get('resources', {})),
                    now,
                    now
                ))
            
            db.commit()
        except Exception as e:
            print(f"Error saving learning path: {e}")
            db.rollback()
    
    @staticmethod
    def get_learning_path(user_id):
        """Retrieve learning path for user."""
        db = get_db()
        try:
            results = db.execute(
                '''SELECT * FROM learning_paths 
                   WHERE user_id = ? 
                   ORDER BY learning_order ASC''',
                (user_id,)
            ).fetchall()
            
            if results:
                return [LearningPathGenerator._format_path_item(row) for row in results]
            return None
        except:
            return None
    
    @staticmethod
    def _format_path_item(row):
        """Format a learning path item for display."""
        return {
            'skill_area': row['skill_area'],
            'priority': row['priority'],
            'category': row['skill_category'],
            'description': row['skill_description'],
            'why_matters': row['why_matters'],
            'order': row['learning_order'],
            'weeks': row['estimated_weeks'],
            'resources': json.loads(row['resources']) if row['resources'] else {},
            'completed': row['completed'],
            'progress_text': f"Step {row['learning_order']} • {row['estimated_weeks']} weeks"
        }
    
    @staticmethod
    def mark_skill_complete(user_id, skill_area):
        """Mark a skill as completed."""
        db = get_db()
        now = datetime.utcnow().isoformat()
        
        try:
            db.execute('''
                UPDATE learning_paths
                SET completed = 1, completed_at = ?, updated_at = ?
                WHERE user_id = ? AND skill_area = ?
            ''', (now, now, user_id, skill_area))
            
            db.commit()
            return True
        except:
            return False
    
    @staticmethod
    def get_learning_progress(user_id):
        """Get overall learning progress."""
        db = get_db()
        try:
            all_items = db.execute(
                'SELECT * FROM learning_paths WHERE user_id = ? ORDER BY learning_order',
                (user_id,)
            ).fetchall()
            
            if not all_items:
                return None
            
            completed = len([item for item in all_items if item['completed']])
            total = len(all_items)
            
            return {
                'completed': completed,
                'total': total,
                'percentage': int((completed / total) * 100) if total > 0 else 0,
                'next_skill': all_items[completed]['skill_area'] if completed < total else None,
                'expected_completion_date': all_items[-1]['estimated_weeks'] if all_items else None
            }
        except:
            return None
