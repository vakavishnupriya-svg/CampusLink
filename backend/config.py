import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Campus Event Pro"
    ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    
    SECRET_KEY: str = "supersecretjwtkeycampuseventpro2026enterprisegrade"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    DATABASE_URL: str = "sqlite:///./campus_event_pro.db"
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
