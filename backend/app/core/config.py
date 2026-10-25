from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("USERPROFILE", os.path.expanduser("~"))) / "JewelleryERP_Data"
DATA_ENV = DATA_DIR / ".env"

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./jewellery_erp.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "jewellery-erp-desktop-offline-secret-key-2026")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 14400
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: str = "*"
    GOOGLE_CLIENT_ID: str = ""
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    model_config = SettingsConfigDict(
        env_file=[str(DATA_ENV), ".env", "backend/.env"],
        extra="ignore"
    )

settings = Settings()
