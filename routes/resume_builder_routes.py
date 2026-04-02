"""
Resume Builder Routes - API endpoints for resume building and management
"""

from flask import Blueprint, request, jsonify, send_file, session, redirect
from services.resume_builder_service import (
    ResumeBuilder, 
    ResumeFieldValidator, 
    ResumePDFGenerator,
    RESUME_TEMPLATES
)
import json
from datetime import datetime
from functools import wraps

resume_builder_bp = Blueprint('resume_builder', __name__)


def login_required(f):
    """Simple login check decorator."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


@resume_builder_bp.route('/api/resume/templates', methods=['GET'])
def get_templates():
    """Get available resume templates."""
    try:
        templates = ResumeBuilder.get_templates()
        return jsonify({
            'success': True,
            'templates': templates
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@resume_builder_bp.route('/api/resume/create', methods=['POST'])
@login_required
def create_resume():
    """Create a new resume draft."""
    try:
        data = request.get_json()
        template_id = data.get('template_id', 'clean')
        
        resume = ResumeBuilder.create_draft(
            user_id=str(session.get('user_id')),
            template_id=template_id
        )
        
        # TODO: Save to database
        # db_service.save_resume_draft(resume)
        
        return jsonify({
            'success': True,
            'resume': resume
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@resume_builder_bp.route('/api/resume/<resume_id>/update', methods=['PUT'])
@login_required
def update_resume(resume_id):
    """Update resume content."""
    try:
        data = request.get_json()
        
        # TODO: Fetch from database
        # resume = db_service.get_resume(session.get('user_id'), resume_id)
        
        # Update specific section
        section = data.get('section')  # 'personal', 'education', 'experience', etc.
        
        if section == 'personal':
            # TODO: Update personal info
            pass
        elif section == 'education':
            # Validate education
            validation = ResumeFieldValidator.validate_education(data.get('data', {}))
            if not validation['valid']:
                return jsonify({
                    'success': False,
                    'errors': validation['errors']
                }), 400
        elif section == 'experience':
            # Validate experience
            validation = ResumeFieldValidator.validate_experience(data.get('data', {}))
            if not validation['valid']:
                return jsonify({
                    'success': False,
                    'errors': validation['errors']
                }), 400
        elif section == 'projects':
            # Validate project
            validation = ResumeFieldValidator.validate_project(data.get('data', {}))
            if not validation['valid']:
                return jsonify({
                    'success': False,
                    'errors': validation['errors']
                }), 400
        elif section == 'skills':
            # Validate skills
            validation = ResumeFieldValidator.validate_skills(data.get('data', []))
            if not validation['valid']:
                return jsonify({
                    'success': False,
                    'errors': validation['errors']
                }), 400
        
        # TODO: Save to database
        # db_service.update_resume(resume)
        
        return jsonify({
            'success': True,
            'message': f'{section} updated successfully',
            'suggestions': validation.get('suggestions', []) if section != 'personal' else []
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@resume_builder_bp.route('/api/resume/<resume_id>/validate', methods=['POST'])
@login_required
def validate_resume(resume_id):
    """Validate entire resume."""
    try:
        data = request.get_json()
        resume_data = data.get('resume_data', {})
        
        validation = ResumeBuilder.validate_resume_data(resume_data)
        
        return jsonify({
            'success': True,
            'validation': validation
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@resume_builder_bp.route('/api/resume/<resume_id>/preview', methods=['POST'])
@login_required
def preview_resume(resume_id):
    """Generate HTML preview of resume."""
    try:
        data = request.get_json()
        resume_data = data.get('resume_data', {})
        template_id = data.get('template_id', 'clean')
        
        html = ResumeBuilder.export_to_html(resume_data, template_id)
        
        return jsonify({
            'success': True,
            'html': html
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@resume_builder_bp.route('/api/resume/<resume_id>/export/pdf', methods=['POST'])
@login_required
def export_pdf(resume_id):
    """Export resume as PDF."""
    try:
        data = request.get_json()
        resume_data = data.get('resume_data', {})
        template_id = data.get('template_id', 'clean')
        
        pdf = ResumePDFGenerator.generate_pdf(resume_data, template_id)
        
        filename = ResumeBuilder.export_to_pdf_filename(
            resume_data.get('personal', {}).get('full_name', 'Resume')
        )
        
        return send_file(
            pdf,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@resume_builder_bp.route('/api/resume/<resume_id>/suggestions', methods=['GET'])
@login_required
def get_suggestions(resume_id):
    """Get AI suggestions to improve resume."""
    try:
        # TODO: Fetch resume from database
        # resume_data = db_service.get_resume(session.get('user_id'), resume_id)
        
        user_phase = request.args.get('phase', 'professional')  # college, internship, professional
        
        suggestions = ResumeBuilder.get_resume_suggestions(
            resume_data={},  # TODO: Use actual resume_data from DB
            user_phase=user_phase
        )
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@resume_builder_bp.route('/api/resume/field-validator/education', methods=['POST'])
def validate_education_field():
    """Validate education field with suggestions."""
    try:
        data = request.get_json()
        validation = ResumeFieldValidator.validate_education(data)
        
        return jsonify({
            'success': True,
            'validation': validation
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@resume_builder_bp.route('/api/resume/field-validator/experience', methods=['POST'])
def validate_experience_field():
    """Validate experience field with suggestions."""
    try:
        data = request.get_json()
        validation = ResumeFieldValidator.validate_experience(data)
        
        return jsonify({
            'success': True,
            'validation': validation
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@resume_builder_bp.route('/api/resume/field-validator/project', methods=['POST'])
def validate_project_field():
    """Validate project field with suggestions."""
    try:
        data = request.get_json()
        validation = ResumeFieldValidator.validate_project(data)
        
        return jsonify({
            'success': True,
            'validation': validation
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@resume_builder_bp.route('/api/resume/field-validator/skills', methods=['POST'])
def validate_skills_field():
    """Validate skills field with suggestions."""
    try:
        data = request.get_json()
        skills = data.get('skills', [])
        validation = ResumeFieldValidator.validate_skills(skills)
        
        return jsonify({
            'success': True,
            'validation': validation
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@resume_builder_bp.route('/api/resume/action-verbs', methods=['GET'])
def get_action_verbs():
    """Get action verbs for resume writing."""
    try:
        action_verbs = ResumeFieldValidator.ACTION_VERBS
        
        return jsonify({
            'success': True,
            'action_verbs': [
                {'verb': verb, 'category': category}
                for verb, category in action_verbs
            ]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
