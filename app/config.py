from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://username:password@localhost:5432/pixelforge_db"
    
    # JWT
    secret_key: str = "your-super-secret-jwt-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # SMTP
    smtp_server: str = "smtp.office365.com"
    smtp_port: int = 587
    smtp_username: str = "support@pixelforgestudio.in"
    smtp_password: str = ""
    smtp_from_email: str = "support@pixelforgestudio.in"
    admin_email: str = "admin@pfs.in"
    
    # File Upload
    upload_dir: str = "uploads"
    max_file_size: int = 5242880  # 5MB
    allowed_image_extensions: str = "jpg,jpeg,png,gif,webp"
    
    # ImageKit Configuration
    imagekit_private_key: str = ""
    imagekit_public_key: str = ""
    imagekit_url_endpoint: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
