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

    #: Origins allowed to call the API. Comma-separated in .env.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    #: Public appointment form: how many submissions one IP may make per window.
    public_form_rate_limit: int = 5
    public_form_rate_window_seconds: int = 3600

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def secret_key_is_default(self) -> bool:
        return self.secret_key in ("", "change-me")


@lru_cache
def get_settings() -> Settings:
    return Settings()
