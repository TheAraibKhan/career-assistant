"""
Career Mentor Service - Provides contextual career guidance and industry insights.
Uses Groq API for fast, reliable LLM responses.
"""

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
from database.models import insert_chat_message, get_user_chat_history, track_chatbot_analytics
from datetime import datetime
import traceback

# Initialize Groq client
client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        print(f"Groq initialized with model: {GROQ_MODEL}")
    except Exception as e:
        print(f"Failed to initialize Groq: {e}")
        client = None
else:
    print("GROQ_API_KEY not configured")

# System prompt for chatbot
SYSTEM_PROMPT = """You are a career mentor with experience in tech, data science, design, and product.

You help people navigate career decisions, build skills, and understand role requirements.

Your guidance:
- Stay specific. Reference their actual context (skills, experience level, interest).
- Explain your thinking. Users want to understand why, not just what.
- Be actionable. Provide concrete next steps, realistic timelines, and specific resources.
- Be honest. Acknowledge tradeoffs and realistic constraints.
- Keep it concise. Use clear formatting, under 250 words per response.

When discussing:
- Role recommendations: Explain why it fits their background and what's next.
- Skill development: Prioritize skills, estimate learning time, suggest resources.
- Timelines: Be realistic about how long transitions take based on effort.
- Career switches: Show adjacent roles and skill bridges.
- Resume/interview: Give specific, actionable feedback.

Remember: You're helping real people with real decisions. Be thoughtful and grounded."""


def build_context_prompt(user_context: dict) -> str:
    """
    Build a contextual prompt that personalizes chatbot responses.
    
    Args:
        user_context: Dictionary with user profile info
    
    Returns:
        Formatted context string for system prompt
    """
    if not user_context:
        return ""
    
    context_parts = []
    
    # Build user profile context
    if user_context.get('name'):
        context_parts.append(f"User: {user_context.get('name')}")
    
    if user_context.get('interest'):
        context_parts.append(f"Career Interest: {user_context.get('interest')}")
    
    if user_context.get('level'):
        context_parts.append(f"Experience Level: {user_context.get('level')}")
    
    if user_context.get('known_skills'):
        context_parts.append(f"Current Skills: {user_context.get('known_skills')}")
    
    if user_context.get('missing_skills'):
        context_parts.append(f"Skills to Develop: {user_context.get('missing_skills')}")
    
    if user_context.get('readiness_score') is not None:
        context_parts.append(f"Readiness Score: {user_context.get('readiness_score')}%")
    
    if user_context.get('confidence_score') is not None:
        context_parts.append(f"Role Confidence: {user_context.get('confidence_score')}%")
    
    if user_context.get('recommended_role'):
        context_parts.append(f"Recommended Role: {user_context.get('recommended_role')}")
    
    if not context_parts:
        return ""
    
    return f"""
USER CONTEXT:
{chr(10).join('- ' + part for part in context_parts)}

INSTRUCTIONS:
- Reference this specific context in your response
- Provide personalized, actionable advice based on their level and skills
- Be realistic about timelines and effort required
"""


def generate_chat_response(user_id: str, user_message: str, user_context: dict = None) -> dict:
    """
    Generate a contextual chatbot response using Groq Free API.
    
    Args:
        user_id: Unique identifier for the user (for SaaS tracking)
        user_message: The user's message
        user_context: Optional context about the user (name, career interest, level, etc.)
    
    Returns:
        dict with 'success', 'message', 'error' keys
    """
    try:
        if not GROQ_API_KEY or not client:
            return {
                'success': False,
                'message': None,
                'error': 'Groq API key not configured. Get your FREE key at https://console.groq.com'
            }

        # Validate input
        validation = validate_user_message(user_message)
        if not validation['valid']:
            return {
                'success': False,
                'message': None,
                'error': validation['error']
            }

        # Build personalized system prompt
        context_prompt = build_context_prompt(user_context)
        full_system_prompt = SYSTEM_PROMPT + context_prompt

        # Get recent conversation history for context (last 8 messages = 4 exchanges)
        chat_history = get_user_chat_history(user_id, limit=8)
        
        # Build messages for Groq chat API
        messages = [
            {"role": "system", "content": full_system_prompt}
        ]
        
        # Add previous messages for context
        for msg in chat_history:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Call Groq API with optimized settings
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
            top_p=0.9
        )

        bot_message = response.choices[0].message.content if response.choices else "I couldn't generate a response. Please try again."

        # Log conversation for analytics
        insert_chat_message(user_id, 'user', user_message)
        insert_chat_message(user_id, 'assistant', bot_message)
        
        # Track analytics
        track_chatbot_analytics(
            user_id=user_id,
            message_type='user_query',
            metadata={
                'has_context': bool(user_context),
                'context_keys': list(user_context.keys()) if user_context else [],
                'model': GROQ_MODEL
            }
        )

        return {
            'success': True,
            'message': bot_message,
            'error': None
        }

    except Exception as e:
        print(f"Chatbot error: {e}")
        traceback.print_exc()
        
        track_chatbot_analytics(
            user_id=user_id,
            message_type='error',
            metadata={'error': str(e)}
        )
        
        return {
            'success': False,
            'message': None,
            'error': 'Unable to generate response. Please try again.'
        }


def get_guidance_message(topic: str = None) -> str:
    """Get contextual guidance messages from the mentor."""
    messages = {
        'greeting': "Hi. I'm here to help you think through your career path. I can help you understand your recommended role, work through skill gaps, or discuss what comes next. What would be helpful?",
        'skill_gap': "Let's break down your skill gaps. I'll show you what to prioritize, realistic timelines, and specific resources. Start with high-impact skills first.",
        'motivation': "Career progress comes from understanding the path clearly. You've already identified your gaps—that's key. Let's build a concrete plan with near-term wins and longer-term goals.",
        'readiness': "Your readiness score reflects where you stand now. I can help identify which skills have the most impact, quick wins you can pursue in the next few weeks, and the longer-term investments.",
        'interview': "Interview success comes from being able to articulate your experience clearly. Let's work on how to frame your background in ways that matter for this role.",
        'next_steps': "What would help most right now? Understanding the role better, building specific skills, or planning your transition timeline?"
    }
    return messages.get(topic, messages['greeting'])


def get_follow_up_suggestions(user_context: dict = None) -> list:
    """
    Generate follow-up suggestions based on user context.
    
    Args:
        user_context: User profile context
    
    Returns:
        List of suggested questions the user might ask
    """
    suggestions = [
        "Why was this role recommended?",
        "What skills should I focus on?",
        "How long does this transition take?",
        "What's my readiness compared to the role?",
        "What should I learn in the next 90 days?",
        "Are there adjacent roles to consider?"
    ]
    
    # Add context-specific suggestions
    if user_context:
        if user_context.get('readiness_score'):
            score = user_context.get('readiness_score')
            if score < 50:
                suggestions.insert(0, "I'm early in my career. What's a realistic path?")
        
        if user_context.get('confidence_score'):
            conf = user_context.get('confidence_score')
            if conf < 70:
                suggestions.insert(0, "Am I well-suited for this role?")
    
    return suggestions[:4]  # Return top 4 suggestions


def validate_user_message(message: str) -> dict:
    """
    Validate and sanitize user input.
    
    Returns:
        dict with 'valid' and 'error' keys
    """
    if not message or not message.strip():
        return {'valid': False, 'error': 'Message cannot be empty'}
    
    if len(message) > 2000:
        return {'valid': False, 'error': 'Message is too long (max 2000 characters)'}
    
    if len(message) < 2:
        return {'valid': False, 'error': 'Message is too short (min 2 characters)'}
    
    return {'valid': True, 'error': None}
