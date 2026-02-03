"""Resume Parser Service - Extract skills and data from resumes."""
import os
import json
import hashlib
from datetime import datetime
from database.db import get_db


class ResumeParser:
    """Parse resumes and extract key information."""
    
    # Common skill keywords
    TECHNICAL_SKILLS = {
        'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin'],
        'web': ['html', 'css', 'react', 'vue', 'angular', 'node.js', 'express', 'django', 'flask', 'asp.net'],
        'data': ['sql', 'pandas', 'numpy', 'spark', 'hadoop', 'kafka', 'mongodb', 'mysql', 'postgresql'],
        'ml': ['tensorflow', 'pytorch', 'scikit-learn', 'keras', 'nltk', 'spacy', 'opencv'],
        'devops': ['docker', 'kubernetes', 'jenkins', 'aws', 'azure', 'gcp', 'terraform', 'ansible'],
        'tools': ['git', 'jira', 'confluence', 'slack', 'figma', 'adobe', 'excel', 'tableau']
    }
    
    SOFT_SKILLS = [
        'leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking',
        'project management', 'agile', 'scrum', 'analytical', 'strategic thinking',
        'negotiation', 'presentation', 'creativity', 'adaptability', 'time management'
    ]
    
    def __init__(self):
        self.extracted_data = {
            'skills': [],
            'technical_skills': [],
            'soft_skills': [],
            'experience_years': 0,
            'education': [],
            'job_titles': [],
            'industries': [],
            'confidence': 0
        }
    
    def parse_text(self, text):
        """Parse resume text and extract data."""
        if not text:
            return self.extracted_data
        
        text_lower = text.lower()
        
        # Extract technical skills
        self.extracted_data['technical_skills'] = self._extract_technical_skills(text_lower)
        
        # Extract soft skills
        self.extracted_data['soft_skills'] = self._extract_soft_skills(text_lower)
        
        # Extract experience level
        self.extracted_data['experience_years'] = self._estimate_experience(text_lower)
        
        # Extract education
        self.extracted_data['education'] = self._extract_education(text_lower)
        
        # Extract job titles
        self.extracted_data['job_titles'] = self._extract_job_titles(text_lower)
        
        # Extract industries
        self.extracted_data['industries'] = self._extract_industries(text_lower)
        
        # Combine skills
        self.extracted_data['skills'] = list(set(
            self.extracted_data['technical_skills'] + 
            self.extracted_data['soft_skills']
        ))
        
        # Calculate confidence
        self.extracted_data['confidence'] = self._calculate_confidence()
        
        return self.extracted_data
    
    def _extract_technical_skills(self, text):
        """Extract technical skills from text."""
        skills = []
        for category, skill_list in self.TECHNICAL_SKILLS.items():
            for skill in skill_list:
                if skill in text:
                    skills.append(skill.title())
        return list(set(skills))
    
    def _extract_soft_skills(self, text):
        """Extract soft skills from text."""
        skills = []
        for skill in self.SOFT_SKILLS:
            if skill in text:
                skills.append(skill.title())
        return list(set(skills))
    
    def _estimate_experience(self, text):
        """Estimate years of experience from text."""
        # Look for year patterns and experience indicators
        import re
        
        # Find year ranges
        year_matches = re.findall(r'(20\d{2}|19\d{2})', text)
        if len(year_matches) >= 2:
            years = int(max(year_matches)) - int(min(year_matches))
            return min(years, 40)  # Cap at 40 years
        
        # Look for experience descriptions
        if '10+ years' in text or '10 years' in text:
            return 10
        elif '5-10' in text:
            return 7
        elif '3-5' in text or '5 years' in text:
            return 4
        elif '1-3' in text or '2 years' in text:
            return 2
        elif 'entry' in text or 'recent grad' in text:
            return 0
        
        return 1  # Default to 1 year if nothing found
    
    def _extract_education(self, text):
        """Extract education information."""
        degrees = []
        degree_keywords = ['bachelor', 'master', 'phd', 'b.s.', 'm.s.', 'b.a.', 'm.a.', 'diploma', 'associate']
        
        for keyword in degree_keywords:
            if keyword in text:
                degrees.append(keyword.title())
        
        return list(set(degrees))
    
    def _extract_job_titles(self, text):
        """Extract potential job titles."""
        titles = []
        common_titles = [
            'software engineer', 'data scientist', 'product manager', 'designer', 'analyst',
            'developer', 'engineer', 'manager', 'consultant', 'specialist',
            'architect', 'lead', 'director', 'coordinator', 'representative'
        ]
        
        for title in common_titles:
            if title in text:
                titles.append(title.title())
        
        return list(set(titles))
    
    def _extract_industries(self, text):
        """Extract industry experience."""
        industries = []
        industry_keywords = [
            'tech', 'finance', 'healthcare', 'retail', 'manufacturing',
            'education', 'government', 'startup', 'enterprise', 'consulting'
        ]
        
        for industry in industry_keywords:
            if industry in text:
                industries.append(industry.title())
        
        return list(set(industries))
    
    def _calculate_confidence(self):
        """Calculate confidence score of extraction."""
        score = 0
        
        if len(self.extracted_data['technical_skills']) > 2:
            score += 30
        elif len(self.extracted_data['technical_skills']) > 0:
            score += 15
        
        if len(self.extracted_data['soft_skills']) > 2:
            score += 20
        elif len(self.extracted_data['soft_skills']) > 0:
            score += 10
        
        if self.extracted_data['experience_years'] > 0:
            score += 20
        
        if len(self.extracted_data['education']) > 0:
            score += 10
        
        if len(self.extracted_data['job_titles']) > 0:
            score += 10
        
        return min(score, 100)
    
    def match_against_role(self, role_skills):
        """Calculate match percentage against a role."""
        if not role_skills:
            return 0
        
        matched = 0
        for skill in self.extracted_data['skills']:
            if any(s.lower() in skill.lower() or skill.lower() in s.lower() 
                   for s in role_skills):
                matched += 1
        
        return round((matched / len(role_skills) * 100)) if role_skills else 0
    
    def get_skill_gaps(self, role_skills):
        """Identify missing skills for a role."""
        resume_skills_lower = [s.lower() for s in self.extracted_data['skills']]
        gaps = []
        
        for skill in role_skills:
            if not any(skill.lower() in rs or rs in skill.lower() for rs in resume_skills_lower):
                gaps.append(skill)
        
        return gaps


def parse_resume_from_file(file_path):
    """Parse resume file (text or PDF path)."""
    parser = ResumeParser()
    
    try:
        # For now, support text files
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return parser.parse_text(text)
        
        # PDF support would require pypdf or similar
        # For now, return empty with note
        return parser.extracted_data
    
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return parser.extracted_data


def cache_resume_parse(file_hash, parsed_data):
    """Cache parsed resume data in database."""
    db = get_db()
    now = datetime.utcnow().isoformat()
    
    try:
        db.execute(
            '''INSERT OR REPLACE INTO resume_cache (file_hash, parsed_skills, parsed_experience, parsed_education, created_at)
               VALUES (?, ?, ?, ?, ?)''',
            (file_hash, json.dumps(parsed_data.get('skills', [])), 
             parsed_data.get('experience_years'),
             json.dumps(parsed_data.get('education', [])),
             now)
        )
        db.commit()
        return True
    except Exception as e:
        print(f"Error caching resume: {e}")
        return False


def get_cached_resume(file_hash):
    """Get cached resume parse data."""
    db = get_db()
    try:
        result = db.execute(
            'SELECT parsed_skills, parsed_experience, parsed_education FROM resume_cache WHERE file_hash = ?',
            (file_hash,)
        ).fetchone()
        
        if result:
            return {
                'skills': json.loads(result['parsed_skills']),
                'experience_years': result['parsed_experience'],
                'education': json.loads(result['parsed_education']),
                'cached': True
            }
    except Exception as e:
        print(f"Error getting cached resume: {e}")
    
    return None


def calculate_file_hash(content):
    """Calculate hash of file content for caching."""
    return hashlib.md5(content.encode() if isinstance(content, str) else content).hexdigest()
