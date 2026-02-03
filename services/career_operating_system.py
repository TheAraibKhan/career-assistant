"""Career Operating System Service

Provides comprehensive career intelligence and guidance:
- Career Timeline tracking (Past → Present → Target)
- Resume Health Analysis (ATS score, section improvements)
- Skill Gap Intelligence (current vs required, learning priorities)
- Career Confidence Index (composite readiness score)
- Weekly Check-ins (progress tracking, reflections)
- Decision Support (Should I apply? Which skill next?)
"""

import json
from datetime import datetime, timedelta
from database.db import get_db


class CareerTimeline:
    """Manages career progression tracking."""
    
    @staticmethod
    def create_or_update(user_id, current_role, current_level, years_experience, 
                        target_role, target_level, timeline_months):
        """Create or update user's career timeline."""
        db = get_db()
        now = datetime.utcnow().isoformat()
        
        db.execute('''
            INSERT OR REPLACE INTO career_timeline 
            (user_id, current_role, current_level, years_experience, target_role, 
             target_level, timeline_months, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, current_role, current_level, years_experience, target_role,
              target_level, timeline_months, now, now))
        db.commit()
    
    @staticmethod
    def get_timeline(user_id):
        """Get user's career timeline."""
        db = get_db()
        row = db.execute(
            'SELECT * FROM career_timeline WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        
        if not row:
            return None
        
        cols = [description[0] for description in 
                db.execute('SELECT * FROM career_timeline LIMIT 0').description]
        return dict(zip(cols, row))


class ResumeHealthSystem:
    """Analyzes resume quality and provides improvement suggestions."""
    
    @staticmethod
    def calculate_scores(resume_text):
        """
        Calculate resume health scores.
        Returns: dict with ATS, keyword, formatting, completeness, overall scores.
        """
        if not resume_text or len(resume_text.strip()) == 0:
            return {
                'ats_score': 0,
                'keyword_score': 0,
                'formatting_score': 0,
                'completeness_score': 0,
                'overall_score': 0,
                'suggestions': ['Upload or paste your resume to get started']
            }
        
        scores = {}
        suggestions = []
        
        # ATS Score (keyword recognition, formatting)
        # Check for common ATS-friendly keywords
        ats_keywords = ['experience', 'skills', 'education', 'certification', 'achievement']
        keyword_count = sum(1 for kw in ats_keywords if kw.lower() in resume_text.lower())
        scores['ats_score'] = min(100, 40 + (keyword_count * 12))
        
        if scores['ats_score'] < 70:
            suggestions.append('Add more action verbs and quantified results')
        
        # Keyword Score (technical keywords, role-specific terms)
        tech_keywords = ['python', 'javascript', 'sql', 'aws', 'api', 'database', 
                        'project', 'team', 'led', 'managed', 'developed']
        tech_count = sum(1 for kw in tech_keywords if kw.lower() in resume_text.lower())
        scores['keyword_score'] = min(100, 30 + (tech_count * 7))
        
        if scores['keyword_score'] < 70:
            suggestions.append('Include more industry-specific keywords')
        
        # Formatting Score (length, structure)
        lines = resume_text.split('\n')
        word_count = len(resume_text.split())
        
        # Ideal: 200-500 words per section, 1-2 pages
        if 300 < word_count < 1000:
            scores['formatting_score'] = 90
        elif 150 < word_count < 1500:
            scores['formatting_score'] = 75
        else:
            scores['formatting_score'] = 60
            suggestions.append('Optimize length - aim for 1-2 pages')
        
        # Completeness (has sections for experience, skills, education)
        sections = ['experience', 'skills', 'education']
        section_count = sum(1 for sec in sections if sec.lower() in resume_text.lower())
        scores['completeness_score'] = 60 + (section_count * 13)
        
        if section_count < 3:
            suggestions.append('Include all key sections: Experience, Skills, Education')
        
        # Overall score
        scores['overall_score'] = int((scores['ats_score'] + scores['keyword_score'] + 
                                      scores['formatting_score'] + scores['completeness_score']) / 4)
        
        scores['suggestions'] = suggestions if suggestions else ['Your resume looks strong!']
        
        return scores
    
    @staticmethod
    def save_health_analysis(user_id, analysis):
        """Save resume health analysis."""
        db = get_db()
        now = datetime.utcnow().isoformat()
        
        db.execute('''
            INSERT OR REPLACE INTO resume_health
            (user_id, ats_score, keyword_score, formatting_score, content_completeness,
             overall_health, suggestions, last_analyzed_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, analysis['ats_score'], analysis['keyword_score'],
              analysis['formatting_score'], analysis['completeness_score'],
              analysis['overall_score'], json.dumps(analysis['suggestions']),
              now, now, now))
        db.commit()
    
    @staticmethod
    def get_health_analysis(user_id):
        """Get user's latest resume health analysis."""
        db = get_db()
        row = db.execute(
            'SELECT * FROM resume_health WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        
        if not row:
            return None
        
        cols = [d[0] for d in db.execute('SELECT * FROM resume_health LIMIT 0').description]
        data = dict(zip(cols, row))
        
        if data.get('suggestions'):
            data['suggestions'] = json.loads(data['suggestions'])
        
        return data


class SkillGapAnalysis:
    """Identifies skill gaps and learning priorities."""
    
    @staticmethod
    def analyze_gaps(current_skills, required_skills):
        """
        Compare current skills against required skills.
        Returns: dict with gaps, priorities, learning plan.
        """
        current = set(s.strip().lower() for s in current_skills if s.strip())
        required = set(s.strip().lower() for s in required_skills if s.strip())
        
        gaps = list(required - current)
        matched = list(current & required)
        
        # Assign priority scores to gaps (rough estimation)
        prioritized_gaps = []
        priority_keywords = ['leadership', 'management', 'communication', 'project']
        
        for gap in gaps:
            priority = 5  # default
            weeks = 6     # default
            
            if any(kw in gap for kw in priority_keywords):
                priority = 10
                weeks = 8
            elif gap in ['aws', 'python', 'javascript', 'react']:
                priority = 7
                weeks = 4
            
            prioritized_gaps.append({
                'skill': gap,
                'priority': priority,
                'estimated_weeks': weeks
            })
        
        # Sort by priority
        prioritized_gaps.sort(key=lambda x: x['priority'], reverse=True)
        
        return {
            'current_skills': list(current),
            'required_skills': list(required),
            'matched_skills': matched,
            'gap_count': len(gaps),
            'priority_gaps': prioritized_gaps,
            'estimated_total_weeks': sum(g['estimated_weeks'] for g in prioritized_gaps)
        }
    
    @staticmethod
    def save_analysis(user_id, analysis):
        """Save skill gap analysis."""
        db = get_db()
        now = datetime.utcnow().isoformat()
        
        gap_count = len(analysis.get('priority_gaps', []))
        
        db.execute('''
            INSERT OR REPLACE INTO skill_gap_analysis
            (user_id, current_skills, required_skills, gap_count, priority_gaps,
             estimated_learning_weeks, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, json.dumps(analysis['current_skills']),
              json.dumps(analysis['required_skills']), gap_count,
              json.dumps(analysis['priority_gaps']),
              analysis['estimated_total_weeks'], now, now))
        db.commit()


class CareerConfidenceIndex:
    """Composite readiness score based on multiple factors."""
    
    @staticmethod
    def calculate(resume_health, skill_gap_analysis, timeline):
        """
        Calculate career confidence index (0-100).
        Factors: resume strength, skill readiness, market alignment, consistency.
        """
        if not resume_health:
            resume_strength = 40
        else:
            resume_strength = min(100, resume_health.get('overall_health', 40))
        
        # Skill readiness: 100 - (gap_percentage * 100)
        if skill_gap_analysis:
            total_required = len(skill_gap_analysis.get('required_skills', []))
            gap_count = skill_gap_analysis.get('gap_count', 0)
            skill_readiness = max(10, 100 - (gap_count / max(total_required, 1) * 100))
        else:
            skill_readiness = 50
        
        # Market alignment: estimated based on timeline
        if timeline and timeline.get('timeline_months'):
            months = timeline['timeline_months']
            # Closer timeline = better alignment (assumes they chose realistic goal)
            market_alignment = max(40, min(95, 100 - (months * 2)))
        else:
            market_alignment = 60
        
        # Consistency: placeholder, would track over time
        consistency = 75
        
        overall = int((resume_strength + skill_readiness + market_alignment + consistency) / 4)
        
        return {
            'overall_score': overall,
            'resume_strength': int(resume_strength),
            'skill_readiness': int(skill_readiness),
            'market_alignment': int(market_alignment),
            'consistency': consistency,
            'trend': 'stable'  # Would track over time
        }
    
    @staticmethod
    def save_index(user_id, confidence_data):
        """Save confidence index."""
        db = get_db()
        now = datetime.utcnow().isoformat()
        
        db.execute('''
            INSERT OR REPLACE INTO confidence_index
            (user_id, resume_strength, skill_readiness, market_alignment, overall_score,
             trend, last_updated, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, confidence_data['resume_strength'], confidence_data['skill_readiness'],
              confidence_data['market_alignment'], confidence_data['overall_score'],
              confidence_data.get('trend', 'stable'), now, now))
        db.commit()


class WeeklyCheckin:
    """Manages weekly career check-ins."""
    
    @staticmethod
    def get_weekly_prompt(week_num=None):
        """Get this week's check-in prompt."""
        prompts = [
            "What progress have you made toward your goal this week?",
            "What challenges did you face, and how did you overcome them?",
            "Which skill did you focus on developing this week?",
            "How confident do you feel about your career path right now?",
            "What's one win you achieved this week, no matter how small?",
            "What would you like to focus on next week?",
            "How is your resume health improving?",
            "Are you on track with your career timeline?"
        ]
        
        if week_num is None:
            week_num = int(datetime.now().timestamp() / (7 * 24 * 3600)) % len(prompts)
        
        return prompts[week_num % len(prompts)]
    
    @staticmethod
    def save_checkin(user_id, response, areas_of_progress, challenges, actions_planned,
                    confidence_rating):
        """Save weekly check-in response."""
        db = get_db()
        now = datetime.utcnow().isoformat()
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).date().isoformat()
        
        db.execute('''
            INSERT OR REPLACE INTO weekly_checkins
            (user_id, week_start_date, response, areas_of_progress, challenges,
             actions_planned, confidence_rating, completed_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, week_start, response, areas_of_progress, challenges,
              actions_planned, confidence_rating, now, now))
        db.commit()
    
    @staticmethod
    def get_latest_checkin(user_id):
        """Get user's latest check-in."""
        db = get_db()
        row = db.execute(
            '''SELECT * FROM weekly_checkins 
               WHERE user_id = ? 
               ORDER BY completed_at DESC LIMIT 1''',
            (user_id,)
        ).fetchone()
        
        if not row:
            return None
        
        cols = [d[0] for d in db.execute('SELECT * FROM weekly_checkins LIMIT 0').description]
        return dict(zip(cols, row))


class DecisionSupport:
    """Provides career decision guidance."""
    
    DECISION_TEMPLATES = {
        'apply_for_role': {
            'question': 'Should I apply for this {} role?',
            'factors': ['skill_match', 'timeline_readiness', 'market_demand', 'growth_potential']
        },
        'learn_skill': {
            'question': 'Which skill should I learn next?',
            'factors': ['impact_on_target', 'learning_time', 'market_demand', 'prerequisites']
        },
        'role_switch': {
            'question': 'Should I switch to a {} role?',
            'factors': ['skill_alignment', 'career_timeline', 'market_opportunity', 'risk_assessment']
        }
    }
    
    @staticmethod
    def analyze_role_application(target_role, user_skills, required_skills, timeline):
        """
        Analyze if user should apply for a specific role.
        Returns: recommendation, success_estimate, reasoning.
        """
        matched = len(set(user_skills) & set(required_skills))
        total_required = len(required_skills)
        match_percentage = (matched / total_required * 100) if total_required > 0 else 0
        
        # Timeline factor
        months_until_goal = timeline.get('timeline_months', 12) if timeline else 12
        timeline_readiness = max(10, 100 - (months_until_goal * 5))
        
        # Combined score
        success_estimate = int((match_percentage + timeline_readiness) / 2)
        
        if success_estimate >= 70:
            recommendation = "Apply now - you're well-positioned"
            confidence = "High"
        elif success_estimate >= 50:
            recommendation = "Apply with caution - you have good fundamentals but some gaps"
            confidence = "Medium"
        else:
            months_to_wait = max(1, (100 - success_estimate) // 10)
            recommendation = f"Wait {months_to_wait}-{months_to_wait+2} months to strengthen key skills"
            confidence = "Low"
        
        return {
            'success_estimate': success_estimate,
            'recommendation': recommendation,
            'confidence': confidence,
            'match_percentage': int(match_percentage),
            'reasoning': {
                'skill_match': f"{matched}/{total_required} required skills",
                'timeline_factor': f"Timeline confidence: {int(timeline_readiness)}%"
            }
        }
    
    @staticmethod
    def recommend_next_skill(priority_gaps):
        """
        Recommend which skill to learn next based on impact.
        """
        if not priority_gaps:
            return {
                'recommendation': 'You have all required skills!',
                'reasoning': 'Continue deepening existing skills and exploring adjacent areas.'
            }
        
        top_skill = priority_gaps[0]
        
        return {
            'skill': top_skill['skill'],
            'priority': top_skill['priority'],
            'estimated_weeks': top_skill['estimated_weeks'],
            'impact': 'Highest impact on target role',
            'reasoning': f"This skill is critical for your goal and will unlock the most opportunities."
        }
    
    @staticmethod
    def save_decision(user_id, context, question, analysis, recommendation):
        """Save decision analysis."""
        db = get_db()
        now = datetime.utcnow().isoformat()
        
        db.execute('''
            INSERT INTO decision_support
            (user_id, decision_context, question, analysis_data, recommendation, 
             confidence_level, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, context, question, json.dumps(analysis), recommendation,
              analysis.get('confidence', 'medium'), now))
        db.commit()
