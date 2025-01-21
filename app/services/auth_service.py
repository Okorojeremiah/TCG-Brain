from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from flask import jsonify, json
import uuid
from app.models.database import db
from flask_jwt_extended import create_access_token
from datetime import timedelta

def register_user(data):
    try:
        email = data.get("email")
        password = data.get("password")
        if User.query.filter_by(email=email).first():
            return {"error": "Email already exists", "status": 400}
        
        user = User(
            name=data.get("name"),
            email=email,
            password=generate_password_hash(password),
            job_role=data.get("job_role"),
        )
        db.session.add(user)
        db.session.commit()
        return {"message": "User registered successfully", "status": 201}
    except Exception as e:
        return {"error": str(e), "status": 500}

def authenticate_user(data):
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401 
    
    session_id = str(uuid.uuid4())
    
    identity_payload = json.dumps({
        "user_id": user.id,
        "session_id": session_id,
    })

    access_token = create_access_token(
        identity=identity_payload,
        expires_delta=timedelta(hours=12)
    )
    
    update_session_id(session_id, user.id)
    
    return jsonify({"message": "Login successful", "access_token": access_token}), 200

def logout_current_user(current_user):
    if current_user:  
        current_user = json.loads(current_user)  
        user_id = current_user["user_id"]
        update_session_id(None, user_id)
    return {"message": "Logged out successfully"}


def update_session_id(session_id, user_id):
    user = User.query.get(user_id)
    if user:
        user.session_id = session_id
        db.session.commit()
