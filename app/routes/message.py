from flask import Blueprint, request, jsonify, Flask
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.verify_session import verify_session
from app.services.message_service import send_message_receive_response
from app.utils.logger import logger
from app.utils.config import config



message_bp = Blueprint('message', __name__, url_prefix='/user/chat')


@message_bp.route('/messages', methods=["OPTIONS", "POST"])
@jwt_required()
def query():
   if request.method == 'OPTIONS':
        return ' ', 204  
     
   user_message = request.json.get('user_message', '').strip()
   chat_id = request.json.get('chat_id')
   if not user_message:
            return jsonify({"error": "Query cannot be empty."}), 400

   identity = get_jwt_identity()
   session_response = verify_session(identity)
   if "error" in session_response:
        return jsonify(session_response), 401
   
   user_id = session_response.get("user_id")
   session_id = session_response.get("session_id")
   if not user_id:
        return jsonify({"error": "User ID not found in session."}), 401
   
   chat_response = send_message_receive_response(user_message, identity, user_id, chat_id, session_id)
   if "error" in chat_response:
        return jsonify(chat_response), 500
   else:
        return jsonify(chat_response), 200
 

@message_bp.route('/voice', methods=["OPTIONS", "POST"])
@jwt_required()
def voice_mode():
    if request.method == 'OPTIONS':
        return ' ', 204

    # Get the transcribed text from the frontend
    transcribed_text = request.json.get('transcribed_text', '').strip()
    chat_id = request.json.get('chat_id')

    if not transcribed_text:
        return jsonify({"error": "Transcribed text cannot be empty."}), 400

    # Verify the user session
    identity = get_jwt_identity()
    session_response = verify_session(identity)
    if "error" in session_response:
        return jsonify(session_response), 401

    user_id = session_response.get("user_id")
    session_id = session_response.get("session_id")
    if not user_id:
        return jsonify({"error": "User ID not found in session."}), 401

    # Process the transcribed text using your existing AI service
    try:
        chat_response = send_message_receive_response(transcribed_text, identity, user_id, chat_id, session_id)
        if "error" in chat_response:
            return jsonify(chat_response), 500

        return jsonify({
            "response_text": chat_response["answer"]
        }), 200
    except Exception as e:
        logger.error(f"Error in voice mode: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

