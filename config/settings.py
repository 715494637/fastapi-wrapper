"""
Configuration settings for the FastAPI wrapper.
"""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")

    # Gemini API settings
    secure_1psid: Optional[str] = Field(default=None, env="SECURE_1PSID")
    secure_1psidts: Optional[str] = Field(default=None, env="SECURE_1PSIDTS")
    gemini_proxy: Optional[str] = Field(default=None, env="GEMINI_PROXY")
    gemini_timeout: int = Field(default=300, env="GEMINI_TIMEOUT")
    gemini_auto_refresh: bool = Field(default=True, env="GEMINI_AUTO_REFRESH")

    # CORS settings
    cors_origins: str = Field(
        default="*",
        env="CORS_ORIGINS",
    )
    cors_methods: str = Field(
        default="*",
        env="CORS_METHODS",
    )
    cors_headers: str = Field(
        default="*",
        env="CORS_HEADERS",
    )

    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # API settings
    api_title: str = Field(default="Gemini API Wrapper", env="API_TITLE")
    api_version: str = Field(default="1.0.0", env="API_VERSION")
    api_description: str = Field(
        default="OpenAI-compatible API wrapper for Google Gemini",
        env="API_DESCRIPTION",
    )

    # Rate limiting
    rate_limit_enabled: bool = Field(default=False, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=60, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()