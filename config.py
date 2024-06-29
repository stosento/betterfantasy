from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    DISCORD_WEBHOOK_URL: str
    DATABASE_URL: Optional[str] = None
    API_KEY: Optional[str] = None
    cfbd_api_key: str
    twilio_number: str
    discord_bot_token: str
    discord_channel_id: str
    bf_api_keys: str
    current_year: str
    past_year: str
    environment: str
    dev_postgres_url: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Create a global instance of the settings
settings = get_settings()