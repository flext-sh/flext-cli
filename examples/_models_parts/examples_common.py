"""Split example model common namespace."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Annotated, ClassVar

from examples import c, t
from flext_cli import m, u


class ExamplesFlextCliModelsExamplesCommon:
    """Split example model common namespace."""

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
            return ExamplesFlextCliModelsExamplesCommon.merge_env_overrides(
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
            payload = m.Cli.DisplayData(
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


__all__: list[str] = ["ExamplesFlextCliModelsExamplesCommon"]
