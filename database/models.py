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
            last_updated TEXT,
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

