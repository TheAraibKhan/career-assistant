# Career chatbot service with rule-based responses
import requests
import json
from datetime import datetime
from database.models import insert_chat_message, get_chat_history
from database.db import get_db


class CareerChatbot:
    
    def __init__(self, user_id=None, session_id=None):
        self.user_id = user_id
        self.session_id = session_id or datetime.utcnow().isoformat()
    
    def build_context(self, user_context):
        if not user_context:
            return ""
        
        interest = user_context.get('interest', '')
        level = user_context.get('level', '')
        skills = user_context.get('skills', '')
        goal = user_context.get('goal', '')
        
        return f"User Context: {interest} ({level} level), Skills: {skills}, Goal: {goal}"
    
    def generate_response(self, user_message, user_context=None):
        # Validate input
        if not user_message or len(user_message.strip()) < 2:
            return {
                'response': "Could you provide more details? I'm here to help with your career questions.",
                'success': True
            }
        
        # Check for nonsense/gibberish (no letters)
        if not any(c.isalpha() for c in user_message):
            return {
                'response': "I didn't quite understand that. Try asking about careers, skills, resumes, or interviews.",
                'success': True
            }
        
        try:
            return self._get_response(user_message, user_context)
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                'response': "I encountered an error. Please rephrase your question and try again.",
                'success': True
            }
    

    
    def _get_response(self, user_message, user_context=None):
        message_lower = user_message.lower()
        
        interest = user_context.get('interest', '').lower() if user_context else ''
        level = user_context.get('level', '').lower() if user_context else ''
        skills = user_context.get('skills', '').lower() if user_context else ''
        
        if any(word in message_lower for word in ['what career', 'recommend', 'best for me', 'suitable']):
            return self._handle_career_recommendation(interest, level, skills)
        elif any(word in message_lower for word in ['improve', 'ready', 'prepare', 'readiness', 'gap']):
            return self._handle_readiness_question(interest, level, skills)
        elif any(word in message_lower for word in ['learn', 'study', 'course', 'skill', 'training']):
            return self._handle_learning_path(interest, level, skills)
        elif any(word in message_lower for word in ['salary', 'pay', 'income', 'money', 'cost']):
            return self._handle_salary_question(interest)
        elif any(word in message_lower for word in ['resume', 'cv', 'cover', 'application']):
            return self._handle_resume_question(interest)
        elif any(word in message_lower for word in ['interview', 'question', 'prepare', 'tips']):
            return self._handle_interview_question(interest)
        elif any(word in message_lower for word in ['switch', 'change', 'transition', 'pivot']):
            return self._handle_career_switch(interest, level, skills)
        else:
            return self._handle_general_question(message_lower)
    
    def _handle_career_recommendation(self, interest, level, skills):
        if not interest:
            return {
                'response': """To give you a great career recommendation, I need to know more about you. Could you tell me:
1. What industry interests you most? (Tech, Data, Design, Business, etc.)
2. What's your current level? (Beginner, Intermediate, Advanced)
3. What are your key skills?

Once I know these facts, I can guide you toward roles that match your profile.""",
                'success': True
            }
        
        response = f"""Based on your interest in {interest.title()} and {level} level:

**Immediate opportunities:**
- Look for entry to mid-level roles in {interest}
- Build 2-3 key technical or domain skills
- Create 1-2 projects for your portfolio

**Next steps:**
1. Take 1 focused online course (Udemy, Coursera)
2. Build a portfolio project
3. Apply to 5-10 matching roles
4. Network with people in your target field

Need help with a specific part of this plan?"""
        
        return {'response': response, 'success': True}
    
    def _handle_readiness_question(self, interest, level, skills):
        """Handle readiness and skill gap questions."""
        response = """To assess your career readiness, I need more specifics:

**Try running a career analysis** on our platform with:
- Your interest area
- Your current level
- Your skills

This will give you a **readiness score** and **specific skill gaps** to work on.

In the meantime:
- **For quick wins**: Focus on the top 3 skills your target role needs
- **For confidence**: Build 1 small project using new skills
- **For networking**: Connect with 2-3 people in your target role

What specific skills do you want to improve?"""
        
        return {
            'response': response,
            'success': True
        }
    
    def _handle_learning_path(self, interest, level, skills):
        """Handle learning and skill development questions."""
        response = f"""Here's a personalized learning path for **{interest.title() if interest else 'your career'}**:

**Week 1-2: Foundation**
- Take a free intro course (freeCodeCamp, Codecademy)
- Learn the fundamentals (2-3 hours/day)

**Week 3-4: Practice**
- Build small projects using what you learned
- Solve coding challenges or case studies

**Week 5-6: Portfolio**
- Build 1 substantial project
- Document your process and learnings

**Week 7-8: Apply**
- Update resume and LinkedIn
- Apply to 5-10 positions

**Resources:**
- Udemy, Coursera (free trials available)
- YouTube, freeCodeCamp
- Official documentation
- Community forums (Stack Overflow, Reddit)

Which of these steps do you want help with?"""
        
        return {
            'response': response,
            'success': True
        }
    
    def _handle_salary_question(self, interest):
        """Handle salary and compensation questions."""
        response = f"""Salary varies by:
- **Location** (SF pays 30-50% more than other US cities)
- **Experience** (entry: $50-70K, mid: $100-150K, senior: $150K+)
- **Company** (startups vs big tech vs smaller companies)
- **Role specifics** (specialized skills command more)

**General ranges for {interest.title() if interest else 'tech careers'}:**
- Entry level: $60-85K
- Mid-level (3-5 years): $100-150K  
- Senior (5+ years): $150-250K+

**Increase your salary:**
1. Build specialized skills (highest impact)
2. Gain 3-5 years of solid experience
3. Negotiate well (research market rates first)
4. Consider high-paying markets (SF, NYC, Seattle)

Want help building the skills that lead to higher pay?"""
        
        return {
            'response': response,
            'success': True
        }
    
    def _handle_resume_question(self, interest):
        """Handle resume and application questions."""
        response = """Here's how to make your resume stand out:

**Structure:**
- Contact info at top
- 2-3 key accomplishments/summary
- Experience (focus on impact, not tasks)
- Skills (be specific, not generic)
- Education

**Power tips:**
- Use numbers/metrics: "Increased X by 40%" not "improved performance"
- Show growth: Senior role showing leadership, not just tasks
- Tailor for each job (mirror their language)
- Quantify impact: "Saved $500K" vs "optimized process"

**What to avoid:**
- Typos or grammar errors
- Too long (keep to 1-2 pages)
- Generic descriptions
- Unrelated skills/experience

**Next steps:**
- Review job descriptions for keywords
- Reframe your experience to match
- Use the STAR method (Situation, Task, Action, Result)

Want help tailoring your resume for a specific role?"""
        
        return {
            'response': response,
            'success': True
        }
    
    def _handle_interview_question(self, interest):
        """Handle interview preparation."""
        response = """Here's a quick interview preparation guide:

**Before the interview:**
- Research the company thoroughly
- Prepare 3 success stories using STAR (Situation, Task, Action, Result)
- Know your resume inside and out
- Practice 5-10 common questions
- Prepare 2-3 thoughtful questions to ask them

**During the interview:**
- Be specific with examples
- Show enthusiasm about the role
- Ask about next steps
- Take notes (shows you're interested)
- Dress professionally

**Common questions to practice:**
1. "Tell me about yourself" (2 min summary)
2. "Why this role?" (align with their needs)
3. "Your biggest challenge?" (growth mindset answer)
4. "Where do you see yourself?" (ambition + reality)

**After:**
- Send thank you email within 24 hours
- Mention specific conversation points
- Reiterate interest

Which part would you like to dive deeper into?"""
        
        return {
            'response': response,
            'success': True
        }
    
    def _handle_career_switch(self, interest, level, skills):
        """Handle career transition questions."""
        response = f"""Switching careers is challenging but possible. Here's the playbook:

**Phase 1: Decide** (Week 1-2)
- Confirm the new career interests you
- Research salary, growth, demand
- Talk to 2-3 people in that role

**Phase 2: Build foundation** (Month 1-3)
- Take online course in new field
- Build 1-2 portfolio projects
- Start networking in that community

**Phase 3: Transition** (Month 3-6)
- Update resume/LinkedIn for new direction
- Apply to entry-level or "career switcher" roles
- Emphasize transferable skills
- Be ready to accept entry-level pay temporarily

**Phase 4: Succeed** (Month 6-12)
- Excel in new role
- Build reputation
- Acquire 1-2 specialist skills

**Key challenges:**
- May need to accept lower salary initially
- Build network in new field ASAP
- Focus on what transfers from old career

Your interest in **{interest.title() if interest else 'a new field'}** is a good start. What's your timeline?"""
        
        return {
            'response': response,
            'success': True
        }
    
    def _handle_general_question(self, message_lower):
        """Handle general career questions."""
        response = """I'm here to help with career guidance! I can assist with:

**Common topics:**
- Career recommendations (tell me your interests)
- Skill development and learning paths
- Resume and job application tips
- Interview preparation and techniques
- Salary insights and negotiation
- Career transitions and pivots
- Work-life balance and career satisfaction

**Try asking me:**
- "What career should I pursue?" (I'll ask about your interests)
- "How do I improve my skills?" (I'll suggest a path)
- "How to ace interviews?" (I'll give tactics)
- "Should I change careers?" (I'll help you decide)

What's your main career question today?"""
        
        return {
            'response': response,
            'success': True
        }
    
    def save_message(self, user_message, bot_response):
        """Save conversation to database."""
        if self.user_id and self.session_id:
            try:
                insert_chat_message(
                    user_id=self.user_id,
                    session_id=self.session_id,
                    message=user_message,
                    response=bot_response,
                    context=None
                )
            except Exception as e:
                print(f"Failed to save chat message: {e}")
    
    def get_conversation_history(self, limit=10):
        """Get recent conversation history."""
        if self.user_id and self.session_id:
            try:
                return get_chat_history(self.user_id, self.session_id, limit=limit)
            except:
                return []
        return []
