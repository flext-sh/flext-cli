"""Configuration module for FLEXT CLI."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from flext_core.config.base import BaseSettings


class CLIOutputFormat(StrEnum):
    """CLI output format options."""

    TABLE = "table"
    JSON = "json"
    YAML = "yaml"


class CLIConfig(BaseSettings):
    """CLI configuration settings."""

    api_url: str = "http://localhost:8000"
    timeout: int = 30
    verify_ssl: bool = True
    output_format: CLIOutputFormat = CLIOutputFormat.TABLE
    verbose: bool = False
    config_dir: Path = Path.home() / ".flext-cli"

    class Config:
        """Pydantic configuration."""

        env_prefix = "FLEXT_CLI_"


class CLISettings(CLIConfig):
    """Alias for backward compatibility."""


__all__ = ["CLIConfig", "CLIOutputFormat", "CLISettings"]
