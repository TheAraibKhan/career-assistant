"""
Skills and Experience Analysis Module

Evaluates skill relevance, depth, and experience quality based on field-specific criteria.
Focuses on demonstrable proficiency and real-world impact.
"""

import re
from typing import Dict, List, Tuple, Set
from services.field_config import get_field_config


class SkillsAnalyzer:
    """Analyzes skills based on field-specific requirements and depth indicators."""
    
    # Proficiency indicators
    PROFICIENCY_MARKERS = {
        'expert': ['expert', 'advanced', 'proficient', 'mastery', 'specialized'],
        'strong': ['strong', 'extensive', 'solid', 'deep knowledge'],
        'experienced': ['experienced', 'familiar', 'working knowledge', 'hands-on'],
        'basic': ['basic', 'beginner', 'learning', 'exposure to']
    }
    
    # Duration indicators
    DURATION_PATTERNS = [
        r'(\d+)\+?\s*years?',
        r'(\d+)\s*months?'
    ]
    
    def __init__(self, field_key: str, experience_level: str):
        self.field_config = get_field_config(field_key)
        self.experience_level = experience_level
    
    def analyze(self, resume_text: str, skills_list: List[str]) -> Dict:
        """
        Analyze skills coverage and depth.
        
        Returns:
            {
                'score': int (0-100),
                'breakdown': {
                    'core_coverage': int,
                    'depth': int,
                    'supporting': int,
                    'recency': int
                },
                'core_skills_found': List[str],
                'missing_core_skills': List[str],
                'strengths': List[str],
                'improvements': List[str]
            }
        """
        text_lower = resume_text.lower()
        skills_lower = [s.lower() for s in skills_list]
        
        # Analyze core skills coverage
        core_coverage, core_found = self._analyze_core_skills(text_lower, skills_lower)
        
        # Analyze skill depth
        depth_score = self._analyze_skill_depth(resume_text, core_found)
        
        # Analyze supporting skills
        supporting_score = self._analyze_supporting_skills(text_lower, skills_lower)
        
        # Analyze recency
        recency_score = self._analyze_skill_recency(resume_text, core_found)
        
        # Calculate weighted score
        total_score = int(
            core_coverage * 0.40 +
            depth_score * 0.30 +
            supporting_score * 0.20 +
            recency_score * 0.10
        )
        
        # Identify missing core skills
        missing_core = self._identify_missing_core_skills(core_found)
        
        # Generate insights
        strengths = self._identify_strengths(core_coverage, depth_score, core_found)
        improvements = self._generate_improvements(
            core_coverage, depth_score, supporting_score, missing_core
        )
        
        return {
            'score': total_score,
            'breakdown': {
                'core_coverage': int(core_coverage),
                'depth': depth_score,
                'supporting': supporting_score,
                'recency': recency_score
            },
            'core_skills_found': list(core_found),
            'missing_core_skills': missing_core,
            'strengths': strengths,
            'improvements': improvements
        }
    
    def _analyze_core_skills(
        self, text_lower: str, skills_lower: List[str]
    ) -> Tuple[float, Set[str]]:
        """Analyze coverage of core skills for the field."""
        core_keywords = self.field_config.core_keywords
        core_found = set()
        
        for keyword in core_keywords:
            if keyword in text_lower or keyword in skills_lower:
                core_found.add(keyword)
        
        coverage = (len(core_found) / len(core_keywords)) * 100 if core_keywords else 0
        
        # Adjust expectations by experience level
        if self.experience_level == 'entry':
            coverage = min(100, coverage * 1.3)  # More lenient for entry-level
        elif self.experience_level == 'senior':
            coverage = coverage * 0.9  # Higher bar for senior
        
        return coverage, core_found
    
    def _analyze_skill_depth(self, text: str, core_skills: Set[str]) -> int:
        """Analyze depth of skill proficiency based on context."""
        if not core_skills:
            return 0
        
        depth_score = 0
        text_lower = text.lower()
        
        # Check for proficiency markers
        for level, markers in self.PROFICIENCY_MARKERS.items():
            for marker in markers:
                if marker in text_lower:
                    if level == 'expert':
                        depth_score += 15
                    elif level == 'strong':
                        depth_score += 10
                    elif level == 'experienced':
                        depth_score += 5
        
        # Check for duration indicators
        for pattern in self.DURATION_PATTERNS:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                years = int(match) if 'year' in pattern else int(match) / 12
                if years >= 5:
                    depth_score += 15
                elif years >= 3:
                    depth_score += 10
                elif years >= 1:
                    depth_score += 5
        
        # Check for project-based evidence
        project_indicators = ['built', 'developed', 'designed', 'implemented', 'architected']
        for skill in list(core_skills)[:10]:  # Check top skills
            for indicator in project_indicators:
                pattern = f'{indicator}.*{skill}|{skill}.*{indicator}'
                if re.search(pattern, text_lower):
                    depth_score += 3
                    break
        
        # Check for certifications
        cert_pattern = r'certified|certification|certificate'
        if re.search(cert_pattern, text_lower):
            depth_score += 10
        
        return min(100, depth_score)
    
    def _analyze_supporting_skills(
        self, text_lower: str, skills_lower: List[str]
    ) -> int:
        """Analyze supporting skills that complement core skills."""
        supporting_keywords = self.field_config.supporting_keywords
        supporting_found = 0
        
        for keyword in supporting_keywords:
            if keyword in text_lower or keyword in skills_lower:
                supporting_found += 1
        
        coverage = (supporting_found / len(supporting_keywords)) * 100 if supporting_keywords else 0
        return min(100, int(coverage))
    
    def _analyze_skill_recency(self, text: str, core_skills: Set[str]) -> int:
        """Analyze if skills are recent or outdated."""
        if not core_skills:
            return 50  # Neutral score
        
        # Extract years from experience section
        year_pattern = r'\b(20\d{2})\b'
        years = [int(y) for y in re.findall(year_pattern, text)]
        
        if not years:
            return 50  # Cannot determine
        
        most_recent_year = max(years)
        current_year = 2026  # Update this dynamically in production
        
        # If most recent experience is within 2 years, assume skills are current
        if current_year - most_recent_year <= 2:
            return 100
        elif current_year - most_recent_year <= 4:
            return 75
        elif current_year - most_recent_year <= 6:
            return 50
        else:
            return 25
    
    def _identify_missing_core_skills(self, core_found: Set[str]) -> List[str]:
        """Identify important missing core skills."""
        all_core = self.field_config.core_keywords
        missing = all_core - core_found
        
        # Return top 5 most important missing skills
        # In a real system, this would be ranked by job posting frequency
        return list(missing)[:5]
    
    def _identify_strengths(
        self, core_coverage: float, depth_score: int, core_found: Set[str]
    ) -> List[str]:
        """Identify skill-related strengths."""
        strengths = []
        
        if core_coverage >= 70:
            strengths.append(
                f"Strong coverage of {self.field_config.name} core skills ({len(core_found)} skills)"
            )
        
        if depth_score >= 70:
            strengths.append("Clear evidence of skill proficiency and depth")
        
        if len(core_found) >= 15:
            strengths.append("Diverse technical skill set")
        
        return strengths
    
    def _generate_improvements(
        self, core_coverage: float, depth_score: int,
        supporting_score: int, missing_core: List[str]
    ) -> List[str]:
        """Generate skill improvement recommendations."""
        improvements = []
        
        if core_coverage < 60:
            if missing_core:
                improvements.append(
                    f"Add these high-value skills if you have them: {', '.join(missing_core[:3])}"
                )
            improvements.append(
                f"Increase coverage of {self.field_config.name} core skills"
            )
        
        if depth_score < 50:
            improvements.append(
                "Show skill depth - add years of experience, proficiency levels, or certifications"
            )
            improvements.append(
                "Demonstrate skills through project descriptions, not just listing them"
            )
        
        if supporting_score < 40:
            improvements.append(
                "Add complementary skills that strengthen your core expertise"
            )
        
        return improvements


class ExperienceAnalyzer:
    """Analyzes work experience quality and relevance."""
    
    # Strong action verbs by category
    ACTION_VERBS = {
        'leadership': ['led', 'directed', 'managed', 'coordinated', 'mentored', 'guided', 'supervised'],
        'creation': ['built', 'developed', 'designed', 'architected', 'created', 'established', 'launched'],
        'improvement': ['optimized', 'enhanced', 'streamlined', 'improved', 'increased', 'reduced', 'accelerated'],
        'analysis': ['analyzed', 'evaluated', 'assessed', 'investigated', 'researched', 'identified'],
        'delivery': ['shipped', 'delivered', 'implemented', 'deployed', 'released', 'executed']
    }
    
    # Weak verbs to avoid
    WEAK_VERBS = [
        'responsible for', 'worked on', 'helped with', 'involved in',
        'participated in', 'assisted', 'did', 'made', 'used'
    ]
    
    # Quantification patterns
    METRIC_PATTERNS = [
        r'\d+%',  # Percentages
        r'\$\d+[KMB]?',  # Dollar amounts
        r'\d+[KMB]\+?\s*(users|requests|records|customers)',  # Scale
        r'\d+x',  # Multipliers
        r'\d+\s*(hours|days|weeks|months)',  # Time savings
    ]
    
    def __init__(self, field_key: str, experience_level: str):
        self.field_config = get_field_config(field_key)
        self.experience_level = experience_level
    
    def analyze(self, resume_text: str) -> Dict:
        """
        Analyze experience quality and impact.
        
        Returns:
            {
                'score': int (0-100),
                'breakdown': {
                    'alignment': int,
                    'impact': int,
                    'progression': int,
                    'relevance': int
                },
                'strengths': List[str],
                'improvements': List[str]
            }
        """
        # Analyze components
        alignment_score = self._analyze_role_alignment(resume_text)
        impact_score = self._analyze_impact_demonstration(resume_text)
        progression_score = self._analyze_career_progression(resume_text)
        relevance_score = self._analyze_relevance(resume_text)
        
        # Weighted total
        total_score = int(
            alignment_score * 0.30 +
            impact_score * 0.30 +
            progression_score * 0.20 +
            relevance_score * 0.20
        )
        
        strengths = self._identify_strengths(
            alignment_score, impact_score, progression_score
        )
        improvements = self._generate_improvements(
            alignment_score, impact_score, progression_score, resume_text
        )
        
        return {
            'score': total_score,
            'breakdown': {
                'alignment': alignment_score,
                'impact': impact_score,
                'progression': progression_score,
                'relevance': relevance_score
            },
            'strengths': strengths,
            'improvements': improvements
        }
    
    def _analyze_role_alignment(self, text: str) -> int:
        """Analyze if experience aligns with target role."""
        text_lower = text.lower()
        score = 0
        
        # Check for role-relevant keywords in experience section
        exp_section = self._extract_experience_section(text_lower)
        if not exp_section:
            return 30  # Partial credit if section not clearly identified
        
        # Count relevant keywords in experience
        relevant_keywords = self.field_config.core_keywords
        keyword_count = sum(1 for keyword in relevant_keywords if keyword in exp_section)
        
        # Score based on keyword density
        keyword_density = keyword_count / len(relevant_keywords) if relevant_keywords else 0
        score = int(keyword_density * 100)
        
        # Bonus for role-specific titles
        role_indicators = {
            'Software Engineering': ['engineer', 'developer', 'programmer', 'architect'],
            'Data Science': ['data scientist', 'ml engineer', 'analyst', 'researcher'],
            'Product Management': ['product manager', 'product owner', 'pm'],
            'UX/UI Design': ['designer', 'ux', 'ui', 'product designer'],
            'Marketing': ['marketing', 'growth', 'demand gen', 'content']
        }
        
        for field_name, titles in role_indicators.items():
            if field_name in self.field_config.name:
                if any(title in exp_section for title in titles):
                    score += 15
                break
        
        return min(100, score)
    
    def _analyze_impact_demonstration(self, text: str) -> int:
        """Analyze how well impact is demonstrated with metrics."""
        score = 0
        
        # Check for quantified achievements
        metric_count = 0
        for pattern in self.METRIC_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metric_count += len(matches)
        
        # Score based on metric frequency
        if metric_count >= 10:
            score += 40
        elif metric_count >= 6:
            score += 30
        elif metric_count >= 3:
            score += 20
        elif metric_count >= 1:
            score += 10
        
        # Check for strong action verbs
        strong_verb_count = 0
        for category, verbs in self.ACTION_VERBS.items():
            for verb in verbs:
                strong_verb_count += len(re.findall(r'\b' + verb + r'\b', text, re.IGNORECASE))
        
        if strong_verb_count >= 15:
            score += 30
        elif strong_verb_count >= 10:
            score += 20
        elif strong_verb_count >= 5:
            score += 10
        
        # Penalize weak verbs
        weak_verb_count = sum(
            len(re.findall(verb, text, re.IGNORECASE))
            for verb in self.WEAK_VERBS
        )
        if weak_verb_count > 5:
            score -= 10
        
        # Check for field-specific impact metrics
        impact_metrics = self.field_config.impact_metrics
        impact_metric_count = sum(
            1 for metric in impact_metrics
            if metric.lower() in text.lower()
        )
        if impact_metric_count >= 3:
            score += 20
        elif impact_metric_count >= 1:
            score += 10
        
        return min(100, max(0, score))
    
    def _analyze_career_progression(self, text: str) -> int:
        """Analyze career growth and progression."""
        # Extract job titles and years
        title_pattern = r'([A-Z][a-z]+\s+)*(?:Engineer|Developer|Manager|Designer|Analyst|Scientist|Lead|Senior|Junior|Associate)'
        titles = re.findall(title_pattern, text)
        
        if len(titles) < 2:
            return 50  # Cannot assess progression with < 2 roles
        
        score = 50  # Base score
        
        # Check for seniority progression
        seniority_levels = ['junior', 'associate', 'mid', 'senior', 'lead', 'principal', 'staff', 'director']
        text_lower = text.lower()
        
        levels_found = [level for level in seniority_levels if level in text_lower]
        if len(levels_found) >= 2:
            score += 25  # Shows progression
        
        # Check for increasing responsibility indicators
        responsibility_indicators = [
            'led team', 'managed', 'mentored', 'architected', 'directed'
        ]
        if any(indicator in text_lower for indicator in responsibility_indicators):
            score += 25
        
        return min(100, score)
    
    def _analyze_relevance(self, text: str) -> int:
        """Analyze recency and relevance of experience."""
        # Extract years
        year_pattern = r'\b(20\d{2})\b'
        years = [int(y) for y in re.findall(year_pattern, text)]
        
        if not years:
            return 50  # Cannot determine
        
        most_recent = max(years)
        current_year = 2026
        
        # Score based on recency
        years_since = current_year - most_recent
        if years_since <= 1:
            return 100
        elif years_since <= 2:
            return 90
        elif years_since <= 3:
            return 75
        elif years_since <= 5:
            return 60
        else:
            return 40
    
    def _extract_experience_section(self, text_lower: str) -> str:
        """Extract the experience section from resume."""
        exp_start = -1
        for header in ['experience', 'work history', 'employment', 'professional experience']:
            pos = text_lower.find(header)
            if pos != -1:
                exp_start = pos
                break
        
        if exp_start == -1:
            return text_lower  # Return full text if section not found
        
        # Find next major section
        next_sections = ['education', 'skills', 'projects', 'certifications']
        exp_end = len(text_lower)
        for section in next_sections:
            pos = text_lower.find(section, exp_start + 10)
            if pos != -1 and pos < exp_end:
                exp_end = pos
        
        return text_lower[exp_start:exp_end]
    
    def _identify_strengths(
        self, alignment: int, impact: int, progression: int
    ) -> List[str]:
        """Identify experience strengths."""
        strengths = []
        
        if alignment >= 75:
            strengths.append(f"Experience strongly aligns with {self.field_config.name}")
        
        if impact >= 70:
            strengths.append("Clear demonstration of quantified impact and achievements")
        
        if progression >= 75:
            strengths.append("Strong career progression and increasing responsibility")
        
        return strengths
    
    def _generate_improvements(
        self, alignment: int, impact: int, progression: int, text: str
    ) -> List[str]:
        """Generate experience improvement recommendations."""
        improvements = []
        
        if impact < 60:
            improvements.append(
                "Add specific metrics to quantify your impact (e.g., '40% faster', '2M users', '$500K saved')"
            )
            
            weak_verb_count = sum(
                len(re.findall(verb, text, re.IGNORECASE))
                for verb in self.WEAK_VERBS
            )
            if weak_verb_count > 3:
                improvements.append(
                    "Replace weak phrases like 'responsible for' with strong action verbs like 'led', 'built', 'optimized'"
                )
        
        if alignment < 60:
            improvements.append(
                f"Highlight experience more relevant to {self.field_config.name}"
            )
            improvements.append(
                "Emphasize projects and achievements that match the target role"
            )
        
        if progression < 50:
            improvements.append(
                "Show career growth - highlight increasing scope, leadership, or technical complexity"
            )
        
        return improvements
