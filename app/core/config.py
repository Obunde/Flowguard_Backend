"""Single source of truth for all environment/configuration values.

Every setting the app needs is declared here and nowhere else. No module
outside this file should call `os.environ` / `os.getenv` directly — import
`settings` from here instead. This keeps configuration auditable in one
place and makes it trivial to see the full surface of external inputs the
app depends on.
"""
from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "flowgard"
    environment: str = "development"
    debug: bool = False

    # app/core/db.py builds the single engine/session factory from this value.
    # migrations/env.py imports `settings` and reuses it too — never a second
    # hardcoded connection string.
    database_url: str

    # Used only by tests/conftest.py, kept separate from database_url so the
    # test suite never touches real data.
    test_database_url: str | None = None

    # JWT auth (app/core/auth.py)
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # NoDecode: read as a plain string from .env (comma-separated) instead
    # of pydantic-settings' default JSON decoding for list-typed fields —
    # the `_split_csv` validator below turns it into a list.
    cors_allow_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]

    # ETL (app/etl/)
    weather_api_base_url: str = "https://api.open-meteo.com/v1"
    simulator_interval_seconds: int = 5

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def _split_csv(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor. Use `settings` below for normal imports;
    this exists mainly so tests can call `get_settings.cache_clear()`.
    """
    return Settings()


settings = get_settings()
