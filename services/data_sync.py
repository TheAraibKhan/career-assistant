"""Keeps dependent modules in sync when user data changes."""

import json
from datetime import datetime
from database.db import get_db


def refresh_user_data(user_id):
    """Reload profile and regenerate roadmap, insights, and actions."""
    from services.profile_service import get_user_profile
    from services.roadmap_service import generate_roadmap
    from services.insight_service import generate_insights
    from services.action_guidance_service import ActionGuidanceService
    
    db = get_db()
    
    try:
        profile = get_user_profile(user_id)
        profile_data = profile['profile']
        stats = profile['stats']
        
        # Regenerate roadmap
        roadmap_items = generate_roadmap(profile_data, stats)
        _save_roadmap(db, user_id, roadmap_items)
        
        # Regenerate insights
        insights_result = generate_insights(
            profile_data, 
            stats, 
            profile.get('skills', {}),
            resume_data=None
        )

        # Convert recommendations to the list format _save_insights expects
        insight_items = []
        for rec in insights_result.get('recommendations', []):
            insight_items.append({
                'text': rec.get('description', rec.get('title', '')),
                'category': 'recommendation',
                'priority': 1,
            })
        _save_insights(db, user_id, insight_items)
        
        # 4. Generate action items from profile
        # ActionGuidanceService expects skill_gaps as a dict with 'core_gaps' key
        skill_gaps = profile_data.get('skill_gaps', {'core_gaps': []})
        if isinstance(skill_gaps, list):
            skill_gaps = {'core_gaps': [{'skill': g} for g in skill_gaps]}
        learning_path = profile_data.get('learning_path', [])
        # generate_action_plan saves to DB internally via _save_action_plan
        # so we do NOT call _save_actions on its result
        ActionGuidanceService.generate_action_plan(user_id, profile_data, skill_gaps, learning_path)
        
        # 5. Update sync metadata
        now = datetime.utcnow().isoformat()
        db.execute('''
            INSERT OR REPLACE INTO data_sync_log 
            (user_id, last_sync, sync_type, modules_updated)
            VALUES (?, ?, ?, ?)
        ''', (user_id, now, 'FULL_REFRESH', 'roadmap,insights,actions'))
        
        db.commit()
        
        return get_user_profile(user_id)
        
    except Exception as e:
        print(f"Error refreshing user data for {user_id}: {e}")
        db.rollback()
        raise


def sync_profile_update(user_id, profile_data):
    """Update profile and refresh dependent modules."""
    from services.profile_service import update_user_profile
    return update_user_profile(user_id, profile_data)


def sync_resume_analysis(user_id, analysis_result):
    """Store resume analysis results and refresh dependent modules."""
    db = get_db()
    now = datetime.utcnow().isoformat()
    
    try:
        # Store analysis
        db.execute('''
            INSERT INTO quick_analyses 
            (user_id, ats_score, overall_score, skills_found, recommendations, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            analysis_result.get('ats_score', 0),
            analysis_result.get('overall_score', 0),
            json.dumps(analysis_result.get('skills_found', [])),
            json.dumps(analysis_result.get('recommendations', [])),
            now
        ))
        
        # Store section analysis if available
        if 'section_analysis' in analysis_result:
            for section in analysis_result['section_analysis']:
                db.execute('''
                    INSERT OR REPLACE INTO resume_sections 
                    (user_id, section_name, section_status, improvement_suggestion, priority, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 0, ?, ?)
                ''', (
                    user_id,
                    section['name'],
                    section.get('status', 'needs_work'),
                    section.get('suggestion', ''),
                    now,
                    now
                ))
        
        # Store health metrics
        if 'health_metrics' in analysis_result:
            metrics = analysis_result['health_metrics']
            db.execute('''
                INSERT OR REPLACE INTO resume_health 
                (user_id, ats_score, keyword_score, formatting_score, overall_health, last_analyzed_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                metrics.get('ats_score', 0),
                metrics.get('keyword_score', 0),
                metrics.get('formatting_score', 0),
                metrics.get('overall_health', 0),
                now,
                now,
                now
            ))
        
        db.commit()
        
        # Refresh all modules with new data
        return refresh_user_data(user_id)
        
    except Exception as e:
        print(f"Error syncing resume analysis for {user_id}: {e}")
        db.rollback()
        raise


def sync_skill_update(user_id, skill_name, proficiency_level, tasks_completed=None, xp_earned=0):
    """
    Sync when user makes progress on a skill (completes task, gains XP).
    
    This may trigger:
    - Roadmap adjustments
    - New actions generated
    - Insights updated
    
    Args:
        user_id: User ID
        skill_name: Name of skill being updated
        proficiency_level: New proficiency (0-5)
        tasks_completed: Optional number of tasks completed
        xp_earned: XP gained
    
    Returns: Updated profile
    """
    db = get_db()
    now = datetime.utcnow().isoformat()
    
    try:
        # Update skill progress
        current = db.execute('''
            SELECT tasks_completed, total_xp FROM skill_progress 
            WHERE user_id = ? AND skill_name = ?
        ''', (user_id, skill_name)).fetchone()
        
        new_tasks = (current['tasks_completed'] if current else 0) + (tasks_completed or 1)
        new_xp = (current['total_xp'] if current else 0) + xp_earned
        
        db.execute('''
            INSERT OR REPLACE INTO skill_progress 
            (user_id, skill_name, proficiency_level, tasks_completed, total_xp, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, skill_name, proficiency_level, new_tasks, new_xp, now))
        
        # Update user stats
        db.execute('''
            UPDATE user_stats 
            SET total_xp = total_xp + ?, 
                tasks_completed = tasks_completed + ?,
                updated_at = ?
            WHERE user_id = ?
        ''', (xp_earned, 1, now, user_id))
        
        db.commit()
        
        # Refresh modules - new skill progress may unlock new actions
        return refresh_user_data(user_id)
        
    except Exception as e:
        print(f"Error syncing skill update for {user_id}: {e}")
        db.rollback()
        raise


def sync_action_completion(user_id, action_id):
    """
    Sync when user completes an action item.
    
    This:
    - Marks action as completed
    - Awards XP
    - Updates streak
    - Regenerates remaining actions
    
    Args:
        user_id: User ID
        action_id: ID of completed action
    
    Returns: Updated profile
    """
    db = get_db()
    now = datetime.utcnow().isoformat()
    
    try:
        # Get action details
        action = db.execute('''
            SELECT xp_reward FROM action_plans WHERE id = ? AND user_id = ?
        ''', (action_id, user_id)).fetchone()
        
        if not action:
            raise ValueError(f"Action {action_id} not found for user {user_id}")
        
        xp_reward = action['xp_reward'] or 50
        
        # Mark action as completed
        db.execute('''
            UPDATE action_plans 
            SET status = 'completed', completed_date = ?
            WHERE id = ? AND user_id = ?
        ''', (now, action_id, user_id))
        
        # Update user stats
        db.execute('''
            UPDATE user_stats 
            SET total_xp = total_xp + ?,
                tasks_completed = tasks_completed + 1,
                updated_at = ?
            WHERE user_id = ?
        ''', (xp_reward, now, user_id))
        
        db.commit()
        
        # Regenerate actions - previous one is done, new ones should be available
        return refresh_user_data(user_id)
        
    except Exception as e:
        print(f"Error syncing action completion for {user_id}: {e}")
        db.rollback()
        raise


# ============================================================================
# INTERNAL: Storage functions - DO NOT USE DIRECTLY
# These are called by refresh_user_data() to store sync results
# ============================================================================

def _save_roadmap(db, user_id, roadmap_items):
    """Store generated roadmap in database."""
    now = datetime.utcnow().isoformat()
    
    # Clear old roadmap items for this user
    db.execute('DELETE FROM user_roadmap WHERE user_id = ?', (user_id,))
    
    # Insert new items
    for idx, item in enumerate(roadmap_items):
        db.execute('''
            INSERT INTO user_roadmap 
            (user_id, title, description, duration, xp, order_num, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            item.get('title', ''),
            item.get('description', ''),
            item.get('duration', ''),
            item.get('xp', 0),
            idx,
            now
        ))


def _save_insights(db, user_id, insights):
    """Store generated insights in database."""
    now = datetime.utcnow().isoformat()
    
    # Clear old insights
    db.execute('DELETE FROM user_insights WHERE user_id = ?', (user_id,))
    
    # Insert new insights
    for idx, insight in enumerate(insights or []):
        db.execute('''
            INSERT INTO user_insights 
            (user_id, insight_text, category, priority, order_num, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            insight.get('text', ''),
            insight.get('category', 'general'),
            insight.get('priority', 1),
            idx,
            now
        ))


def _save_actions(db, user_id, actions):
    """Store generated action items in database."""
    now = datetime.utcnow().isoformat()
    
    # Don't clear old actions - keep them for history
    # Only insert new PENDING actions
    existing = db.execute('''
        SELECT action_title FROM action_plans 
        WHERE user_id = ? AND status = 'pending'
    ''', (user_id,)).fetchall()
    
    existing_titles = {row['action_title'] for row in existing}
    
    for idx, action in enumerate(actions or []):
        title = action.get('title', '')
        
        # Skip if this action already exists
        if title in existing_titles:
            continue
        
        db.execute('''
            INSERT INTO action_plans 
            (user_id, action_category, action_title, action_description, description, time_commitment, 
             xp_reward, status, order_num, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            action.get('category', 'learning'),
            title,
            action.get('description', ''),
            action.get('description', ''),
            action.get('time_commitment', '30 min'),
            action.get('xp_reward', 50),
            'pending',
            idx,
            now,
            now
        ))


# ============================================================================
# ADMIN: Maintenance functions
# ============================================================================

def reset_user_sync_data(user_id, keep_history=False):
    """
    Reset all synced data for a user (for testing/admin).
    
    Args:
        user_id: User ID
        keep_history: If True, keep completed items for history
    """
    db = get_db()
    
    if keep_history:
        # Only delete pending/current items
        db.execute('DELETE FROM user_roadmap WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM user_insights WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM action_plans WHERE user_id = ? AND status = ?', 
                  (user_id, 'pending'))
    else:
        # Delete everything
        db.execute('DELETE FROM user_roadmap WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM user_insights WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM action_plans WHERE user_id = ?', (user_id,))
    
    db.commit()
