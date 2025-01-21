import os
from flask_migrate import Migrate
from app import create_app
from app.models.database import db
import app.models


app = create_app()
migrate = Migrate(app, db)


def setup_database():
    with app.app_context():
        
        if not os.path.exists('migrations'):
            os.system("flask db init")
        
        
        os.system('flask db migrate -m "Create tables"')
        
       
        os.system("flask db upgrade")
        print("Database setup complete!")

if __name__ == "__main__":
    setup_database()
