from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.verify_session import verify_session
from app.services.user_service import fetch_user_profile, send_feedback, update_profile


user_bp = Blueprint('users', __name__, url_prefix="/user")

@user_bp.route("/profile", methods=["OPTIONS", "GET"])
@jwt_required()
def get_user_profile():
    if request.method == "OPTIONS":
        return ' ', 204
    
    identity = get_jwt_identity()
    session_response = verify_session(identity)
    
    if "error" in session_response:
        return jsonify(session_response), 401
    
    user_id = session_response.get("user_id")
    
    if not user_id:
        return jsonify({"error": "User ID not found in session."}), 401
    
    user_profile = fetch_user_profile(user_id)
    
    if "error" in user_profile:
        return jsonify(user_profile), 500
    else:
        return jsonify(user_profile), 200
    
@user_bp.route('/profile/update/<int:user_id>', methods=["OPTIONS", "PUT"])
@jwt_required()
def update_user_profile(user_id):
    if request.method == "OPTIONS":
        return ' ', 204
    
    data = request.json
    
    identity = get_jwt_identity()
    session_response = verify_session(identity)
    
    if "error" in session_response:
        return jsonify(session_response), 401 
    
    updated_profile = update_profile(user_id, data)
    if "error" in updated_profile:
        return jsonify(updated_profile), 500
    else: 
        return jsonify(updated_profile), 200
    

@user_bp.route("/send-feedback", methods=["OPTIONS", "POST"])
@jwt_required()
def receive_feedback():
    if request.method == "OPTIONS":
        return ' ', 204
    
    feedback = request.json.get('feedback', '').strip()
    if not feedback:
            return jsonify({"error": "feedback message cannot be empty."}), 400
    
    identity = get_jwt_identity()
    session_response = verify_session(identity)
    
    if "error" in session_response:
        return jsonify(session_response), 401 
    
    user_id = session_response.get("user_id")
    
    if not user_id:
        return jsonify({"error": "User ID not found in session."}), 401
    
    feedback_message = send_feedback(user_id, feedback)
    
    if "error" in feedback_message:
        return jsonify(feedback_message), 500
    else:
        return jsonify(feedback_message), 200
