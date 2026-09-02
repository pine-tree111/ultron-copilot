"""Application configuration using Pydantic Settings.

Enforces strict type validation and SecretStr masking for sensitive credentials.
"""

from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime application settings validated by Pydantic v2."""

    openrouter_api_key: SecretStr = Field(
        ...,
        alias="OPENROUTER_API_KEY",
        description="OpenRouter API key required for cognitive processing.",
    )
    model_name: str = Field(
        default="openrouter/free",
        alias="ULTRON_MODEL",
        description="Model identifier on Openrouter",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Sampling temperature for Ultron's creative and theatrical cadence.",
    )
    max_retries: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Maximum retry attempts on transient network failures.",
    )
    project_root: Path = Field(
        default_factory=lambda: Path.cwd().resolve(),
        description="Absolute path to the project root used for security boundary checks.",
    )
    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
        description="Application logging level (DEBUG, INFO, WARNING, ERROR).",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Singleton instance accessor
_settings_instance: Settings | None = None


def get_settings() -> Settings:
    """Retrieve the application settings singleton."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
