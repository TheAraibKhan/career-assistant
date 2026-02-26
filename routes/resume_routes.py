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
    
    # Check if coming from analysis results page
    show_results = request.args.get('results') == 'true'
    if show_results and 'analysis_result' in session:
        result = session.pop('analysis_result')
        return render_template('resume/upload.html', error=error, result=result)
    
    if request.method == 'POST':
        if 'resume' not in request.files:
            error = 'No file selected'
        else:
            file = request.files['resume']
            
            if file.filename == '':
                error = 'No file selected'
            else:
                validation = ResumeUploadService.validate_resume_file(file, file.filename)
                
                if not validation['valid']:
                    # Use the first error message, which is already human-friendly
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
                            
                            # Store result in session and redirect to analysis page
                            session['analysis_result'] = result
                            return redirect(url_for('resume.analysis_results'))
                        else:
                            error = parse_result.get('error', 'Could not parse resume')
                    except Exception as e:
                        # Log the actual error for debugging
                        print(f"Resume processing error: {str(e)}")
                        error = 'We had trouble processing your file. Please ensure it\'s a valid PDF or Word document and try again.'
    
    return render_template('resume/upload.html', error=error, result=result)


@resume_bp.route('/analysis-results', methods=['GET'])
def analysis_results():
    """Display detailed analysis results page."""
    if 'analysis_result' not in session:
        return redirect(url_for('resume.upload'))
    
    result = session.get('analysis_result', {})
    return render_template('resume/analysis_results.html', result=result)


@resume_bp.route('/<int:submission_id>/view', methods=['GET'])
def view_analysis(submission_id):
    """View a specific analysis by ID."""
    from database.db import get_db
    
    db = get_db()
    submission = db.execute('''
        SELECT * FROM submissions WHERE id = ?
    ''', (submission_id,)).fetchone()
    
    if not submission:
        return redirect(url_for('dashboard.index'))
    
    # Helper to safely read sqlite3.Row columns
    def col(name, default=''):
        try:
            val = submission[name]
            return val if val is not None else default
        except (IndexError, KeyError):
            return default
    
    strengths_raw = col('strengths', '')
    gaps_raw = col('gaps', '')
    skills_raw = col('resume_parsed_skills', '')
    
    result = {
        'success': True,
        'role': col('recommendation', 'N/A'),
        'readiness_score': col('readiness_score', 0),
        'confidence': col('confidence_score', 0),
        'strengths': [s.strip() for s in strengths_raw.split(',') if s.strip()] if strengths_raw else [],
        'gaps': [s.strip() for s in gaps_raw.split(',') if s.strip()] if gaps_raw else [],
        'skills': [s.strip() for s in skills_raw.split(',') if s.strip()] if skills_raw else [],
        'submission_id': submission['id']
    }
    
    return render_template('resume/analysis_results.html', result=result)


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