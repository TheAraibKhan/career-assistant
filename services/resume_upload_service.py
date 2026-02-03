"""Enhanced resume upload with human-centered UX and validation."""
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from services.resume_parser import parse_resume, get_file_hash, cache_resume_parse, get_cached_parse


class ResumeUploadService:
    """Manage resume uploads with user-friendly feedback."""
    
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    UPLOAD_FOLDER = 'uploads'
    
    @staticmethod
    def validate_resume_file(file, filename):
        """Validate resume file with user-friendly error messages."""
        
        errors = []
        warnings = []
        
        # Check filename
        if not filename:
            errors.append('Please select a file to upload')
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Check file extension
        _, ext = os.path.splitext(filename)
        ext = ext.lower().strip('.')
        
        if ext not in ResumeUploadService.ALLOWED_EXTENSIONS:
            errors.append(
                f'File type ".{ext}" is not supported. Please upload PDF, DOCX, or TXT files.'
            )
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size == 0:
            errors.append('The file appears to be empty. Please check and try again.')
        
        if file_size > ResumeUploadService.MAX_FILE_SIZE:
            errors.append(
                f'File is too large ({file_size / 1024 / 1024:.1f}MB). Maximum size is 5MB.'
            )
        
        # Warnings
        if file_size < 1024:
            warnings.append('This file is very small. Make sure it uploaded correctly.')
        
        if file_size > 3 * 1024 * 1024:
            warnings.append('This is a large file. Processing may take longer.')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'file_size': file_size,
            'extension': ext
        }
    
    @staticmethod
    def parse_with_feedback(file_path, filename):
        """Parse resume and provide human-friendly feedback."""
        
        try:
            # Check cache first
            file_hash = get_file_hash(file_path)
            cached = get_cached_parse(file_hash)
            
            if cached:
                # Reconstruct insights from cached parsed data to match fresh parse
                cached_parsed = {
                    'skills': cached['skills'],
                    'has_experience': cached['experience'].get('has_experience', False),
                    'education': cached['education'],
                    'text_length': cached.get('text_length', 0)
                }
                insights = ResumeUploadService.generate_insights(cached_parsed)
                
                return {
                    'success': True,
                    'skills': cached['skills'],
                    'experience': cached['experience'],
                    'education': cached['education'],
                    'source': 'cache',
                    'message': f'Loaded from cache - {len(cached["skills"])} skills detected',
                    'feedback': {
                        'skills_found': len(cached['skills']),
                        'has_experience': cached['experience'].get('has_experience', False),
                        'education_detected': len(cached['education'])
                    },
                    'insights': insights,
                    'extracted_at': cached.get('extracted_at')
                }
            
            # Parse resume
            parsed = parse_resume(file_path)
            
            if not parsed:
                return {
                    'success': False,
                    'error': 'Unable to extract text from this file. Please ensure it\'s a valid resume file.',
                    'hint': 'Try converting to PDF or TXT format and upload again.'
                }
            
            # Generate user-friendly feedback
            feedback = {
                'skills_found': len(parsed['skills']),
                'has_experience': parsed['has_experience'],
                'education_detected': len(parsed['education']),
                'text_length': parsed['text_length']
            }
            
            # Create insights
            insights = ResumeUploadService.generate_insights(parsed)
            
            # Cache the result
            cache_resume_parse(file_hash, parsed)
            
            return {
                'success': True,
                'skills': parsed['skills'],
                'experience': parsed.get('has_experience'),
                'education': parsed.get('education', []),
                'message': f'Successfully processed resume - Found {len(parsed["skills"])} skills',
                'feedback': feedback,
                'insights': insights,
                'source': 'parsed',
                'extracted_at': parsed.get('extracted_at'),
                'text_length': parsed.get('text_length'),
                'text': parsed.get('text', '')
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': 'Error processing your resume. Please try again.',
                'details': str(e),
                'hint': 'If this error persists, please contact support or try a different file format.'
            }
    
    @staticmethod
    def generate_insights(parsed_data):
        """Generate insights and suggestions from parsed resume."""
        
        skills = parsed_data.get('skills', [])
        has_experience = parsed_data.get('has_experience', False)
        education = parsed_data.get('education', [])
        
        insights_list = []
        suggestions = []
        
        # Skill-based insights
        if len(skills) == 0:
            suggestions.append('No skills detected. Please review your resume and ensure technical skills are clearly listed.')
        elif len(skills) < 3:
            suggestions.append(f'Only {len(skills)} skills detected. Add more technical keywords to improve ATS matching.')
        else:
            insights_list.append(f'{len(skills)} technical skills identified - good coverage.')
        
        # Experience insights
        if has_experience:
            insights_list.append('Work experience information detected.')
        else:
            suggestions.append('Add work experience with company names, job titles, and dates.')
        
        # Education insights
        if education:
            insights_list.append(f'Education detected: {", ".join(education)}')
        else:
            suggestions.append('Include education information (degree, institution).')
        
        # Formatting insights
        text_length = parsed_data.get('text_length', 0)
        if text_length < 500:
            suggestions.append('Resume is brief. Add more detail about your experience and accomplishments.')
        elif text_length > 4000:
            suggestions.append('Resume is lengthy. Aim for 1-2 pages of clear, concise information.')
        else:
            insights_list.append('Resume length is appropriate.')
        
        # Categorize skills
        categorized = categorize_skills(skills) if skills else {}
        
        return {
            'positive_findings': insights_list,
            'improvement_suggestions': suggestions,
            'skill_categories': categorized
        }
    
    @staticmethod
    def save_upload(file, user_id):
        """Save uploaded file securely."""
        
        if not os.path.exists(ResumeUploadService.UPLOAD_FOLDER):
            os.makedirs(ResumeUploadService.UPLOAD_FOLDER)
        
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
        unique_filename = f"{user_id}_{timestamp}{filename}"
        
        file_path = os.path.join(ResumeUploadService.UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        return file_path


class SkillMatcher:
    """Match detected skills to skill categories."""
    
    SKILL_CATEGORIES = {
        'Programming Languages': ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 
                                 'php', 'ruby', 'swift', 'kotlin', 'typescript', 'r', 'scala',
                                 'perl', 'objective-c', 'dart', 'lua', 'groovy', 'elixir'],
        'Data & Analytics': ['sql', 'tableau', 'power bi', 'excel', 'pandas', 'numpy',
                            'matplotlib', 'scikit-learn', 'tensorflow', 'hadoop', 'spark',
                            'analytics', 'data science', 'bigquery', 'redshift', 'looker'],
        'Web Development': ['html', 'css', 'react', 'vue', 'angular', 'node', 'nodejs',
                           'express', 'django', 'flask', 'rest', 'api', 'graphql', 'fastapi',
                           'html5', 'css3', 'webpack', 'npm', 'yarn'],
        'Cloud & DevOps': ['aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes',
                          'jenkins', 'ci/cd', 'linux', 'git', 'gitlab', 'heroku', 'terraform',
                          'ansible', 'vagrant', 'circleci', 'travis'],
        'ML & AI': ['machine learning', 'deep learning', 'nlp', 'computer vision', 'pytorch',
                   'keras', 'ai', 'artificial intelligence', 'neural network', 'cnn', 'rnn'],
        'Databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'oracle', 
                     'dynamodb', 'elasticsearch', 'firebase', 'cosmos', 'sql server'],
        'Soft Skills': ['leadership', 'communication', 'project management', 'teamwork',
                       'problem solving', 'creativity', 'critical thinking', 'agile', 'scrum'],
        'Tools & Platforms': ['jira', 'confluence', 'slack', 'asana', 'trello', 'github',
                             'gitlab', 'bitbucket', 'salesforce', 'sap']
    }
    
    @staticmethod
    def categorize_skills(skills):
        """Categorize detected skills using case-insensitive matching."""
        
        categorized = {}
        uncategorized = []
        
        for skill in skills:
            found = False
            skill_lower = skill.lower().strip()
            
            for category, category_skills in SkillMatcher.SKILL_CATEGORIES.items():
                for cat_skill in category_skills:
                    # Case-insensitive exact match
                    if skill_lower == cat_skill.lower():
                        if category not in categorized:
                            categorized[category] = []
                        categorized[category].append(skill)
                        found = True
                        break
                    
                    # Partial match (skill contains category keyword or vice versa)
                    if cat_skill.lower() in skill_lower or skill_lower in cat_skill.lower():
                        if category not in categorized:
                            categorized[category] = []
                        categorized[category].append(skill)
                        found = True
                        break
                
                if found:
                    break
            
            if not found:
                uncategorized.append(skill)
        
        if uncategorized:
            categorized['Other'] = uncategorized
        
        return categorized


def categorize_skills(skills):
    """Helper function to categorize skills."""
    return SkillMatcher.categorize_skills(skills)


class ResumeQualityScore:
    """Score resume quality and provide improvement suggestions."""
    
    @staticmethod
    def calculate_quality_score(parsed_data, skill_count=0):
        """Calculate resume quality score (0-100)."""
        
        score = 0
        
        # Skills detection (20 points)
        if skill_count >= 10:
            score += 20
        elif skill_count >= 5:
            score += 15
        elif skill_count >= 2:
            score += 10
        else:
            score += 5
        
        # Experience mention (20 points)
        if parsed_data.get('has_experience', False):
            score += 20
        else:
            score += 5
        
        # Education (20 points)
        education = parsed_data.get('education', [])
        if len(education) > 0:
            score += 20
        
        # Length (20 points)
        text_length = int(parsed_data.get('text_length', 0))
        if 1000 <= text_length <= 4000:
            score += 20
        elif 500 <= text_length < 5000:
            score += 15
        else:
            score += 5
        
        # Structure (20 points)
        lines = parsed_data.get('text_length', 0) // 40  # Estimate line count
        if lines >= 15:
            score += 20
        elif lines >= 10:
            score += 15
        else:
            score += 10
        
        return min(100, score)
    
    @staticmethod
    def get_quality_recommendations(score):
        """Get improvement recommendations based on quality score."""
        
        if score >= 80:
            return {
                'level': 'Strong',
                'message': 'Your resume covers the key elements. Ready to apply.',
                'tips': ['Keep it updated with recent work', 'Review for typos and clarity']
            }
        elif score >= 60:
            return {
                'level': 'Solid',
                'message': 'Your resume is functional. A few improvements would strengthen it.',
                'tips': ['Add more specific technical skills', 'Include company names and dates', 'Expand on measurable results']
            }
        elif score >= 40:
            return {
                'level': 'Developing',
                'message': 'Your resume needs more structure and detail.',
                'tips': ['Organize with clear sections', 'Add quantifiable metrics', 'Include relevant technical keywords', 'Fix formatting issues']
            }
        else:
            return {
                'level': 'Incomplete',
                'message': 'Focus on building out the core sections first.',
                'tips': ['Add contact information', 'List technical skills clearly', 'Include work experience or projects', 'Add education']
            }
