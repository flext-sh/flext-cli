"""Split example model advanced namespace."""

from __future__ import annotations

from collections.abc import MutableSequence
from pathlib import Path
from typing import Annotated, ClassVar

from examples import c, p, r, t
from examples._models_parts.examples_common import ExamplesFlextCliModelsExamplesCommon
from flext_cli import m, p, u


class ExamplesFlextCliModelsExamplesAdvanced:
    """Split example model advanced namespace."""

    class AppSettingsAdvanced(m.Value):
        """Advanced application settings — Pydantic v2 only."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            extra="forbid", validate_assignment=True
        )
        database_url: Annotated[str, m.Field(description="Database URL")] = (
            c.EXAMPLE_DEFAULT_DB_URL
        )
        redis_url: Annotated[str, m.Field(description="Redis URL")] = (
            c.EXAMPLE_DEFAULT_REDIS_URL
        )
        api_key: Annotated[str, m.Field(description="API key")] = ""
        environment: Annotated[
            c.DeploymentEnvironment, m.Field(description="Deployment environment")
        ] = c.EXAMPLE_DEFAULT_ENVIRONMENT
        max_workers: Annotated[
            int,
            m.Field(ge=1, le=c.EXAMPLE_MAX_CONNECTION_POOL, description="Max workers"),
        ] = c.EXAMPLE_DEFAULT_MAX_WORKERS
        enable_metrics: Annotated[bool, m.Field(description="Enable metrics")] = True
        log_level: Annotated[str, m.Field(description="Log level")] = (
            c.EXAMPLE_DEFAULT_LOG_LEVEL
        )
        temp_dir: Path = m.Field(
            Path.home() / c.Cli.PATH_FLEXT_DIR_NAME / c.EXAMPLE_DEFAULT_TEMP_SUBDIR,
            description="Temp directory",
            validate_default=True,
        )

        @u.model_validator(mode="before")
        @classmethod
        def _inject_env(cls, data: t.ExampleModelInput) -> t.ExampleModelInput:
            return ExamplesFlextCliModelsExamplesCommon.merge_env_overrides(
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


__all__: list[str] = ["ExamplesFlextCliModelsExamplesAdvanced"]
