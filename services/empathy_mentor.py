"""Career mentor service - provides personalized guidance based on user context."""
from services.user_experience import PersonalizationEngine


class CareerMentor:
    """Career guidance service with personalized mentorship."""
    
    @staticmethod
    def get_system_prompt(user_context):
        """Generate system prompt based on user situation and confidence level."""
        
        style = user_context.get('communication_style', 'professional')
        pace = user_context.get('learning_pace', 'moderate')
        goal = user_context.get('goal_focus', 'career advancement')
        confidence = user_context.get('confidence_score', 50)
        
        base_prompt = """You are a career mentor. Help people with job transitions, skill development, and career planning."""
        
        # Adjust tone based on confidence level
        if confidence < 40:
            tone_layer = """
The person is uncertain about their career. Focus on:
- Validating concerns ("This is a common challenge")
- Breaking goals into concrete steps
- Acknowledging progress made so far
- Building confidence through small wins
- Realistic timelines
"""
        elif confidence < 70:
            tone_layer = """
The person is building confidence. Focus on:
- Recognizing progress and growth
- Leveraging existing strengths
- Practical next steps
- Evidence of their capability
- Clear milestones
"""
        else:
            tone_layer = """
The person is ready for strategic work. Focus on:
- Long-term career planning
- Complex career decisions
- Industry trends and opportunities
- Leadership development
- Major transitions
"""
        
        # Add communication style
        style_guidance = {
            'professional': 'Be direct and practical. Focus on actionable advice.',
            'friendly': 'Be conversational and approachable. Use simple language.',
            'detailed': 'Provide context and reasoning. Explain the "why" behind advice.',
            'technical': 'Be precise. Provide concrete details and depth.'
        }[style]
        
        pace_guidance = {
            'slow': 'Build from fundamentals. Use analogies and examples.',
            'moderate': 'Balance foundation and progression. Move steadily.',
            'fast': 'Assume some knowledge. Focus on advancement quickly.'
        }[pace]
        
        # Realistic guidance
        realistic_guidance = """
KEY PRINCIPLES:
- Be honest about timelines. If it takes 6 months, say so.
- Acknowledge real barriers without dismissing them.
- Suggest legitimate alternatives when the direct path isn't feasible.
- Explain WHY decisions matter, not just WHAT to do.
- Admit uncertainty. Don't guess about job market data.
- Use specific examples from real careers.
- Help them see transferable skills they may not realize they have.
"""
        
        # Combine into full prompt
        full_prompt = f"""{base_prompt}

{tone_layer}

STYLE: {style_guidance}

PACE: {pace_guidance}

{realistic_guidance}

When responding:
1. Understand their situation
2. Provide specific next steps
3. Show how this fits their bigger picture
4. Offer alternatives and choices
5. Be encouraging and realistic

Keep responses under 250 words. Treat them as a professional adult.
"""
        
        return full_prompt
    
    @staticmethod
    def add_encouragement(response_text, user_metrics):
        """Add encouragement based on user progress level."""
        
        readiness = user_metrics.get('readiness_score', 50)
        
        encouragements = {
            'strong': [
                "You're on the right track.",
                "This is solid thinking.",
                "You're making real progress.",
                "This shows good self-awareness.",
                "You're building momentum.",
            ],
            'moderate': [
                "You're building a good foundation.",
                "Progress looks solid - keep going.",
                "This is a good approach.",
                "You're moving in the right direction.",
                "This is practical and achievable.",
            ],
            'early': [
                "Good question. That shows you're thinking ahead.",
                "This is exactly what you should be learning.",
                "Good foundation to start with.",
                "The fact that you're asking shows initiative.",
                "You're off to a solid start.",
            ]
        }
        
        # Select level
        if readiness > 70:
            level = 'strong'
        elif readiness > 40:
            level = 'moderate'
        else:
            level = 'early'
        
        import random
        encouragement = random.choice(encouragements[level])
        
        return f"{encouragement}\n\n{response_text}"
    
    @staticmethod
    def generate_followup_questions(user_metrics):
        """Generate contextual follow-up questions."""
        
        interest = user_metrics.get('interest', '')
        level = user_metrics.get('level', '')
        known_skills = user_metrics.get('known_skills', '')
        missing_skills = user_metrics.get('missing_skills', '')
        
        followups = []
        
        # Career-focused follow-ups
        if interest:
            followups.append(f"What aspects of {interest} interest you most?")
            followups.append(f"How do you see yourself using {interest} skills?")
        
        # Skill-focused follow-ups
        if missing_skills:
            followups.append("Which gap would you like to tackle first?")
            followups.append("What's stopping you from learning these skills right now?")
        
        # Timeline follow-ups
        if level == 'beginner':
            followups.append("What's your timeline for making this transition?")
            followups.append("Are you planning to learn full-time or part-time?")
        
        # Practical follow-ups
        followups.extend([
            "What resources do you have access to?",
            "How can I help you break this down into smaller steps?",
            "Would you like me to create a learning timeline?"
        ])
        
        return followups[:3]  # Return top 3


class MentorshipJourney:
    """Track user's career journey and celebrate milestones."""
    
    @staticmethod
    def get_journey_status(user_id):
        """Get user's current position in their career journey."""
        from database.db import get_db
        
        db = get_db()
        
        submission = db.execute('''
            SELECT readiness_score, confidence_score, created_at
            FROM submissions WHERE user_id = ? ORDER BY created_at DESC LIMIT 1
        ''', (user_id,)).fetchone()
        
        if not submission:
            return None
        
        readiness = submission['readiness_score'] or 0
        confidence = submission['confidence_score'] or 0
        
        journey_map = {
            'exploring': {
                'description': 'Exploring career options and building foundational knowledge',
                'readiness_range': (0, 30),
                'message': 'You are discovering what interests you. This is a good starting point.'
            },
            'building': {
                'description': 'Building skills and gaining confidence in your chosen path',
                'readiness_range': (30, 60),
                'message': 'You are making solid progress. Keep building on this foundation.'
            },
            'accelerating': {
                'description': 'Accelerating growth and filling final gaps',
                'readiness_range': (60, 85),
                'message': 'You are getting close. Time to accelerate your learning.'
            },
            'ready': {
                'description': 'Ready for the next step in your career',
                'readiness_range': (85, 100),
                'message': 'You are ready. Time to apply what you have learned.'
            }
        }
        
        current_stage = None
        for stage, info in journey_map.items():
            if info['readiness_range'][0] <= readiness <= info['readiness_range'][1]:
                current_stage = stage
                break
        
        return {
            'stage': current_stage,
            'readiness_score': readiness,
            'confidence_score': confidence,
            'stage_info': journey_map.get(current_stage, {}),
            'progress_to_next': readiness % 30,
            'boost_areas': get_confidence_boosts(confidence, readiness)
        }
    
    @staticmethod
    def get_motivational_message(stage, readiness, confidence):
        """Generate messages based on career stage."""
        
        messages = {
            'exploring': [
                "You are asking the right questions.",
                "Being intentional about your path is important.",
                "Every expert started in this phase."
            ],
            'building': [
                "Notice how far you have come already.",
                "You are developing real expertise.",
                "The challenges you face are building your skills."
            ],
            'accelerating': [
                "You are in an exciting phase where things are working.",
                "The skills you are developing will differentiate you.",
                "You are close to making that leap."
            ],
            'ready': [
                "You have done the work. You are ready.",
                "This is your moment.",
                "Go show what you are capable of."
            ]
        }
        
        import random
        return random.choice(messages.get(stage, ["You have got this."])) if stage else "You have got this."


def get_confidence_boosts(confidence_score, readiness_score):
    """Suggest ways to boost confidence based on current metrics."""
    
    if confidence_score < 40:
        return {
            'issue': 'Low confidence despite building skills',
            'suggestions': [
                'Complete small projects to build proof of competence',
                'Document your learning with before and after examples',
                'Find a peer or mentor to practice with',
                'Review past wins and challenges you have overcome'
            ]
        }
    elif confidence_score < readiness_score - 10:
        return {
            'issue': 'Skills ahead of confidence',
            'suggestions': [
                'Practice explaining your skills to others',
                'Apply to positions slightly above your comfort zone',
                'Join communities with similar learners',
                'Remember: everyone feels this way at this stage'
            ]
        }
    else:
        return {
            'issue': 'You are in sync. Well done.',
            'suggestions': ['Keep building', 'Push yourself slightly', 'Help others on similar paths']
        }

# Compatibility aliases
CareerChatbot = CareerMentor  # For backward compatibility