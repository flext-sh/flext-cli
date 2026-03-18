"""Pydantic models for flext-cli examples only.

All example-domain models live here; examples MUST NOT define models inline.
Import: from models import ... (when run from examples/ dir).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from pathlib import Path

from flext_core import r, t as core_t
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    field_validator,
    model_validator,
)

from flext_cli import FlextCli, FlextCliSettings, m, t as cli_t

_JsonDictAdapter: TypeAdapter[object] = TypeAdapter(object)

# ---------------------------------------------------------------------------
# Example 03 - Interactive Prompts
# ---------------------------------------------------------------------------


class DatabaseWizardConfig(BaseModel):
    """Database setup wizard result — Pydantic v2 only."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1, le=65535, description="Port")
    database: str = Field(default="", description="Database name")
    password: str = Field(default="", description="Password")


class AppWizardConfig(BaseModel):
    """App configuration wizard result — Pydantic v2 only."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    app_name: str = Field(default="my-app", description="Application name")
    environment: str = Field(default="development", description="Environment")
    port: int = Field(default=8080, ge=1024, le=65535, description="Port")
    cpu_limit: float = Field(default=1.0, ge=0.0, description="CPU limit")
    enable_cache: bool = Field(default=True, description="Enable cache")
    enable_auth: bool = Field(default=True, description="Enable auth")


class NumericPromptResult(BaseModel):
    """Numeric prompts result — Pydantic v2 only."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    workers: int = Field(default=4, ge=1, le=32, description="Workers")
    cpu_limit: float = Field(default=2.5, ge=0.0, description="CPU limit")
    percentage: int = Field(default=50, ge=0, le=100, description="Percentage")


# ---------------------------------------------------------------------------
# Example 06 - Configuration
# ---------------------------------------------------------------------------


class MyAppConfig(BaseModel):
    """Custom configuration for YOUR CLI application — Pydantic v2 only."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    app_name: str = Field(default="my-cli-tool", description="Application name")
    api_key: str = Field(default="", description="API key")
    max_workers: int = Field(default=4, ge=1, description="Max workers")
    timeout: int = Field(default=30, ge=1, description="Timeout in seconds")

    @model_validator(mode="before")
    @classmethod
    def _inject_env(
        cls,
        data: object,
    ) -> dict[str, str | int | bool | Path] | core_t.Primitives | None:
        if not isinstance(data, dict):
            return data
        try:
            typed_data = _JsonDictAdapter.validate_python(data)
        except ValidationError:
            return {
                "app_name": "my-cli-tool",
                "api_key": "",
                "max_workers": 4,
                "timeout": 30,
            }
        if not isinstance(typed_data, dict):
            return None
        str_keys: set[str] = {"app_name", "api_key"}
        int_keys: set[str] = {"max_workers", "timeout"}
        updates = {
            k: val
            for k, val in typed_data.items()
            if (isinstance(val, str) and k in str_keys)
            or (isinstance(val, int) and k in int_keys)
        }
        return {
            "app_name": os.getenv("APP_NAME", "my-cli-tool"),
            "api_key": os.getenv("API_KEY", ""),
            "max_workers": int(os.getenv("MAX_WORKERS", "4")),
            "timeout": int(os.getenv("TIMEOUT", "30")),
            **updates,
        }

    def display(self, cli: FlextCli) -> None:
        """Display app configuration; uses cli for base settings."""
        base: FlextCliSettings = cli.config
        payload = m.Cli.DisplayData(
            data={
                "App Name": self.app_name,
                "API Key": f"{self.api_key[:10]}..." if self.api_key else "Not set",
                "Max Workers": str(self.max_workers),
                "Timeout": f"{self.timeout}s",
                "Debug": str(base.debug),
                "Profile": base.profile,
            }
        )
        cli.show_table(
            payload.data,
            headers=["Setting", "Value"],
            title="⚙️  Application Configuration",
        )

    def validate_config(self, cli: FlextCli) -> bool:
        """Run validation; uses cli for output."""
        if not self.api_key:
            cli.print("❌ API_KEY not configured", style="bold red")
            return False
        if self.max_workers < 1:
            cli.print("❌ MAX_WORKERS must be >= 1", style="bold red")
            return False
        cli.print("✅ Configuration valid", style="green")
        return True


class AppConfigAdvanced(BaseModel):
    """Advanced application configuration — Pydantic v2 only."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    database_url: str = Field(
        default="postgresql://localhost:5432/myapp",
        description="Database URL",
    )
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis URL",
    )
    api_key: str = Field(default="", description="API key")
    max_workers: int = Field(default=4, ge=1, le=100, description="Max workers")
    enable_metrics: bool = Field(default=True, description="Enable metrics")
    log_level: str = Field(default="INFO", description="Log level")
    temp_dir: Path = Field(
        default_factory=lambda: Path.home() / ".cache" / "myapp",
        description="Temp directory",
    )

    @model_validator(mode="before")
    @classmethod
    def _inject_env(
        cls,
        data: object,
    ) -> dict[str, str | int | bool | Path] | core_t.Primitives | None:
        if not isinstance(data, dict):
            return data
        try:
            typed_data = _JsonDictAdapter.validate_python(data)
        except ValidationError:
            return {
                "database_url": "postgresql://localhost:5432/myapp",
                "redis_url": "redis://localhost:6379",
                "api_key": "",
                "max_workers": 4,
                "enable_metrics": True,
                "log_level": "INFO",
                "temp_dir": Path.home() / ".cache" / "myapp",
            }
        if not isinstance(typed_data, dict):
            return None
        typed_dict: dict[str, object] = typed_data
        result = {
            "database_url": os.getenv(
                "DATABASE_URL", "postgresql://localhost:5432/myapp"
            ),
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "api_key": os.getenv("API_KEY", ""),
            "max_workers": int(os.getenv("MAX_WORKERS", "4")),
            "enable_metrics": (os.getenv("ENABLE_METRICS", "true").lower() == "true"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "temp_dir": Path(
                os.getenv("TEMP_DIR", str(Path.home() / ".cache" / "myapp"))
            ),
        }
        updates = {
            k: typed_dict[k]
            for k in (
                "database_url",
                "redis_url",
                "api_key",
                "max_workers",
                "enable_metrics",
                "log_level",
                "temp_dir",
            )
            if k in typed_dict and isinstance(typed_dict[k], (str, int, bool, Path))
        }
        return {**result, **updates}

    @field_validator("database_url")
    @classmethod
    def _validate_database_url(cls, v: str) -> str:
        if not v.startswith(("postgresql://", "mysql://")):
            msg = "DATABASE_URL must be a valid database URL"
            raise ValueError(msg)
        return v

    @field_validator("redis_url")
    @classmethod
    def _validate_redis_url(cls, v: str) -> str:
        if not v.startswith("redis://"):
            msg = "REDIS_URL must be a valid Redis URL"
            raise ValueError(msg)
        return v

    @field_validator("log_level")
    @classmethod
    def _validate_log_level(cls, v: str) -> str:
        valid: tuple[str, ...] = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        if v.upper() not in valid:
            msg = f"LOG_LEVEL must be one of: {', '.join(valid)}"
            raise ValueError(msg)
        return v.upper()

    def validate_to_mapping(self) -> r[dict[str, cli_t.Cli.JsonValue]]:
        """Validate configuration and return as mapping or failure."""
        errors: list[str] = []
        if not self.api_key and os.getenv("ENVIRONMENT") == "production":
            errors.append("API_KEY is required in production")
        if not self.temp_dir.exists():
            try:
                self.temp_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                errors.append(f"Cannot create TEMP_DIR: {e}")
        elif not self.temp_dir.is_dir():
            errors.append("TEMP_DIR must be a directory")
        if errors:
            return r.fail("; ".join(errors))
        return r.ok({
            "database_url": self.database_url,
            "redis_url": self.redis_url,
            "api_key": "***" if self.api_key else "",
            "max_workers": self.max_workers,
            "enable_metrics": self.enable_metrics,
            "log_level": self.log_level,
            "temp_dir": str(self.temp_dir),
        })


# ---------------------------------------------------------------------------
# Example 12 - Pydantic-driven CLI
# ---------------------------------------------------------------------------


class DeployConfig(BaseModel):
    """Deployment configuration - auto-generates CLI parameters."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    environment: str = Field(
        default="development",
        description="Deployment environment (dev/staging/prod)",
    )
    workers: int = Field(
        default=4, ge=1, le=32, description="Number of worker processes"
    )
    enable_cache: bool = Field(default=True, description="Enable application cache")
    timeout: int = Field(
        default=30, ge=1, le=300, description="Request timeout in seconds"
    )

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Restrict environment to development, staging, production."""
        valid_envs: list[str] = ["development", "staging", "production"]
        if v not in valid_envs:
            msg = f"Must be one of: {', '.join(valid_envs)}"
            raise ValueError(msg)
        return v


class DatabaseConfig(BaseModel):
    """Database configuration."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1024, le=65535, description="Database port")
    name: str = Field(description="Database name")


class AppConfigNested(BaseModel):
    """Application configuration with nested database model."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    app_name: str = Field(description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    database: DatabaseConfig = Field(description="Database configuration")
    debug: bool = Field(default=False, description="Enable debug mode")


class AdvancedDatabaseConfig(BaseModel):
    """Database configuration with advanced validation."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    host: str = Field(description="Database host", default="localhost")
    port: int = Field(description="Database port", ge=1024, le=65535, default=5432)
    name: str = Field(description="Database name", min_length=1)
    username: str = Field(description="Database username", min_length=1)
    password: str = Field(description="Database password", min_length=8)
    ssl_enabled: bool = Field(description="Enable SSL", default=True)
    connection_pool: int = Field(
        description="Connection pool size",
        ge=1,
        le=100,
        default=10,
    )

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Ensure host looks like a hostname or IP."""
        if not v or "." not in v:
            msg = "Host must be a valid hostname or IP"
            raise ValueError(msg)
        return v


__all__ = [
    "AdvancedDatabaseConfig",
    "AppConfigAdvanced",
    "AppConfigNested",
    "AppWizardConfig",
    "DatabaseConfig",
    "DatabaseWizardConfig",
    "DeployConfig",
    "MyAppConfig",
    "NumericPromptResult",
]
