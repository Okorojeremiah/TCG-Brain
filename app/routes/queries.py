from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.verify_session import verify_session
from app.services.query_service import query_documents, fetch_user_query_history


queries_bp = Blueprint('queries', __name__, url_prefix='/user')


@queries_bp.route('/query', methods=["OPTIONS", "POST"])
@jwt_required()
def query():
   if request.method == 'OPTIONS':
        return ' ', 200  
     
   user_query = request.json.get('user_query', '').strip()
   if not user_query:
            return jsonify({"error": "Query cannot be empty."}), 400

   identity = get_jwt_identity()
   session_response = verify_session(identity)
   if "error" in session_response:
        return jsonify(session_response), 401
   
   user_id = session_response.get("user_id")
   session_id = session_response.get("session_id")
   if not user_id:
        return jsonify({"error": "User ID not found in session."}), 401
   
   chat_response = query_documents(user_query, identity, user_id, session_id)
   if "error" in chat_response:
        return jsonify(chat_response), 500
   else:
        return jsonify(chat_response), 200
 
@queries_bp.route('/query-history', methods=["OPTIONS", "GET"]) 
@jwt_required()
def get_user_query_history():
     if request.method == 'OPTIONS':
          return ' ', 200
     
     identity = get_jwt_identity()
     session_response = verify_session(identity)
     if "error" in session_response:
          return jsonify(session_response), 401
     
     user_id = session_response.get("user_id")
     if not user_id:
          return jsonify({"error": "User ID not found in session."}), 401
     
     topic = request.args.get('topic', None)
     query_history = fetch_user_query_history(user_id, topic)
     if "error" in query_history:
        return jsonify(query_history), 500
     else:
        return jsonify(query_history), 200