from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
import re
import logging
from database.db import get_db
from datetime import datetime

contact_bp = Blueprint("contact", __name__)
logger = logging.getLogger(__name__)


@contact_bp.route("/", methods=["GET"])
def index():
    """Contact page"""
    return render_template('contact.html')


@contact_bp.route("/submit", methods=["POST"])
def submit():
    """Submit feedback via HTML form"""
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    subject = request.form.get('subject', '').strip()
    message = request.form.get('message', '').strip()
    
    if not all([name, email, subject, message]):
        flash('All fields are required', 'error')
        return redirect(url_for('contact.index'))
    
    try:
        db = get_db()
        feedback_text = f"From: {name} ({email})\nSubject: {subject}\n\n{message}"
        db.execute('''
            INSERT INTO user_feedback (user_id, feedback_text, rating, feature, submitted_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (None, feedback_text, None, 'general', datetime.now().isoformat()))
        db.commit()
        
        logger.info(f"Contact form submission - Name: {name}, Email: {email}, Subject: {subject}")
        flash('Thanks for your feedback! We appreciate you.', 'success')
        return redirect(url_for('contact.index'))
    except Exception as e:
        logger.error(f"Contact form error: {str(e)}")
        flash('Something went wrong. Please try again.', 'error')
        return redirect(url_for('contact.index'))


@contact_bp.route("/api/contact", methods=["POST"])
def submit_contact():
    """
    Handle contact form submissions
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        message = data.get("message", "").strip()

        # Validation
        if not name or len(name) < 2:
            return jsonify({"success": False, "message": "Please enter a valid name"}), 400

        # Email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not email or not re.match(email_pattern, email):
            return jsonify({"success": False, "message": "Please enter a valid email"}), 400

        if not message or len(message) < 10:
            return jsonify({"success": False, "message": "Please write a message (at least 10 characters)"}), 400

        # Log the contact submission
        logger.info(f"Contact form submission - Name: {name}, Email: {email}, Message: {message[:50]}...")

        # Return success response
        return jsonify({"success": True, "message": "Thanks for reaching out. I'll get back to you soon."}), 200

    except Exception as error:
        logger.error(f"Contact form error: {str(error)}")
        return jsonify({"success": False, "message": "An error occurred. Please try again later."}), 500
