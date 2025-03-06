from flask import Flask, current_app
from app.models.database import db
from app.models.user import User
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.utils.config import config  
from flask_migrate import Migrate 
from app.utils.ai_helper_methods import load_faiss_index, clear_faiss_index
from app.utils.setup_nltk import download_nltk
from flask_caching import Cache
import click
from werkzeug.security import generate_password_hash




jwt = JWTManager()
migrate = Migrate()




def create_app():
    app = Flask(__name__)
    app.config.from_object(config)  
    
    CORS(app, origins=config.CORS_ORIGINS, supports_credentials=True)
    
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db) 
    load_faiss_index()
    # clear_faiss_index()
    download_nltk()

    
    from app.routes.auth import auth_bp
    from app.routes.documents import documents_bp
    from app.routes.user import user_bp
    from app.routes.message import message_bp
    from app.routes.chat import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(chat_bp)

    return app

app = create_app()

@app.cli.command("create-superuser")
@click.argument("name")
@click.argument("email")
@click.argument("password")
@click.argument("department")
def create_superuser(name, email, password, department):
    """Create a superuser."""
    # Check if a user with the same email already exists
    if User.query.filter_by(email=email).first():
        print("Error: A user with this email already exists.")
        return

    # Create the superuser
    user = User(
        name=name,
        email=email,
        password=generate_password_hash(password),
        department=department,
        job_role="Admin",
        is_superuser=True
    )
    db.session.add(user)
    db.session.commit()
    print(f"Superuser '{name}' created successfully.")


    
    


