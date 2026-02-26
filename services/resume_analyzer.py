"""
Comprehensive Field-Aware Resume Analyzer

Orchestrates all analysis components to provide complete, actionable resume feedback.
Based on real recruiter practices and ATS behavior, not generic scoring.
"""

from typing import Dict, List, Optional
from services.ats_analyzer import ATSAnalyzer
from services.skills_experience_analyzer import SkillsAnalyzer, ExperienceAnalyzer
from services.field_config import get_field_config, get_available_fields


class ResumeAnalyzer:
    """
    Comprehensive resume analysis system.
    Field-aware, experience-level calibrated, recruiter-aligned.
    """
    
    def __init__(
        self,
        field_key: str = 'software_backend',
        experience_level: str = 'mid'
    ):
        """
        Initialize analyzer for specific field and experience level.
        
        Args:
            field_key: Target career field (see get_available_fields())
            experience_level: 'entry' (0-2 years), 'mid' (3-7 years), 'senior' (8+ years)
        """
        self.field_key = field_key
        self.experience_level = experience_level
        self.field_config = get_field_config(field_key)
        
        # Initialize component analyzers
        self.ats_analyzer = ATSAnalyzer(field_key, experience_level)
        self.skills_analyzer = SkillsAnalyzer(field_key, experience_level)
        self.experience_analyzer = ExperienceAnalyzer(field_key, experience_level)
    
    def analyze(
        self,
        resume_text: str,
        parsed_data: Dict,
        skills_list: Optional[List[str]] = None
    ) -> Dict:
        """
        Perform comprehensive resume analysis.
        
        Args:
            resume_text: Full resume text
            parsed_data: Parsed resume data (from resume parser)
            skills_list: Optional list of extracted skills
        
        Returns:
            {
                'overall_score': int (0-100),
                'grade': str ('Excellent', 'Strong', 'Good', 'Fair', 'Needs Work'),
                'scores': {
                    'ats': int,
                    'skills': int,
                    'experience': int,
                    'structure': int,
                    'impact': int
                },
                'analysis': {
                    'ats': {...},
                    'skills': {...},
                    'experience': {...}
                },
                'summary': {
                    'strengths': List[str],
                    'priority_improvements': List[Dict],
                    'quick_wins': List[str]
                },
                'field_specific_advice': List[str],
                'metadata': {
                    'field': str,
                    'experience_level': str,
                    'analysis_version': str
                }
            }
        """
        # Extract skills if not provided
        if skills_list is None:
            skills_list = parsed_data.get('skills', [])
        
        # Run component analyses
        ats_analysis = self.ats_analyzer.analyze(resume_text, parsed_data)
        skills_analysis = self.skills_analyzer.analyze(resume_text, skills_list)
        experience_analysis = self.experience_analyzer.analyze(resume_text)
        
        # Calculate component scores
        ats_score = ats_analysis['score']
        skills_score = skills_analysis['score']
        experience_score = experience_analysis['score']
        
        # Structure score (from ATS section analysis)
        structure_score = ats_analysis['breakdown']['sections']
        
        # Impact score (from experience impact analysis)
        impact_score = experience_analysis['breakdown']['impact']
        
        # Calculate overall score with field-specific weights
        overall_score = self._calculate_overall_score(
            ats_score, skills_score, experience_score, structure_score, impact_score
        )
        
        # Determine grade
        grade = self._determine_grade(overall_score)
        
        # Generate comprehensive summary
        summary = self._generate_summary(
            ats_analysis, skills_analysis, experience_analysis, overall_score
        )
        
        # Generate field-specific advice
        field_advice = self._generate_field_specific_advice(
            ats_analysis, skills_analysis, experience_analysis
        )
        
        return {
            'overall_score': overall_score,
            'grade': grade,
            'scores': {
                'ats': ats_score,
                'skills': skills_score,
                'experience': experience_score,
                'structure': structure_score,
                'impact': impact_score
            },
            'analysis': {
                'ats': ats_analysis,
                'skills': skills_analysis,
                'experience': experience_analysis
            },
            'summary': summary,
            'field_specific_advice': field_advice,
            'metadata': {
                'field': self.field_config.name,
                'experience_level': self.experience_level,
                'analysis_version': '2.0'
            }
        }
    
    def _calculate_overall_score(
        self, ats: int, skills: int, experience: int, structure: int, impact: int
    ) -> int:
        """Calculate weighted overall score based on field priorities."""
        
        # Base weights
        weights = {
            'ats': 0.25,
            'skills': 0.20,
            'experience': 0.25,
            'structure': 0.10,
            'impact': 0.20
        }
        
        # Adjust weights by field
        if 'Software' in self.field_config.name or 'Data Science' in self.field_config.name:
            # Technical fields: skills and projects matter more
            weights['skills'] = 0.25
            weights['experience'] = 0.20
        elif 'Product' in self.field_config.name or 'Marketing' in self.field_config.name:
            # Business fields: experience and impact matter more
            weights['experience'] = 0.30
            weights['impact'] = 0.25
            weights['skills'] = 0.15
        elif 'Design' in self.field_config.name:
            # Design: portfolio (experience) matters most
            weights['experience'] = 0.35
            weights['ats'] = 0.15
        
        # Adjust by experience level
        if self.experience_level == 'entry':
            weights['skills'] += 0.05
            weights['experience'] -= 0.05
        elif self.experience_level == 'senior':
            weights['experience'] += 0.05
            weights['impact'] += 0.05
            weights['skills'] -= 0.05
            weights['structure'] -= 0.05
        
        # Calculate weighted score
        overall = int(
            ats * weights['ats'] +
            skills * weights['skills'] +
            experience * weights['experience'] +
            structure * weights['structure'] +
            impact * weights['impact']
        )
        
        return min(100, max(0, overall))
    
    def _determine_grade(self, score: int) -> str:
        """Determine letter grade from score."""
        if score >= 90:
            return 'Excellent'
        elif score >= 80:
            return 'Strong'
        elif score >= 70:
            return 'Good'
        elif score >= 60:
            return 'Fair'
        else:
            return 'Needs Work'
    
    def _generate_summary(
        self, ats_analysis: Dict, skills_analysis: Dict,
        experience_analysis: Dict, overall_score: int
    ) -> Dict:
        """Generate comprehensive summary with prioritized recommendations."""
        
        # Collect all strengths
        all_strengths = []
        all_strengths.extend(ats_analysis.get('strengths', []))
        all_strengths.extend(skills_analysis.get('strengths', []))
        all_strengths.extend(experience_analysis.get('strengths', []))
        
        # Collect all improvements with priority
        improvements = []
        
        # ATS blockers are highest priority
        for blocker in ats_analysis.get('blockers', []):
            improvements.append({
                'priority': 'critical',
                'category': 'ATS Compatibility',
                'issue': blocker,
                'impact': 'High - May prevent resume from being read',
                'effort': 'Medium'
            })
        
        # High-impact ATS improvements
        for improvement in ats_analysis.get('improvements', [])[:2]:
            improvements.append({
                'priority': 'high',
                'category': 'ATS Compatibility',
                'issue': improvement,
                'impact': 'High - Improves parsing and keyword matching',
                'effort': 'Low to Medium'
            })
        
        # Skills improvements
        if skills_analysis['score'] < 70:
            for improvement in skills_analysis.get('improvements', [])[:2]:
                improvements.append({
                    'priority': 'high',
                    'category': 'Skills',
                    'issue': improvement,
                    'impact': 'Medium to High - Increases relevance',
                    'effort': 'Low'
                })
        
        # Experience improvements
        if experience_analysis['score'] < 70:
            for improvement in experience_analysis.get('improvements', [])[:2]:
                improvements.append({
                    'priority': 'high',
                    'category': 'Experience',
                    'issue': improvement,
                    'impact': 'High - Demonstrates value',
                    'effort': 'Medium'
                })
        
        # Quick wins (low effort, medium impact)
        quick_wins = []
        
        # Contact info quick wins
        if ats_analysis['breakdown']['contact'] < 80:
            for improvement in ats_analysis.get('improvements', []):
                if 'linkedin' in improvement.lower() or 'github' in improvement.lower():
                    quick_wins.append(improvement)
        
        # Formatting quick wins
        if ats_analysis['breakdown']['sections'] < 75:
            quick_wins.append("Use standard section headers in ALL CAPS (EXPERIENCE, EDUCATION, SKILLS)")
        
        # Skills quick wins
        if skills_analysis['score'] < 80:
            missing = skills_analysis.get('missing_core_skills', [])
            if missing:
                quick_wins.append(f"Add these skills if you have them: {', '.join(missing[:3])}")
        
        return {
            'strengths': all_strengths[:5],  # Top 5 strengths
            'priority_improvements': improvements[:5],  # Top 5 priority items
            'quick_wins': quick_wins[:3]  # Top 3 quick wins
        }
    
    def _generate_field_specific_advice(
        self, ats_analysis: Dict, skills_analysis: Dict, experience_analysis: Dict
    ) -> List[str]:
        """Generate advice specific to the target field."""
        advice = []
        
        field_name = self.field_config.name
        
        # Software Engineering specific
        if 'Software' in field_name:
            if 'github' not in str(ats_analysis).lower():
                advice.append(
                    "Add GitHub profile - recruiters want to see your code for engineering roles"
                )
            
            if experience_analysis['breakdown']['impact'] < 70:
                advice.append(
                    "Quantify technical impact: system scale (requests/sec, users), performance improvements (latency reduction), or reliability metrics (uptime)"
                )
            
            if skills_analysis['score'] < 70:
                advice.append(
                    "For engineering roles, show both breadth (multiple languages/frameworks) and depth (years of experience, complex projects)"
                )
        
        # Data Science specific
        elif 'Data Science' in field_name:
            advice.append(
                "Highlight end-to-end ML projects: data collection → model training → deployment → business impact"
            )
            
            if experience_analysis['breakdown']['impact'] < 70:
                advice.append(
                    "Quantify model performance (accuracy, AUC, F1) AND business impact (revenue, cost savings, efficiency)"
                )
            
            advice.append(
                "Include both statistical foundations and modern ML tools - recruiters look for both"
            )
        
        # Product Management specific
        elif 'Product' in field_name:
            if experience_analysis['breakdown']['impact'] < 70:
                advice.append(
                    "Product roles require clear metrics: user growth (DAU/MAU), engagement, conversion, retention, revenue"
                )
            
            advice.append(
                "Emphasize cross-functional leadership and stakeholder management - PMs are connectors"
            )
            
            advice.append(
                "Show data-driven decision making: A/B tests, user research, analytics"
            )
        
        # Design specific
        elif 'Design' in field_name:
            if 'portfolio' not in str(ats_analysis).lower():
                advice.append(
                    "CRITICAL: Add portfolio link - for design roles, portfolio matters more than resume"
                )
            
            advice.append(
                "Show design process, not just final outputs: research → ideation → iteration → validation"
            )
            
            advice.append(
                "Highlight user impact: improved task completion, reduced errors, increased satisfaction"
            )
        
        # Marketing specific
        elif 'Marketing' in field_name:
            if experience_analysis['breakdown']['impact'] < 70:
                advice.append(
                    "Marketing roles require ROI metrics: CAC, LTV, ROAS, conversion rates, revenue growth"
                )
            
            advice.append(
                "Show multi-channel expertise - modern marketers need to work across digital channels"
            )
            
            advice.append(
                "Demonstrate data-driven optimization: A/B testing, analytics, attribution"
            )
        
        # Experience level specific advice
        if self.experience_level == 'entry':
            advice.append(
                "For entry-level: emphasize projects, internships, and relevant coursework - show potential and learning ability"
            )
        elif self.experience_level == 'senior':
            advice.append(
                "For senior roles: emphasize leadership, strategic impact, and mentorship - show you can multiply team effectiveness"
            )
        
        return advice[:5]  # Top 5 pieces of advice


def analyze_resume(
    resume_text: str,
    parsed_data: Dict,
    field_key: str = 'software_backend',
    experience_level: str = 'mid',
    skills_list: Optional[List[str]] = None
) -> Dict:
    """
    Convenience function for comprehensive resume analysis.
    
    Args:
        resume_text: Full resume text
        parsed_data: Parsed resume data
        field_key: Target career field
        experience_level: Career stage
        skills_list: Optional extracted skills
    
    Returns:
        Complete analysis results
    """
    analyzer = ResumeAnalyzer(field_key, experience_level)
    return analyzer.analyze(resume_text, parsed_data, skills_list)
