"""
Field-Aware ATS Analysis Module

Analyzes resumes based on real ATS behavior and field-specific requirements.
Not generic scoring - grounded in how recruiters and ATS systems actually work.
"""

import re
from typing import Dict, List, Tuple, Set
from services.field_config import get_field_config, FieldConfig


class ATSAnalyzer:
    """
    Analyzes resume ATS compatibility based on field-specific criteria.
    Focuses on real ATS behavior, not myths.
    """
    
    # Common ATS parsing blockers
    ATS_BLOCKERS = {
        'tables': r'<table|\\begin{tabular}',
        'images': r'<img|\\includegraphics',
        'text_boxes': r'<textbox',
        'columns_indicator': r'\\begin{multicols}',
    }
    
    # Standard section headers ATS systems look for
    STANDARD_SECTIONS = {
        'contact': ['contact', 'personal information'],
        'summary': ['summary', 'profile', 'objective', 'about'],
        'experience': ['experience', 'work history', 'employment', 'professional experience'],
        'education': ['education', 'academic', 'qualifications'],
        'skills': ['skills', 'technical skills', 'competencies', 'expertise'],
        'projects': ['projects', 'portfolio', 'work samples']
    }
    
    def __init__(self, field_key: str = 'software_backend', experience_level: str = 'mid'):
        """
        Initialize ATS analyzer for specific field and experience level.
        
        Args:
            field_key: Target career field
            experience_level: 'entry', 'mid', or 'senior'
        """
        self.field_config = get_field_config(field_key)
        self.experience_level = experience_level
    
    def analyze(self, resume_text: str, parsed_data: Dict) -> Dict:
        """
        Comprehensive ATS analysis.
        
        Returns:
            {
                'score': int (0-100),
                'breakdown': {
                    'format': int,
                    'sections': int,
                    'keywords': int,
                    'contact': int
                },
                'blockers': List[str],
                'strengths': List[str],
                'improvements': List[str]
            }
        """
        # Calculate component scores
        format_score = self._score_format_parseability(resume_text)
        section_score = self._score_section_structure(resume_text, parsed_data)
        keyword_score = self._score_keyword_optimization(resume_text)
        contact_score = self._score_contact_info(resume_text, parsed_data)
        
        # Weighted total (based on ATS priorities)
        total_score = int(
            format_score * 0.30 +
            section_score * 0.25 +
            keyword_score * 0.25 +
            contact_score * 0.20
        )
        
        # Identify specific issues and strengths
        blockers = self._identify_blockers(resume_text)
        strengths = self._identify_strengths(
            format_score, section_score, keyword_score, contact_score
        )
        improvements = self._generate_improvements(
            format_score, section_score, keyword_score, contact_score,
            resume_text, parsed_data
        )
        
        return {
            'score': total_score,
            'breakdown': {
                'format': format_score,
                'sections': section_score,
                'keywords': keyword_score,
                'contact': contact_score
            },
            'blockers': blockers,
            'strengths': strengths,
            'improvements': improvements
        }
    
    def _score_format_parseability(self, text: str) -> int:
        """
        Score how easily ATS can parse the resume format.
        Real ATS systems struggle with tables, columns, images.
        """
        score = 100
        
        # Check for parsing blockers
        if re.search(self.ATS_BLOCKERS['tables'], text, re.IGNORECASE):
            score -= 15
        if re.search(self.ATS_BLOCKERS['images'], text, re.IGNORECASE):
            score -= 10
        if re.search(self.ATS_BLOCKERS['text_boxes'], text, re.IGNORECASE):
            score -= 10
        if re.search(self.ATS_BLOCKERS['columns_indicator'], text, re.IGNORECASE):
            score -= 10
        
        # Check for consistent date formatting
        date_patterns = re.findall(r'\b\d{1,2}/\d{4}\b|\b\d{4}\b|\b[A-Z][a-z]+ \d{4}\b', text)
        if date_patterns:
            # Check consistency
            formats = set()
            for date in date_patterns:
                if '/' in date:
                    formats.add('slash')
                elif re.match(r'^\d{4}$', date):
                    formats.add('year_only')
                else:
                    formats.add('month_year')
            
            if len(formats) > 1:
                score -= 5  # Inconsistent date formatting
        
        # Check text length (too short or too long)
        word_count = len(text.split())
        if word_count < 200:
            score -= 10  # Too sparse
        elif word_count > 1500:
            score -= 5  # Too verbose
        
        return max(0, score)
    
    def _score_section_structure(self, text: str, parsed_data: Dict) -> int:
        """
        Score presence and clarity of standard resume sections.
        ATS systems look for specific section headers.
        """
        score = 0
        text_lower = text.lower()
        
        # Check for required sections based on field
        required_sections = self.field_config.required_sections
        sections_found = []
        
        for section_type, headers in self.STANDARD_SECTIONS.items():
            if section_type in required_sections:
                found = any(header in text_lower for header in headers)
                if found:
                    sections_found.append(section_type)
                    score += 25 // len(required_sections)  # Distribute points
        
        # Bonus for clear section headers (all caps or bold indicators)
        section_header_pattern = r'\n[A-Z\s]{3,}\n|^[A-Z\s]{3,}\n'
        clear_headers = re.findall(section_header_pattern, text, re.MULTILINE)
        if len(clear_headers) >= 3:
            score += 10
        
        # Check for logical order (Experience before Education for experienced, vice versa for entry)
        exp_pos = text_lower.find('experience')
        edu_pos = text_lower.find('education')
        
        if exp_pos != -1 and edu_pos != -1:
            if self.experience_level == 'entry' and edu_pos < exp_pos:
                score += 5
            elif self.experience_level in ['mid', 'senior'] and exp_pos < edu_pos:
                score += 5
        
        return min(100, score)
    
    def _score_keyword_optimization(self, text: str) -> int:
        """
        Score keyword presence without encouraging stuffing.
        Based on field-specific core and supporting keywords.
        """
        text_lower = text.lower()
        
        # Count core keywords
        core_keywords = self.field_config.core_keywords
        core_found = sum(1 for keyword in core_keywords if keyword in text_lower)
        core_coverage = (core_found / len(core_keywords)) * 100 if core_keywords else 0
        
        # Count supporting keywords
        supporting_keywords = self.field_config.supporting_keywords
        supporting_found = sum(1 for keyword in supporting_keywords if keyword in text_lower)
        supporting_coverage = (supporting_found / len(supporting_keywords)) * 100 if supporting_keywords else 0
        
        # Core keywords are more important (70% weight)
        keyword_score = int(core_coverage * 0.70 + supporting_coverage * 0.30)
        
        # Penalize keyword stuffing (same keyword repeated too many times)
        for keyword in list(core_keywords)[:10]:  # Check top keywords
            count = text_lower.count(keyword)
            if count > 8:  # Excessive repetition
                keyword_score -= 5
        
        # Bonus for keyword context (in bullet points, not just listed)
        bullet_pattern = r'[•\-\*]\s*(.+)'
        bullets = re.findall(bullet_pattern, text)
        if bullets:
            keywords_in_context = sum(
                1 for bullet in bullets
                for keyword in list(core_keywords)[:20]
                if keyword in bullet.lower()
            )
            if keywords_in_context > 5:
                keyword_score += 10
        
        return min(100, max(0, keyword_score))
    
    def _score_contact_info(self, text: str, parsed_data: Dict) -> int:
        """
        Score contact information completeness and parseability.
        ATS must be able to extract email, phone, LinkedIn.
        """
        score = 0
        
        # Email (required)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, text):
            score += 30
        
        # Phone (required)
        phone_pattern = r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b|\(\d{3}\)\s*\d{3}[-.\s]?\d{4}'
        if re.search(phone_pattern, text):
            score += 25
        
        # LinkedIn (highly recommended)
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        if re.search(linkedin_pattern, text, re.IGNORECASE):
            score += 25
        
        # GitHub/Portfolio (field-specific)
        if self.field_config.name.startswith('Software') or 'Data Science' in self.field_config.name:
            github_pattern = r'github\.com/[\w-]+'
            if re.search(github_pattern, text, re.IGNORECASE):
                score += 20
        elif 'Design' in self.field_config.name:
            portfolio_keywords = ['portfolio', 'behance', 'dribbble']
            if any(keyword in text.lower() for keyword in portfolio_keywords):
                score += 20
        else:
            score += 10  # Partial credit for other fields
        
        # Location (city, state) - not full address
        location_pattern = r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b'
        if re.search(location_pattern, text):
            score += 10
        
        return min(100, score)
    
    def _identify_blockers(self, text: str) -> List[str]:
        """Identify specific ATS parsing blockers."""
        blockers = []
        
        if re.search(self.ATS_BLOCKERS['tables'], text, re.IGNORECASE):
            blockers.append("Table-based layout detected - ATS may misread content order")
        
        if re.search(self.ATS_BLOCKERS['images'], text, re.IGNORECASE):
            blockers.append("Images or graphics detected - ATS cannot parse visual content")
        
        if re.search(self.ATS_BLOCKERS['columns_indicator'], text, re.IGNORECASE):
            blockers.append("Multi-column layout detected - text order may be scrambled by ATS")
        
        # Check for contact info in header/footer (common mistake)
        lines = text.split('\n')
        if len(lines) > 10:
            header_text = ' '.join(lines[:3]).lower()
            if 'page' in header_text or 'resume' in header_text:
                blockers.append("Contact information may be in header - ATS often ignores headers")
        
        return blockers
    
    def _identify_strengths(
        self, format_score: int, section_score: int,
        keyword_score: int, contact_score: int
    ) -> List[str]:
        """Identify specific ATS strengths."""
        strengths = []
        
        if format_score >= 90:
            strengths.append("Clean, parseable format - ATS will read this easily")
        
        if section_score >= 85:
            strengths.append("Well-organized sections with clear headers")
        
        if keyword_score >= 70:
            strengths.append(f"Strong keyword coverage for {self.field_config.name}")
        
        if contact_score >= 90:
            strengths.append("Complete contact information - easy for recruiters to reach you")
        
        return strengths
    
    def _generate_improvements(
        self, format_score: int, section_score: int,
        keyword_score: int, contact_score: int,
        text: str, parsed_data: Dict
    ) -> List[str]:
        """Generate specific, actionable ATS improvements."""
        improvements = []
        
        # Format improvements
        if format_score < 80:
            if re.search(self.ATS_BLOCKERS['tables'], text, re.IGNORECASE):
                improvements.append(
                    "Remove table-based layout - use simple text formatting with clear section breaks"
                )
            if re.search(self.ATS_BLOCKERS['columns_indicator'], text, re.IGNORECASE):
                improvements.append(
                    "Convert multi-column layout to single column - ATS reads left-to-right, top-to-bottom"
                )
        
        # Section improvements
        if section_score < 70:
            missing_sections = []
            text_lower = text.lower()
            for section in self.field_config.required_sections:
                headers = self.STANDARD_SECTIONS.get(section, [])
                if not any(header in text_lower for header in headers):
                    missing_sections.append(section.title())
            
            if missing_sections:
                improvements.append(
                    f"Add missing sections: {', '.join(missing_sections)}"
                )
            
            improvements.append(
                "Use standard section headers in ALL CAPS or bold (e.g., EXPERIENCE, EDUCATION, SKILLS)"
            )
        
        # Keyword improvements
        if keyword_score < 60:
            core_keywords = list(self.field_config.core_keywords)[:10]
            improvements.append(
                f"Increase relevant keyword coverage - consider adding: {', '.join(core_keywords[:5])}"
            )
            improvements.append(
                "Incorporate keywords naturally in your experience bullets, not just in a skills list"
            )
        
        # Contact improvements
        if contact_score < 80:
            if not re.search(r'linkedin\.com', text, re.IGNORECASE):
                improvements.append("Add LinkedIn profile URL")
            
            if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
                improvements.append("Ensure email address is clearly visible")
            
            if self.field_config.name.startswith('Software') and not re.search(r'github\.com', text, re.IGNORECASE):
                improvements.append("Add GitHub profile to showcase your code")
        
        return improvements


def analyze_ats_compatibility(
    resume_text: str,
    parsed_data: Dict,
    field_key: str = 'software_backend',
    experience_level: str = 'mid'
) -> Dict:
    """
    Convenience function for ATS analysis.
    
    Args:
        resume_text: Full resume text
        parsed_data: Parsed resume data
        field_key: Target career field
        experience_level: Career stage
    
    Returns:
        ATS analysis results
    """
    analyzer = ATSAnalyzer(field_key, experience_level)
    return analyzer.analyze(resume_text, parsed_data)
