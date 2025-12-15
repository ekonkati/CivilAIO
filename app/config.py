from __future__ import annotations

import os
from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = Field("CivilAIO", description="Service display name")
    environment: str = Field("dev", description="Environment identifier (dev/stage/prod)")
    api_prefix: str = Field("/api", description="Base API prefix")
    version: str = Field("0.1.0", description="Semantic version for the backend")

    class Config:
        env_prefix = "CIVIL_AIO_"
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()
