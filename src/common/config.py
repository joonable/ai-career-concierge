from __future__ import annotations

import os
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(str, Enum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_file_encoding="utf-8")

    app_env: AppEnv = Field(default=AppEnv.DEVELOPMENT, alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    internal_api_key: str = Field(default="replace-me", alias="INTERNAL_API_KEY")
    web_origin: str = Field(default="", alias="WEB_ORIGIN")

    database_url: str = Field(
        default="",
        alias="DATABASE_URL",
    )

    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_anon_key: str = Field(default="", alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")

    google_client_id: str = Field(default="", alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", alias="GOOGLE_CLIENT_SECRET")

    slack_bot_token: str = Field(default="", alias="SLACK_BOT_TOKEN")
    slack_signing_secret: str = Field(default="", alias="SLACK_SIGNING_SECRET")
    slack_webhook_url: str = Field(default="", alias="SLACK_WEBHOOK_URL")
    slack_alerts_channel: str = Field(default="#system-alerts", alias="SLACK_ALERTS_CHANNEL")

    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL")

    langsmith_api_key: str = Field(default="", alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(
        default="ai-career-concierge-dev",
        alias="LANGSMITH_PROJECT",
    )

    pipeline_enabled: bool = Field(default=False, alias="PIPELINE_ENABLED")
    allow_dev_schedule: bool = Field(default=False, alias="ALLOW_DEV_SCHEDULE")

    scraper_headless: bool = Field(default=True, alias="SCRAPER_HEADLESS")
    scraper_timeout_ms: int = Field(default=15000, alias="SCRAPER_TIMEOUT_MS")
    scraper_max_pages: int = Field(default=2, alias="SCRAPER_MAX_PAGES")
    scraper_incruit_base_url: str = Field(
        default="https://job.incruit.com",
        alias="SCRAPER_INCRUIT_BASE_URL",
    )

    @property
    def supabase_jwks_url(self) -> str:
        return f"{self.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"

    @property
    def supabase_issuer(self) -> str:
        return f"{self.supabase_url.rstrip('/')}/auth/v1"

    @model_validator(mode="after")
    def validate_environment(self) -> "Settings":
        if self.app_env == AppEnv.PRODUCTION:
            required = {
                "SUPABASE_URL": self.supabase_url,
                "SUPABASE_SERVICE_ROLE_KEY": self.supabase_service_role_key,
                "WEB_ORIGIN": self.web_origin,
                "GOOGLE_CLIENT_ID": self.google_client_id,
                "GOOGLE_CLIENT_SECRET": self.google_client_secret,
                "SLACK_SIGNING_SECRET": self.slack_signing_secret,
                "GEMINI_API_KEY": self.gemini_api_key,
            }
            missing = [key for key, value in required.items() if not value]
            if missing:
                raise ValueError(
                    "Production settings are missing required variables: "
                    + ", ".join(sorted(missing))
                )

        if (
            self.pipeline_enabled
            and self.app_env != AppEnv.PRODUCTION
            and not self.allow_dev_schedule
        ):
            raise ValueError(
                "PIPELINE_ENABLED cannot be true outside production unless "
                "ALLOW_DEV_SCHEDULE is also true."
            )

        if self.scraper_timeout_ms <= 0:
            raise ValueError("SCRAPER_TIMEOUT_MS must be greater than 0.")

        if self.scraper_max_pages <= 0:
            raise ValueError("SCRAPER_MAX_PAGES must be greater than 0.")

        if not self.scraper_incruit_base_url:
            raise ValueError("SCRAPER_INCRUIT_BASE_URL must not be empty.")

        return self

    @classmethod
    def from_env_file(cls, env_file: Optional[str] = None) -> "Settings":
        return cls(_env_file=env_file)


def resolve_default_env_file() -> Optional[str]:
    app_env = os.getenv("APP_ENV", AppEnv.DEVELOPMENT.value)
    candidates = [f".env.{app_env}", ".env"]

    for candidate in candidates:
        if Path(candidate).exists():
            return candidate

    return None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env_file(resolve_default_env_file())
