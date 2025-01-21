from app.models.user import User


def fetch_user_profile(user_id):
    user_profile = User.query.filter(User.id==user_id).first()
    
    if not user_profile:
        return {"error": "User no found"}
    else:
        return user_profile.to_dict()