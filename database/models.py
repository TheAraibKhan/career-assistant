from database.db import get_db
import json
from datetime import datetime

def create_table():
    """Create or migrate database tables."""
    db = get_db()
    
    # Main submissions table with enhanced schema
    db.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            name TEXT NOT NULL,
            email TEXT,
            interest TEXT NOT NULL,
            level TEXT NOT NULL,
            known_skills TEXT,
            recommendation TEXT NOT NULL,
            readiness_score INTEGER,
            confidence_score INTEGER,
            recommended_role_tier TEXT,
            strengths TEXT,
            gaps TEXT,
            resume_file_path TEXT,
            resume_parsed_skills TEXT,
            profile_image_path TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Migrate existing submissions table if needed (add user_id column)
    try:
        db.execute('ALTER TABLE submissions ADD COLUMN user_id TEXT')
    except:
        pass  # Column already exists
    
    # User accounts table with SaaS tier support
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            profile_image_path TEXT,
            is_premium INTEGER DEFAULT 0,
            tier TEXT DEFAULT 'free',
            features_enabled TEXT,
            usage_limits TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_login TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Chat history table
    db.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            message TEXT NOT NULL,
            response TEXT,
            message_type TEXT DEFAULT 'user',
            context TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Analytics table
    db.execute('''
        CREATE TABLE IF NOT EXISTS chatbot_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            message_type TEXT NOT NULL,
            metadata TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Resume analysis cache
    db.execute('''
        CREATE TABLE IF NOT EXISTS resume_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_hash TEXT UNIQUE NOT NULL,
            parsed_skills TEXT,
            parsed_experience TEXT,
            parsed_education TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # SaaS Usage Tracking - Daily
    db.execute('''
        CREATE TABLE IF NOT EXISTS usage_tracking_daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            career_analyses_used INTEGER DEFAULT 0,
            resume_uploads_used INTEGER DEFAULT 0,
            chatbot_messages_used INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            UNIQUE(user_id, date),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # SaaS Usage Tracking - Monthly
    db.execute('''
        CREATE TABLE IF NOT EXISTS usage_tracking_monthly (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            year_month TEXT NOT NULL,
            career_analyses_used INTEGER DEFAULT 0,
            resume_uploads_used INTEGER DEFAULT 0,
            chatbot_messages_used INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            UNIQUE(user_id, year_month),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Feature Flags & Tier Configuration
    db.execute('''
        CREATE TABLE IF NOT EXISTS tier_config (
            tier TEXT PRIMARY KEY,
            career_analyses_limit INTEGER,
            resume_uploads_limit INTEGER,
            chatbot_messages_limit INTEGER,
            features_json TEXT,
            description TEXT,
            price_monthly REAL DEFAULT 0.0
        )
    ''')
    
    # User Experience & Feedback
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            feedback_text TEXT NOT NULL,
            rating INTEGER,
            feature TEXT,
            submitted_at TEXT NOT NULL
        )
    ''')
    
    # User Stats & Activity Tracking
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            total_xp INTEGER DEFAULT 0,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            tasks_completed INTEGER DEFAULT 0,
            career_readiness INTEGER DEFAULT 0,
            skills_tracked INTEGER DEFAULT 1,
            last_activity_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Activity Log - Track all user actions
    db.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            task_id TEXT,
            xp_earned INTEGER DEFAULT 0,
            description TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Task Completion - Track which tasks user completed
    db.execute('''
        CREATE TABLE IF NOT EXISTS task_completion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            task_title TEXT NOT NULL,
            xp_earned INTEGER DEFAULT 0,
            completed_at TEXT NOT NULL,
            roadmap_item TEXT
        )
    ''')
    
    # Skill Progress - Track progress per skill
    db.execute('''
        CREATE TABLE IF NOT EXISTS skill_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            skill_name TEXT NOT NULL,
            proficiency_level INTEGER DEFAULT 0,
            tasks_completed INTEGER DEFAULT 0,
            total_xp INTEGER DEFAULT 0,
            last_updated TEXT,
            UNIQUE(user_id, skill_name)
        )
    ''')

    # User Interactions for UX Analytics
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            interaction_type TEXT NOT NULL,
            metadata TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Onboarding Progress Tracking
    db.execute('''
        CREATE TABLE IF NOT EXISTS onboarding_progress (
            user_id TEXT PRIMARY KEY,
            profile_complete INTEGER DEFAULT 0,
            resume_uploaded INTEGER DEFAULT 0,
            preferences_set INTEGER DEFAULT 0,
            tutorial_watched INTEGER DEFAULT 0,
            first_recommendation INTEGER DEFAULT 0,
            completion_percentage INTEGER DEFAULT 0,
            started_at TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
    ''')
    
    # User Preferences & Personalization
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            communication_style TEXT DEFAULT 'friendly',
            learning_pace TEXT DEFAULT 'balanced',
            goal_orientation TEXT DEFAULT 'career',
            notification_frequency TEXT DEFAULT 'daily',
            dark_mode INTEGER DEFAULT 0,
            email_updates INTEGER DEFAULT 1,
            show_tips INTEGER DEFAULT 1,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # User Achievements & Milestones
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            achievement_key TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            icon TEXT,
            unlocked_at TEXT NOT NULL,
            UNIQUE(user_id, achievement_key)
        )
    ''')
    
    # Goal Tracking
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            goal_title TEXT NOT NULL,
            goal_description TEXT,
            category TEXT,
            target_date TEXT,
            milestone_count INTEGER DEFAULT 0,
            completion_percentage INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Goal Milestones
    db.execute('''
        CREATE TABLE IF NOT EXISTS goal_milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER NOT NULL,
            milestone_title TEXT NOT NULL,
            order_num INTEGER,
            completed INTEGER DEFAULT 0,
            completed_at TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(goal_id) REFERENCES user_goals(id)
        )
    ''')
    
    # Subscription Management
    db.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,
            tier TEXT DEFAULT 'free',
            status TEXT DEFAULT 'active',
            trial_started_at TEXT,
            trial_ends_at TEXT,
            current_period_start TEXT NOT NULL,
            current_period_end TEXT,
            payment_method TEXT,
            last_payment_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Email Notification Queue
    db.execute('''
        CREATE TABLE IF NOT EXISTS notification_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            notification_type TEXT NOT NULL,
            data TEXT,
            scheduled_for TEXT NOT NULL,
            sent_at TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Career Timeline - Track progression over time
    db.execute('''
        CREATE TABLE IF NOT EXISTS career_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,
            current_role TEXT,
            current_level TEXT,
            years_experience INTEGER,
            target_role TEXT,
            target_level TEXT,
            timeline_months INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Resume Health System
    db.execute('''
        CREATE TABLE IF NOT EXISTS resume_health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,
            ats_score INTEGER,
            keyword_score INTEGER,
            formatting_score INTEGER,
            content_completeness INTEGER,
            overall_health INTEGER,
            last_analyzed_at TEXT,
            suggestions TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Resume Section Analysis
    db.execute('''
        CREATE TABLE IF NOT EXISTS resume_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            section_name TEXT NOT NULL,
            section_status TEXT DEFAULT 'incomplete',
            improvement_suggestion TEXT,
            priority INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(user_id, section_name)
        )
    ''')
    
    # Skill Gap Intelligence
    db.execute('''
        CREATE TABLE IF NOT EXISTS skill_gap_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,
            current_skills TEXT,
            required_skills TEXT,
            gap_count INTEGER,
            priority_gaps TEXT,
            learning_resources TEXT,
            estimated_learning_weeks INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Career Confidence Index
    db.execute('''
        CREATE TABLE IF NOT EXISTS confidence_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,
            resume_strength INTEGER,
            skill_readiness INTEGER,
            market_alignment INTEGER,
            overall_score INTEGER,
            trend TEXT DEFAULT 'stable',
            updated_at TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Weekly Check-ins
    db.execute('''
        CREATE TABLE IF NOT EXISTS weekly_checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            week_start_date TEXT NOT NULL,
            prompt TEXT,
            response TEXT,
            areas_of_progress TEXT,
            challenges TEXT,
            actions_planned TEXT,
            confidence_rating INTEGER,
            completed_at TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(user_id, week_start_date)
        )
    ''')
    
    # Decision Support Context
    db.execute('''
        CREATE TABLE IF NOT EXISTS decision_support (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            decision_context TEXT NOT NULL,
            question TEXT NOT NULL,
            analysis_data TEXT,
            recommendation TEXT,
            confidence_level TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Career Milestones & Achievements
    db.execute('''
        CREATE TABLE IF NOT EXISTS career_milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            milestone_title TEXT NOT NULL,
            milestone_description TEXT,
            category TEXT,
            target_date TEXT,
            completed INTEGER DEFAULT 0,
            completed_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Application Recommendations
    db.execute('''
        CREATE TABLE IF NOT EXISTS application_readiness (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            target_role TEXT NOT NULL,
            match_score INTEGER,
            recommendation TEXT,
            strengths TEXT,
            improvement_areas TEXT,
            estimated_success_rate INTEGER,
            analyzed_at TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # GDPR Consent Log
    db.execute('''
        CREATE TABLE IF NOT EXISTS gdpr_consent_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            consent_type TEXT NOT NULL,
            version TEXT,
            agreed_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Security Audit Log
    db.execute('''
        CREATE TABLE IF NOT EXISTS security_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            description TEXT,
            severity TEXT DEFAULT 'info',
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Student Profile - Initial discovery & intake
    db.execute('''
        CREATE TABLE IF NOT EXISTS student_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,
            education_level TEXT,
            interests TEXT,
            current_skills TEXT,
            career_goals TEXT,
            experience_level TEXT,
            confusion_areas TEXT,
            learning_style TEXT,
            available_hours_per_week INTEGER,
            target_timeline_months INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Learning Paths - Structured, prioritized learning directions
    db.execute('''
        CREATE TABLE IF NOT EXISTS learning_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            skill_area TEXT NOT NULL,
            priority INTEGER,
            skill_category TEXT,
            skill_description TEXT,
            why_matters TEXT,
            learning_order INTEGER,
            estimated_weeks INTEGER,
            resources TEXT,
            completed INTEGER DEFAULT 0,
            started_at TEXT,
            completed_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(user_id, skill_area)
        )
    ''')
    
    # Resume Evolution Plans - How their resume should grow
    db.execute('''
        CREATE TABLE IF NOT EXISTS resume_evolution_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,
            current_resume_level TEXT,
            target_resume_level TEXT,
            timeline_months INTEGER,
            phase_1_description TEXT,
            phase_1_target_date TEXT,
            phase_1_actions TEXT,
            phase_2_description TEXT,
            phase_2_target_date TEXT,
            phase_2_actions TEXT,
            phase_3_description TEXT,
            phase_3_target_date TEXT,
            phase_3_actions TEXT,
            proof_and_projects TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Action Plans - What to do today/week/month
    db.execute('''
        CREATE TABLE IF NOT EXISTS action_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            action_category TEXT NOT NULL,
            action_title TEXT NOT NULL,
            action_description TEXT,
            time_commitment TEXT,
            priority TEXT DEFAULT 'medium',
            target_date TEXT,
            status TEXT DEFAULT 'pending',
            completed_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Guidance Sessions - Track student interactions with guidance
    db.execute('''
        CREATE TABLE IF NOT EXISTS guidance_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            session_type TEXT NOT NULL,
            stage TEXT,
            data TEXT,
            insights TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Indexes for performance (wrapped in try-except for migration safety)
    indexes = [
        'CREATE INDEX IF NOT EXISTS idx_submissions_user_id ON submissions(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_submissions_created_at ON submissions(created_at)',
        'CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id, created_at)',
        'CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)',
        'CREATE INDEX IF NOT EXISTS idx_usage_daily_user_date ON usage_tracking_daily(user_id, date)',
        'CREATE INDEX IF NOT EXISTS idx_usage_monthly_user_month ON usage_tracking_monthly(user_id, year_month)'
    ]
    
    for idx in indexes:
        try:
            db.execute(idx)
        except:
            pass  # Index might already exist

    # Unified User Profile - Onboarding & Progress Data
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            skills TEXT,
            interests TEXT,
            phase TEXT,
            goals TEXT,
            daily_time INTEGER DEFAULT 1,
            primary_skill TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    # User Roadmap - Generated learning roadmap items
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_roadmap (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            duration TEXT,
            xp INTEGER DEFAULT 0,
            order_num INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')

    # User Insights - Generated career insights
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            insight_text TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            priority INTEGER DEFAULT 1,
            order_num INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')

    # Data Sync Log - Tracks synchronisation runs
    db.execute('''
        CREATE TABLE IF NOT EXISTS data_sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            last_sync TEXT NOT NULL,
            sync_type TEXT,
            modules_updated TEXT
        )
    ''')

    # ── Phase 4 migrations: add columns that may not exist in older DBs ──────
    _safe_alters = [
        "ALTER TABLE confidence_index ADD COLUMN updated_at TEXT",
        "ALTER TABLE skill_gap_analysis ADD COLUMN target_role TEXT",
        "ALTER TABLE resume_health ADD COLUMN created_at TEXT",
        # action_plans columns expected by data_sync.py
        "ALTER TABLE action_plans ADD COLUMN xp_reward INTEGER DEFAULT 50",
        "ALTER TABLE action_plans ADD COLUMN description TEXT",
        "ALTER TABLE action_plans ADD COLUMN order_num INTEGER DEFAULT 0",
        "ALTER TABLE action_plans ADD COLUMN completed_at TEXT",
    ]
    for _stmt in _safe_alters:
        try:
            db.execute(_stmt)
        except Exception:
            pass  # Column already exists — safe to ignore

    # Initialize tier configurations if not exist
    try:
        db.execute('''INSERT OR IGNORE INTO tier_config (tier, career_analyses_limit, resume_uploads_limit, chatbot_messages_limit, features_json, description, price_monthly)
                     VALUES ('free', 5, 2, 20, ?, 'Free tier - limited usage', 0.0)''',
                  (json.dumps({'resume_parser': False, 'premium_insights': False, 'export': False}),))
        
        db.execute('''INSERT OR IGNORE INTO tier_config (tier, career_analyses_limit, resume_uploads_limit, chatbot_messages_limit, features_json, description, price_monthly)
                     VALUES ('pro', 50, 20, 500, ?, 'Pro tier - unlimited usage', 9.99)''',
                  (json.dumps({'resume_parser': True, 'premium_insights': True, 'export': True}),))
    except:
        pass
    
    db.commit()
    print("Database schema initialized")


def insert_submission(user_id, name, email, interest, level, known_skills, 
                     recommendation, readiness_score, confidence_score,
                     recommended_role_tier, strengths, gaps, 
                     resume_file_path=None, resume_parsed_skills=None,
                     profile_image_path=None):
    """Insert a new submission with all enhanced fields."""
    db = get_db()
    now = datetime.utcnow().isoformat()
    
    try:
        cursor = db.execute(
            '''INSERT INTO submissions 
            (user_id, name, email, interest, level, known_skills, recommendation, 
             readiness_score, confidence_score, recommended_role_tier, strengths, gaps,
             resume_file_path, resume_parsed_skills, profile_image_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id, name, email, interest, level, known_skills, recommendation,
             readiness_score, confidence_score, recommended_role_tier,
             json.dumps(strengths) if strengths else None,
             json.dumps(gaps) if gaps else None,
             resume_file_path, json.dumps(resume_parsed_skills) if resume_parsed_skills else None,
             profile_image_path, now, now)
        )
        db.commit()
        return cursor.lastrowid
    except Exception as e:
        db.rollback()
        print(f"Insert error: {e}")
        return None

def get_user_submissions(user_id, limit=50, offset=0):
    """Retrieve user's past submissions."""
    db = get_db()
    cursor = db.execute(
        '''SELECT * FROM submissions 
           WHERE user_id = ? 
           ORDER BY created_at DESC 
           LIMIT ? OFFSET ?''',
        (user_id, limit, offset)
    )
    
    # Convert rows to dictionaries
    cols = [description[0] for description in cursor.description]
    submissions = [dict(zip(cols, row)) for row in cursor.fetchall()]
    
    return submissions

def get_dashboard_analytics():
    """Get analytics for admin dashboard."""
    db = get_db()
    
    total_submissions = db.execute('SELECT COUNT(*) FROM submissions').fetchone()[0]
    
    roles_distribution = db.execute(
        '''SELECT recommendation, COUNT(*) as count 
           FROM submissions 
           GROUP BY recommendation 
           ORDER BY count DESC'''
    ).fetchall()
    
    avg_readiness = db.execute(
        'SELECT AVG(readiness_score) FROM submissions'
    ).fetchone()[0] or 0
    
    top_skills_gaps = db.execute(
        '''SELECT gaps, COUNT(*) as count 
           FROM submissions 
           WHERE gaps IS NOT NULL 
           GROUP BY gaps 
           LIMIT 10'''
    ).fetchall()
    
    return {
        'total_submissions': total_submissions,
        'roles_distribution': roles_distribution,
        'avg_readiness': round(avg_readiness, 1),
        'top_skills_gaps': top_skills_gaps
    }

def insert_chat_message(user_id, session_id, message, response=None, context=None):
    """Insert chat message into history."""
    db = get_db()
    now = datetime.utcnow().isoformat()
    
    db.execute(
        '''INSERT INTO chat_history (user_id, session_id, message, response, context, created_at)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, session_id, message, response, 
         json.dumps(context) if context else None, now)
    )
    db.commit()

def get_chat_history(user_id, session_id, limit=20):
    """Retrieve chat history for a session."""
    db = get_db()
    messages = db.execute(
        '''SELECT * FROM chat_history 
           WHERE user_id = ? AND session_id = ?
           ORDER BY created_at DESC 
           LIMIT ?''',
        (user_id, session_id, limit)
    ).fetchall()
    return messages

def track_chatbot_analytics(user_id, message_type, metadata=None):
    """Track analytics for the chatbot."""
    db = get_db()
    now = datetime.utcnow().isoformat()
    
    db.execute(
        '''INSERT INTO chatbot_analytics (user_id, message_type, metadata, created_at)
           VALUES (?, ?, ?, ?)''',
        (user_id, message_type, 
         json.dumps(metadata) if metadata else None, now)
    )
    db.commit()

def get_chatbot_insights():
    """Get insights for admin dashboard about chatbot usage."""
    db = get_db()
    
    total_messages = db.execute(
        'SELECT COUNT(*) FROM chatbot_analytics'
    ).fetchone()[0]
    
    message_types = db.execute(
        '''SELECT message_type, COUNT(*) as count 
           FROM chatbot_analytics 
           GROUP BY message_type'''
    ).fetchall()
    
    recent_activity = db.execute(
        '''SELECT user_id, message_type, created_at 
           FROM chatbot_analytics 
           ORDER BY created_at DESC 
           LIMIT 20'''
    ).fetchall()
    
    return {
        'total_messages': total_messages,
        'message_types': message_types,
        'recent_activity': recent_activity
    }

def fetch_all_logs(limit=100):
    """Fetch all activity logs from the database."""
    db = get_db()
    try:
        # Get recent submissions (activity logs)
        logs = db.execute(
            '''SELECT id, name, interest, level, recommendation, created_at 
               FROM submissions 
               ORDER BY created_at DESC 
               LIMIT ?''',
            (limit,)
        ).fetchall()
        return logs if logs else []
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return []

def get_database_stats():
    """Get database statistics for admin dashboard."""
    db = get_db()
    try:
        total_users = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        total_submissions = db.execute('SELECT COUNT(*) FROM submissions').fetchone()[0]
        total_messages = db.execute('SELECT COUNT(*) FROM chatbot_analytics').fetchone()[0]
        
        # Stats by interest
        by_interest = db.execute(
            '''SELECT interest, COUNT(*) as count 
               FROM submissions 
               GROUP BY interest 
               ORDER BY count DESC 
               LIMIT 10'''
        ).fetchall()
        
        # Stats by level
        by_level = db.execute(
            '''SELECT level, COUNT(*) as count 
               FROM submissions 
               GROUP BY level 
               ORDER BY count DESC'''
        ).fetchall()
        
        return {
            'total_users': total_users,
            'total_submissions': total_submissions,
            'total_messages': total_messages,
            'by_interest': [dict(row) for row in by_interest],
            'by_level': [dict(row) for row in by_level]
        }
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return {
            'total_users': 0,
            'total_submissions': 0,
            'total_messages': 0,
            'by_interest': [],
            'by_level': []
        }

