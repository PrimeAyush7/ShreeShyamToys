import os
import logging
from typing import List
from pydantic import BaseModel

logger = logging.getLogger("sst.config")

class Settings(BaseModel):
    # App
    APP_NAME: str = "Shree Shyam Toys"
    APP_URL: str = "http://localhost:8000"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Secret Key - hardened for production
    SECRET_KEY: str = ""

    # Database
    DATABASE_URL: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"
    
    # Admin Authorization Allowlist (No hardcoded fallback in production)
    ADMIN_EMAILS: str = ""
    
    # WhatsApp Default (No fake number; must be configured via Admin Settings or ENV)
    WHATSAPP_NUMBER: str = ""
    
    # Storage
    STORAGE_BACKEND: str = "local"
    SUPABASE_STORAGE_BUCKET: str = "product-media"
    UPLOAD_DIR: str = ""

    @property
    def is_production(self) -> bool:
        return (self.ENVIRONMENT.lower() == "production") or bool(os.getenv("RENDER")) or bool(os.getenv("RENDER_SERVICE_ID"))

    @property
    def admin_email_list(self) -> List[str]:
        return [email.strip().lower() for email in self.ADMIN_EMAILS.split(",") if email.strip()]

    def __init__(self, **data):
        super().__init__(**data)
        env = os.getenv("ENVIRONMENT", "development")
        self.ENVIRONMENT = env
        self.APP_URL = os.getenv("APP_URL", "http://localhost:8000")
        self.DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1")
        self.DATABASE_URL = os.getenv("DATABASE_URL", "")
        self.SUPABASE_URL = os.getenv("SUPABASE_URL", "")
        self.SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
        self.SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
        self.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
        self.WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "")
        self.STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "supabase" if (env == "production" or os.getenv("RENDER")) else "local")
        self.SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "product-media")
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads")))

        # SECRET_KEY validation
        env_secret = os.getenv("SECRET_KEY", "").strip()
        if self.is_production:
            if not env_secret:
                raise RuntimeError(
                    "CRITICAL CONFIGURATION ERROR: SECRET_KEY environment variable is missing or empty in production mode. "
                    "A secure random secret key must be set in your production environment variables."
                )
            self.SECRET_KEY = env_secret
        else:
            # Documented development-only fallback key for local offline testing
            self.SECRET_KEY = env_secret or "sst-dev-insecure-secret-key-for-local-development-only-2026"
            if not env_secret:
                logger.info("Using development secret key for local environment.")

        # ADMIN_EMAILS validation - hardened for production
        env_admin_emails = os.getenv("ADMIN_EMAILS", "").strip()
        if self.is_production:
            if not env_admin_emails:
                raise RuntimeError(
                    "CRITICAL CONFIGURATION ERROR: ADMIN_EMAILS environment variable is missing or empty in production mode. "
                    "At least one authorized administrator Google email address must be explicitly configured in your production environment variables."
                )
            self.ADMIN_EMAILS = env_admin_emails
        else:
            # Development-only fallback allowlist for local offline testing
            self.ADMIN_EMAILS = env_admin_emails or "admin@shreeshyamtoys.com,owner@shreeshyamtoys.com"

settings = Settings()
