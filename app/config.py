import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./minipay.db"
    api_key: str = "testkey"
    auto_create_tables: bool = True
    log_level: str = "INFO"
    http_timeout_seconds: int = 5

    # Look for a local system environmental .env configuration file if present
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
