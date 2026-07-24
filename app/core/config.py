from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: Literal["development", "test", "staging", "production"] = "development"
    debug: bool = Field(default=False, validation_alias="APP_DEBUG")
    secret_key: str = Field(min_length=32, default="development-secret-change-me-please-123")
    access_token_expire_minutes: int = Field(default=15, ge=1, le=1440)
    refresh_token_expire_days: int = Field(default=14, ge=1, le=90)
    database_url: str = "sqlite+aiosqlite:///./cryptosage.db"
    redis_url: str = "redis://localhost:6379/0"
    coingecko_base_url: AnyHttpUrl = "https://api.coingecko.com/api/v3"
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    rate_limit_per_minute: int = Field(default=120, ge=1, le=10000)
    log_level: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
