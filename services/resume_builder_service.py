"""
Resume Builder Service - Build resumes from templates with live preview and export

Features:
- Template selection (Clean, Modern, Professional)
- Input fields for education, skills, projects, experience
- Live preview generation
- Smart suggestions (action verbs, quantification)
- PDF export capability
- Save/load resume drafts
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from io import BytesIO


# Resume Templates
RESUME_TEMPLATES = {
    'clean': {
        'name': 'Clean & Simple',
        'description': 'Classic, ATS-friendly format. Perfect for any industry.',
        'preview': '━━━━━━━━━━━━━━━━━━━\n  JOHN DOE  |  john@email.com\n━━━━━━━━━━━━━━━━━━━',
        'sections': ['header', 'summary', 'experience', 'projects', 'skills', 'education'],
        'styling': {
            'colors': ['#000000', '#333333'],  # Black, dark gray
            'font': 'Helvetica',
            'spacing': 'compact'
        }
    },
    'modern': {
        'name': 'Modern & Bold',
        'description': 'Eye-catching design with color. Great for tech roles.',
        'preview': '╔════════════════════╗\n║  JANE DOE          ║\n║  Tech Leader       ║\n╚════════════════════╝',
        'sections': ['header', 'summary', 'projects', 'experience', 'skills', 'education'],
        'styling': {
            'colors': ['#1f77e2', '#333333'],  # Blue accent
            'font': 'Calibri',
            'spacing': 'generous'
        }
    },
    'professional': {
        'name': 'Professional & Formal',
        'description': 'Executive style. Best for corporate/senior roles.',
        'preview': '┌─────────────────────┐\n│ ROBERT SMITH        │\n│ Senior Engineer     │\n└─────────────────────┘',
        'sections': ['header', 'executive-summary', 'experience', 'skills', 'projects', 'certifications', 'education'],
        'styling': {
            'colors': ['#1a1a1a', '#4a4a4a'],  # Very dark
            'font': 'Garamond',
            'spacing': 'formal'
        }
    }
}


class ResumeFieldValidator:
    """Validates resume input fields and provides suggestions."""
    
    # Action verbs for resume
    ACTION_VERBS = [
        ('Developed', 'Building/Creating'),
        ('Designed', 'Creating design/architecture'),
        ('Led', 'Leadership/Management'),
        ('Managed', 'Management/Coordination'),
        ('Implemented', 'Implementation/Execution'),
        ('Improved', 'Enhancement/Optimization'),
        ('Increased', 'Growth/Metrics'),
        ('Reduced', 'Efficiency/Cost Savings'),
        ('Optimized', 'Performance/Efficiency'),
        ('Deployed', 'Launch/Release'),
        ('Architected', 'System Design'),
        ('Collaborated', 'Teamwork'),
        ('Mentored', 'Leadership/Teaching'),
        ('Directed', 'Leadership/Direction'),
    ]
    
    @staticmethod
    def validate_education(data: Dict) -> Dict:
        """Validate education entry."""
        errors = []
        warnings = []
        
        if not data.get('degree'):
            errors.append('Degree is required (e.g., B.S., M.S., B.Tech)')
        
        if not data.get('school'):
            errors.append('School/University name is required')
        
        if not data.get('graduation_year'):
            errors.append('Graduation year is required')
        
        gpa = data.get('gpa')
        if gpa:
            try:
                gpa_float = float(gpa)
                if gpa_float < 2.0:
                    warnings.append('Include GPA only if > 3.0. Current is low.')
                elif gpa_float > 4.5:
                    errors.append('GPA seems too high. Max is usually 4.0')
            except ValueError:
                errors.append('GPA must be a number (e.g., 3.85)')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'suggestions': [
                'Add degree to format: "B.S. in Computer Science"',
                'Include GPA if > 3.5',
                'Add relevant coursework if in college'
            ] if not data.get('degree') else []
        }
    
    @staticmethod
    def validate_experience(data: Dict) -> Dict:
        """Validate work experience entry."""
        errors = []
        suggestions = []
        
        if not data.get('job_title'):
            errors.append('Job title is required')
        
        if not data.get('company'):
            errors.append('Company name is required')
        
        description = data.get('description', '')
        if not description:
            errors.append('Add what you did')
        elif len(description) < 50:
            suggestions.append('Description is short. Add more details about impact.')
        
        # Check for action verbs
        has_action_verb = any(verb.lower() in description.lower() for verb, _ in ResumeFieldValidator.ACTION_VERBS)
        if description and not has_action_verb:
            suggestions.append(f'Start with action verb. Example: Developed..., Designed..., Led...')
        
        # Check for quantification
        has_numbers = any(char.isdigit() for char in description)
        if description and not has_numbers:
            suggestions.append('Add numbers/metrics. Example: "Improved performance by 40%"')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'suggestions': suggestions[:3],  # Top 3
            'action_verb_examples': [f'{verb} - {category}' for verb, category in ResumeFieldValidator.ACTION_VERBS[:5]]
        }
    
    @staticmethod
    def validate_project(data: Dict) -> Dict:
        """Validate project entry."""
        errors = []
        suggestions = []
        
        if not data.get('title'):
            errors.append('Project title is required')
        
        if not data.get('description'):
            errors.append('Project description is required')
        
        if not data.get('tech_stack'):
            suggestions.append('Add technologies used (Python, React, MongoDB, etc.)')
        
        if not data.get('github_link') and not data.get('demo_link'):
            suggestions.append('Include GitHub link or demo link to project')
        
        description = data.get('description', '')
        if description and len(description) < 30:
            suggestions.append('Add more context about what the project does')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'suggestions': suggestions,
            'tech_stack_examples': ['Python', 'JavaScript', 'React', 'Node.js', 'MongoDB', 'AWS']
        }
    
    @staticmethod
    def validate_skills(skills_list: List[str]) -> Dict:
        """Validate skills section."""
        errors = []
        suggestions = []
        
        if len(skills_list) == 0:
            errors.append('Add at least one skill')
        elif len(skills_list) < 5:
            suggestions.append(f'Add {5 - len(skills_list)} more skills')
        elif len(skills_list) > 25:
            suggestions.append('Limit to top 15-20 most relevant skills')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'suggestions': suggestions,
            'count': len(skills_list),
            'recommended_count': 15
        }


class ResumeBuilder:
    """Main resume builder service."""
    
    @staticmethod
    def get_templates() -> List[Dict]:
        """Get available resume templates."""
        return [
            {
                'id': key,
                'name': template['name'],
                'description': template['description'],
                'preview': template['preview'],
            }
            for key, template in RESUME_TEMPLATES.items()
        ]
    
    @staticmethod
    def create_draft(user_id: str, template_id: str = 'clean') -> Dict:
        """Create a new resume draft."""
        if template_id not in RESUME_TEMPLATES:
            template_id = 'clean'
        
        template = RESUME_TEMPLATES[template_id]
        
        return {
            'id': f"resume_{datetime.utcnow().timestamp()}",
            'user_id': user_id,
            'template_id': template_id,
            'template_name': template['name'],
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'data': {
                'personal': {
                    'full_name': '',
                    'email': '',
                    'phone': '',
                    'location': '',
                    'website': '',
                    'linkedin': ''
                },
                'summary': '',
                'education': [],
                'experience': [],
                'projects': [],
                'skills': [],
                'certifications': []
            },
            'status': 'draft'
        }
    
    @staticmethod
    def validate_resume_data(resume_data: Dict) -> Dict:
        """Validate entire resume data."""
        issues = {
            'errors': [],
            'warnings': [],
            'suggestions': [],
            'sections_score': {}
        }
        
        # Personal info
        if not resume_data.get('personal', {}).get('full_name'):
            issues['errors'].append('Name is required')
        if not resume_data.get('personal', {}).get('email'):
            issues['errors'].append('Email is required')
        
        # Education
        if not resume_data.get('education'):
            issues['warnings'].append('No education added yet')
        else:
            issues['sections_score']['education'] = len(resume_data['education']) * 25  # Each entry = 25 points
        
        # Experience
        if not resume_data.get('experience'):
            issues['warnings'].append('No work experience added')
        else:
            issues['sections_score']['experience'] = len(resume_data['experience']) * 30
        
        # Projects
        if not resume_data.get('projects'):
            issues['suggestions'].append('Add 1-2 projects to strengthen resume')
        else:
            issues['sections_score']['projects'] = len(resume_data['projects']) * 20
        
        # Skills
        skills = resume_data.get('skills', [])
        if not skills:
            issues['warnings'].append('Add your key skills')
        elif len(skills) < 5:
            issues['suggestions'].append(f'Add {5 - len(skills)} more skills')
        else:
            issues['sections_score']['skills'] = min(100, len(skills) * 5)
        
        # Calculate completeness
        sections_completed = sum(1 for v in issues['sections_score'].values() if v > 0)
        total_possible_sections = 5  # education, experience, projects, skills, certifications
        completeness = int((sections_completed / total_possible_sections) * 100)
        
        return {
            'valid': len(issues['errors']) == 0,
            **issues,
            'completeness': completeness,
            'next_steps': [
                s for group in [issues['errors'], issues['warnings'], issues['suggestions']]
                for s in group
            ][:3]
        }
    
    @staticmethod
    def export_to_html(resume_data: Dict, template_id: str = 'clean') -> str:
        """Generate HTML preview of resume."""
        template = RESUME_TEMPLATES.get(template_id, RESUME_TEMPLATES['clean'])
        personal = resume_data.get('personal', {})
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{personal.get('full_name', 'Resume')}</title>
    <style>
        body {{ font-family: {template['styling']['font']}, Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ border-bottom: 2px solid {template['styling']['colors'][0]}; padding-bottom: 20px; margin-bottom: 20px; }}
        .name {{ font-size: 28px; font-weight: bold; color: {template['styling']['colors'][0]}; }}
        .contact {{ font-size: 12px; color: {template['styling']['colors'][1]}; }}
        .section-title {{ font-size: 14px; font-weight: bold; color: {template['styling']['colors'][0]}; margin-top: 20px; border-bottom: 1px solid {template['styling']['colors'][0]}; padding-bottom: 5px; }}
        .entry {{ margin-bottom: 15px; }}
        .entry-title {{ font-weight: bold; }}
        .entry-subtitle {{ font-style: italic; color: {template['styling']['colors'][1]}; }}
        .entry-description {{ margin-top: 5px; }}
        .skills {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .skill-tag {{ background-color: {template['styling']['colors'][0]}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="name">{personal.get('full_name', '')}</div>
        <div class="contact">
            {personal.get('email', '')} | {personal.get('phone', '')} | {personal.get('location', '')}
        </div>
    </div>
    
    {'<div class="section"><div class="section-title">SUMMARY</div><p>' + resume_data.get('summary', '') + '</p></div>' if resume_data.get('summary') else ''}
    
    {'<div class="section"><div class="section-title">EXPERIENCE</div>' if resume_data.get('experience') else ''}
    {''.join([f'''<div class="entry">
        <div class="entry-title">{exp.get('job_title', '')} @ {exp.get('company', '')}</div>
        <div class="entry-subtitle">{exp.get('start_date', '')} - {exp.get('end_date', '')}</div>
        <div class="entry-description">{exp.get('description', '')}</div>
    </div>''' for exp in resume_data.get('experience', [])]) if resume_data.get('experience') else ''}
    {'</div>' if resume_data.get('experience') else ''}
    
    {'<div class="section"><div class="section-title">PROJECTS</div>' if resume_data.get('projects') else ''}
    {''.join([f'''<div class="entry">
        <div class="entry-title">{proj.get('title', '')}</div>
        <div class="entry-subtitle">Tech: {proj.get('tech_stack', '')}</div>
        <div class="entry-description">{proj.get('description', '')}</div>
    </div>''' for proj in resume_data.get('projects', [])]) if resume_data.get('projects') else ''}
    {'</div>' if resume_data.get('projects') else ''}
    
    {'<div class="section"><div class="section-title">EDUCATION</div>' if resume_data.get('education') else ''}
    {''.join([f'''<div class="entry">
        <div class="entry-title">{edu.get('degree', '')} in {edu.get('major', '')}</div>
        <div class="entry-subtitle">{edu.get('school', '')} - {edu.get('graduation_year', '')}</div>
    </div>''' for edu in resume_data.get('education', [])]) if resume_data.get('education') else ''}
    {'</div>' if resume_data.get('education') else ''}
    
    {'<div class="section"><div class="section-title">SKILLS</div><div class="skills">' + ''.join([f'<span class="skill-tag">{skill}</span>' for skill in resume_data.get('skills', [])]) + '</div></div>' if resume_data.get('skills') else ''}
</body>
</html>
        """
        return html
    
    @staticmethod
    def export_to_pdf_filename(full_name: str) -> str:
        """Generate PDF filename from resume name."""
        # Sanitize name for filename
        safe_name = "".join(c for c in full_name if c.isalnum() or c in (' ', '-', '_')).strip()
        return f"{safe_name}_Resume.pdf"
    
    @staticmethod
    def get_resume_suggestions(resume_data: Dict, user_phase: str = 'college') -> Dict:
        """Get AI suggestions to improve resume."""
        personal = resume_data.get('personal', {})
        education = resume_data.get('education', [])
        experience = resume_data.get('experience', [])
        projects = resume_data.get('projects', [])
        skills = resume_data.get('skills', [])
        
        suggestions = {
            'strengths': [],
            'improvements': [],
            'quick_wins': []
        }
        
        # Strengths
        if len(skills) >= 10:
            suggestions['strengths'].append('Strong skills section - 10+ skills')
        if len(projects) >= 2:
            suggestions['strengths'].append('Good project coverage - shows practical skills')
        if len(experience) >= 2:
            suggestions['strengths'].append('Good experience - multiple roles')
        
        # Improvements
        if len(skills) < 8:
            suggestions['improvements'].append('Add more relevant skills (target 12+)')
        if not projects:
            suggestions['improvements'].append('Add 1-2 portfolio projects - crucial for tech roles')
        if user_phase == 'college' and not education:
            suggestions['improvements'].append('Add education details')
        
        # Quick wins
        if resume_data.get('summary'):
            suggestions['quick_wins'].append('Professional summary makes strong first impression')
        if not resume_data.get('summary'):
            suggestions['quick_wins'].append('Add 2-3 line professional summary at top')
        
        return suggestions


class ResumePDFGenerator:
    """Handle PDF generation (simplified - would use reportlab in production)."""
    
    @staticmethod
    def generate_pdf(resume_data: Dict, template_id: str = 'clean') -> BytesIO:
        """
        Generate PDF from resume data.
        Note: In production, use reportlab or similar library.
        For now, this returns a placeholder.
        """
        # In production, would use:
        # from reportlab.pdfgen import canvas
        # from reportlab.lib.pagesizes import letter
        
        pdf_content = BytesIO()
        # Placeholder - actual PDF generation would happen here
        pdf_content.write(b"PDF placeholder - in production, would use reportlab")
        pdf_content.seek(0)
        
        return pdf_content
