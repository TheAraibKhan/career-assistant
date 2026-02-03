"""ATS (Applicant Tracking System) Resume Scoring Service."""

import re
from typing import Dict, List, Tuple


class ATSScorer:
    """Score resumes based on ATS (Applicant Tracking System) standards."""
    
    # ATS keywords that improve parsing and match
    ATS_KEYWORDS = {
        'contact': ['phone', 'email', 'linkedin', 'github', 'portfolio', 'website'],
        'format': ['section', 'header', 'bold', 'standard', 'clean'],
        'skills': ['technical skills', 'hard skills', 'software', 'tools', 'languages'],
        'experience': ['work experience', 'professional experience', 'employment', 'position', 'role'],
        'education': ['education', 'bachelor', 'master', 'phd', 'degree', 'university', 'college'],
        'achievements': ['achievement', 'accomplishment', 'result', 'success', 'improved', 'increased'],
        'metrics': ['%', '$', 'increased', 'decreased', 'improved', 'reduced', 'grew', '2x', '3x']
    }
    
    # Common ATS parsing blockers
    ATS_BLOCKERS = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', 'image', 'logo'],
        'tables': ['table', 'tabular'],
        'graphics': ['chart', 'graph', 'visual', 'infographic'],
        'headers_footers': ['header', 'footer', 'page number'],
        'special_chars': ['©', '®', '™', '†', '‡'],
        'columns': ['column', 'columnar', 'multi-column'],
    }
    
    @staticmethod
    def score_resume(parsed_resume_data: Dict) -> Dict:
        """Calculate comprehensive ATS score (0-100)."""
        
        skills = parsed_resume_data.get('skills', [])
        has_experience = parsed_resume_data.get('has_experience', False)
        education = parsed_resume_data.get('education', [])
        text_length = parsed_resume_data.get('text_length', 0)
        text = parsed_resume_data.get('text', '')
        
        score = 0
        categories = {}
        
        # 1. Contact Information (10 points)
        contact_score = ATSScorer._score_contact_info(text)
        score += contact_score
        categories['contact_info'] = contact_score
        
        # 2. Professional Summary/Objective (5 points)
        summary_score = ATSScorer._score_summary(text)
        score += summary_score
        categories['summary'] = summary_score
        
        # 3. Skills Section (15 points)
        skills_score = ATSScorer._score_skills_section(skills, text)
        score += skills_score
        categories['skills'] = skills_score
        
        # 4. Work Experience (20 points)
        experience_score = ATSScorer._score_experience(text, has_experience)
        score += experience_score
        categories['experience'] = experience_score
        
        # 5. Education (10 points)
        education_score = ATSScorer._score_education(education, text)
        score += education_score
        categories['education'] = education_score
        
        # 6. Quantifiable Achievements (15 points)
        metrics_score = ATSScorer._score_metrics(text)
        score += metrics_score
        categories['metrics'] = metrics_score
        
        # 7. Format & Readability (10 points)
        format_score = ATSScorer._score_format(text_length, text)
        score += format_score
        categories['format'] = format_score
        
        # 8. Keywords & Relevance (15 points)
        keywords_score = ATSScorer._score_keywords(text, skills)
        score += keywords_score
        categories['keywords'] = keywords_score
        
        return {
            'ats_score': min(100, score),
            'categories': categories,
            'recommendations': ATSScorer._generate_recommendations(score, categories, text, skills),
            'blockers': ATSScorer._identify_blockers(text),
            'strengths': ATSScorer._identify_strengths(score, categories)
        }
    
    @staticmethod
    def _score_contact_info(text: str) -> int:
        """Score presence and clarity of contact information."""
        score = 0
        text_lower = text.lower()
        
        # Email
        if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text):
            score += 3
        
        # Phone
        if re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text):
            score += 2
        
        # LinkedIn
        if 'linkedin' in text_lower:
            score += 2
        
        # GitHub/Portfolio
        if 'github' in text_lower or 'portfolio' in text_lower:
            score += 2
        
        # Location/City
        if re.search(r'\b(?:New York|Los Angeles|Chicago|Houston|Phoenix|Philadelphia|San Antonio|San Diego|Dallas|San Jose)\b', text, re.IGNORECASE):
            score += 1
        
        return min(score, 10)
    
    @staticmethod
    def _score_summary(text: str) -> int:
        """Score presence and quality of professional summary."""
        score = 0
        text_lower = text.lower()
        
        # Check for summary/objective section
        if any(keyword in text_lower for keyword in ['professional summary', 'objective', 'about', 'profile']):
            score += 3
            
            # Check length (should be 2-3 sentences)
            summary_match = re.search(
                r'(?:professional summary|objective|about|profile)[:\s]+([^\.]*\.){2,3}',
                text_lower, re.IGNORECASE
            )
            if summary_match:
                score += 2
        
        return min(score, 5)
    
    @staticmethod
    def _score_skills_section(skills: List[str], text: str) -> int:
        """Score skills section presence and clarity."""
        score = 0
        text_lower = text.lower()
        
        # Dedicated skills section
        if 'skills' in text_lower or 'technical skills' in text_lower:
            score += 5
        
        # Number of skills
        if len(skills) >= 10:
            score += 5
        elif len(skills) >= 5:
            score += 3
        elif len(skills) > 0:
            score += 1
        
        # Skills properly categorized
        if any(cat in text_lower for cat in ['programming', 'languages', 'tools', 'software', 'frameworks']):
            score += 3
        
        # Skill keywords appear multiple times (shows reinforcement)
        if len(skills) > 0:
            skill_count = sum(1 for skill in skills if text_lower.count(skill.lower()) > 1)
            if skill_count >= len(skills) * 0.5:  # At least 50% of skills mentioned multiple times
                score += 2
        
        return min(score, 15)
    
    @staticmethod
    def _score_experience(text: str, has_experience: bool) -> int:
        """Score work experience section."""
        score = 0
        text_lower = text.lower()
        
        if has_experience or any(keyword in text_lower for keyword in ['work experience', 'professional experience', 'employment']):
            score += 5
        
        # Date ranges
        year_pattern = r'(19|20)\d{2}'
        years = re.findall(year_pattern, text)
        if len(years) >= 4:  # At least 2 date ranges
            score += 5
        elif len(years) >= 2:
            score += 3
        
        # Company names
        company_keywords = ['inc', 'corp', 'ltd', 'llc', 'company', 'corporation']
        if any(keyword in text_lower for keyword in company_keywords):
            score += 3
        
        # Job titles
        job_keywords = ['engineer', 'developer', 'manager', 'analyst', 'specialist', 'director', 'lead', 'architect']
        if any(keyword in text_lower for keyword in job_keywords):
            score += 4
        
        # Action verbs
        action_verbs = ['led', 'managed', 'developed', 'designed', 'implemented', 'improved', 'created', 'built', 'delivered']
        if sum(1 for verb in action_verbs if verb in text_lower) >= 3:
            score += 3
        
        return min(score, 20)
    
    @staticmethod
    def _score_education(education: List[str], text: str) -> int:
        """Score education section."""
        score = 0
        text_lower = text.lower()
        
        if 'education' in text_lower:
            score += 3
        
        # Degree present
        if len(education) > 0:
            score += 4
        
        # Major/Field of study
        if any(field in text_lower for field in ['computer science', 'engineering', 'mathematics', 'business', 'data science']):
            score += 2
        
        # University/College name
        if any(keyword in text_lower for keyword in ['university', 'college', 'institute']):
            score += 1
        
        return min(score, 10)
    
    @staticmethod
    def _score_metrics(text: str) -> int:
        """Score presence of quantifiable achievements."""
        score = 0
        text_lower = text.lower()
        
        # Numbers and percentages
        numbers = re.findall(r'\d+[%x]?', text)
        if len(numbers) >= 10:
            score += 5
        elif len(numbers) >= 5:
            score += 3
        elif len(numbers) > 0:
            score += 1
        
        # Action words with metrics
        metric_phrases = [
            r'increased.*\d+',
            r'improved.*\d+',
            r'reduced.*\d+',
            r'grew.*\d+',
            r'saved.*\$',
            r'generated.*\$',
            r'delivered.*\d+',
            r'managed.*\d+'
        ]
        metric_count = sum(1 for phrase in metric_phrases if re.search(phrase, text_lower))
        if metric_count >= 3:
            score += 5
        elif metric_count >= 1:
            score += 3
        
        # Dollar amounts
        if re.search(r'\$\d+', text):
            score += 3
        
        # ROI/Performance metrics
        if any(keyword in text_lower for keyword in ['roi', 'conversion', 'efficiency', 'productivity', 'revenue']):
            score += 2
        
        return min(score, 15)
    
    @staticmethod
    def _score_format(text_length: int, text: str) -> int:
        """Score resume format and readability."""
        score = 0
        
        # Length (1-2 pages = 500-1000 words for 1 page, 1000-2000 for 2 pages)
        if 1000 <= text_length <= 2000:
            score += 5
        elif 500 <= text_length < 3000:
            score += 3
        elif text_length >= 3000:
            score += 2  # Too long
        else:
            score += 1  # Too short
        
        # Line breaks and structure
        lines = text.split('\n')
        if 20 <= len(lines) <= 100:
            score += 3
        
        # Section headers (clear structure)
        headers = ['experience', 'education', 'skills', 'summary', 'projects', 'certifications']
        if sum(1 for header in headers if header in text.lower()) >= 3:
            score += 2
        
        return min(score, 10)
    
    @staticmethod
    def _score_keywords(text: str, skills: List[str]) -> int:
        """Score keyword optimization and relevance."""
        score = 0
        text_lower = text.lower()
        
        # Industry keywords
        industry_count = sum(1 for keyword in ATSScorer.ATS_KEYWORDS['skills'] 
                           if keyword in text_lower)
        if industry_count >= 3:
            score += 5
        
        # Action verbs
        action_verbs = ['achieved', 'led', 'managed', 'designed', 'implemented', 'developed']
        action_count = sum(1 for verb in action_verbs if verb in text_lower)
        if action_count >= 4:
            score += 5
        
        # Skills reinforcement
        if len(skills) > 0:
            skill_mentions = sum(1 for skill in skills if text_lower.count(skill.lower()) > 1)
            if skill_mentions >= len(skills) * 0.7:
                score += 3
        
        # Technical depth
        if any(keyword in text_lower for keyword in ['api', 'database', 'framework', 'architecture', 'algorithm']):
            score += 2
        
        return min(score, 15)
    
    @staticmethod
    def _generate_recommendations(score: int, categories: Dict, text: str, skills: List[str]) -> List[str]:
        """Generate ATS improvement recommendations."""
        recommendations = []
        text_lower = text.lower()
        
        if categories.get('contact_info', 0) < 8:
            recommendations.append("Add clear contact information (email, phone, LinkedIn) at the top")
        
        if categories.get('summary', 0) < 4:
            recommendations.append("Add a professional summary (2-3 sentences) highlighting your career focus")
        
        if categories.get('skills', 0) < 12:
            recommendations.append("Create a dedicated 'Skills' section with at least 10-15 technical skills")
        
        if categories.get('experience', 0) < 15:
            recommendations.append("Clearly list work experience with job titles, company names, and dates")
        
        if categories.get('education', 0) < 8:
            recommendations.append("Include your education details (degree, field, university)")
        
        if categories.get('metrics', 0) < 10:
            recommendations.append("Add quantifiable achievements with numbers, percentages, or dollar amounts")
        
        if categories.get('format', 0) < 7:
            recommendations.append("Optimize resume length (keep to 1-2 pages with clear sections)")
        
        if categories.get('keywords', 0) < 12:
            recommendations.append("Add industry-specific keywords related to your target roles")
        
        if score < 50:
            recommendations.insert(0, "This resume needs significant restructuring for ATS optimization")
        elif score < 70:
            recommendations.insert(0, "This resume has moderate ATS issues that should be addressed")
        
        return recommendations[:5]  # Top 5 recommendations
    
    @staticmethod
    def _identify_blockers(text: str) -> List[str]:
        """Identify ATS-blocking elements."""
        blockers = []
        text_lower = text.lower()
        
        # Check for common blockers
        if re.search(r'\.jpg|\.jpeg|\.png|\.gif|image|logo', text_lower):
            blockers.append("Contains images or graphics (may not parse)")
        
        if re.search(r'table|tabular', text_lower):
            blockers.append("Uses tables for layout (may cause parsing issues)")
        
        if re.search(r'©|®|™', text):
            blockers.append("Contains special characters that ATS may not recognize")
        
        if 'column' in text_lower:
            blockers.append("Uses columnar layout (may confuse ATS parsing)")
        
        if re.search(r'[A-Z]{10,}', text):  # ALL CAPS sections
            blockers.append("Contains excessive all-caps text")
        
        return blockers
    
    @staticmethod
    def _identify_strengths(score: int, categories: Dict) -> List[str]:
        """Identify ATS strengths in the resume."""
        strengths = []
        
        if categories.get('contact_info', 0) >= 8:
            strengths.append("Excellent contact information placement")
        
        if categories.get('skills', 0) >= 12:
            strengths.append("Strong skills section with good coverage")
        
        if categories.get('experience', 0) >= 15:
            strengths.append("Clear work experience with proper formatting")
        
        if categories.get('metrics', 0) >= 10:
            strengths.append("Good use of quantifiable achievements")
        
        if categories.get('keywords', 0) >= 12:
            strengths.append("Excellent keyword optimization")
        
        if score >= 80:
            strengths.append("Overall ATS-friendly resume structure")
        
        return strengths if strengths else ["Resume has potential for ATS parsing"]


def get_ats_score(parsed_resume_data: Dict) -> Dict:
    """Get ATS score for a parsed resume."""
    return ATSScorer.score_resume(parsed_resume_data)
