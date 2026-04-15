"""Career Guidance Routes - Integrate student discovery and guidance."""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
from datetime import datetime
import json

from services.student_profile_service import StudentProfileService, suggest_next_steps
from services.skill_gap_analyzer import SkillGapAnalyzer
from services.learning_path_generator import LearningPathGenerator
from services.action_guidance_service import ActionGuidanceService
from services.roadmap_service import generate_roadmap

guidance_bp = Blueprint('guidance', __name__, url_prefix='/guidance')


def login_required(f):
    """Require user to be logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function



# STEP 1: Student Profile Discovery

@guidance_bp.route('/discover', methods=['GET', 'POST'])
@login_required
def discover():
    """Student discovery form - understand their background and goals."""
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        # Parse form data
        education_level = request.form.get('education_level')
        interests = request.form.getlist('interests')
        current_skills = request.form.getlist('current_skills')
        career_goals = request.form.get('career_goals')
        experience_level = request.form.get('experience_level')
        confusion_areas = request.form.getlist('confusion_areas')
        learning_style = request.form.get('learning_style')
        available_hours = int(request.form.get('available_hours', 10))
        target_timeline = int(request.form.get('target_timeline', 6))
        
        # Create profile
        success = StudentProfileService.create_profile(
            user_id=user_id,
            education_level=education_level,
            interests=interests,
            current_skills=current_skills,
            career_goals=career_goals,
            experience_level=experience_level,
            confusion_areas=confusion_areas,
            learning_style=learning_style,
            available_hours_per_week=available_hours,
            target_timeline_months=target_timeline
        )
        
        if success:
            return redirect(url_for('guidance.analyze_gaps'))
        else:
            return render_template('guidance/discover.html', error='Could not save profile')
    
    # GET request - show form
    existing_profile = StudentProfileService.get_profile(user_id)
    return render_template('guidance/discover.html', profile=existing_profile)



# STEP 2: Skill Gap Analysis

@guidance_bp.route('/gaps', methods=['GET'])
@login_required
def analyze_gaps():
    """Show skill gaps analysis."""
    user_id = session.get('user_id')
    
    # Get profile
    profile = StudentProfileService.get_profile(user_id)
    if not profile:
        return redirect(url_for('guidance.discover'))
    
    # Analyze gaps
    skill_gaps = SkillGapAnalyzer.analyze_gaps(user_id, profile)
    
    if not skill_gaps:
        return render_template('guidance/gaps.html', 
                             error='Could not analyze skill gaps')
    
    # Format gaps for display
    formatted_gaps = {
        'core': [SkillGapAnalyzer.format_gap_explanation(gap) for gap in skill_gaps.get('core_gaps', [])],
        'supporting': [SkillGapAnalyzer.format_gap_explanation(gap) for gap in skill_gaps.get('supporting_gaps', [])],
        'strengths': skill_gaps.get('strengths', []),
        'summary': skill_gaps.get('summary'),
    }
    
    return render_template('guidance/gaps.html', 
                         profile=profile,
                         gaps=formatted_gaps)



# STEP 3: Learning Path

@guidance_bp.route('/learning-path', methods=['GET'])
@login_required
def learning_path():
    """Show structured learning path."""
    user_id = session.get('user_id')
    
    profile = StudentProfileService.get_profile(user_id)
    if not profile:
        return redirect(url_for('guidance.discover'))
    
    # Get or generate learning path
    existing_path = LearningPathGenerator.get_learning_path(user_id)
    
    if not existing_path:
        # Generate new path
        skill_gaps = SkillGapAnalyzer.get_gap_analysis(user_id)
        if not skill_gaps:
            skill_gaps = SkillGapAnalyzer.analyze_gaps(user_id, profile)
        
        path_result = LearningPathGenerator.generate_learning_path(user_id, profile, skill_gaps)
        learning_path_data = path_result['path']
        total_weeks = path_result['total_weeks']
        learning_focus = path_result['learning_focus']
    else:
        learning_path_data = existing_path
        total_weeks = sum(item['weeks'] for item in learning_path_data)
        learning_focus = LearningPathGenerator._determine_learning_focus(
            SkillGapAnalyzer.get_gap_analysis(user_id) or {'core_gaps': [], 'supporting_gaps': []}
        )
    
    progress = LearningPathGenerator.get_learning_progress(user_id)
    
    return render_template('guidance/learning_path.html',
                         path=learning_path_data,
                         total_weeks=total_weeks,
                         learning_focus=learning_focus,
                         progress=progress,
                         profile=profile)



# STEP 4: Resume Evolution

@guidance_bp.route('/resume-evolution', methods=['GET'])
@login_required
def resume_evolution():
    """Show how resume should evolve."""
    user_id = session.get('user_id')
    
    profile = StudentProfileService.get_profile(user_id)
    if not profile:
        return redirect(url_for('guidance.discover'))
    
    # Generate roadmap for evolution plan
    try:
        # Use profile data to generate roadmap instead of evolution planner
        profile_data = {
            'goals': profile.get('goals', []),
            'skills': profile.get('skills', []),
            'experience': profile.get('experience', 0),
            'daily_time': profile.get('daily_time', 1)
        }
        evolution_plan = generate_roadmap(profile_data, {})
    except Exception:
        evolution_plan = {'phases': [], 'message': 'Unable to generate plan'}
    
    return render_template('guidance/resume_evolution.html',
                         plan=evolution_plan,
                         profile=profile)



# STEP 5: Action Plan

@guidance_bp.route('/actions', methods=['GET'])
@login_required
def actions():
    """Show daily, weekly, monthly action items."""
    user_id = session.get('user_id')
    
    profile = StudentProfileService.get_profile(user_id)
    if not profile:
        return redirect(url_for('guidance.discover'))
    
    # Get or generate action plan
    existing_actions = ActionGuidanceService.get_action_plan(user_id)
    
    if not existing_actions:
        skill_gaps = SkillGapAnalyzer.analyze_gaps(user_id, profile)
        learning_path = LearningPathGenerator.get_learning_path(user_id) or []
        action_plan = ActionGuidanceService.generate_action_plan(user_id, profile, skill_gaps, learning_path)
    else:
        action_plan = existing_actions
    
    return render_template('guidance/actions.html',
                         actions=action_plan,
                         profile=profile)



# Integrated Dashboard View

@guidance_bp.route('/overview', methods=['GET'])
@login_required
def overview():
    """Comprehensive guidance overview."""
    user_id = session.get('user_id')
    
    profile = StudentProfileService.get_profile(user_id)
    if not profile:
        return redirect(url_for('guidance.discover'))
    
    # Get all guidance components
    profile_complete = StudentProfileService.is_profile_complete(user_id)
    profile_completeness = StudentProfileService.calculate_profile_completeness(user_id)
    
    skill_gaps = SkillGapAnalyzer.get_gap_analysis(user_id)
    if not skill_gaps:
        skill_gaps = SkillGapAnalyzer.analyze_gaps(user_id, profile)
    
    learning_path = LearningPathGenerator.get_learning_path(user_id)
    learning_progress = LearningPathGenerator.get_learning_progress(user_id)
    
    # Generate roadmap for evolution plan
    try:
        profile_data = {
            'goals': profile.get('goals', []),
            'skills': profile.get('skills', []),
            'experience': profile.get('experience', 0),
            'daily_time': profile.get('daily_time', 1)
        }
        evolution_plan = generate_roadmap(profile_data, {})
    except Exception:
        evolution_plan = {'phases': [], 'message': 'Unable to generate plan'}
    
    action_plan = ActionGuidanceService.get_action_plan(user_id)
    
    next_steps = suggest_next_steps(profile)
    
    return render_template('guidance/overview.html',
                         profile=profile,
                         profile_complete=profile_complete,
                         profile_completeness=profile_completeness,
                         skill_gaps=skill_gaps,
                         learning_path=learning_path,
                         learning_progress=learning_progress,
                         evolution_plan=evolution_plan,
                         action_plan=action_plan,
                         next_steps=next_steps)



# API Endpoints for AJAX/Real-time updates

@guidance_bp.route('/api/profile', methods=['POST'])
@login_required
def api_save_profile():
    """Save profile via API."""
    user_id = session.get('user_id')
    data = request.get_json()
    
    success = StudentProfileService.create_profile(
        user_id=user_id,
        education_level=data.get('education_level'),
        interests=data.get('interests', []),
        current_skills=data.get('current_skills', []),
        career_goals=data.get('career_goals'),
        experience_level=data.get('experience_level'),
        confusion_areas=data.get('confusion_areas', []),
        learning_style=data.get('learning_style'),
        available_hours_per_week=data.get('available_hours'),
        target_timeline_months=data.get('target_timeline')
    )
    
    if success:
        return jsonify({'success': True, 'message': 'Profile saved'})
    else:
        return jsonify({'success': False, 'message': 'Could not save profile'}), 400


@guidance_bp.route('/api/skill-complete/<skill_area>', methods=['POST'])
@login_required
def api_mark_skill_complete(skill_area):
    """Mark a skill as completed."""
    user_id = session.get('user_id')
    success = LearningPathGenerator.mark_skill_complete(user_id, skill_area)
    
    if success:
        return jsonify({'success': True, 'message': f'{skill_area} marked as complete'})
    else:
        return jsonify({'success': False, 'message': 'Could not update skill'}), 400


@guidance_bp.route('/api/action-complete/<int:action_id>', methods=['POST'])
@login_required
def api_mark_action_complete(action_id):
    """Mark an action as completed."""
    user_id = session.get('user_id')
    success = ActionGuidanceService.mark_action_complete(user_id, action_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Action marked complete'})
    else:
        return jsonify({'success': False, 'message': 'Could not update action'}), 400


@guidance_bp.route('/api/regenerate-path', methods=['POST'])
@login_required
def api_regenerate_path():
    """Regenerate learning path."""
    user_id = session.get('user_id')
    
    profile = StudentProfileService.get_profile(user_id)
    if not profile:
        return jsonify({'success': False, 'message': 'No profile found'}), 400
    
    skill_gaps = SkillGapAnalyzer.analyze_gaps(user_id, profile)
    path_result = LearningPathGenerator.generate_learning_path(user_id, profile, skill_gaps)
    
    return jsonify({
        'success': True,
        'path': path_result['path'],
        'total_weeks': path_result['total_weeks']
    })



# Navigation Helper

@guidance_bp.route('/')
@login_required
def index():
    """Career guidance hub - entry point."""
    user_id = session.get('user_id')
    
    # Check if profile exists
    has_profile = StudentProfileService.has_profile(user_id)
    
    if has_profile:
        return redirect(url_for('guidance.overview'))
    else:
        return redirect(url_for('guidance.discover'))
