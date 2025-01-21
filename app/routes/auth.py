from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.database import db
from app.services.auth_service import register_user, authenticate_user, logout_current_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['OPTIONS', 'POST'])
def register():
    if request.method == 'OPTIONS':
        return ' ', 200
    
    data = request.json
    response = register_user(data)
    return jsonify(response), response.get("status", 400) 

@auth_bp.route('/login', methods=['OPTIONS', 'POST'])
def login():
    if request.method == 'OPTIONS':
        return ' ', 200
    
    data = request.json
    response = authenticate_user(data)
    return response

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():  
    identity = get_jwt_identity()
    logout_current_user(identity)
    return jsonify({"message": "Logged out successfully"}), 200
   
