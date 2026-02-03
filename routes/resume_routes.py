"""Resume upload and analysis routes."""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
from services.resume_parser import parse_resume, get_file_hash, cache_resume_parse, get_cached_parse
from services.resume_upload_service import ResumeUploadService, ResumeQualityScore
from services.ats_scorer import get_ats_score
from services.user_experience import UserExperienceTracker
from config import UPLOAD_FOLDER, ALLOWED_RESUME_EXTENSIONS, MAX_RESUME_FILE_SIZE
import os

resume_bp = Blueprint('resume', __name__, url_prefix='/resume')


def allowed_file(filename):
    """Check if file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_RESUME_EXTENSIONS


@resume_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """Resume upload page with enhanced UX."""
    error = None
    result = None
    
    if request.method == 'POST':
        if 'resume' not in request.files:
            error = 'No file selected'
        else:
            file = request.files['resume']
            
            if file.filename == '':
                error = 'No file selected'
            else:
                # Validate file with human-friendly messages
                validation = ResumeUploadService.validate_resume_file(file, file.filename)
                
                if not validation['valid']:
                    error = validation['errors'][0]
                else:
                    try:
                        # Save file
                        file_path = ResumeUploadService.save_upload(file, session.get('user_id', 'anonymous'))
                        
                        # Parse with feedback
                        parse_result = ResumeUploadService.parse_with_feedback(file_path, file.filename)
                        
                        if parse_result['success']:
                            # Calculate quality score
                            quality_score = ResumeQualityScore.calculate_quality_score(
                                {
                                    'has_experience': parse_result.get('experience', False),
                                    'education': parse_result.get('education', []),
                                    'text_length': parse_result.get('text_length', 0)
                                },
                                len(parse_result.get('skills', []))
                            )
                            
                            quality_rec = ResumeQualityScore.get_quality_recommendations(quality_score)
                            
                            ats_result = get_ats_score({
                                'skills': parse_result.get('skills', []),
                                'has_experience': parse_result.get('experience', False),
                                'education': parse_result.get('education', []),
                                'text_length': int(parse_result.get('text_length', 0)) or 0,
                                'text': parse_result.get('text', '')
                            })
                            
                            ats_score_value = int(ats_result.get('ats_score', 0)) if ats_result.get('ats_score') is not None else 0
                            ats_score_value = max(0, min(100, ats_score_value))
                            
                            result = {
                                'success': True,
                                'skills': parse_result.get('skills', []),
                                'education': parse_result.get('education', []),
                                'experience': parse_result.get('experience', False),
                                'feedback': parse_result.get('feedback', {}),
                                'insights': parse_result.get('insights', {}),
                                'quality_score': int(quality_score) if quality_score else 0,
                                'quality_recommendation': quality_rec or 'Good resume structure',
                                'ats_score': ats_score_value,
                                'ats_categories': ats_result.get('categories', {}),
                                'ats_recommendations': ats_result.get('recommendations', []),
                                'ats_blockers': ats_result.get('blockers', []),
                                'ats_strengths': ats_result.get('strengths', []),
                                'message': parse_result.get('message', 'Resume processed successfully'),
                                'text_length': int(parse_result.get('text_length', 0)) or 0,
                                'extracted_at': parse_result.get('extracted_at')
                            }
                            
                            user_id = session.get('user_id')
                            if user_id:
                                UserExperienceTracker.track_interaction(
                                    user_id, 
                                    'resume_uploaded',
                                    {
                                        'skills_found': len(result.get('skills', [])),
                                        'quality_score': int(quality_score) if quality_score else 0,
                                        'ats_score': ats_score_value,
                                        'file_size': validation.get('file_size', 0)
                                    }
                                )
                        else:
                            error = parse_result.get('error', 'Could not parse resume')
                    except Exception as e:
                        error = 'Error processing file. Please try again.'
    
    return render_template('resume/upload.html', error=error, result=result)


@resume_bp.route('/api/extract', methods=['POST'])
def extract_api():
    """API endpoint for resume extraction with enhanced feedback."""
    if 'resume' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['resume']
    
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate
    validation = ResumeUploadService.validate_resume_file(file, file.filename)
    if not validation['valid']:
        return jsonify({
            'success': False,
            'error': validation['errors'][0],
            'warnings': validation['warnings']
        }), 400
    
    try:
        # Save file
        file_path = ResumeUploadService.save_upload(file, session.get('user_id', 'anonymous'))
        
        # Parse with feedback
        parse_result = ResumeUploadService.parse_with_feedback(file_path, file.filename)
        
        if parse_result.get('success'):
            quality_score = ResumeQualityScore.calculate_quality_score(
                {
                    'has_experience': parse_result.get('experience', False),
                    'education': parse_result.get('education', []),
                    'text_length': int(parse_result.get('text_length', 0)) or 0
                },
                len(parse_result.get('skills', []))
            )
            
            quality_rec = ResumeQualityScore.get_quality_recommendations(quality_score) or 'Good resume structure'
            
            user_id = session.get('user_id')
            if user_id:
                UserExperienceTracker.track_interaction(
                    user_id,
                    'resume_uploaded',
                    {
                        'skills_found': len(parse_result.get('skills', [])),
                        'quality_score': int(quality_score) if quality_score else 0
                    }
                )
            
            return jsonify({
                'success': True,
                'skills': parse_result.get('skills', []),
                'education': parse_result.get('education', []),
                'has_experience': parse_result.get('experience', False),
                'feedback': parse_result.get('feedback', {}),
                'insights': parse_result.get('insights', {}),
                'quality_score': int(quality_score) if quality_score else 0,
                'quality_recommendation': quality_rec,
                'message': parse_result.get('message', 'Resume processed successfully')
            })
        else:
            return jsonify({
                'success': False,
                'error': parse_result.get('error', 'Could not parse resume'),
                'hint': parse_result.get('hint', 'Please try a different file format')
            }), 400
    
    except Exception as e:
        return jsonify({'error': 'Error processing file: ' + str(e)}), 500