from flask import Blueprint, request, jsonify, Flask
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.verify_session import verify_session
from app.services.message_service import send_message_receive_response
from app.utils.logger import logger
from flask import jsonify, request, send_file
from io import BytesIO
from gtts import gTTS
from app.models.database import db
from app.models.message import Message
import json
from datetime import datetime




message_bp = Blueprint('message', __name__, url_prefix='/user/chat')


@message_bp.route('/messages', methods=["OPTIONS", "POST"])
@jwt_required()
def message():
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
   user_department = session_response.get("department")
   if not user_id:
        return jsonify({"error": "User ID not found in session."}), 401
   
   chat_response = send_message_receive_response(user_message, identity, user_id, chat_id, session_id, user_department, is_update=False)
   if "error" in chat_response:
        return jsonify(chat_response), 500
   else:
        return jsonify(chat_response), 200
    

@message_bp.route('/messages/update_full', methods=['PUT'])
@jwt_required()
def update_full():
    """
    Expects a JSON payload with:
      - userMessageId: ID of the user message to update
      - aiMessageId: ID of the corresponding AI message to update
      - newContent: New content for the user message (which will trigger regeneration of the AI response)
    """
    data = request.json
    user_message_id = data.get('userMessageId')
    ai_message_id = data.get('aiMessageId')
    new_content = data.get('newContent')

    if not user_message_id or not ai_message_id or not new_content:
        return jsonify({"error": "userMessageId, aiMessageId and newContent are required"}), 400

    # Fetch both the user message and the AI message from the database
    user_message = Message.query.get(user_message_id)
    ai_message = Message.query.get(ai_message_id)

    if not user_message or not ai_message:
        return jsonify({"error": "User or AI Message not found"}), 404

    try:
        # ------------------------
        # Update the User Message
        # ------------------------
        user_edits = json.loads(user_message.edits) if user_message.edits else []
        # Append current version before updating
        user_edits.append({
            'content': user_message.content,
            'timestamp': user_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
        user_message.edits = json.dumps(user_edits)
        user_message.edit_count += 1
        user_message.content = new_content
        user_message.timestamp = datetime.utcnow()

        # ---------------------------------------
        # Regenerate the AI Response for the edit
        # ---------------------------------------
        identity = get_jwt_identity()
        session_response = verify_session(identity)
        if "error" in session_response:
            return jsonify(session_response), 401

        user_id = session_response.get("user_id")
        session_id = session_response.get("session_id")
        user_department = session_response.get("department")

        chat_response = send_message_receive_response(
            new_content, identity, user_id, user_message.chat_id, session_id, user_department, is_update=True
        )
        if "error" in chat_response:
            return jsonify(chat_response), 500

        # ------------------------
        # Update the AI Message
        # ------------------------
        ai_edits = json.loads(ai_message.edits) if ai_message.edits else []
        # Save the current AI response version before updating
        ai_edits.append({
            'content': ai_message.content,
            'timestamp': ai_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
        ai_message.edits = json.dumps(ai_edits)
        ai_message.edit_count += 1
        ai_message.content = chat_response["answer"]
        ai_message.timestamp = datetime.utcnow()

        db.session.commit()

        return jsonify({
            "message": "Messages updated successfully",
            "updated_user_message": user_message.to_dict(),
            "updated_ai_message": ai_message.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update messages: {e}", exc_info=True)
        return jsonify({"error": "Failed to update messages"}), 500


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
    user_department = session_response.get("department")
    if not user_id:
        return jsonify({"error": "User ID not found in session."}), 401

    try:
        # Get the chat response from your existing function
        chat_response = send_message_receive_response(
            transcribed_text, identity, user_id, chat_id, session_id, user_department, is_update=True
        )
        if "error" in chat_response:
            return jsonify(chat_response), 500

        response_text = chat_response["answer"]

        # Convert the text response to speech using gTTS
        tts = gTTS(text=response_text, lang='en', tld='co.uk')
        audio_io = BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)

        # Return the generated audio file (MP3)
        return send_file(
            audio_io,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name="response.mp3"
        )

    except Exception as e:
        logger.error(f"Error in voice mode: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


