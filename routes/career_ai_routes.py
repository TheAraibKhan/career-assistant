from flask import Blueprint, render_template, session, redirect, request, jsonify
import json
from datetime import datetime

career_ai_bp = Blueprint('career_ai', __name__)


def login_required(f):
    """Simple login check decorator for career_ai pages."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/auth/login')
        return f(*args, **kwargs)
    return decorated


def _get_current_user():
    """Get current user data for templates."""
    try:
        from database.db import get_db
        db = get_db()
        user = db.execute(
            "SELECT id, full_name, email FROM users WHERE id = ?",
            (session.get('user_id'),)
        ).fetchone()
        return dict(user) if user else {'full_name': 'Profile', 'email': ''}
    except Exception:
        return {'full_name': 'Profile', 'email': ''}


def _get_user_onboarding():
    """Get user's onboarding profile - wrapper around profile_service for templates."""
    try:
        from services.profile_service import get_user_profile
        
        user_id = session.get('user_id')
        if not user_id:
            return None
        
        # Use unified profile service as source of truth
        profile = get_user_profile(user_id)
        
        if profile and profile['profile']['completed']:
            return {
                'skills': profile['profile']['skills'],
                'interests': profile['profile']['interests'],
                'phase': profile['user']['phase'],
                'goals': profile['profile']['goals'],
                'daily_time': profile['profile']['daily_time'],
                'completed': True
            }
        return None
    except Exception as e:
        print(f"DEBUG: Error in _get_user_onboarding: {str(e)}")
        return None


@career_ai_bp.route('/app')
@login_required
def dashboard():
    user = _get_current_user()
    onboarding = _get_user_onboarding()
    return render_template('career_ai/dashboard.html', 
                         current_user=user, 
                         onboarding=onboarding)


@career_ai_bp.route('/api/onboarding', methods=['POST'])
@login_required
def save_onboarding():
    """Save user's onboarding profile to database using unified profile service."""
    from services.profile_service import update_user_profile
    
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        # Validate required fields
        required_fields = ['skills', 'interests', 'phase', 'goals', 'daily_time']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        if not isinstance(data['skills'], list) or len(data['skills']) == 0:
            return jsonify({'success': False, 'error': 'Please select at least one skill'}), 400
        
        if not isinstance(data['interests'], list) or len(data['interests']) == 0:
            return jsonify({'success': False, 'error': 'Please select at least one interest'}), 400
        
        if not isinstance(data['goals'], list) or len(data['goals']) == 0:
            return jsonify({'success': False, 'error': 'Please select at least one goal'}), 400
        
        # Use unified profile service for all data updates
        profile = update_user_profile(user_id, {
            'skills': data['skills'],
            'interests': data['interests'],
            'phase': data['phase'],
            'goals': data['goals'],
            'daily_time': int(data['daily_time']),
        })
        
        print(f"DEBUG: Onboarding profile saved for user {user_id} via profile_service")
        
        return jsonify({
            'success': True,
            'message': 'Profile saved successfully',
            'user_profile': profile
        }), 200
    
    except Exception as e:
        print(f"Error saving onboarding: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@career_ai_bp.route('/api/onboarding', methods=['GET'])
@login_required
def get_onboarding():
    """Get user's onboarding profile."""
    onboarding = _get_user_onboarding()
    if onboarding:
        return jsonify({'success': True, 'data': onboarding}), 200
    return jsonify({'success': False, 'data': None}), 200



@career_ai_bp.route('/app/journey')
@login_required
def journey():
    user = _get_current_user()
    onboarding = _get_user_onboarding()
    return render_template('career_ai/journey.html', current_user=user, onboarding=onboarding)


@career_ai_bp.route('/app/roadmap')
@login_required
def roadmap():
    user = _get_current_user()
    onboarding = _get_user_onboarding()
    return render_template('career_ai/roadmap.html', current_user=user, onboarding=onboarding)


@career_ai_bp.route('/app/projects')
@login_required
def projects():
    user = _get_current_user()
    onboarding = _get_user_onboarding()
    return render_template('career_ai/projects.html', current_user=user, onboarding=onboarding)


@career_ai_bp.route('/app/resume-lab')
@login_required
def resume_lab():
    user = _get_current_user()
    onboarding = _get_user_onboarding()
    return render_template('career_ai/resume_lab.html', current_user=user, onboarding=onboarding)


@career_ai_bp.route('/app/resume-builder')
@login_required
def resume_builder():
    """Resume builder page with templates and interactive form."""
    user = _get_current_user()
    onboarding = _get_user_onboarding()
    return render_template('career_ai/resume_builder.html', current_user=user, onboarding=onboarding)


@career_ai_bp.route('/app/insights')
@login_required
def insights():
    user = _get_current_user()
    onboarding = _get_user_onboarding()
    return render_template('career_ai/insights.html', current_user=user, onboarding=onboarding)


@career_ai_bp.route('/app/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Profile page with dark theme matching CareerAssist design."""
    from services.auth_service import get_user_by_id, update_user_profile
    user_id = session.get('user_id')
    user = get_user_by_id(user_id) or {'full_name': 'Profile', 'email': ''}
    error = None
    success = None

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        if full_name:
            update_user_profile(user_id, full_name=full_name)
            session['full_name'] = full_name
            success = 'Profile updated successfully!'
            user = get_user_by_id(user_id)

    return render_template('career_ai/profile.html', user=user, error=error, success=success)


# ===== API ENDPOINTS =====


@career_ai_bp.route('/api/user-profile', methods=['GET'])
@login_required
def get_user_profile_api():
    """
    Master endpoint - Returns complete user profile with all data.
    Uses profile_service as single source of truth.
    """
    from services.profile_service import get_user_profile
    from services.roadmap_service import generate_roadmap
    
    try:
        user_id = session.get('user_id')
        
        # Get unified profile from the single source of truth
        profile = get_user_profile(user_id)
        
        # Generate roadmap from profile data
        try:
            roadmap = generate_roadmap(profile['profile'], profile['stats'])
        except Exception:
            roadmap = []
        
        user_profile = {
            'success': True,
            'user': profile['user'],
            'profile': profile['profile'],
            'stats': profile['stats'],
            'skills': profile['skills'],
            'roadmap': {
                'items': roadmap,
            },
            'projects': [],
            'lastUpdated': datetime.utcnow().isoformat(),
        }
        
        print(f"DEBUG: /api/user-profile - skills={profile['profile'].get('skills')}, phase={profile['user'].get('phase')}")
        
        return jsonify(user_profile), 200
        
    except Exception as e:
        print(f"Error getting user profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@career_ai_bp.route('/api/insights', methods=['GET'])
@login_required
def get_insights():
    """
    Generate personalized career insights based on user progress.
    Uses insight_service with unified profile data.
    """
    from services.profile_service import get_user_profile
    from services.insight_service import generate_insights
    
    try:
        user_id = session.get('user_id')
        
        # Get unified profile
        profile = get_user_profile(user_id)
        
        # Generate insights from unified data
        insights = generate_insights(
            profile_data=profile['profile'],
            stats=profile['stats'],
            skills_data=profile['skills'],
            resume_data=profile.get('resume_data'),
        )
        
        print(f"DEBUG: /api/insights - readiness={profile['stats'].get('career_readiness', 0)}%")
        
        return jsonify(insights), 200
        
    except Exception as e:
        print(f"Error generating insights: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@career_ai_bp.route('/api/roadmap', methods=['GET'])
@login_required
def get_roadmap():
    """Get personalized learning roadmap from user's profile data."""
    from services.profile_service import get_user_profile
    from services.roadmap_service import generate_roadmap
    
    try:
        user_id = session.get('user_id')
        print(f"DEBUG: /api/roadmap called for user {user_id}")
        
        # Get unified profile
        profile = get_user_profile(user_id)
        
        # Generate roadmap from user's actual skills + goals
        roadmap = generate_roadmap(profile['profile'], profile['stats'])
        
        print(f"DEBUG: /api/roadmap returning {len(roadmap)} personalized items for skills={profile['profile'].get('skills')}")
        return jsonify({'success': True, 'roadmap': roadmap}), 200
        
    except Exception as e:
        import traceback
        print(f"ERROR in /api/roadmap: {str(e)}")
        print(traceback.format_exc())
        # Fallback: still return guidance instead of breaking
        return jsonify({'success': True, 'roadmap': [
            {'title': 'Complete Your Profile', 'description': 'Set up your skills, interests, and goals to generate a personalized roadmap.', 'duration': '5 minutes', 'xp': 50},
        ]}), 200


@career_ai_bp.route('/api/roadmap/refresh', methods=['POST'])
@login_required
def refresh_roadmap():
    """Recalculate roadmap and all dependent data."""
    from services.data_sync import refresh_user_data
    
    try:
        user_id = session.get('user_id')
        print(f"DEBUG: /api/roadmap/refresh triggered for user {user_id}")
        
        # Trigger full sync across all modules
        profile = refresh_user_data(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Roadmap and all modules refreshed',
            'profile': profile
        }), 200
        
    except Exception as e:
        print(f"ERROR in /api/roadmap/refresh: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@career_ai_bp.route('/api/actions', methods=['GET'])
@login_required
def get_actions():
    """
    Get personalized action items for the user.
    
    Actions are AI-generated, daily-focused tasks based on:
    - Current roadmap phase
    - Time commitment
    - Skill gaps
    - Career goals
    
    Actions are stored in DB once generated and retrieved here.
    """
    from database.db import get_db
    from services.profile_service import get_user_profile
    from services.action_guidance_service import generate_actions_for_user
    
    try:
        user_id = session.get('user_id')
        db = get_db()
        
        # Try to get existing pending actions from DB
        actions_from_db = db.execute('''
            SELECT id, action_category, action_title, description, time_commitment, 
                   xp_reward, status, order_num, created_at
            FROM action_plans 
            WHERE user_id = ? AND status = 'pending'
            ORDER BY order_num, created_at
            LIMIT 10
        ''', (user_id,)).fetchall()
        
        if actions_from_db:
            # Return existing actions
            actions = [{
                'id': a['id'],
                'category': a['action_category'],
                'title': a['action_title'],
                'description': a['description'],
                'time_commitment': a['time_commitment'],
                'xp_reward': a['xp_reward'],
                'status': a['status']
            } for a in actions_from_db]
        else:
            # Generate new actions if none exist
            profile = get_user_profile(user_id)
            actions_data = generate_actions_for_user(user_id, profile)
            
            # Store generated actions
            if actions_data:
                now = datetime.utcnow().isoformat()
                for idx, action in enumerate(actions_data or []):
                    db.execute('''
                        INSERT INTO action_plans 
                        (user_id, action_category, action_title, description, 
                         time_commitment, xp_reward, status, order_num, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        user_id,
                        action.get('category', 'learning'),
                        action.get('title', ''),
                        action.get('description', ''),
                        action.get('time_commitment', '30 min'),
                        action.get('xp_reward', 50),
                        'pending',
                        idx,
                        now
                    ))
                db.commit()
            
            actions = actions_data or []
        
        print(f"DEBUG: /api/actions returning {len(actions)} actions for user {user_id}")
        return jsonify({'success': True, 'actions': actions}), 200
        
    except Exception as e:
        import traceback
        print(f"ERROR in /api/actions: {str(e)}")
        print(traceback.format_exc())
        # Return empty actions instead of breaking
        return jsonify({'success': True, 'actions': []}), 200


@career_ai_bp.route('/api/actions/<int:action_id>/complete', methods=['POST'])
@login_required
def complete_action(action_id):
    """
    Mark an action as complete and trigger data sync.
    
    This:
    - Marks action as completed
    - Awards XP
    - Updates stats
    - Regenerates actions
    """
    from services.data_sync import sync_action_completion
    
    try:
        user_id = session.get('user_id')
        
        # Use sync layer to handle completion
        profile = sync_action_completion(user_id, action_id)
        
        return jsonify({
            'success': True,
            'message': 'Action completed!',
            'profile': profile
        }), 200
        
    except Exception as e:
        print(f"ERROR completing action: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@career_ai_bp.route('/api/projects', methods=['GET'])
@login_required
def get_projects():
    """Get AI-recommended projects based on user's skills and level."""
    try:
        onboarding = _get_user_onboarding()
        if not onboarding:
            return jsonify({'success': True, 'projects': []}), 200
        
        skills = onboarding.get('skills', [])
        primary_skill = skills[0] if skills else 'Python'
        
        # Project templates organized by difficulty and category
        projects = [
            # Beginner Web Projects
            {
                'title': 'Personal Portfolio Website',
                'description': 'Create a stunning portfolio site to showcase your projects, skills, and achievements. Deploy it live on GitHub Pages.',
                'level': 'beginner',
                'category': 'web',
                'icon': '🌐',
                'xp': 200,
                'duration': '1-2 weeks',
                'tech': ['HTML', 'CSS', 'JavaScript', 'GitHub Pages'],
                'status': 'completed',
                'steps': [
                    'Design layout with HTML5 semantic elements',
                    'Style with CSS Grid/Flexbox (responsive)',
                    'Add JavaScript interactivity (smooth scroll, form validation)',
                    'Deploy to GitHub Pages',
                ]
            },
            # Beginner Project
            {
                'title': 'ToDo Task Manager',
                'description': 'Build an app to manage daily tasks with add, delete, and mark-complete features. Learn localStorage for data persistence.',
                'level': 'beginner',
                'category': 'web',
                'icon': 'task',
                'xp': 150,
                'duration': '1 week',
                'tech': ['HTML', 'CSS', 'JavaScript', 'LocalStorage'],
                'status': 'in-progress',
                'steps': [
                    'Create layout for task input & display',
                    'Implement add/delete task functionality',
                    'Save tasks to localStorage',
                    'Add filtering (all, active, completed)',
                ]
            },
            # Intermediate Web Project
            {
                'title': 'Real-time Weather Dashboard',
                'description': 'Fetch real-time weather data using OpenWeatherMap API. Display temperature, humidity, forecasts with beautiful UI.',
                'level': 'intermediate',
                'category': 'web',
                'icon': '🌤️',
                'xp': 300,
                'duration': '2-3 weeks',
                'tech': ['React', 'API Integration', 'CSS', 'Geolocation'],
                'status': 'locked',
                'steps': [
                    'Sign up for OpenWeatherMap API key',
                    'Build React components for weather display',
                    'Integrate geolocation for auto-location',
                    'Add 5-day forecast & weather alerts',
                ]
            },
            # Intermediate Project
            {
                'title': 'E-Commerce Shopping Cart',
                'description': 'Build a fully functional shopping cart with product filtering, sorting, and checkout. Practice React state management.',
                'level': 'intermediate',
                'category': 'web',
                'icon': '🛒',
                'xp': 350,
                'duration': '3-4 weeks',
                'tech': ['React', 'Redux/Context', 'Express', 'MongoDB'],
                'status': 'locked',
                'steps': [
                    'Design product database schema',
                    'Build React components (product list, cart, checkout)',
                    'Implement state management with Redux',
                    'Create backend API endpoints',
                ]
            },
            # Advanced AI/ML Project
            {
                'title': 'Movie Recommendation Engine',
                'description': 'Build ML model using collaborative filtering. Recommend movies based on user ratings and watching patterns.',
                'level': 'advanced',
                'category': 'ai',
                'icon': '🎬',
                'xp': 500,
                'duration': '4-6 weeks',
                'tech': ['Python', 'TensorFlow', 'Pandas', 'Scikit-learn'],
                'status': 'locked',
                'steps': [
                    'Load and analyze MovieLens dataset',
                    'Implement collaborative filtering algorithm',
                    'Train ML model (matrix factorization)',
                    'Build web interface to display recommendations',
                ]
            },
            # Advanced Full Stack
            {
                'title': 'Social Network Platform',
                'description': 'Full-stack social platform with user authentication, posts, likes, comments, and real-time notifications.',
                'level': 'advanced',
                'category': 'web',
                'icon': '👥',
                'xp': 800,
                'duration': '8-10 weeks',
                'tech': ['React', 'Node.js', 'MongoDB', 'Socket.io', 'JWT'],
                'status': 'locked',
                'steps': [
                    'Design database schema for users, posts, comments',
                    'Implement JWT authentication',
                    'Build React frontend components',
                    'Create REST API with Express',
                    'Add real-time notifications with Socket.io',
                ]
            },
        ]
        
        return jsonify({'success': True, 'projects': projects}), 200
    except Exception as e:
        print(f"Error getting projects: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@career_ai_bp.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Generate daily tasks based on user's daily_time commitment and goals."""
    try:
        onboarding = _get_user_onboarding()
        if not onboarding:
            return jsonify({'success': True, 'tasks': []}), 200
        
        daily_time = onboarding.get('daily_time', 1)
        goals = onboarding.get('goals', [])
        skills = onboarding.get('skills', [])
        
        # Task templates
        task_templates = [
            {
                'title': f'Practice {skills[0]} fundamentals',
                'description': f'Complete coding exercises in {skills[0]}.',
                'duration': '30 mins',
                'xp': 50,
                'priority': 'high',
                'category': 'Practice'
            },
            {
                'title': 'Read documentation',
                'description': 'Study official docs for your current learning topic.',
                'duration': '20 mins',
                'xp': 30,
                'priority': 'medium',
                'category': 'Study'
            },
            {
                'title': 'Build a mini-project',
                'description': 'Create a small project using today\'s learnings.',
                'duration': '45 mins',
                'xp': 75,
                'priority': 'high',
                'category': 'Project'
            },
            {
                'title': 'Review concepts',
                'description': 'Revisit yesterday\'s learning and connect dots.',
                'duration': '25 mins',
                'xp': 40,
                'priority': 'medium',
                'category': 'Review'
            },
            {
                'title': 'Solve coding problems',
                'description': 'Complete 3-5 LeetCode/HackerRank problems.',
                'duration': '60 mins',
                'xp': 100,
                'priority': 'high',
                'category': 'DSA'
            },
        ]
        
        # Select tasks based on daily_time (1-8 hours)
        num_tasks = max(2, min(5, daily_time // 1))  # 2-5 tasks based on hours
        tasks = task_templates[:num_tasks]
        
        return jsonify({'success': True, 'tasks': tasks}), 200
    except Exception as e:
        print(f"Error getting tasks: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@career_ai_bp.route('/api/journey', methods=['GET'])
@login_required
def get_journey():
    """Get phase-specific journey and milestones."""
    try:
        onboarding = _get_user_onboarding()
        if not onboarding:
            return jsonify({'success': True, 'journey': {}}), 200
        
        user_phase = onboarding.get('phase', 'college')
        requested_phase = request.args.get('phase')  # Allow querying any phase
        phase = requested_phase if requested_phase in ['pre-college', 'college', 'post-college'] else user_phase
        
        # Phase-specific milestones
        journey_paths = {
            'pre-college': [
                {'title': 'Discover Your Interests', 'description': 'Take aptitude tests, explore different tech domains.', 'xp': 100, 'status': 'Completed'},
                {'title': 'Learn Programming Basics', 'description': 'Start with Python or JavaScript. Learn variables, loops, functions.', 'xp': 200, 'status': 'In Progress'},
                {'title': 'Build Your First Project', 'description': 'Create a simple calculator, to-do app, or personal webpage.', 'xp': 250, 'status': 'Upcoming'},
                {'title': 'Explore Career Paths', 'description': 'Research different roles: Frontend, Backend, Data Science, etc.', 'xp': 150, 'status': 'Locked'},
            ],
            'college': [
                {'title': 'Master Core Skills', 'description': 'Deepen knowledge in chosen domain (Web, ML, Mobile, etc).', 'xp': 300, 'status': 'Completed'},
                {'title': 'Build Portfolio Projects', 'description': 'Create 2-3 impressive projects for your resume.', 'xp': 350, 'status': 'In Progress'},
                {'title': 'Prepare for Internship', 'description': 'DSA practice, system design basics, interview prep.', 'xp': 400, 'status': 'Upcoming'},
                {'title': 'Land Your Internship', 'description': 'Apply, interview, and secure an internship position.', 'xp': 500, 'status': 'Locked'},
            ],
            'post-college': [
                {'title': 'Specialize in Your Domain', 'description': 'Master advanced topics in your chosen specialization.', 'xp': 500, 'status': 'Completed'},
                {'title': 'Lead Technical Projects', 'description': 'Take ownership of complex projects, mentor juniors.', 'xp': 600, 'status': 'In Progress'},
                {'title': 'Build Your Personal Brand', 'description': 'Write blogs, contribute to open source, speak at conferences.', 'xp': 400, 'status': 'Upcoming'},
                {'title': 'Reach Senior Level', 'description': 'Advance to senior/staff engineer, architect solutions.', 'xp': 800, 'status': 'Locked'},
            ]
        }
        
        journey = journey_paths.get(phase, journey_paths['college'])
        return jsonify({'success': True, 'journey': journey, 'phase': phase, 'user_phase': user_phase}), 200
    except Exception as e:
        print(f"Error getting journey: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@career_ai_bp.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Get user's current stats (initially 0, tracked via activity)."""
    try:
        from database.db import get_db
        db = get_db()
        user_id = session.get('user_id')
        
        # Check if user has activity tracked
        stats = db.execute(
            '''SELECT COALESCE(total_xp, 0) as xp, 
                      COALESCE(current_streak, 0) as streak,
                      COALESCE(tasks_completed, 0) as tasks_done,
                      COALESCE(skills_tracked, 1) as skills_count,
                      COALESCE(career_readiness, 0) as readiness
               FROM user_stats WHERE user_id = ?''',
            (user_id,)
        ).fetchone()
        
        if stats:
            return jsonify({
                'success': True,
                'stats': {
                    'xp': stats['xp'],
                    'streak': stats['streak'],
                    'tasks_done': stats['tasks_done'],
                    'career_readiness': stats['readiness'],
                    'skills_tracked': stats['skills_count']
                }
            }), 200
        else:
            # New user - return initial stats (all zeros/defaults)
            return jsonify({
                'success': True,
                'stats': {
                    'xp': 0,
                    'streak': 0,
                    'tasks_done': 0,
                    'career_readiness': 0,
                    'skills_tracked': 1
                }
            }), 200
    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        # Return default stats if table doesn't exist yet
        return jsonify({
            'success': True,
            'stats': {
                'xp': 0,
                'streak': 0,
                'tasks_done': 0,
                'career_readiness': 0,
                'skills_tracked': 1
            }
        }), 200


# ===== ACTIVITY TRACKING =====

@career_ai_bp.route('/api/app-state', methods=['GET'])
@login_required
def get_app_state():
    """Get complete app state for client initialization. Uses unified profile_service."""
    from services.profile_service import get_user_profile
    from services.roadmap_service import generate_roadmap
    
    try:
        user_id = session.get('user_id')
        
        # Use single source of truth
        profile = get_user_profile(user_id)
        
        # Generate roadmap from profile
        try:
            roadmap = generate_roadmap(profile['profile'], profile['stats'])
        except Exception:
            roadmap = []
        
        appState = {
            'user': profile['user'],
            'profile': profile['profile'],
            'stats': profile['stats'],
            'skills': profile['skills'],
            'roadmap': {
                'items': roadmap,
            },
        }
        
        return jsonify({
            'success': True,
            'appState': appState,
        }), 200
        
    except Exception as e:
        print(f"Error getting app state: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@career_ai_bp.route('/api/task-complete', methods=['POST'])
@login_required
def complete_task():
    """Record task completion and update user stats."""
    from database.db import get_db
    from datetime import date, timedelta
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        user_id = session.get('user_id')
        task_title = str(data.get('title', 'Unknown Task'))[:200]  # sanitize
        xp_earned = max(0, min(500, int(data.get('xp', 30))))  # clamp 0-500
        skill = data.get('skill', None)
        
        db = get_db()
        
        # Tables are created at startup by models.py — no inline CREATE TABLE needed
        
        # Log the activity
        now = datetime.utcnow().isoformat()
        today = date.today().isoformat()
        
        db.execute('''
            INSERT INTO activity_log (user_id, activity_type, task_id, xp_earned, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, 'task_complete', skill, xp_earned, task_title, now))
        
        # Get or create user stats
        stats = db.execute(
            'SELECT * FROM user_stats WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        
        if stats:
            # Update existing stats
            new_xp = stats['total_xp'] + xp_earned
            new_tasks = stats['tasks_completed'] + 1
            
            # Calculate streak
            last_activity = stats['last_activity_date']
            if last_activity == today:
                new_streak = stats['current_streak']
            elif last_activity:
                try:
                    last_date = date.fromisoformat(last_activity)
                    today_date = date.today()
                    if (today_date - last_date).days == 1:
                        new_streak = stats['current_streak'] + 1
                    elif (today_date - last_date).days == 0:
                        new_streak = stats['current_streak']
                    else:
                        new_streak = 1
                except ValueError:
                    new_streak = 1
            else:
                new_streak = 1
            
            # Track longest streak
            longest_streak = max(stats.get('longest_streak', 0) or 0, new_streak)
            
            # Multi-dimensional career readiness formula:
            #   Task contribution: sqrt(tasks) * 8, up to 35 points
            #   Skill depth: skills_tracked * 5, up to 20 points  
            #   XP milestone: log(xp) * 5, up to 25 points
            #   Streak bonus: min(streak, 14) * 1, up to 14 points
            #   Base: 5 points
            import math
            task_score = min(35, int(math.sqrt(new_tasks) * 8))
            skills_count = stats.get('skills_tracked', 1) or 1
            skill_score = min(20, skills_count * 5)
            xp_score = min(25, int(math.log(max(1, new_xp)) * 3.5))
            streak_score = min(14, new_streak)
            new_readiness = min(95, 5 + task_score + skill_score + xp_score + streak_score)
            
            db.execute('''
                UPDATE user_stats
                SET total_xp = ?, tasks_completed = ?, career_readiness = ?, 
                    current_streak = ?, longest_streak = ?,
                    last_activity_date = ?, updated_at = ?
                WHERE user_id = ?
            ''', (new_xp, new_tasks, new_readiness, new_streak, longest_streak, today, now, user_id))
        else:
            # Create new stats entry
            now_date = datetime.utcnow().isoformat()
            db.execute('''
                INSERT INTO user_stats (user_id, total_xp, current_streak, longest_streak,
                                       tasks_completed, career_readiness, skills_tracked,
                                       last_activity_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, xp_earned, 1, 1, 1, 12, 1, today, now_date, now_date))
        
        # Update skill progress if skill provided
        if skill:
            try:
                from services.data_sync import sync_skill_update
                sync_skill_update(user_id, skill, 1, tasks_completed=1, xp_earned=xp_earned)
            except Exception as e:
                print(f"Warning: skill sync failed: {e}")
        
        db.commit()
        
        # Get updated stats to return
        updated_stats = db.execute(
            'SELECT total_xp, tasks_completed, career_readiness, current_streak FROM user_stats WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        
        return jsonify({
            'success': True,
            'message': f'+{xp_earned} XP earned!',
            'xp_earned': xp_earned,
            'stats': {
                'total_xp': updated_stats['total_xp'],
                'tasks_completed': updated_stats['tasks_completed'],
                'career_readiness': updated_stats['career_readiness'],
                'current_streak': updated_stats['current_streak'],
            }
        }), 200
        
    except Exception as e:
        print(f"Error completing task: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@career_ai_bp.route('/api/user-stats', methods=['GET'])
@login_required
def get_user_stats():
    """Get current user stats."""
    from database.db import get_db
    
    try:
        user_id = session.get('user_id')
        db = get_db()
        
        # Try to get user stats, return defaults if not found
        stats = db.execute(
            'SELECT total_xp, tasks_completed, career_readiness FROM user_stats WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        
        if stats:
            return jsonify({
                'success': True,
                'stats': {
                    'total_xp': stats['total_xp'],
                    'tasks_completed': stats['tasks_completed'],
                    'career_readiness': stats['career_readiness'],
                    'skills_tracked': 1
                }
            }), 200
        else:
            # User has no stats yet
            return jsonify({
                'success': True,
                'stats': {
                    'total_xp': 0,
                    'tasks_completed': 0,
                    'career_readiness': 0,
                    'skills_tracked': 1
                }
            }), 200
            
    except Exception as e:
        print(f"Error getting user stats: {str(e)}")
        return jsonify({
            'success': True,
            'stats': {
                'total_xp': 0,
                'tasks_completed': 0,
                'career_readiness': 0,
                'skills_tracked': 1
            }
        }), 200


@career_ai_bp.route('/resume/api/extract', methods=['POST'])
def extract_resume():
    """
    Comprehensive resume analysis endpoint.
    Returns detailed section analysis, multi-category scores, insights, and evolution recommendations.
    """
    import os
    import tempfile
    from werkzeug.utils import secure_filename
    from services.resume_analysis_enhanced import ResumeAnalyzer, ResumeTextExtractor
    from services.resume_detailed_analyzer import DetailedResumeAnalyzer
    from services.profile_service import update_user_profile
    
    try:
        # File validation
        if 'resume' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded. Please select a resume file.'}), 400
        
        file = request.files['resume']
        if not file or file.filename == '':
            return jsonify({'success': False, 'error': 'Please select a file to upload.'}), 400
        
        # Validate file extension
        allowed_extensions = {'pdf', 'docx', 'txt'}
        file_ext = os.path.splitext(file.filename)[1].lower().strip('.')
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': f'File type ".{file_ext}" not supported. Use PDF, DOCX, or TXT.'
            }), 400
        
        # Validate file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size == 0:
            return jsonify({'success': False, 'error': 'File is empty. Please check and try again.'}), 400
        if file_size > 5 * 1024 * 1024:
            return jsonify({'success': False, 'error': f'File too large ({file_size/1024/1024:.1f}MB). Max is 5MB.'}), 400
        
        # Save file temporarily
        temp_dir = tempfile.gettempdir()
        filename = secure_filename(file.filename)
        timestamp = __import__('datetime').datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
        user_id = session.get('user_id', 'anonymous')
        temp_filename = f"{user_id}_{timestamp}{filename}"
        temp_path = os.path.join(temp_dir, temp_filename)
        file.save(temp_path)
        
        try:
            # Extract text from file
            text, extract_warnings = ResumeTextExtractor.extract_from_file(temp_path)
            if not text:
                return jsonify({
                    'success': False,
                    'error': 'Could not extract text from file. Try a different format.'
                }), 400
            
            # Run comprehensive analysis
            detailed_analysis = DetailedResumeAnalyzer.analyze_resume_detailed(text)
            
            # Run basic analysis for ATS scores
            basic_analysis = ResumeAnalyzer.analyze_resume(temp_path, user_id=user_id)
            
            # Build enhanced response
            response_data = {
                'success': True,
                
                # Basic scores (for template compatibility)
                'ats_score': detailed_analysis['scores']['overall'],
                'quality_score': detailed_analysis['scores']['content_quality'],
                'overall_score': detailed_analysis['scores']['overall'],
                
                # Section-wise analysis
                'sections': {
                    'education': {
                        'status': detailed_analysis['sections']['education']['status'],
                        'explanation': detailed_analysis['sections']['education']['explanation'],
                        'tips': detailed_analysis['sections']['education']['tips'],
                        'score': detailed_analysis['sections']['education']['score']
                    },
                    'skills': {
                        'status': detailed_analysis['sections']['skills']['status'],
                        'count': detailed_analysis['sections']['skills']['count'],
                        'list': detailed_analysis['sections']['skills']['skills'],
                        'explanation': detailed_analysis['sections']['skills']['explanation'],
                        'tips': detailed_analysis['sections']['skills']['tips'],
                        'score': detailed_analysis['sections']['skills']['score']
                    },
                    'experience': {
                        'status': detailed_analysis['sections']['experience']['status'],
                        'count': detailed_analysis['sections']['experience']['count'],
                        'has_dates': detailed_analysis['sections']['experience']['has_dates'],
                        'has_metrics': detailed_analysis['sections']['experience']['has_metrics'],
                        'explanation': detailed_analysis['sections']['experience']['explanation'],
                        'tips': detailed_analysis['sections']['experience']['tips'],
                        'score': detailed_analysis['sections']['experience']['score']
                    },
                    'projects': {
                        'status': detailed_analysis['sections']['projects']['status'],
                        'count': detailed_analysis['sections']['projects']['count'],
                        'explanation': detailed_analysis['sections']['projects']['explanation'],
                        'tips': detailed_analysis['sections']['projects']['tips'],
                        'score': detailed_analysis['sections']['projects']['score']
                    },
                    'achievements': {
                        'status': detailed_analysis['sections']['achievements']['status'],
                        'count': detailed_analysis['sections']['achievements']['count'],
                        'has_metrics': detailed_analysis['sections']['achievements']['has_metrics'],
                        'explanation': detailed_analysis['sections']['achievements']['explanation'],
                        'tips': detailed_analysis['sections']['achievements']['tips'],
                        'score': detailed_analysis['sections']['achievements']['score']
                    }
                },
                
                # Category scores breakdown
                'scores': {
                    'format': detailed_analysis['scores']['format'],
                    'keywords': detailed_analysis['scores']['keywords'],
                    'completeness': detailed_analysis['scores']['completeness'],
                    'content_quality': detailed_analysis['scores']['content_quality'],
                    'overall': detailed_analysis['scores']['overall']
                },
                
                # Insights (gaps, strengths, role-based)
                'insights': detailed_analysis['insights'],
                
                # Evolution recommendations
                'evolution': detailed_analysis['evolution'],
                
                # Professional level and readiness
                'professional_level': detailed_analysis['professional_level'],
                'readiness_for_role': detailed_analysis.get('readiness_for_role'),
                
                # Skills for UI display
                'skills': detailed_analysis['sections']['skills']['skills'][:15],
                'has_experience': detailed_analysis['sections']['experience']['present'],
                'education': detailed_analysis['sections']['education']['degrees'],
                
                # Personalized suggestions
                'suggestions': detailed_analysis['suggestions'],
                'ats_strengths': [insight['message'] for insight in detailed_analysis['insights'] if insight.get('type') == 'strength'][:3]
            }
            
            # Save to profile if user is logged in
            if user_id and user_id != 'anonymous':
                try:
                    update_user_profile(user_id, {
                        'resume_data': {
                            'ats_score': response_data['ats_score'],
                            'quality_score': response_data['quality_score'],
                            'skills': response_data['skills'],
                            'professional_level': response_data['professional_level'],
                            'last_analyzed': __import__('datetime').datetime.utcnow().isoformat()
                        }
                    })
                except Exception as sync_err:
                    print(f"Warning: Could not sync resume data: {sync_err}")
            
            return jsonify(response_data), 200
            
        finally:
            # Clean up
            try:
                os.remove(temp_path)
            except:
                pass
    
    except Exception as e:
        print(f"Error in /resume/api/extract: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Error analyzing resume. Please try again.'
        }), 500


def extract_skills_from_resume(file_path):
    """Extract detected skills from resume file."""
    try:
        from services.resume_parser_saas import parse_resume_text
        from services.resume_analysis_enhanced import ResumeTextExtractor
        
        # Extract text using the same method as analyzer
        text, _ = ResumeTextExtractor.extract_from_file(file_path)
        if not text:
            return []
        
        # Try parsing for skills
        try:
            parsed = parse_resume_text(text)
            return parsed.get('skills', [])
        except:
            # Fallback: look for common skill keywords
            common_skills = [
                'python', 'javascript', 'java', 'c++', 'sql', 'react', 'node',
                'html', 'css', 'git', 'aws', 'docker', 'kubernetes', 'api',
                'database', 'linux', 'typescript', 'golang', 'rust', 'mongodb'
            ]
            text_lower = text.lower()
            found_skills = [skill for skill in common_skills if skill in text_lower]
            return found_skills[:10]  # Return top 10
    except:
        return []


def extract_education_from_resume(file_path):
    """Extract education details from resume."""
    try:
        from services.resume_analysis_enhanced import ResumeTextExtractor
        
        text, _ = ResumeTextExtractor.extract_from_file(file_path)
        if not text:
            return []
        
        # Look for common education keywords
        text_lower = text.lower()
        education = []
        
        education_keywords = [
            'bachelor', 'master', 'mba', 'phd', 'diploma', 'certificate',
            'bs in', 'ba in', 'ms in', 'ma in'
        ]
        
        for keyword in education_keywords:
            if keyword in text_lower:
                education.append(keyword.title())
        
        return education[:3]  # Return top 3
    except:
        return []


def generate_ats_strengths(analysis):
    """Generate user-friendly ATS strengths from analysis."""
    strengths = []
    
    # Check ATS score
    ats_score = analysis.get('ats_score', 0)
    if ats_score >= 80:
        strengths.append("Strong ATS compatibility - resume is well-structured")
    elif ats_score >= 60:
        strengths.append("Good ATS score - but could be improved")
    
    # Check keyword score
    keyword_score = analysis.get('keyword_score', 0)
    if keyword_score >= 80:
        strengths.append("Excellent keyword density for ATS parsing")
    
    # Check section count
    section_count = analysis.get('section_count', 0)
    if section_count >= 4:
        strengths.append(f"Well-organized with {section_count} clear sections")
    
    # Check content quality
    content_quality = analysis.get('content_quality', 0)
    if content_quality >= 70:
        strengths.append("Good use of metrics and quantified results")
    
    # Default if no other strengths
    if not strengths:
        strengths.append("Resume successfully analyzed")
    
    return strengths
