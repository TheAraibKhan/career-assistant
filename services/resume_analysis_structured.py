"""
Enhanced Resume Analysis Service - Section-wise Scoring & Insights

This service provides:
1. Section-wise analysis (Education, Skills, Projects, Experience, Achievements)
2. Multi-dimensional scoring (Structure, Content, Impact, ATS)
3. Role-based feedback & recommendations
4. Resume evolution tracking
5. Personalized insights based on user profile

CRITICAL: This replaces duplicated analysis logic.
All resume analysis goes through this service.
"""

from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime


class SectionAnalyzer:
    """Analyzes individual resume sections."""
    
    # Section quality rubric
    SECTION_RUBRICS = {
        'education': {
            'ideal': 'Degree, Institution, GPA (if >3.5), Graduation Date',
            'expectations': {
                'college': ['Degree', 'Institution', 'Graduation'],
                'post-college': ['Advanced degrees', 'Relevant certifications'],
            }
        },
        'skills': {
            'ideal': '15-20 relevant skills, organized by category',
            'expectations': {
                'entry': 'Programming languages, tools, basic frameworks',
                'mid': 'Advanced languages, popular frameworks, tools',
                'senior': 'Leadership, architecture, emerging tech',
            }
        },
        'experience': {
            'ideal': 'Role, Company, Duration, 3-5 impact-driven bullets',
            'expectations': {
                'entry': 'Internships, projects, academic experience',
                'mid': '2-3 roles with growing responsibility',
                'senior': 'Leadership, mentorship, strategic work',
            }
        },
        'projects': {
            'ideal': 'Project name, tech stack, 1-2 impact bullets, link',
            'expectations': {
                'entry': '2-3 projects, GitHub links',
                'mid': '3-5 projects with measurable impact',
                'senior': 'Open source contributions, technical leadership',
            }
        },
        'achievements': {
            'ideal': 'Relevant awards, publications, speaking, contributions',
            'expectations': {
                'entry': 'Academic achievements, hackathon wins',
                'mid': 'Conference talks, publications, awards',
                'senior': 'Industry recognition, leadership awards',
            }
        }
    }
    
    @staticmethod
    def analyze_education(resume_text: str, phase: str = 'college') -> Dict:
        """Analyze education section."""
        has_education = any(kw in resume_text.lower() for kw in ['degree', 'university', 'college', 'education', 'graduated', 'gpa'])
        
        status = 'complete' if has_education else 'needs_work'
        score = 80 if has_education else 40
        
        return {
            'name': 'Education',
            'status': status,
            'score': score,
            'explanation': 'Education section shows your academic background and qualifications.',
            'suggestion': 'Include degree, institution, graduation date. Add GPA if >3.5, relevant certifications.',
            'tips': [
                '✓ Format: Degree | Institution | GPA (if strong) | Graduation Date' if status == 'complete' else 'Add education details',
                '✓ Include relevant coursework if applicable' if phase == 'college' else 'Link to certifications',
                '✓ Highlight scholarships or academic honors'
            ]
        }
    
    @staticmethod
    def analyze_skills(resume_text: str, skills_found: List[str] = None, experience_level: str = 'entry') -> Dict:
        """Analyze skills section."""
        if skills_found is None:
            skills_found = []
        
        skill_count = len(skills_found)
        
        # Expected skills count by level
        expected_min = {'entry': 8, 'mid': 12, 'senior': 15}
        target = expected_min.get(experience_level, 12)
        
        if skill_count >= target:
            status = 'complete'
            score = min(100, 70 + (skill_count - target) * 2)
        elif skill_count >= target - 3:
            status = 'good'
            score = 60
        else:
            status = 'needs_work'
            score = max(30, 30 + (skill_count * 5))
        
        return {
            'name': 'Skills',
            'status': status,
            'score': score,
            'count': skill_count,
            'list': skills_found[:20],  # Show top 20
            'explanation': f'Found {skill_count} relevant skills. Aim for {target}+ for {experience_level} level.',
            'suggestion': 'Organize by category (Languages, Frameworks, Tools, Soft Skills). Include in-demand technologies.',
            'tips': [
                f'✓ You have {skill_count}/{target} skills' if skill_count >= target else f'✓ Add {target - skill_count} more relevant skills',
                '✓ Prioritize in-demand: Python, JavaScript, React, AWS, Docker',
                '✓ Group by category for better readability'
            ]
        }
    
    @staticmethod
    def analyze_experience(resume_text: str, phase: str = 'college') -> Dict:
        """Analyze experience/work section."""
        has_experience = any(kw in resume_text.lower() for kw in ['experience', 'intern', 'worked', 'developed', 'led', 'managed', 'role', 'position'])
        has_action_verbs = any(verb in resume_text.lower() for verb in ['developed', 'designed', 'led', 'managed', 'improved', 'increased', 'reduced', 'deployed'])
        
        if phase == 'college':
            has_experience = any(kw in resume_text.lower() for kw in ['intern', 'project', 'experience', 'experience'])
            if has_experience and has_action_verbs:
                status = 'complete'
                score = 85
            elif has_experience:
                status = 'good'
                score = 65
            else:
                status = 'needs_work'
                score = 35
        else:
            if has_experience and has_action_verbs:
                status = 'complete'
                score = 90
            elif has_experience:
                status = 'good'
                score = 70
            else:
                status = 'needs_work'
                score = 40
        
        tips = [
            '✓ Use strong verbs: Developed, Designed, Led, Managed' if has_action_verbs else '✓ Start bullets with action verbs',
            '✓ Quantify impact: "Improved performance by 40%"' if has_action_verbs else '✓ Add measurable results',
            '✓ Show tech stack and business impact'
        ]
        
        return {
            'name': 'Experience',
            'status': status,
            'score': score,
            'explanation': 'Experience/work section shows your practical background.',
            'suggestion': 'Each role needs 3-5 bullet points with action verbs and quantified results.',
            'tips': tips
        }
    
    @staticmethod
    def analyze_projects(resume_text: str, experience_level: str = 'entry') -> Dict:
        """Analyze projects section."""
        has_projects = any(kw in resume_text.lower() for kw in ['project', 'github', 'built', 'created', 'deployed', 'application', 'system'])
        has_links = 'github.com' in resume_text.lower() or 'link' in resume_text.lower()
        
        expected_projects = {'entry': 2, 'mid': 3, 'senior': 3}  # Minimum
        target = expected_projects.get(experience_level, 3)
        
        if has_projects and has_links:
            status = 'complete'
            score = 85 if experience_level in ['mid', 'senior'] else 90
        elif has_projects:
            status = 'good'
            score = 70
        else:
            status = 'needs_work'
            score = 40
        
        return {
            'name': 'Projects',
            'status': status,
            'score': score,
            'explanation': f'Projects showcase your practical skills. Include {target}+ relevant projects.',
            'suggestion': 'Each project: Title | Tech Stack | 1-2 impact bullets | GitHub link',
            'tips': [
                f'✓ Include {target}+ projects with GitHub links' if status == 'complete' else f'✓ Add projects with GitHub links',
                '✓ Prioritize quality over quantity',
                '✓ Show tech stack and impact'
            ]
        }
    
    @staticmethod
    def analyze_achievements(resume_text: str, level: str = 'entry') -> Dict:
        """Analyze achievements/certifications section."""
        has_achievements = any(kw in resume_text.lower() for kw in ['award', 'certification', 'publication', 'speaking', 'contribution', 'achievement', 'honor'])
        
        if has_achievements:
            status = 'good'
            score = 80
        else:
            status = 'optional'
            score = 50
        
        return {
            'name': 'Certifications & Achievements',
            'status': status,
            'score': score,
            'explanation': 'Certifications and achievements add credibility.',
            'suggestion': 'Add relevant certifications (AWS, Google Cloud), speaking engagements, publications.',
            'tips': [
                '✓ Include relevant certifications and awards' if has_achievements else '✓ Consider getting relevant certifications',
                '✓ Remove outdated or irrelevant achievements',
                '✓ Link to speaking gigs, publications, portfolios'
            ]
        }


class ScoreCalculator:
    """Calculate multi-dimensional resume scores."""
    
    @staticmethod
    def calculate_structure_score(sections: List[Dict]) -> int:
        """Score based on section completeness and organization."""
        section_scores = [s['score'] for s in sections]
        return int(sum(section_scores) / len(section_scores)) if section_scores else 0
    
    @staticmethod
    def calculate_content_score(resume_text: str, skills_found: List[str]) -> int:
        """Score based on content quality, relevance, quantification."""
        score = 50  # Base
        
        # Length check (400-1000 words optimal)
        word_count = len(resume_text.split())
        if 400 <= word_count <= 1000:
            score += 15
        elif 300 <= word_count <= 1200:
            score += 10
        
        # Quantification (numbers indicate impact)
        has_numbers = any(char.isdigit() for char in resume_text)
        if has_numbers:
            score += 15
        
        # Skills coverage
        if len(skills_found) >= 10:
            score += 15
        elif len(skills_found) >= 5:
            score += 10
        
        # Action verbs
        action_verbs = ['developed', 'designed', 'led', 'managed', 'improved', 'increased',  'deployed', 'architected', 'optimized']
        verb_count = sum(1 for verb in action_verbs if verb in resume_text.lower())
        if verb_count >= 5:
            score += 10
        
        return min(100, score)
    
    @staticmethod
    def calculate_impact_score(resume_text: str) -> int:
        """Score based on business/technical impact indicators."""
        score = 40  # Base
        
        # Metrics/percentages
        if '%' in resume_text:
            score += 20
        
        # Impact keywords
        impact_words = ['improved', 'increased', 'reduced', 'optimized', 'scaled', 'deployed', 'achieved', 'exceeded']
        if any(word in resume_text.lower() for word in impact_words):
            score += 25
        
        # Leadership/responsibility
        leadership_words = ['led', 'managed', 'mentored', 'directed', 'supervised', 'architected']
        if any(word in resume_text.lower() for word in leadership_words):
            score += 15
        
        return min(100, score)
    
    @staticmethod
    def calculate_ats_score(resume_text: str, sections: List[Dict]) -> int:
        """Score for ATS (Applicant Tracking System) parsability."""
        score = 50  # Base
        
        # Section completeness
        complete_sections = sum(1 for s in sections if s['status'] == 'complete')
        score += complete_sections * 8
        
        # Format indicators (simple format = better for ATS)
        if len(resume_text) < 2000:  # Reasonable length
            score += 10
        
        # No excessive special characters
        special_chars = sum(1 for c in resume_text if c in '@#$%^&*()')
        if special_chars < 5:
            score += 10
        
        # Good keyword density
        keywords = ['experienced', 'skilled', 'proficient', 'expertise', 'background']
        if sum(1 for kw in keywords if kw in resume_text.lower()) >= 2:
            score += 10
        
        return min(100, score)


class ResumAnalysisService:
    """Main service - Orchestrates all analysis."""
    
    @staticmethod
    def analyze_resume_comprehensive(
        resume_text: str,
        skills_found: List[str] = None,
        user_phase: str = 'college',
        user_goal: str = None
    ) -> Dict:
        """
        Comprehensive multi-dimensional resume analysis.
        
        Returns structured analysis with:
        - Section-wise feedback (status, score, tips)
        - Multi-dimensional scores (structure, content, impact, ATS)
        - Role-based recommendations
        - Evolution guidance
        - Personalized insights
        """
        if skills_found is None:
            skills_found = []
        
        # Infer experience level from phase
        exp_level = {'pre-college': 'entry', 'college': 'entry', 'post-college': 'mid'}
        experience_level = exp_level.get(user_phase, 'entry')
        
        # 1. Analyze each section
        sections = [
            SectionAnalyzer.analyze_education(resume_text, user_phase),
            SectionAnalyzer.analyze_skills(resume_text, skills_found, experience_level),
            SectionAnalyzer.analyze_experience(resume_text, user_phase),
            SectionAnalyzer.analyze_projects(resume_text, experience_level),
            SectionAnalyzer.analyze_achievements(resume_text, experience_level),
        ]
        
        # 2. Calculate scores
        structure_score = ScoreCalculator.calculate_structure_score(sections)
        content_score = ScoreCalculator.calculate_content_score(resume_text, skills_found)
        impact_score = ScoreCalculator.calculate_impact_score(resume_text)
        ats_score = ScoreCalculator.calculate_ats_score(resume_text, sections)
        
        # 3. Overall score (weighted average)
        overall_score = int(
            (structure_score * 0.25) +
            (content_score * 0.25) +
            (impact_score * 0.25) +
            (ats_score * 0.25)
        )
        
        # 4. Grade
        grades = {
            (90, 101): 'Excellent',
            (80, 90): 'Strong',
            (70, 80): 'Good',
            (60, 70): 'Fair',
            (0, 60): 'Needs Work'
        }
        grade = next(g for r, g in grades.items() if r[0] <= overall_score < r[1])
        
        # 5. Role-based feedback
        role_feedback = ResumAnalysisService._get_role_feedback(user_goal, skills_found, sections)
        
        # 6. Evolution guidance
        evolution = ResumAnalysisService._get_evolution_guidance(overall_score, user_phase, skills_found)
        
        # 7. Summary
        priority_improvements = ResumAnalysisService._get_priority_improvements(sections, skills_found)
        
        return {
            'success': True,
            'overall_score': overall_score,
            'grade': grade,
            'scores': {
                'structure': structure_score,
                'content': content_score,
                'impact': impact_score,
                'ats': ats_score,
            },
            'sections': sections,
            'role_feedback': role_feedback,
            'evolution': evolution,
            'summary': {
                'strengths': ResumAnalysisService._get_strengths(sections),
                'priority_improvements': priority_improvements,
                'quick_wins': ResumAnalysisService._get_quick_wins(sections),
            },
            'metadata': {
                'analyzed_at': datetime.utcnow().isoformat(),
                'user_phase': user_phase,
                'experience_level': experience_level,
                'user_goal': user_goal,
                'skills_count': len(skills_found),
            }
        }
    
    @staticmethod
    def _get_role_feedback(goal: str, skills: List[str], sections: List[Dict]) -> Dict:
        """Generate role-specific feedback based on user's goal."""
        if not goal:
            return {'message': 'Select a goal to get role-specific feedback'}
        
        role_requirements = {
            'Get a job': {
                'focus': 'Complete all sections, quantify impact, strong skills list',
                'missing': 'Compare your skills to job descriptions',
                'tips': ['Use the same keywords as job postings', 'Highlight transferable skills']
            },
            'Land internship': {
                'focus': 'Projects and skills over experience, relevant coursework',
                'missing': 'GitHub links, project descriptions',
                'tips': ['Emphasize learning and growth', 'Include side projects']
            },
            'Build startup': {
                'focus': 'Full-stack abilities, leadership potential, business impact',
                'missing': 'Entrepreneurship/leadership experience',
                'tips': ['Show systems thinking', 'Demonstrate problem-solving']
            },
        }
        
        feedback = role_requirements.get(goal, {'focus': 'Build a strong foundation', 'missing': '', 'tips': []})
        feedback['skills_aligned'] = len(skills) > 0
        feedback['goal'] = goal
        
        return feedback
    
    @staticmethod
    def _get_evolution_guidance(score: int, phase: str, skills: List[str]) -> Dict:
        """Provide guidance on resume evolution."""
        thresholds = {
            'excellent': (90, 'Your resume is strong! Focus on staying current and adding new skills.'),
            'good': (70, 'Good foundation. Add more quantified impact and projects.'),
            'needs_work': (0, 'Focus on structure first. Fill in all sections, then add detail.'),
        }
        
        level, message = next((l, m) for s, (l, m) in thresholds.items() if (s == 'excellent' and score >= l) or (s == 'good' and 70 <= score < 90) or (s == 'needs_work' and score < 70))
        
        next_version = {
            'current_level': 'Entry' if phase == 'college' else 'Mid',
            'message': message,
            'next_milestones': [
                f'Add {5 - len(skills)} more skills' if len(skills) < 5 else 'Skills well-covered',
                'Add 1-2 more projects' if score < 80 else 'Strengthen project descriptions',
                'Quantify all achievements' if score < 75 else 'Add more metrics',
            ]
        }
        
        return next_version
    
    @staticmethod
    def _get_priority_improvements(sections: List[Dict], skills: List[str]) -> List[Dict]:
        """Identify top 3 priority improvements."""
        improvements = []
        
        # Find lowest scoring sections
        sorted_sections = sorted(sections, key=lambda x: x['score'])
        
        for section in sorted_sections[:3]:
            if section['score'] < 85:
                improvements.append({
                    'section': section['name'],
                    'current_score': section['score'],
                    'recommendation': section['suggestion'],
                    'impact': 'High' if section['status'] == 'needs_work' else 'Medium'
                })
        
        return improvements
    
    @staticmethod
    def _get_strengths(sections: List[Dict]) -> List[str]:
        """Extract strengths from analysis."""
        return [
            f"{s['name']}: {s['explanation']}"
            for s in sections
            if s['score'] >= 75 and s['status'] in ['complete', 'good']
        ]
    
    @staticmethod
    def _get_quick_wins(sections: List[Dict]) -> List[str]:
        """Identify quick wins - easy improvements."""
        quick_wins = []
        for section in sections:
            if 60 <= section['score'] < 80:
                quick_wins.append(f"Enhance {section['name']}: {section['tips'][0]}")
        return quick_wins[:3]  # Top 3
