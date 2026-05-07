"""Pydantic models for flext-cli examples only.

All example-domain models live here; examples MUST NOT define models inline.
Import: from models import ... (when run from examples/ dir).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from collections.abc import (
    Mapping,
    MutableSequence,
)
from ipaddress import ip_address
from pathlib import Path
from typing import Annotated, ClassVar

from examples import c, p, r, t
from flext_cli import m, u


class ExamplesFlextCliModels(m):
    """Public examples model facade extending flext-cli models."""

    class Examples:
        """Examples namespace for example-domain models."""

        @staticmethod
        def merge_env_overrides(
            data: t.ExampleModelInput,
            env_fields: t.StrMapping,
            field_types: t.MappingKV[str, t.TypeHintSpecifier],
        ) -> t.ExampleModelInput:
            """Merge explicit input with environment overrides using Pydantic coercion."""
            if not isinstance(data, Mapping):
                return data
            typed_data = t.JSON_DICT_ADAPTER.validate_python(data)
            env_overrides: dict[str, t.EnvValue] = {}
            for field_name, env_name in env_fields.items():
                if env_name not in os.environ or field_name not in field_types:
                    continue
                validated_value: t.EnvValue = m.TypeAdapter(
                    field_types[field_name]
                ).validate_python(
                    os.environ[env_name],
                )
                if isinstance(validated_value, Mapping):
                    env_overrides[field_name] = dict(
                        t.JSON_DICT_ADAPTER.validate_python(
                            validated_value,
                        ),
                    )
                    continue
                if isinstance(validated_value, Path | str | int | float | bool):
                    env_overrides[field_name] = validated_value
                    continue
                msg = f"Unsupported env override type for {field_name}: {type(validated_value).__name__}"
                raise TypeError(msg)
            return {**env_overrides, **typed_data}

        # -------------------------------------------------------------------
        # Example 06 - Configuration
        # -------------------------------------------------------------------

        class MyAppSettings(m.Value):
            """Custom settings for YOUR CLI application — Pydantic v2 only."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            app_name: Annotated[
                str,
                m.Field(
                    description="Application name",
                ),
            ] = c.EXAMPLE_DEFAULT_TOOL_NAME
            api_key: Annotated[str, m.Field(description="API key")] = ""
            max_workers: Annotated[
                int,
                m.Field(
                    ge=1,
                    description="Max workers",
                ),
            ] = c.EXAMPLE_DEFAULT_MAX_WORKERS
            timeout: Annotated[
                int,
                m.Field(
                    ge=1,
                    description="Timeout in seconds",
                ),
            ] = c.EXAMPLE_DEFAULT_TIMEOUT_SECONDS

            @u.model_validator(mode="before")
            @classmethod
            def _inject_env(
                cls,
                data: t.ExampleModelInput,
            ) -> t.ExampleModelInput:
                return ExamplesFlextCliModels.Examples.merge_env_overrides(
                    data,
                    c.EXAMPLE_ENV_MAP_MY_APP,
                    {
                        field_name: field_info.annotation or str
                        for field_name, field_info in cls.model_fields.items()
                    },
                )

            def display(self, cli: t.CliApi) -> None:
                """Display app settings; uses cli for base settings."""
                settings = cli.settings
                payload_data: t.JsonMapping = {
                    "App Name": self.app_name,
                    "API Key": f"{self.api_key[:10]}..." if self.api_key else "Not set",
                    "Max Workers": str(self.max_workers),
                    "Timeout": f"{self.timeout}s",
                    "Debug": str(settings.debug),
                    "App": settings.Cli.app_name,
                }
                payload = ExamplesFlextCliModels.Cli.DisplayData(
                    data=payload_data,
                )
                if isinstance(payload.data, dict):
                    safe_data: t.Cli.TableMappingRow = {
                        k: str(v) for k, v in payload.data.items()
                    }
                    cli.show_table(
                        safe_data,
                        show_header=True,
                        title="⚙️  Application Settings",
                    )

        class AppSettingsAdvanced(m.Value):
            """Advanced application settings — Pydantic v2 only."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            database_url: Annotated[
                str,
                m.Field(
                    description="Database URL",
                ),
            ] = c.EXAMPLE_DEFAULT_DB_URL
            redis_url: Annotated[
                str,
                m.Field(
                    description="Redis URL",
                ),
            ] = c.EXAMPLE_DEFAULT_REDIS_URL
            api_key: Annotated[str, m.Field(description="API key")] = ""
            environment: Annotated[
                c.DeploymentEnvironment,
                m.Field(description="Deployment environment"),
            ] = c.EXAMPLE_DEFAULT_ENVIRONMENT
            max_workers: Annotated[
                int,
                m.Field(
                    ge=1,
                    le=c.EXAMPLE_MAX_CONNECTION_POOL,
                    description="Max workers",
                ),
            ] = c.EXAMPLE_DEFAULT_MAX_WORKERS
            enable_metrics: Annotated[bool, m.Field(description="Enable metrics")] = (
                True
            )
            log_level: Annotated[
                str,
                m.Field(
                    description="Log level",
                ),
            ] = c.EXAMPLE_DEFAULT_LOG_LEVEL
            temp_dir: Path = m.Field(
                default_factory=lambda: (
                    Path.home()
                    / c.Cli.PATH_FLEXT_DIR_NAME
                    / c.EXAMPLE_DEFAULT_TEMP_SUBDIR
                ),
                description="Temp directory",
            )

            @u.model_validator(mode="before")
            @classmethod
            def _inject_env(
                cls,
                data: t.ExampleModelInput,
            ) -> t.ExampleModelInput:
                return ExamplesFlextCliModels.Examples.merge_env_overrides(
                    data,
                    c.EXAMPLE_ENV_MAP_ADVANCED_APP,
                    {
                        field_name: field_info.annotation or str
                        for field_name, field_info in cls.model_fields.items()
                    },
                )

            @u.field_validator("database_url")
            @classmethod
            def _validate_database_url(cls, v: str) -> str:
                if not v.startswith(c.EXAMPLE_DB_URL_PREFIXES):
                    msg = c.EXAMPLE_ERR_INVALID_DB_URL
                    raise ValueError(msg)
                return v

            @u.field_validator("redis_url")
            @classmethod
            def _validate_redis_url(cls, v: str) -> str:
                if not v.startswith(c.EXAMPLE_REDIS_URL_PREFIX):
                    msg = c.EXAMPLE_ERR_INVALID_REDIS_URL
                    raise ValueError(msg)
                return v

            @u.field_validator("log_level")
            @classmethod
            def _validate_log_level(cls, v: str) -> str:
                valid: t.StrSequence = c.Cli.LOG_LEVELS
                if v.upper() not in valid:
                    msg = f"LOG_LEVEL must be one of: {', '.join(valid)}"
                    raise ValueError(msg)
                return v.upper()

            def validate_to_mapping(self) -> p.Result[t.MappingKV[str, t.JsonValue]]:
                """Validate configuration and return as mapping or failure."""
                errors: MutableSequence[str] = []
                if (
                    not self.api_key
                    and self.environment == c.DeploymentEnvironment.PRODUCTION
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
                    return r[t.MappingKV[str, t.JsonValue]].fail("; ".join(errors))
                return r[t.MappingKV[str, t.JsonValue]].ok({
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

        class AdvancedDatabaseConfig(m.Value):
            """Database configuration with advanced validation."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            host: str = m.Field(
                description="Database host",
            )
            port: int = m.Field(
                c.EXAMPLE_DEFAULT_DB_PORT,
                description="Database port",
                ge=c.EXAMPLE_MIN_PORT,
                le=c.EXAMPLE_MAX_PORT,
                validate_default=True,
            )
            name: str = m.Field(description="Database name", min_length=1)
            username: str = m.Field(description="Database username", min_length=1)
            password: str = m.Field(
                description="Database password",
                min_length=c.EXAMPLE_MIN_PASSWORD_LENGTH,
            )
            ssl_enabled: bool = m.Field(
                True, description="Enable SSL", validate_default=True
            )
            connection_pool: int = m.Field(
                c.EXAMPLE_DEFAULT_CONNECTION_POOL,
                description="Connection pool size",
                ge=1,
                le=c.EXAMPLE_MAX_CONNECTION_POOL,
                validate_default=True,
            )

            @u.field_validator("host")
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

__all__: list[str] = [
    "ExamplesFlextCliModels",
    "m",
]
