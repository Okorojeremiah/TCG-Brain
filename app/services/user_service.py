from app.models.user import User
from app.utils.logger import logger


def fetch_user_profile(user_id):
    try:
        if not user_id or not isinstance(user_id, int):
            raise ValueError("Invalid user_id provided.")
        
        user_profile = User.query.filter(User.id==user_id).first()
        
        if not user_profile:
            logger.warning(f"User with ID {user_id} not found.")
            return {"error": "User not found"}
        else:
            return user_profile.to_dict()
    
    except Exception as e:
        logger.error(f"Error fetching user role for ID {user_id}: {e}")
        return {"error": str(e)}
    
    