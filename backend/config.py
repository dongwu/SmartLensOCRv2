"""
Configuration management for SmartLensOCR backend.
Handles environment variables and application settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""
    
    # API Settings
    TITLE = "SmartLensOCR Backend API"
    VERSION = "1.0.0"
    DESCRIPTION = "Backend server for intelligent document OCR processing"
    
    # Server Settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///smartlensocr.db")
    DB_PATH = os.path.join(os.path.dirname(__file__), "smartlensocr.db")
    
    # CORS
    CORS_ORIGINS = [
        "http://localhost:5173",  # Vite default dev server
        "http://localhost:3000",  # Alternative dev port
        "http://localhost:8000",  # Backend dev
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # Add frontend URL if provided
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url and frontend_url not in CORS_ORIGINS:
        CORS_ORIGINS.append(frontend_url)
    
    # In production, be more restrictive
    if ENVIRONMENT == "production":
        CORS_ORIGINS = [frontend_url] if frontend_url else ["https://yourdomain.com"]
    
    # AI Settings
    GEMINI_MODEL_DETECT = "gemini-2.0-flash"
    GEMINI_MODEL_EXTRACT = "gemini-2.0-flash"
    GEMINI_THINKING_BUDGET = 4000
    
    # Image Processing
    MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20MB
    SUPPORTED_FORMATS = ["image/png", "image/jpeg", "image/gif", "image/webp"]
    
    # Credit System
    CREDITS_PER_DETECTION = 0  # Free
    CREDITS_PER_EXTRACTION = 1
    INITIAL_CREDITS = 5
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_PER_HOUR = 1000
    
    # Logging
    LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENVIRONMENT = "development"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENVIRONMENT = "production"


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    ENVIRONMENT = "testing"
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"


def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()


# Export singleton config instance
config = get_config()
