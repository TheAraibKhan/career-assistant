from flask import Blueprint, request, jsonify
import re
import logging

contact_bp = Blueprint("contact", __name__)
logger = logging.getLogger(__name__)


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
