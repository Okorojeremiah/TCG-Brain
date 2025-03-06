from app.models.user import User
from app.utils.logger import logger
from app.models.database import db
from app.models.feedback import Feedback


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
    
    
def send_feedback(user_id, feedback_text):
    try:
        # Validate input
        if not user_id or not isinstance(user_id, int):
            raise ValueError("Invalid user_id provided.")
        if not feedback_text or not isinstance(feedback_text, str):
            raise ValueError("Feedback text must be a non-empty string.")

        # Create new feedback record
        new_feedback = Feedback(
            user_id=user_id,
            feedback_text=feedback_text
        )

        # Add and commit to database
        db.session.add(new_feedback)
        db.session.commit()

        return {'message': 'Feedback saved successfully!'}
    except Exception as e:
        db.session.rollback()  # Rollback if there's an error
        logger.error(f"Error saving feedback to database: {e}")
        return {'error': str(e)}