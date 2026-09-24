from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: str = "*"
    GOOGLE_CLIENT_ID: str = ""

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
