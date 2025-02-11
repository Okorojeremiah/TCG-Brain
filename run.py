from app import create_app
from app.utils.fetch_okms_documents import save_okms_documents
from app.utils.logger import logger
from flask_apscheduler import APScheduler



# Create and run the app using the factory
app = create_app()
scheduler = APScheduler(app=app)

@scheduler.task('interval', id='fetch_documents', seconds=60000)  # Runs every 10 minutes for testing
def fetch_and_save_documents_job():
    with app.app_context():
        save_okms_documents(app)

@app.route('/')
def home():
    return "Welcome to the Flask server!"  


if __name__ == '__main__':
   
    try:
        scheduler.start()
        app.run(debug=True)
    except Exception as e:
        logger.error(f"Failed during startup: {e}")
