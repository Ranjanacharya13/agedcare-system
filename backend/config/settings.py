from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding="utf-8")

    project_name: str = "Aged Care System"
    api_v1_prefix: str = "/api/v1"

    supabase_url: str = ""
    supabase_key: str = ""

    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
