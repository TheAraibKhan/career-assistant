"""
Detailed Resume Analyzer - Comprehensive section-by-section resume analysis.

Provides the structure expected by /resume/api/extract:
- sections: education, skills, experience, projects, achievements
- scores: format, keywords, completeness, content_quality, overall
- insights: list of {type, message} dicts
- evolution: path-based recommendations
- professional_level: string classification
- suggestions: actionable improvement list
"""

import re
from typing import Dict, List


class DetailedResumeAnalyzer:
    """Detailed resume analysis returning structured multi-section results."""

    # Common skills to detect
    TECH_SKILLS = [
        'python', 'javascript', 'java', 'c++', 'c#', 'typescript', 'go', 'rust',
        'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql',
        'html', 'css', 'react', 'angular', 'vue', 'next.js', 'node.js',
        'express', 'django', 'flask', 'spring', 'rails',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
        'git', 'github', 'jenkins', 'ci/cd', 'jira',
        'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
        'machine learning', 'deep learning', 'tensorflow', 'pytorch',
        'pandas', 'numpy', 'scikit-learn', 'nlp', 'computer vision',
        'rest', 'graphql', 'api', 'microservices', 'linux', 'agile', 'scrum',
        'figma', 'photoshop', 'illustrator', 'ui/ux',
    ]

    ACTION_VERBS = [
        'developed', 'designed', 'led', 'managed', 'improved', 'increased',
        'reduced', 'deployed', 'architected', 'optimized', 'implemented',
        'created', 'built', 'launched', 'automated', 'collaborated',
        'mentored', 'delivered', 'maintained', 'analyzed', 'integrated',
        'resolved', 'migrated', 'refactored', 'scaled', 'streamlined',
    ]

    @staticmethod
    def analyze_resume_detailed(text: str) -> Dict:
        """
        Full detailed analysis of resume text.

        Returns dict with:
          sections, scores, insights, evolution,
          professional_level, readiness_for_role, suggestions
        """
        text_lower = text.lower()
        word_count = len(text.split())
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        # --- Detect skills ---
        skills_found = []
        for skill in DetailedResumeAnalyzer.TECH_SKILLS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                skills_found.append(skill.title() if len(skill) > 3 else skill.upper())

        # --- Detect action verbs ---
        verbs_used = [v for v in DetailedResumeAnalyzer.ACTION_VERBS if v in text_lower]

        # --- Section detection helpers ---
        has_education = any(kw in text_lower for kw in [
            'education', 'university', 'college', 'degree', 'bachelor', 'master',
            'b.tech', 'b.sc', 'm.tech', 'm.sc', 'graduated', 'gpa', 'cgpa',
        ])
        education_degrees = []
        for deg in ['B.Tech', 'B.Sc', 'B.E.', 'M.Tech', 'M.Sc', 'MBA', 'PhD',
                     'Bachelor', 'Master', 'Associate']:
            if deg.lower() in text_lower:
                education_degrees.append(deg)

        has_experience = any(kw in text_lower for kw in [
            'experience', 'work history', 'employment', 'intern', 'worked at',
            'position', 'role', 'company',
        ])
        has_dates = bool(re.search(
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february)[a-z]*[\s,]*\d{4}',
            text_lower,
        )) or bool(re.search(r'\d{4}\s*[-–]\s*(present|\d{4})', text_lower))
        has_metrics = bool(re.search(r'\d+\s*%', text)) or bool(re.search(r'\$\s*\d', text))

        exp_count = len(re.findall(
            r'(intern|software engineer|developer|analyst|manager|associate|consultant)',
            text_lower,
        ))

        has_projects = any(kw in text_lower for kw in [
            'project', 'portfolio', 'built', 'created', 'application', 'system',
            'github.com', 'deployed',
        ])
        project_count = max(1, len(re.findall(
            r'(project|application|system|platform|tool|website|app)\b', text_lower,
        ))) if has_projects else 0

        has_achievements = any(kw in text_lower for kw in [
            'award', 'certification', 'certified', 'publication', 'honor',
            'achievement', 'hackathon', 'competition', 'winner', 'scholarship',
        ])
        achievement_count = len(re.findall(
            r'(award|certif|publication|honor|achievement|hackathon|winner|scholarship)',
            text_lower,
        ))

        # --- Build sections ---
        sections = {
            'education': {
                'present': has_education,
                'status': 'found' if has_education else 'missing',
                'degrees': education_degrees,
                'score': 80 if has_education else 30,
                'explanation': (
                    'Education section detected with relevant qualifications.'
                    if has_education
                    else 'No education section found. Add your academic background.'
                ),
                'tips': [
                    'Include degree, institution, and graduation date',
                    'Add GPA if above 3.5 / 8.0',
                    'List relevant coursework for entry-level roles',
                ],
            },
            'skills': {
                'present': len(skills_found) > 0,
                'status': 'strong' if len(skills_found) >= 10 else (
                    'good' if len(skills_found) >= 5 else 'needs_work'
                ),
                'skills': skills_found,
                'count': len(skills_found),
                'score': min(100, 30 + len(skills_found) * 5),
                'explanation': f'Found {len(skills_found)} technical skills.',
                'tips': [
                    'Organize skills by category (Languages, Frameworks, Tools)',
                    'Include in-demand skills for your target role',
                    'Remove outdated or irrelevant technologies',
                ],
            },
            'experience': {
                'present': has_experience,
                'status': 'strong' if has_experience and has_dates and has_metrics else (
                    'good' if has_experience else 'missing'
                ),
                'count': min(exp_count, 8),
                'has_dates': has_dates,
                'has_metrics': has_metrics,
                'score': (
                    85 if has_experience and has_dates and has_metrics
                    else 65 if has_experience and has_dates
                    else 50 if has_experience
                    else 20
                ),
                'explanation': (
                    f'Experience section found with {exp_count} role(s).'
                    if has_experience
                    else 'No experience section detected.'
                ),
                'tips': [
                    'Start each bullet with a strong action verb',
                    'Quantify achievements (e.g., "Improved load time by 40%")',
                    'Include company name, role title, and dates',
                ],
            },
            'projects': {
                'present': has_projects,
                'status': 'found' if has_projects else 'missing',
                'count': min(project_count, 10),
                'score': 75 if has_projects else 25,
                'explanation': (
                    f'{project_count} project(s) detected.'
                    if has_projects
                    else 'No projects section found. Add portfolio projects.'
                ),
                'tips': [
                    'Include project name, tech stack, and a brief description',
                    'Add GitHub or live demo links',
                    'Highlight your specific contributions',
                ],
            },
            'achievements': {
                'present': has_achievements,
                'status': 'found' if has_achievements else 'optional',
                'count': achievement_count,
                'has_metrics': has_metrics,
                'score': 70 if has_achievements else 40,
                'explanation': (
                    f'{achievement_count} achievement(s)/certification(s) found.'
                    if has_achievements
                    else 'Consider adding certifications or awards.'
                ),
                'tips': [
                    'Add relevant certifications (AWS, Google, etc.)',
                    'Include hackathon wins or competition results',
                    'Link to publications or talks',
                ],
            },
        }

        # --- Calculate scores ---
        section_scores = [s['score'] for s in sections.values()]
        avg_section = int(sum(section_scores) / len(section_scores)) if section_scores else 0

        format_score = 50
        if 300 <= word_count <= 1000:
            format_score = 85
        elif 200 <= word_count <= 1500:
            format_score = 70
        elif word_count > 100:
            format_score = 55
        # Bonus for line structure
        format_score = min(100, format_score + min(10, len(lines) // 10))

        keywords_score = min(100, 20 + len(skills_found) * 6 + len(verbs_used) * 3)

        completeness_items = ['education', 'experience', 'skills', 'projects', 'achievements']
        items_present = sum(1 for k in completeness_items if sections.get(k, {}).get('present'))
        completeness_score = min(100, 20 + items_present * 16)

        content_quality = 40
        if len(verbs_used) >= 5:
            content_quality += 20
        elif len(verbs_used) >= 2:
            content_quality += 10
        if has_metrics:
            content_quality += 20
        if has_dates:
            content_quality += 10
        if len(skills_found) >= 8:
            content_quality += 10
        content_quality = min(100, content_quality)

        overall_score = int(
            format_score * 0.15
            + keywords_score * 0.25
            + completeness_score * 0.25
            + content_quality * 0.20
            + avg_section * 0.15
        )
        overall_score = max(0, min(100, overall_score))

        scores = {
            'format': format_score,
            'keywords': keywords_score,
            'completeness': completeness_score,
            'content_quality': content_quality,
            'overall': overall_score,
        }

        # --- Insights ---
        insights = []
        if len(skills_found) >= 10:
            insights.append({'type': 'strength', 'message': f'Strong skills section with {len(skills_found)} technologies detected.'})
        elif len(skills_found) >= 5:
            insights.append({'type': 'info', 'message': f'{len(skills_found)} skills found. Aim for 10+ relevant skills.'})
        else:
            insights.append({'type': 'gap', 'message': 'Few technical skills detected. Add more relevant technologies.'})

        if has_experience and has_metrics:
            insights.append({'type': 'strength', 'message': 'Experience section includes quantified results — great for ATS.'})
        elif has_experience:
            insights.append({'type': 'info', 'message': 'Experience found but lacks metrics. Add numbers to show impact.'})
        else:
            insights.append({'type': 'gap', 'message': 'No work experience detected. Add internships, freelance, or volunteer work.'})

        if has_projects:
            insights.append({'type': 'strength', 'message': 'Projects section demonstrates hands-on experience.'})
        else:
            insights.append({'type': 'gap', 'message': 'No projects detected. Add 2-3 portfolio projects with links.'})

        if len(verbs_used) >= 5:
            insights.append({'type': 'strength', 'message': 'Good use of action verbs throughout the resume.'})
        else:
            insights.append({'type': 'info', 'message': 'Use more action verbs (Developed, Led, Designed) to strengthen bullets.'})

        if word_count < 200:
            insights.append({'type': 'gap', 'message': f'Resume is very short ({word_count} words). Aim for 400-800 words.'})
        elif word_count > 1200:
            insights.append({'type': 'info', 'message': f'Resume is long ({word_count} words). Consider trimming to 1-2 pages.'})

        # --- Professional level ---
        if overall_score >= 80 and len(skills_found) >= 12 and has_experience:
            professional_level = 'Advanced'
        elif overall_score >= 55 and len(skills_found) >= 6:
            professional_level = 'Intermediate'
        else:
            professional_level = 'Beginner'

        # --- Readiness ---
        readiness_for_role = {
            'level': professional_level,
            'ready': overall_score >= 65,
            'message': (
                'Your resume is ready for applications. Fine-tune for specific roles.'
                if overall_score >= 65
                else 'Your resume needs improvement before applying. Focus on the suggestions below.'
            ),
        }

        # --- Evolution ---
        evolution = {
            'current_level': professional_level,
            'next_level': 'Intermediate' if professional_level == 'Beginner' else (
                'Advanced' if professional_level == 'Intermediate' else 'Expert'
            ),
            'steps': [],
        }
        if len(skills_found) < 10:
            evolution['steps'].append(f'Add {10 - len(skills_found)} more relevant skills')
        if not has_metrics:
            evolution['steps'].append('Quantify achievements with metrics and percentages')
        if not has_projects:
            evolution['steps'].append('Add 2-3 portfolio projects with GitHub links')
        if not has_achievements:
            evolution['steps'].append('Get relevant certifications (AWS, Google, etc.)')
        if len(verbs_used) < 5:
            evolution['steps'].append('Strengthen bullet points with action verbs')
        if not evolution['steps']:
            evolution['steps'].append('Continue refining and tailoring for specific roles')

        # --- Suggestions ---
        suggestions = []
        if scores['format'] < 70:
            suggestions.append({
                'title': 'Improve Formatting',
                'description': 'Use clear section headers, consistent spacing, and aim for 1-2 pages.',
            })
        if scores['keywords'] < 70:
            suggestions.append({
                'title': 'Add More Keywords',
                'description': 'Include industry-specific technologies and tools relevant to your target role.',
            })
        if scores['completeness'] < 70:
            suggestions.append({
                'title': 'Complete Missing Sections',
                'description': 'Ensure your resume has Education, Skills, Experience, and Projects sections.',
            })
        if scores['content_quality'] < 70:
            suggestions.append({
                'title': 'Strengthen Content Quality',
                'description': 'Use action verbs, quantify results, and show business/technical impact.',
            })
        if not has_metrics:
            suggestions.append({
                'title': 'Add Quantified Results',
                'description': 'Include numbers: "Improved performance by 35%", "Managed team of 5".',
            })
        if len(skills_found) < 8:
            suggestions.append({
                'title': 'Expand Skills Section',
                'description': f'You have {len(skills_found)} skills. Add more relevant technologies to reach 10+.',
            })
        if not suggestions:
            suggestions.append({
                'title': 'Looking Good!',
                'description': 'Your resume is well-structured. Tailor it for each specific role you apply to.',
            })

        return {
            'sections': sections,
            'scores': scores,
            'insights': insights,
            'evolution': evolution,
            'professional_level': professional_level,
            'readiness_for_role': readiness_for_role,
            'suggestions': suggestions,
        }
