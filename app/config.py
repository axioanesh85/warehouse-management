from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database URL - Handle both local and Render formats
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/warehouse_db")
    
    # Fix for Render's PostgreSQL URL format
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        url = self.DATABASE_URL
        
        # Handle Render's format
        if url and url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        
        # Handle asyncpg for async operations
        if "postgresql://" in url and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        return url
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    APP_NAME: str = "Warehouse Management System"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    PORT: int = int(os.getenv("PORT", 8000))
    
    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Registration
    REGISTRATION_OPEN: bool = os.getenv("REGISTRATION_OPEN", "False").lower() == "true"
    
    class Config:
        env_file = ".env"

settings = Settings()