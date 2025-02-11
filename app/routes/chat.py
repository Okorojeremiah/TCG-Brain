from flask import Blueprint, request, jsonify
from app.models import User
from app.services.chat_service import create_chat_instance, fetch_chat_history, fetch_chat_messages, edit_chat_history_name, delete_chat_history
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.verify_session import verify_session


chat_bp = Blueprint('chat', __name__, url_prefix='/user')

@chat_bp.route('/chat', methods=["OPTIONS", "POST"])
@jwt_required()
def create_chat():
    """
    Endpoint to create a new chat for a user.
    Expects a JSON payload with 'user_id'.
    """
    if request.method == 'OPTIONS':
        return ' ', 204
    
        
    identity = get_jwt_identity()
    session_response = verify_session(identity)
    if "error" in session_response:
            return jsonify(session_response), 401
    
    user_id = session_response.get("user_id")
    session_id = session_response.get("session_id")
    if not user_id:
        return jsonify({"error": "User ID not found in session."}), 401
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        new_chat = create_chat_instance(user_id, session_id)
        return jsonify({
            'message': 'Chat created successfully',
            'chat_id': new_chat.id,
        }), 201
    except Exception as e:
        return jsonify({'error': 'Failed to create chat', 'details': str(e)}), 500


@chat_bp.route('/chat_history', methods=["OPTIONS","GET"])
@jwt_required()
def get_chat_history():
    """
    Returns a list of chat histories for the authenticated user.
    """
    if request.method == 'OPTIONS':
        return ' ', 204 
    
    identity = get_jwt_identity()
    session_response = verify_session(identity)
    if "error" in session_response:
        return jsonify(session_response), 401

    user_id = session_response.get("user_id")
    chats = fetch_chat_history(user_id)
    return jsonify(chats), 200


@chat_bp.route('/chat_history/<int:chat_id>', methods=["OPTIONS", "GET"])
@jwt_required()
def get_chat_messages(chat_id):
    """
    HTTP route to fetch chat messages.
    """
    if request.method == 'OPTIONS':
        return ' ', 204

    result = fetch_chat_messages(chat_id)
    if result["status"] == 404:
        return jsonify({"error": result["error"]}), 404

    return jsonify({"name": result["name"], "messages": result["messages"]}), 200


@chat_bp.route('/chat_history/edit_chat_name/<int:chat_id>', methods=["OPTIONS", "PUT"])
@jwt_required()
def edit_chat_name(chat_id):
    """
    HTTP route to change chat name.
    """
    if request.method == 'OPTIONS':
        return ' ', 204
    
    data = request.json
    if not data or "name" not in data:
        return jsonify({"error": "Missing chat name"}), 400
    
    new_chat_name = data.get("name")
    

    result = edit_chat_history_name(new_chat_name, chat_id)
    if result["status"] == 500:
        return jsonify({"error": result["error"]}), 500

    return jsonify({"message": result["message"]}), 200


@chat_bp.route('/chat_history/delete_chat/<int:chat_id>', methods=["OPTIONS", "DELETE"])
@jwt_required()
def delete_chat(chat_id):
    """
    HTTP route to delete a chat.
    """
    if request.method == 'OPTIONS':
        return ' ', 204

    result = delete_chat_history(chat_id)
    if result["status"] == 500:
        return jsonify({"error": result["error"]}), 500

    return jsonify({"message": result["message"]}), 200