"""AI Chatbot service using free API."""
import os
import requests
from datetime import datetime

# Try to use Groq (free tier) or fallback to simple rules
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GROQ_MODEL = os.environ.get('GROQ_MODEL', 'mixtral-8x7b-32768')

# Fallback career advice database
CAREER_KNOWLEDGE_BASE = {
    'machine learning': {
        'skills': ['Python', 'Statistics', 'Deep Learning', 'Data Preprocessing'],
        'resources': ['Fast.ai', 'Coursera ML', 'DeepLearning.AI', 'Kaggle'],
        'next_steps': 'Build portfolio projects, contribute to open source ML repos'
    },
    'web development': {
        'skills': ['HTML/CSS', 'JavaScript', 'React/Vue', 'Backend Framework', 'Databases'],
        'resources': ['FreeCodeCamp', 'MDN Docs', 'The Odin Project', 'Frontend Masters'],
        'next_steps': 'Build 3-5 portfolio projects, contribute to open source'
    },
    'data science': {
        'skills': ['Python', 'SQL', 'Statistics', 'Data Visualization', 'Machine Learning'],
        'resources': ['DataCamp', 'Kaggle', 'Towards Data Science', 'Mode Analytics'],
        'next_steps': 'Participate in Kaggle competitions, build analysis projects'
    },
    'devops': {
        'skills': ['Linux', 'Docker', 'Kubernetes', 'CI/CD', 'Cloud Platforms'],
        'resources': ['Linux Academy', 'KodeKloud', 'CloudAcademy', 'Docker Docs'],
        'next_steps': 'Set up your own infrastructure, get cloud certifications'
    },
    'ui/ux': {
        'skills': ['Design Thinking', 'Figma/Adobe XD', 'User Research', 'Prototyping', 'CSS'],
        'resources': ['Nielsen Norman Group', 'Interaction Design Foundation', 'Figma Tutorials'],
        'next_steps': 'Build design portfolio, conduct user research projects'
    }
}

def get_groq_response(message, context):
    """Get response from Groq API (free tier)."""
    if not GROQ_API_KEY:
        return None
    
    try:
        system_prompt = """You are an expert career advisor helping professionals grow their careers. 
        Be concise, actionable, and supportive. Focus on practical advice.
        
        User context:
        - Interest: {}
        - Level: {}
        - Known Skills: {}
        
        Provide helpful career guidance, skill recommendations, and actionable next steps.
        """.format(
            context.get('interest', 'Not specified'),
            context.get('level', 'Not specified'),
            ', '.join(context.get('known_skills', []))
        )
        
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': GROQ_MODEL,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': message}
                ],
                'max_tokens': 300,
                'temperature': 0.7
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        
    except Exception as e:
        print(f"Groq API error: {e}")
    
    return None

def get_fallback_response(message, context):
    """Provide fallback responses using rule-based system."""
    message_lower = message.lower()
    interest = context.get('interest', '').lower()
    
    # Career-specific responses
    if 'skill' in message_lower and interest in CAREER_KNOWLEDGE_BASE:
        kb = CAREER_KNOWLEDGE_BASE[interest]
        return f"For {interest}, focus on these core skills: {', '.join(kb['skills'])}. " \
               f"Great resources: {', '.join(kb['resources'])}."
    
    elif 'resume' in message_lower:
        return "To improve your resume: 1) Add quantified achievements 2) Include relevant keywords " \
               "3) Show measurable impact 4) Keep it to 1 page 5) Tailor for each role."
    
    elif 'project' in message_lower:
        return "Building projects is essential! Start with: 1) Small, focused projects 2) Real problems " \
               "you want to solve 3) Publish on GitHub 4) Document your process 5) Include in portfolio."
    
    elif 'interview' in message_lower:
        return "Ace your interviews: 1) Practice STAR method 2) Prepare for technical questions " \
               "3) Ask thoughtful questions 4) Research the company 5) Do mock interviews beforehand."
    
    elif 'learning' in message_lower or 'learn' in message_lower:
        return "Best learning approach: 1) Start with fundamentals 2) Practice consistently 3) Build projects " \
               "4) Join communities 5) Teach others what you learn."
    
    elif 'next' in message_lower or 'next step' in message_lower:
        if interest in CAREER_KNOWLEDGE_BASE:
            return f"Your next steps: {CAREER_KNOWLEDGE_BASE[interest]['next_steps']}"
        return "1) Identify your goal 2) Learn required skills 3) Build portfolio 4) Network 5) Apply to roles"
    
    elif 'salary' in message_lower or 'compensation' in message_lower:
        return "Salary ranges vary by: location, experience, company size, and market demand. " \
               "Research on Glassdoor, Levels.fyi, and Blind for accurate data."
    
    elif 'career' in message_lower or 'path' in message_lower:
        return "A strong career path: 1) Build strong fundamentals 2) Specialize in a niche 3) Gain leadership experience " \
               "4) Network continuously 5) Stay updated with trends."
    
    else:
        return "I can help you with career advice, skill development, resume improvement, interview prep, " \
               "and career planning. What would you like to know more about?"

def get_chatbot_response(message, context):
    """Get chatbot response with fallback mechanism."""
    # Try Groq first
    response = get_groq_response(message, context)
    
    # Fallback to rule-based system
    if not response:
        response = get_fallback_response(message, context)
    
    return response

def get_chat_context():
    """Get context-aware chat information."""
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'features_available': [
            'Career advice',
            'Skill recommendations',
            'Resume tips',
            'Interview prep',
            'Career planning'
        ]
    }