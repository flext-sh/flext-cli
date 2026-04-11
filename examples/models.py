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

from examples import c, t
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
            port: int = Field(
                default=c.EXAMPLE_DEFAULT_DB_PORT,
                ge=1,
                le=c.EXAMPLE_MAX_PORT,
                description="Port",
            )
            database: str = Field(default="", description="Database name")
            password: str = Field(default="", description="Password")

        class AppWizardConfig(m.Value):
            """App configuration wizard result — Pydantic v2 only."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            app_name: str = Field(
                default=c.EXAMPLE_DEFAULT_APP_NAME,
                description="Application name",
            )
            environment: str = Field(
                default=c.EXAMPLE_DEFAULT_ENVIRONMENT,
                description="Environment",
            )
            port: int = Field(
                default=c.EXAMPLE_DEFAULT_APP_PORT,
                ge=c.EXAMPLE_MIN_PORT,
                le=c.EXAMPLE_MAX_PORT,
                description="Port",
            )
            cpu_limit: float = Field(
                default=c.EXAMPLE_DEFAULT_CPU_LIMIT,
                ge=0.0,
                description="CPU limit",
            )
            enable_cache: bool = Field(default=True, description="Enable cache")
            enable_auth: bool = Field(default=True, description="Enable auth")

        class NumericPromptResult(m.Value):
            """Numeric prompts result — Pydantic v2 only."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            workers: int = Field(
                default=c.EXAMPLE_DEFAULT_MAX_WORKERS,
                ge=1,
                le=c.EXAMPLE_MAX_WORKERS,
                description="Workers",
            )
            cpu_limit: float = Field(
                default=c.EXAMPLE_DEFAULT_CPU_LIMIT_PROMPTS,
                ge=0.0,
                description="CPU limit",
            )
            percentage: int = Field(
                default=c.EXAMPLE_DEFAULT_PERCENTAGE,
                ge=0,
                le=100,
                description="Percentage",
            )

        # -------------------------------------------------------------------
        # Example 06 - Configuration
        # -------------------------------------------------------------------

        class MyAppConfig(m.Value):
            """Custom configuration for YOUR CLI application — Pydantic v2 only."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            app_name: str = Field(
                default=c.EXAMPLE_DEFAULT_TOOL_NAME,
                description="Application name",
            )
            api_key: str = Field(default="", description="API key")
            max_workers: int = Field(
                default=c.EXAMPLE_DEFAULT_MAX_WORKERS,
                ge=1,
                description="Max workers",
            )
            timeout: int = Field(
                default=c.EXAMPLE_DEFAULT_TIMEOUT_SECONDS,
                ge=1,
                description="Timeout in seconds",
            )

            @model_validator(mode="before")
            @classmethod
            def _inject_env(
                cls,
                data: t.ModelInput,
            ) -> t.ModelInput:
                return ExamplesFlextCliModels.Examples.merge_env_overrides(
                    data,
                    c.EXAMPLE_ENV_MAP_MY_APP,
                    {
                        field_name: field_info.annotation or str
                        for field_name, field_info in cls.model_fields.items()
                    },
                )

            def display(self, cli: t.CliApi) -> None:
                """Display app configuration; uses cli for base settings."""
                settings = cli.settings
                payload_data: t.Cli.JsonMapping = {
                    "App Name": self.app_name,
                    "API Key": f"{self.api_key[:10]}..." if self.api_key else "Not set",
                    "Max Workers": str(self.max_workers),
                    "Timeout": f"{self.timeout}s",
                    "Debug": str(settings.debug),
                    "App": str(settings.app_name),
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
                    cli.print(
                        "❌ API_KEY not configured", style=c.Cli.MessageStyles.BOLD_RED
                    )
                    return False
                if self.max_workers < 1:
                    cli.print(
                        "❌ MAX_WORKERS must be >= 1",
                        style=c.Cli.MessageStyles.BOLD_RED,
                    )
                    return False
                cli.print("✅ Configuration valid", style=c.Cli.MessageStyles.GREEN)
                return True

        class AppConfigAdvanced(m.Value):
            """Advanced application configuration — Pydantic v2 only."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            database_url: str = Field(
                default=c.EXAMPLE_DEFAULT_DB_URL,
                description="Database URL",
            )
            redis_url: str = Field(
                default=c.EXAMPLE_DEFAULT_REDIS_URL,
                description="Redis URL",
            )
            api_key: str = Field(default="", description="API key")
            max_workers: int = Field(
                default=c.EXAMPLE_DEFAULT_MAX_WORKERS,
                ge=1,
                le=c.EXAMPLE_MAX_CONNECTION_POOL,
                description="Max workers",
            )
            enable_metrics: bool = Field(default=True, description="Enable metrics")
            log_level: str = Field(
                default=c.EXAMPLE_DEFAULT_LOG_LEVEL,
                description="Log level",
            )
            temp_dir: Path = Field(
                default_factory=lambda: (
                    Path.home()
                    / c.Cli.PATH_FLEXT_DIR_NAME
                    / c.EXAMPLE_DEFAULT_TEMP_SUBDIR
                ),
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
                    c.EXAMPLE_ENV_MAP_ADVANCED_APP,
                    {
                        field_name: field_info.annotation or str
                        for field_name, field_info in cls.model_fields.items()
                    },
                )

            @field_validator("database_url")
            @classmethod
            def _validate_database_url(cls, v: str) -> str:
                if not v.startswith(c.EXAMPLE_DB_URL_PREFIXES):
                    msg = c.EXAMPLE_ERR_INVALID_DB_URL
                    raise ValueError(msg)
                return v

            @field_validator("redis_url")
            @classmethod
            def _validate_redis_url(cls, v: str) -> str:
                if not v.startswith(c.EXAMPLE_REDIS_URL_PREFIX):
                    msg = c.EXAMPLE_ERR_INVALID_REDIS_URL
                    raise ValueError(msg)
                return v

            @field_validator("log_level")
            @classmethod
            def _validate_log_level(cls, v: str) -> str:
                valid: tuple[str, ...] = c.Cli.LOG_LEVELS
                if v.upper() not in valid:
                    msg = f"LOG_LEVEL must be one of: {', '.join(valid)}"
                    raise ValueError(msg)
                return v.upper()

            def validate_to_mapping(self) -> r[Mapping[str, t.Cli.JsonValue]]:
                """Validate configuration and return as mapping or failure."""
                errors: MutableSequence[str] = []
                if (
                    not self.api_key
                    and os.getenv(c.EXAMPLE_ENV_KEY_ENVIRONMENT)
                    == c.EXAMPLE_ENV_VALUE_PRODUCTION
                ):
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
                default=c.EXAMPLE_DEFAULT_ENVIRONMENT,
                description="Deployment environment (dev/staging/prod)",
            )
            workers: int = Field(
                default=c.EXAMPLE_DEFAULT_MAX_WORKERS,
                ge=1,
                le=c.EXAMPLE_MAX_WORKERS,
                description="Number of worker processes",
            )
            enable_cache: bool = Field(
                default=True, description="Enable application cache"
            )
            timeout: int = Field(
                default=c.EXAMPLE_DEFAULT_TIMEOUT_SECONDS,
                ge=1,
                le=300,
                description="Request timeout in seconds",
            )

            @field_validator("environment")
            @classmethod
            def validate_environment(cls, v: str) -> str:
                """Restrict environment to development, staging, production."""
                if v not in c.EXAMPLE_DEPLOYMENT_ENVIRONMENTS_SET:
                    msg = f"Must be one of: {', '.join(c.EXAMPLE_DEPLOYMENT_ENVIRONMENTS)}"
                    raise ValueError(msg)
                return v

        class DatabaseConfig(m.Value):
            """Database configuration."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            host: str = Field(
                default=c.EXAMPLE_DEFAULT_HOST,
                description="Database host",
            )
            port: int = Field(
                default=c.EXAMPLE_DEFAULT_DB_PORT,
                ge=c.EXAMPLE_MIN_PORT,
                le=c.EXAMPLE_MAX_PORT,
                description="Database port",
            )
            name: str = Field(description="Database name")

        class AppConfigNested(m.Value):
            """Application configuration with nested database model."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            app_name: str = Field(description="Application name")
            version: str = Field(
                default=c.EXAMPLE_DEFAULT_APP_VERSION,
                description="Application version",
            )
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
            host: str = Field(
                description="Database host",
                default=c.EXAMPLE_DEFAULT_HOST,
            )
            port: int = Field(
                description="Database port",
                ge=c.EXAMPLE_MIN_PORT,
                le=c.EXAMPLE_MAX_PORT,
                default=c.EXAMPLE_DEFAULT_DB_PORT,
            )
            name: str = Field(description="Database name", min_length=1)
            username: str = Field(description="Database username", min_length=1)
            password: str = Field(
                description="Database password",
                min_length=c.EXAMPLE_MIN_PASSWORD_LENGTH,
            )
            ssl_enabled: bool = Field(description="Enable SSL", default=True)
            connection_pool: int = Field(
                description="Connection pool size",
                ge=1,
                le=c.EXAMPLE_MAX_CONNECTION_POOL,
                default=c.EXAMPLE_DEFAULT_CONNECTION_POOL,
            )

            @field_validator("host")
            @classmethod
            def validate_host(cls, v: str) -> str:
                """Ensure host looks like a hostname or IP."""
                host = v.strip()
                if not host:
                    msg = c.EXAMPLE_ERR_INVALID_HOST
                    raise ValueError(msg)
                if host == c.EXAMPLE_DEFAULT_HOST:
                    return host
                try:
                    _ = ip_address(host)
                    return host
                except ValueError:
                    if not c.EXAMPLE_REGEX_DOT.search(host):
                        msg = c.EXAMPLE_ERR_INVALID_HOST
                        raise ValueError(msg) from None
                    return host


m = ExamplesFlextCliModels

__all__ = [
    "ExamplesFlextCliModels",
    "m",
]
