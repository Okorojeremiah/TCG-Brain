from flask import Flask, current_app
from app.models.database import db
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.utils.config import config  
from flask_migrate import Migrate 
from app.utils.ai_helper_methods import load_faiss_index, clear_faiss_index
from app.utils.setup_nltk import download_nltk
from flask_caching import Cache



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


    
    


