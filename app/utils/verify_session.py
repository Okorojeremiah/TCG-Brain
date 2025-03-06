from flask import json
from app.models.user import User
from app.utils.logger import logger

def verify_session(identity):
    try:
        user_data = json.loads(identity)
        user_id = user_data.get("user_id")
        session_id = user_data.get("session_id")
        is_superuser = user_data.get("is_superuser")
        user_department = user_data.get("department")
        
        user = User.query.get(user_id)
        if user and user.session_id == session_id:
            return {"user_id": user_id, "session_id": session_id, "is_superuser": is_superuser, "department": user_department}
        else:
            return {"error": "Invalid session"}
    except Exception as e:
        logger.error(f"Error verifying session: {e}", exc_info=True)
        return {"error": "Session verification failed"}
