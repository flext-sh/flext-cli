"""FLEXT CLI Configuration Module.

CLI-specific settings extending FlextSettings. All Pydantic v2; no compatibility layers.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Annotated

import yaml
from flext_core import FlextLogger, FlextSettings, r
from pydantic import Field, TypeAdapter, ValidationError, computed_field

from flext_cli import c, m, t, u

_JSON_OBJECT_ADAPTER: TypeAdapter[t.Cli.JsonValue] = TypeAdapter(t.Cli.JsonValue)

logger = FlextLogger(__name__)


class FlextCliSettings(FlextSettings):
    """CLI-specific configuration; extends FlextSettings with profile and CLI fields."""

    @staticmethod
    def _default_config_dir() -> Path:
        """Resolve default CLI config directory (e.g. ~/.flext or XDG)."""
        return Path.home() / ".flext"

    profile: Annotated[str, Field(default="default", description="CLI profile name")]
    verbose: Annotated[
        bool,
        Field(default=c.Cli.CliDefaults.DEFAULT_VERBOSE, description="Verbose output"),
    ]
    quiet: Annotated[
        bool,
        Field(default=c.Cli.CliDefaults.DEFAULT_QUIET, description="Quiet output"),
    ]
    log_verbosity: Annotated[
        str,
        Field(
            default=c.Cli.LogVerbosity.COMPACT.value,
            description="Log format (compact, detailed, full)",
        ),
    ]
    cli_log_level: Annotated[
        c.Cli.Settings.LogLevel,
        Field(default=c.Cli.Settings.LogLevel.INFO, description="CLI log level"),
    ]
    no_color: Annotated[
        bool,
        Field(
            default=c.Cli.CliDefaults.DEFAULT_NO_COLOR,
            description="Disable colored output",
        ),
    ]
    output_format: Annotated[
        str,
        Field(
            default=c.Cli.OutputDefaults.DEFAULT_FORMAT_TYPE,
            description="Output format (table, json, yaml, csv, plain)",
        ),
    ]
    config_file: Annotated[
        str | None,
        Field(default=None, description="Path to config file"),
    ]
    config_dir: Annotated[
        Path,
        Field(
            default_factory=lambda: FlextCliSettings._default_config_dir(),
            description="CLI config directory",
        ),
    ]
    token_file: Annotated[
        str | None,
        Field(default=None, description="Path to auth token file"),
    ]
    environment: Annotated[
        str,
        Field(
            default="development",
            description="Environment name (development, staging, production)",
        ),
    ]
    max_retries: Annotated[
        t.NonNegativeInt,
        Field(default=3, description="Max retries"),
    ]
    cli_timeout: Annotated[
        t.PositiveFloat,
        Field(default=30.0, description="CLI timeout seconds"),
    ]
    max_width: Annotated[
        t.NonNegativeInt,
        Field(default=120, le=200, description="Max output width"),
    ]

    @classmethod
    def get_instance(cls) -> FlextCliSettings:
        """Return shared settings instance expected by CLI tests."""
        return cls.get_global()

    @computed_field
    @property
    def auto_output_format(self) -> str:
        """Computed output format for display (mirrors output_format)."""
        return self.output_format

    @computed_field
    @property
    def auto_verbosity(self) -> str:
        """Computed verbosity for display: one of normal, quiet, verbose."""
        if self.verbose:
            return "verbose"
        if self.quiet:
            return "quiet"
        return "normal"

    @computed_field
    @property
    def auto_color_support(self) -> bool:
        """Whether color is supported (inverse of no_color)."""
        return not self.no_color

    @computed_field
    @property
    def optimal_table_format(self) -> str:
        """Optimal table format for display (one of simple, grid, github, plain)."""
        return "simple"

    def execute_service(self) -> r[Mapping[str, t.Cli.JsonValue]]:
        """Execute config as service; return status dict."""
        return r.ok({"config": "loaded", "profile": self.profile})

    def load_config(self) -> r[Mapping[str, t.Cli.JsonValue]]:
        """Load current config as dict."""
        return r.ok(self.model_dump(mode="json"))

    def save_config(self, data: t.Cli.JsonValue) -> r[bool]:
        """Apply config updates from dict."""
        if not isinstance(data, Mapping):
            return r[bool].fail(c.Cli.CmdErrorMessages.CONFIG_NOT_DICT)

        validated_data: Mapping[str, t.Cli.JsonValue] = {
            str(key): m.Cli.normalize_json_value(value) for key, value in data.items()
        }

        def _apply_updates() -> bool:
            updated = self.model_copy(update=validated_data)
            for key in validated_data:
                if hasattr(self, key):
                    setattr(self, key, getattr(updated, key))
            return True

        return u.try_(_apply_updates).map_error(str)

    def update_from_cli_args(self, **kwargs: t.Scalar) -> r[bool]:
        """Update config from CLI args."""
        data: Mapping[str, t.Cli.JsonValue] = {
            k: v for k, v in kwargs.items() if k in self.__class__.model_fields
        }
        return self.save_config(data)

    def validate_cli_overrides(self, **kwargs: str | bool | None) -> r[bool]:
        """Validate CLI override keys."""
        for key in kwargs:
            if key not in self.__class__.model_fields:
                return r[bool].fail(f"Unknown config key: {key}")
        return r[bool].ok(value=True)

    def validate_output_format_result(self, output_format: str) -> r[bool]:
        """Validate output_format against allowed values. Returns r[bool]."""
        if output_format in c.Cli.ValidationLists.OUTPUT_FORMATS:
            return r[bool].ok(value=True)
        valid_str = ", ".join(c.Cli.ValidationLists.OUTPUT_FORMATS)
        return r[bool].fail(
            f"{c.Cli.ErrorMessages.INVALID_OUTPUT_FORMAT.format(format=output_format)}. Valid: {valid_str}",
        )

    @classmethod
    def load_from_config_file(cls, path: Path) -> r[FlextCliSettings]:
        """Load settings from a JSON or YAML config file."""
        if not path.exists():
            return r[FlextCliSettings].fail(
                c.Cli.ErrorMessages.CONFIG_FILE_NOT_FOUND.format(file=str(path)),
            )
        suffix = path.suffix.lower()
        if suffix not in {".json", ".yaml", ".yml"}:
            return r[FlextCliSettings].fail(
                c.Cli.ErrorMessages.UNSUPPORTED_CONFIG_FORMAT.format(suffix=suffix),
            )
        try:
            raw = path.read_text(encoding="utf-8")
            if suffix == ".json":
                parsed: t.Cli.JsonValue = _JSON_OBJECT_ADAPTER.validate_json(raw)
            else:
                parsed = yaml.safe_load(raw)
            if not isinstance(parsed, dict):
                return r[FlextCliSettings].fail(c.Cli.CmdErrorMessages.CONFIG_NOT_DICT)
            data = _JSON_OBJECT_ADAPTER.validate_python(parsed)
            instance = cls.model_validate(data)
            return r[FlextCliSettings].ok(instance)
        except (
            yaml.YAMLError,
            ValidationError,
            ValueError,
            TypeError,
        ) as e:
            return r[FlextCliSettings].fail(
                c.Cli.ErrorMessages.FAILED_LOAD_CONFIG_FROM_FILE.format(
                    file=str(path),
                    error=e,
                ),
            )


__all__ = ["FlextCliSettings", "logger"]
