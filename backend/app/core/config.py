from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./jewellery_erp.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "jewellery-erp-desktop-offline-secret-key-2026")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 14400
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: str = "*"
    GOOGLE_CLIENT_ID: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
