"""Generates personalized learning roadmaps based on user profile data."""


# Skill-to-roadmap mapping. Each key maps to a structured learning path
# with phases, durations, and XP. This is the reference data;
# the actual roadmap is built from the USER's profile skills + goals.
SKILL_PATHS = {
    'Python': [
        {'title': 'Python Fundamentals', 'description': 'Variables, loops, functions, OOP concepts, file handling.', 'duration': '4 weeks', 'xp': 200},
        {'title': 'Data Structures with Python', 'description': 'Lists, dicts, sets, queues, stacks with real-world applications.', 'duration': '3 weeks', 'xp': 180},
        {'title': 'Web Backend with Flask/Django', 'description': 'Build REST APIs, authentication, databases.', 'duration': '6 weeks', 'xp': 300},
    ],
    'JavaScript': [
        {'title': 'JavaScript Essentials', 'description': 'ES6+, async/await, DOM manipulation, event handling.', 'duration': '4 weeks', 'xp': 200},
        {'title': 'React Fundamentals', 'description': 'Components, hooks, state management, routing.', 'duration': '5 weeks', 'xp': 250},
        {'title': 'Full-Stack Web Development', 'description': 'React + Node.js + MongoDB complete stack.', 'duration': '8 weeks', 'xp': 400},
    ],
    'React': [
        {'title': 'React Core Concepts', 'description': 'JSX, Components, Props, State, Lifecycle.', 'duration': '3 weeks', 'xp': 150},
        {'title': 'Advanced React & State Management', 'description': 'Redux, Context API, performance optimization.', 'duration': '4 weeks', 'xp': 200},
        {'title': 'React Production Apps', 'description': 'Testing, error boundaries, deployment strategies.', 'duration': '3 weeks', 'xp': 150},
    ],
    'Java': [
        {'title': 'Java Fundamentals', 'description': 'Object-oriented programming, classes, inheritance, polymorphism.', 'duration': '4 weeks', 'xp': 200},
        {'title': 'Java Collections & Data Structures', 'description': 'Lists, Maps, Sets, Streams API for practical applications.', 'duration': '3 weeks', 'xp': 180},
        {'title': 'Spring Boot & Backend Development', 'description': 'Build scalable REST services with Spring Framework.', 'duration': '6 weeks', 'xp': 300},
    ],
    'SQL': [
        {'title': 'SQL Fundamentals', 'description': 'SELECT, JOIN, GROUP BY, subqueries, indexes.', 'duration': '3 weeks', 'xp': 150},
        {'title': 'Advanced SQL & Database Design', 'description': 'Normalization, transactions, optimization.', 'duration': '3 weeks', 'xp': 150},
        {'title': 'Database Administration', 'description': 'Backup, security, performance tuning.', 'duration': '2 weeks', 'xp': 100},
    ],
    'Machine Learning': [
        {'title': 'ML Fundamentals', 'description': 'Supervised learning, regression, classification basics.', 'duration': '5 weeks', 'xp': 250},
        {'title': 'Deep Learning Introduction', 'description': 'Neural networks, TensorFlow, Keras fundamentals.', 'duration': '6 weeks', 'xp': 300},
        {'title': 'Advanced ML Projects', 'description': 'NLP, Computer Vision, GANs practical implementation.', 'duration': '8 weeks', 'xp': 400},
    ],
    'Node.js': [
        {'title': 'Node.js Fundamentals', 'description': 'Event loop, modules, async/await, file system operations.', 'duration': '3 weeks', 'xp': 150},
        {'title': 'Express.js & REST APIs', 'description': 'Build robust web servers and RESTful APIs with Express.', 'duration': '4 weeks', 'xp': 200},
        {'title': 'Full-Stack JavaScript', 'description': 'Combine Node.js backend with React frontend for complete applications.', 'duration': '6 weeks', 'xp': 300},
    ],
    'UI/UX Design': [
        {'title': 'Design Fundamentals', 'description': 'Color theory, typography, principles of good UI/UX design.', 'duration': '4 weeks', 'xp': 180},
        {'title': 'Wireframing & Prototyping', 'description': 'Create user flows, wireframes, and interactive prototypes.', 'duration': '3 weeks', 'xp': 150},
        {'title': 'Design Tools Mastery', 'description': 'Figma, Adobe XD, and design systems for professional projects.', 'duration': '4 weeks', 'xp': 200},
    ],
    'DSA': [
        {'title': 'Arrays & Strings', 'description': 'Master fundamental data structures and string manipulation techniques.', 'duration': '3 weeks', 'xp': 150},
        {'title': 'Trees, Graphs & Advanced Structures', 'description': 'Complex data structures for interview preparation.', 'duration': '4 weeks', 'xp': 200},
        {'title': 'Algorithm Design Patterns', 'description': 'Dynamic programming, greedy, divide-and-conquer strategies.', 'duration': '5 weeks', 'xp': 250},
    ],
    'Git / GitHub': [
        {'title': 'Git Basics', 'description': 'Version control fundamentals, commits, branches, merging.', 'duration': '2 weeks', 'xp': 100},
        {'title': 'Collaborative Workflows', 'description': 'Pull requests, code review, conflict resolution, team collaboration.', 'duration': '2 weeks', 'xp': 100},
        {'title': 'Advanced Git & DevOps', 'description': 'Rebasing, cherry-picking, CI/CD pipelines with GitHub Actions.', 'duration': '3 weeks', 'xp': 150},
    ],
    'Git/GitHub': [
        {'title': 'Git Basics', 'description': 'Version control fundamentals, commits, branches, merging.', 'duration': '2 weeks', 'xp': 100},
        {'title': 'Collaborative Workflows', 'description': 'Pull requests, code review, conflict resolution, team collaboration.', 'duration': '2 weeks', 'xp': 100},
        {'title': 'Advanced Git & DevOps', 'description': 'Rebasing, cherry-picking, CI/CD pipelines with GitHub Actions.', 'duration': '3 weeks', 'xp': 150},
    ],
    'Communication': [
        {'title': 'Technical Writing', 'description': 'Write clear documentation, READMEs, technical blog posts.', 'duration': '2 weeks', 'xp': 100},
        {'title': 'Presentation Skills', 'description': 'Pitch ideas, present technical concepts, public speaking.', 'duration': '3 weeks', 'xp': 150},
        {'title': 'Professional Communication', 'description': 'Email etiquette, conflict resolution, stakeholder management.', 'duration': '2 weeks', 'xp': 100},
    ],
    'Leadership': [
        {'title': 'Leadership Fundamentals', 'description': 'Team dynamics, motivation, decision-making as a leader.', 'duration': '3 weeks', 'xp': 150},
        {'title': 'Project Management', 'description': 'Agile, Scrum, planning and execution of technical projects.', 'duration': '4 weeks', 'xp': 200},
        {'title': 'Strategic Thinking', 'description': 'Vision setting, delegation, building high-performance teams.', 'duration': '3 weeks', 'xp': 150},
    ],
}

# Goal-based capstone items appended to the roadmap
GOAL_CAPSTONES = {
    'Get a job': {'title': 'Job Application Sprint', 'description': 'Interview prep, resume optimization, portfolio polish, and strategic applications.', 'duration': '4 weeks', 'xp': 350},
    'Land internship': {'title': 'Internship Preparation', 'description': 'Craft targeted applications, practice behavioral interviews, and build a portfolio.', 'duration': '3 weeks', 'xp': 300},
    'Build startup': {'title': 'Startup MVP Development', 'description': 'Validate idea, build MVP, create pitch deck, and approach investors.', 'duration': '8 weeks', 'xp': 500},
    'Freelance': {'title': 'Freelance Launch Plan', 'description': 'Set up portfolio, find clients, price services, and deliver first project.', 'duration': '4 weeks', 'xp': 350},
    'Higher studies': {'title': 'Graduate School Preparation', 'description': 'Research programs, prepare applications, write SOP, and collect recommendations.', 'duration': '6 weeks', 'xp': 400},
    'Switch career': {'title': 'Career Transition Plan', 'description': 'Identify transferable skills, fill gaps, rebrand yourself, and target new roles.', 'duration': '6 weeks', 'xp': 400},
    'Open source': {'title': 'Open Source Contributor', 'description': 'Find projects, make meaningful contributions, build reputation in the community.', 'duration': '4 weeks', 'xp': 300},
    'Research': {'title': 'Research Project Kickoff', 'description': 'Choose a research topic, study literature, plan experiments, and write a paper.', 'duration': '8 weeks', 'xp': 450},
}


def generate_roadmap(profile_data, stats=None):
    """Build a phased learning roadmap from the user's skills and goals."""
    skills = profile_data.get('skills', [])
    goals = profile_data.get('goals', [])
    interests = profile_data.get('interests', [])
    phase = profile_data.get('phase', 'college')
    daily_time = int(profile_data.get('daily_time', 1))
    
    experience_level = _infer_experience_level(phase, stats)
    
    # If no skills, return guidance
    if not skills:
        return [{
            'phase': 'Getting Started',
            'title': 'Complete Your Profile',
            'description': 'Tell us about your skills, interests, and goals to unlock your personalized roadmap.',
            'duration': '5 minutes',
            'steps': [{
                'title': 'Complete Profile',
                'description': 'Share your skills, interests, and career goals',
                'duration': 'Now',
                'xp': 50
            }]
        }]
    
    # Build structured roadmap with phases
    roadmap_phases = []
    
    # PHASE 1: FOUNDATION
    foundation_steps = _build_foundation_phase(skills, experience_level, daily_time)
    if foundation_steps:
        roadmap_phases.append({
            'phase': 'Foundation',
            'title': 'Master the Fundamentals',
            'description': f'Build strong basics in your primary skill ({skills[0]})',
            'duration': '4-6 weeks',
            'steps': foundation_steps
        })
    
    # PHASE 2: GROWTH
    growth_steps = _build_growth_phase(skills, goals, experience_level, daily_time)
    if growth_steps:
        roadmap_phases.append({
            'phase': 'Growth',
            'title': 'Expand Your Capabilities',
            'description': 'Apply skills to real projects and expand into complementary areas',
            'duration': '6-10 weeks',
            'steps': growth_steps
        })
    
    # PHASE 3: ADVANCED (for mid/senior or those with goals)
    if goals or experience_level in ['mid', 'senior']:
        advanced_steps = _build_advanced_phase(skills, goals, experience_level)
        if advanced_steps:
            roadmap_phases.append({
                'phase': 'Advanced',
                'title': 'Reach Professional Level',
                'description': 'Specialized skills, production readiness, and domain expertise',
                'duration': '4-8 weeks',
                'steps': advanced_steps
            })
    
    # PHASE 4: SPECIALIZATION (if clear goals)
    if goals:
        spec_steps = _build_specialization_phase(goal_list=goals)
        if spec_steps:
            roadmap_phases.append({
                'phase': 'Specialization',
                'title': f'Achieve Your Goal: {goals[0]}',
                'description': 'Targeted preparation for your specific career objective',
                'duration': '3-6 weeks',
                'steps': spec_steps
            })
    
    # Ensure at least 1 phase
    if not roadmap_phases:
        roadmap_phases = [{
            'phase': 'Foundation',
            'title': 'Start Your Journey',
            'description': 'Begin with fundamentals in your selected skill',
            'duration': '1-2 months',
            'steps': [{
                'title': 'Learn & Practice',
                'description': 'Complete foundational tutorials and exercises',
                'duration': '2-3 weeks',
                'xp': 200
            }]
        }]
    
    return roadmap_phases


def _infer_experience_level(phase, stats):
    """Map phase + stats to entry/mid/senior."""
    if stats:
        xp = stats.get('total_xp', 0)
        tasks = stats.get('tasks_completed', 0)
        
        if xp > 5000 or tasks > 50:
            return 'senior'
        elif xp > 1000 or tasks > 20:
            return 'mid'
    
    # Map phase to level
    phase_to_level = {
        'pre-college': 'entry',
        'college': 'entry',
        'post-college': 'mid',
    }
    return phase_to_level.get(phase, 'entry')


def _build_foundation_phase(skills, experience_level, daily_time):
    """First steps for the user's primary skill."""
    if not skills:
        return []
    
    primary_skill = skills[0]
    skill_path = SKILL_PATHS.get(primary_skill, [])
    
    # For entry level, include first 1-2 steps
    # For mid/senior, include just essentials
    if experience_level == 'entry':
        steps = skill_path[:2] if len(skill_path) >= 2 else skill_path[:1]
    else:
        # Mid/senior can skip basics
        steps = skill_path[1:2] if len(skill_path) > 1 else []
    
    if not steps:
        # Fallback
        steps = [{
            'title': f'{primary_skill} Fundamentals',
            'description': f'Learn core concepts and practical basics of {primary_skill}',
            'duration': '3-4 weeks',
            'xp': 200
        }]
    
    return steps


def _build_growth_phase(skills, goals, experience_level, daily_time):
    """Intermediate steps: apply skills and branch out."""
    steps = []
    
    # 1. Deep dive into primary skill (if not entry level)
    if experience_level != 'entry' and SKILL_PATHS.get(skills[0]):
        path = SKILL_PATHS.get(skills[0])
        if len(path) > 1:
            steps.append(dict(path[1]))  # Add 2nd step of primary skill
    
    # 2. Add a secondary skill if available
    if len(skills) > 1:
        secondary_skill = skills[1]
        secondary_path = SKILL_PATHS.get(secondary_skill, [])
        if secondary_path:
            steps.append(dict(secondary_path[0]))  # First step of secondary skill
    
    # 3. Add portfolio/project building
    steps.append({
        'title': 'Build 2 Portfolio Projects',
        'description': 'Create real projects using your skills. Focus on quality over quantity.',
        'duration': '3-4 weeks',
        'xp': 300
    })
    
    # 4. Practice via challenges
    steps.append({
        'title': 'Skill Challenges & Practice',
        'description': 'Complete coding challenges, design exercises, or domain-specific tasks',
        'duration': '2-3 weeks',
        'xp': 250
    })
    
    return steps


def _build_advanced_phase(skills, goals, experience_level):
    """Production-level mastery and system design."""
    if experience_level not in ['mid', 'senior']:
        return []
    
    steps = []
    primary_skill = skills[0]
    
    # Advanced path for primary skill
    skill_path = SKILL_PATHS.get(primary_skill, [])
    if len(skill_path) > 2:
        steps.append(dict(skill_path[2]))  # Add 3rd step of primary skill
    
    # Production readiness
    steps.append({
        'title': 'Production-Ready Code',
        'description': 'Learn testing, debugging, optimization, documentation for production',
        'duration': '2-3 weeks',
        'xp': 200
    })
    
    # System design / architecture
    if primary_skill in ['Python', 'Java', 'JavaScript', 'Node.js']:
        steps.append({
            'title': 'System Design & Architecture',
            'description': 'Design scalable systems, understand trade-offs, plan for scale',
            'duration': '3-4 weeks',
            'xp': 250
        })
    
    return steps


def _build_specialization_phase(goal_list=None):
    """Goal-specific capstone steps."""
    if not goal_list:
        return []
    
    primary_goal = goal_list[0]
    capstone = GOAL_CAPSTONES.get(primary_goal)
    
    if capstone:
        return [{
            'title': capstone['title'],
            'description': capstone['description'],
            'duration': capstone['duration'],
            'xp': capstone['xp']
        }]
    
    return []




def calculate_skill_gaps(profile_data, resume_data=None):
    """Return skills the user is missing for their chosen goals."""
    skills = set(s.lower() for s in profile_data.get('skills', []))
    goals = profile_data.get('goals', [])

    # Skills commonly needed for each goal
    goal_skill_requirements = {
        'Get a job': {'dsa', 'git / github', 'communication'},
        'Land internship': {'dsa', 'git / github', 'communication'},
        'Build startup': {'leadership', 'communication', 'ui/ux design'},
        'Freelance': {'communication', 'ui/ux design', 'git / github'},
        'Higher studies': {'communication', 'machine learning'},
        'Switch career': {'communication', 'leadership'},
    }

    required = set()
    for goal in goals:
        required.update(goal_skill_requirements.get(goal, set()))

    gaps = required - skills

    return list(gaps)
