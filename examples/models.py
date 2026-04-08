"""Pydantic models for flext-cli examples only.

All example-domain models live here; examples MUST NOT define models inline.
Import: from models import ... (when run from examples/ dir).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from collections.abc import Mapping, MutableSequence
from ipaddress import ip_address
from pathlib import Path
from typing import ClassVar

from pydantic import (
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
    model_validator,
)

from examples import t
from flext_cli import m
from flext_core import r


class ExamplesFlextCliModels(m):
    """Public examples model facade extending flext-cli models."""

    class Examples:
        """Examples namespace for example-domain models."""

        @staticmethod
        def merge_env_overrides(
            data: t.ModelInput,
            env_fields: Mapping[str, str],
            field_types: Mapping[str, t.TypeHintSpecifier],
        ) -> t.ModelInput:
            """Merge explicit input with environment overrides using Pydantic coercion."""
            if not isinstance(data, Mapping):
                return data
            typed_data = t.JSON_DICT_ADAPTER.validate_python(data)
            env_overrides: dict[str, t.EnvValue] = {}
            for field_name, env_name in env_fields.items():
                if env_name not in os.environ or field_name not in field_types:
                    continue
                validated_value = TypeAdapter(field_types[field_name]).validate_python(
                    os.environ[env_name],
                )
                if isinstance(validated_value, Mapping):
                    env_overrides[field_name] = t.JSON_DICT_ADAPTER.validate_python(
                        validated_value,
                    )
                    continue
                if isinstance(validated_value, Path | str | int | float | bool):
                    env_overrides[field_name] = validated_value
                    continue
                msg = f"Unsupported env override type for {field_name}: {type(validated_value).__name__}"
                raise TypeError(msg)
            return {**env_overrides, **typed_data}

        class DatabaseWizardConfig(m.Value):
            """Database setup wizard result — Pydantic v2 only."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            host: str = Field(default="localhost", description="Database host")
            port: int = Field(default=5432, ge=1, le=65535, description="Port")
            database: str = Field(default="", description="Database name")
            password: str = Field(default="", description="Password")

        class AppWizardConfig(m.Value):
            """App configuration wizard result — Pydantic v2 only."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            app_name: str = Field(default="my-app", description="Application name")
            environment: str = Field(default="development", description="Environment")
            port: int = Field(default=8080, ge=1024, le=65535, description="Port")
            cpu_limit: float = Field(default=1.0, ge=0.0, description="CPU limit")
            enable_cache: bool = Field(default=True, description="Enable cache")
            enable_auth: bool = Field(default=True, description="Enable auth")

        class NumericPromptResult(m.Value):
            """Numeric prompts result — Pydantic v2 only."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            workers: int = Field(default=4, ge=1, le=32, description="Workers")
            cpu_limit: float = Field(default=2.5, ge=0.0, description="CPU limit")
            percentage: int = Field(default=50, ge=0, le=100, description="Percentage")

        # -------------------------------------------------------------------
        # Example 06 - Configuration
        # -------------------------------------------------------------------

        class MyAppConfig(m.Value):
            """Custom configuration for YOUR CLI application — Pydantic v2 only."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            app_name: str = Field(default="my-cli-tool", description="Application name")
            api_key: str = Field(default="", description="API key")
            max_workers: int = Field(default=4, ge=1, description="Max workers")
            timeout: int = Field(default=30, ge=1, description="Timeout in seconds")

            @model_validator(mode="before")
            @classmethod
            def _inject_env(
                cls,
                data: t.ModelInput,
            ) -> t.ModelInput:
                return ExamplesFlextCliModels.Examples.merge_env_overrides(
                    data,
                    {
                        "app_name": "APP_NAME",
                        "api_key": "API_KEY",
                        "max_workers": "MAX_WORKERS",
                        "timeout": "TIMEOUT",
                    },
                    {
                        field_name: field_info.annotation or str
                        for field_name, field_info in cls.model_fields.items()
                    },
                )

            def display(self, cli: t.CliApi) -> None:
                """Display app configuration; uses cli for base settings."""
                config = cli.settings
                payload_data: t.Cli.JsonMapping = {
                    "App Name": self.app_name,
                    "API Key": f"{self.api_key[:10]}..." if self.api_key else "Not set",
                    "Max Workers": str(self.max_workers),
                    "Timeout": f"{self.timeout}s",
                    "Debug": str(config.debug),
                    "App": str(config.app_name),
                }
                payload = ExamplesFlextCliModels.Cli.DisplayData(
                    data=payload_data,
                )
                if isinstance(payload.data, dict):
                    safe_data: t.Cli.TableMappingRow = {
                        str(k): str(v) for k, v in payload.data.items()
                    }
                    cli.show_table(
                        safe_data,
                        show_header=True,
                        title="⚙️  Application Configuration",
                    )

            def validate_config(self, cli: t.CliApi) -> bool:
                """Run validation; uses cli for output."""
                if not self.api_key:
                    cli.print("❌ API_KEY not configured", style="bold red")
                    return False
                if self.max_workers < 1:
                    cli.print("❌ MAX_WORKERS must be >= 1", style="bold red")
                    return False
                cli.print("✅ Configuration valid", style="green")
                return True

        class AppConfigAdvanced(m.Value):
            """Advanced application configuration — Pydantic v2 only."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
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
                data: t.ModelInput,
            ) -> t.ModelInput:
                return ExamplesFlextCliModels.Examples.merge_env_overrides(
                    data,
                    {
                        "database_url": "DATABASE_URL",
                        "redis_url": "REDIS_URL",
                        "api_key": "API_KEY",
                        "max_workers": "MAX_WORKERS",
                        "enable_metrics": "ENABLE_METRICS",
                        "log_level": "LOG_LEVEL",
                        "temp_dir": "TEMP_DIR",
                    },
                    {
                        field_name: field_info.annotation or str
                        for field_name, field_info in cls.model_fields.items()
                    },
                )

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
                valid: tuple[str, ...] = (
                    "DEBUG",
                    "INFO",
                    "WARNING",
                    "ERROR",
                    "CRITICAL",
                )
                if v.upper() not in valid:
                    msg = f"LOG_LEVEL must be one of: {', '.join(valid)}"
                    raise ValueError(msg)
                return v.upper()

            def validate_to_mapping(self) -> r[Mapping[str, t.Cli.JsonValue]]:
                """Validate configuration and return as mapping or failure."""
                errors: MutableSequence[str] = []
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
                    return r[Mapping[str, t.Cli.JsonValue]].fail("; ".join(errors))
                return r[Mapping[str, t.Cli.JsonValue]].ok({
                    "database_url": self.database_url,
                    "redis_url": self.redis_url,
                    "api_key": "***" if self.api_key else "",
                    "max_workers": self.max_workers,
                    "enable_metrics": self.enable_metrics,
                    "log_level": self.log_level,
                    "temp_dir": str(self.temp_dir),
                })

        # -------------------------------------------------------------------
        # Example 12 - Pydantic-driven CLI
        # -------------------------------------------------------------------

        class DeployConfig(m.Value):
            """Deployment configuration - auto-generates CLI parameters."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            environment: str = Field(
                default="development",
                description="Deployment environment (dev/staging/prod)",
            )
            workers: int = Field(
                default=4,
                ge=1,
                le=32,
                description="Number of worker processes",
            )
            enable_cache: bool = Field(
                default=True, description="Enable application cache"
            )
            timeout: int = Field(
                default=30,
                ge=1,
                le=300,
                description="Request timeout in seconds",
            )

            @field_validator("environment")
            @classmethod
            def validate_environment(cls, v: str) -> str:
                """Restrict environment to development, staging, production."""
                valid_envs: t.StrSequence = ["development", "staging", "production"]
                if v not in valid_envs:
                    msg = f"Must be one of: {', '.join(valid_envs)}"
                    raise ValueError(msg)
                return v

        class DatabaseConfig(m.Value):
            """Database configuration."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            host: str = Field(default="localhost", description="Database host")
            port: int = Field(
                default=5432, ge=1024, le=65535, description="Database port"
            )
            name: str = Field(description="Database name")

        class AppConfigNested(m.Value):
            """Application configuration with nested database model."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            app_name: str = Field(description="Application name")
            version: str = Field(default="1.0.0", description="Application version")
            database: ExamplesFlextCliModels.Examples.DatabaseConfig = Field(
                description="Database configuration"
            )
            debug: bool = Field(default=False, description="Enable debug mode")

        class AdvancedDatabaseConfig(m.Value):
            """Database configuration with advanced validation."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            host: str = Field(description="Database host", default="localhost")
            port: int = Field(
                description="Database port", ge=1024, le=65535, default=5432
            )
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
                host = v.strip()
                if not host:
                    msg = "Host must be a valid hostname or IP"
                    raise ValueError(msg)
                if host == "localhost":
                    return host
                try:
                    _ = ip_address(host)
                    return host
                except ValueError:
                    if "." not in host:
                        msg = "Host must be a valid hostname or IP"
                        raise ValueError(msg) from None
                    return host


m = ExamplesFlextCliModels

__all__ = [
    "ExamplesFlextCliModels",
    "m",
]
