import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    GEMINI_API_SECRET_KEY = os.getenv("GEMINI_API_SECRET_KEY")
    HUGGING_FACE_TRANSFORMER = os.getenv("HUGGING_FACE_TRANSFORMER")
    FAISS_INDEX_FILE = os.getenv("FAISS_INDEX_FILE")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    # SQLALCHEMY_BINDS = {  
    #     "okms": os.getenv("OKMS_DATABASE_URL")  
    # }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "pptx"}
    CORS_ORIGINS = os.getenv("CORS_ORIGINS")
    REDIS_URL = os.getenv("REDIS_URL")
    SECRET_KEY = os.environ.get("SECRET_KEY")

config = Config()


# load_dotenv()

# def get_env_var(key: str, default: Optional[str] = None, required: bool = True) -> str:
#     """Get environment variable with validation."""
#     value = os.getenv(key, default)
#     if required and value is None:
#         raise ValueError(f"Environment variable {key} is required but not set")
#     return value

# class BaseConfig:
#     """Base configuration class with common settings."""
#     # Security
#     SECRET_KEY = get_env_var("GEMINI_API_SECRET_KEY")
#     JWT_SECRET_KEY = get_env_var("JWT_SECRET_KEY")
#     JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
#     JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days
#     JWT_COOKIE_SECURE = True
#     JWT_COOKIE_CSRF_PROTECT = True
    
#     # Database
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     SQLALCHEMY_ENGINE_OPTIONS = {
#         'pool_size': 10,
#         'pool_recycle': 3600,
#         'pool_pre_ping': True
#     }
    
#     # File Upload
#     MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
#     UPLOAD_FOLDER = get_env_var("UPLOAD_FOLDER")
#     ALLOWED_EXTENSIONS: Set[str] = {"pdf", "docx", "txt", "pptx"}
    
#     # AI Models
#     HUGGING_FACE_TRANSFORMER = get_env_var("HUGGING_FACE_TRANSFORMER")
#     FAISS_INDEX_FILE = get_env_var("FAISS_INDEX_FILE")
#     NLIST = int(get_env_var("NLIST", "100"))
#     INDEX_DIM = int(get_env_var("INDEX_DIM", "768"))
#     M = int(get_env_var("M", "16"))
    
#     # Cache
#     CACHE_TYPE = "redis"
#     CACHE_REDIS_URL = get_env_var("REDIS_URL", "redis://localhost:6379/0")
#     CACHE_DEFAULT_TIMEOUT = 300
    
#     # Rate Limiting
#     RATELIMIT_DEFAULT = "200 per day;50 per hour"
#     RATELIMIT_STORAGE_URL = CACHE_REDIS_URL
    
#     # Security Headers
#     SECURITY_HEADERS = {
#         'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
#         'X-Content-Type-Options': 'nosniff',
#         'X-Frame-Options': 'SAMEORIGIN',
#         'X-XSS-Protection': '1; mode=block',
#         'Content-Security-Policy': "default-src 'self'"
#     }

# class DevelopmentConfig(BaseConfig):
#     """Development configuration."""
#     DEBUG = True
#     SQLALCHEMY_DATABASE_URI = get_env_var("DATABASE_URL")
#     SQLALCHEMY_BINDS = {
#         "okms": get_env_var("OKMS_DATABASE_URL")
#     }
#     JWT_COOKIE_SECURE = False
#     CORS_ORIGINS = ["http://localhost:5173"]

# class ProductionConfig(BaseConfig):
#     """Production configuration."""
#     DEBUG = False
#     SQLALCHEMY_DATABASE_URI = get_env_var("DATABASE_URL")
#     SQLALCHEMY_BINDS = {
#         "okms": get_env_var("OKMS_DATABASE_URL")
#     }
#     CORS_ORIGINS = get_env_var("CORS_ORIGINS", "").split(",")
    
#     # Production-specific security settings
#     SESSION_COOKIE_SECURE = True
#     SESSION_COOKIE_HTTPONLY = True
#     SESSION_COOKIE_SAMESITE = 'Lax'
#     PERMANENT_SESSION_LIFETIME = 3600

# class TestingConfig(BaseConfig):
#     """Testing configuration."""
#     TESTING = True
#     SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
#     SQLALCHEMY_BINDS = None
#     JWT_COOKIE_SECURE = False
#     WTF_CSRF_ENABLED = False

# # Configuration dictionary
# config_dict: Dict[str, type[BaseConfig]] = {
#     'development': DevelopmentConfig,
#     'production': ProductionConfig,
#     'testing': TestingConfig
# }

# # Get configuration based on environment
# ENV = get_env_var('FLASK_ENV', 'development', required=False)
# config = config_dict[ENV]()