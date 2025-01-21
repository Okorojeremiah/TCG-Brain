import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("GEMINI_API_SECRET_KEY")
    HUGGING_FACE_TRANSFORMER = os.getenv("HUGGING_FACE_TRANSFORMER")
    FAISS_INDEX_FILE = os.getenv("FAISS_INDEX_FILE")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_BINDS = {  
        "okms": os.getenv("OKMS_DATABASE_URL")  
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "pptx"}
    NLIST = os.getenv("NLIST")
    INDEX_DIM = os.getenv("INDEX_DIM")
    M = os.getenv("M")

config = Config()
