from flask import Flask, current_app
from app.models.database import db
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.utils.config import config  
from flask_migrate import Migrate 
from app.utils.ai_helper_methods import load_faiss_index, clear_faiss_index
# from app.utils.logger import logger
# from apscheduler.schedulers.background import BackgroundScheduler
# from app.utils.fetch_okms_documents import save_okms_documents



# Initialize extensions
jwt = JWTManager()
migrate = Migrate()
# scheduler = BackgroundScheduler()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)  

    CORS(app, origins="http://localhost:5173", supports_credentials=True)
      
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db) 
    load_faiss_index()
    # clear_faiss_index()
    
   
    

    
    from app.routes.auth import auth_bp
    from app.routes.documents import documents_bp
    from app.routes.queries import queries_bp
    from app.routes.user import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(queries_bp)
    app.register_blueprint(user_bp)
    
    # with app.app_context():
    #     scheduler.add_job(save_okms_documents, 'interval', minutes=1)  # Run every hour
    #     scheduler.start()
    #     logger.info("save_okms_documents called by the scheduler.")

 
  
    return app

# def get_scheduler():
#     return scheduler


    
    


