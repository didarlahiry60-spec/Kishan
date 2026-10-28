import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Kishan (কৃষাণ) Agro-Intelligence API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/kishan.db"
    
    # AI Engine
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # SMS Gateway (mock, greenweb, twilio)
    SMS_PROVIDER: str = os.getenv("SMS_PROVIDER", "mock")
    SMS_API_KEY: str = os.getenv("SMS_API_KEY", "")
    SMS_SENDER_ID: str = os.getenv("SMS_SENDER_ID", "KISHAN")
    
    # Static & Audio Output
    STATIC_DIR: Path = BASE_DIR / "app" / "static"
    AUDIO_CACHE_DIR: Path = BASE_DIR / "app" / "static" / "audio_cache"
    
    # Scheduled Daily Sync
    DAILY_SYNC_HOUR: int = 6
    DAILY_SYNC_MINUTE: int = 0
    
    model_config = SettingsConfigDict(
        env_file=f"{BASE_DIR}/.env",
        extra="ignore"
    )

settings = Settings()
