"""FLEXT CLI Configuration Module.

CLI-specific settings extending FlextSettings. All Pydantic v2; no compatibility layers.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from flext_core import FlextLogger, FlextSettings, r
from pydantic import Field, TypeAdapter, ValidationError, computed_field

from flext_cli import c, t

logger = FlextLogger(__name__)


def _default_config_dir() -> Path:
    """Resolve default CLI config directory (e.g. ~/.flext or XDG)."""
    return Path.home() / ".flext"


class FlextCliSettings(FlextSettings):
    """CLI-specific configuration; extends FlextSettings with profile and CLI fields."""

    profile: str = Field(default="default", description="CLI profile name")
    verbose: bool = Field(
        default=c.Cli.CliDefaults.DEFAULT_VERBOSE, description="Verbose output"
    )
    quiet: bool = Field(
        default=c.Cli.CliDefaults.DEFAULT_QUIET, description="Quiet output"
    )
    log_verbosity: str = Field(
        default=c.Cli.LogVerbosity.COMPACT.value,
        description="Log format (compact, detailed, full)",
    )
    cli_log_level: c.Cli.Settings.LogLevel = Field(
        default=c.Cli.Settings.LogLevel.INFO, description="CLI log level"
    )
    no_color: bool = Field(
        default=c.Cli.CliDefaults.DEFAULT_NO_COLOR, description="Disable colored output"
    )
    output_format: str = Field(
        default=c.Cli.OutputDefaults.DEFAULT_FORMAT_TYPE,
        description="Output format (table, json, yaml, csv, plain)",
    )
    config_file: str | None = Field(default=None, description="Path to config file")
    config_dir: Path = Field(
        default_factory=_default_config_dir, description="CLI config directory"
    )
    token_file: str | None = Field(default=None, description="Path to auth token file")
    environment: str = Field(
        default="development",
        description="Environment name (development, staging, production)",
    )
    max_retries: int = Field(default=3, ge=0, description="Max retries")
    cli_timeout: float = Field(default=30.0, gt=0, description="CLI timeout seconds")
    max_width: int = Field(default=120, ge=40, le=200, description="Max output width")

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

    def execute_service(self) -> r[t.JsonDict]:
        """Execute config as service; return status dict."""
        return r[t.JsonDict].ok({"config": "loaded", "profile": self.profile})

    def load_config(self) -> r[t.JsonDict]:
        """Load current config as dict."""
        return r[t.JsonDict].ok(self.model_dump(mode="json"))

    def save_config(self, data: t.JsonDict) -> r[bool]:
        """Apply config updates from dict."""
        try:
            updated = self.model_copy(update=data)
            for key in data:
                if hasattr(self, key):
                    setattr(self, key, getattr(updated, key))
            return r[bool].ok(value=True)
        except (ValueError, TypeError) as e:
            return r[bool].fail(str(e))

    def update_from_cli_args(self, **kwargs: t.JsonValue) -> r[bool]:
        """Update config from CLI args."""
        data: t.JsonDict = {
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
            f"{c.Cli.ErrorMessages.INVALID_OUTPUT_FORMAT.format(format=output_format)}. Valid: {valid_str}"
        )

    @classmethod
    def load_from_config_file(cls, path: Path) -> r[FlextCliSettings]:
        """Load settings from a JSON or YAML config file."""
        if not path.exists():
            return r[FlextCliSettings].fail(
                c.Cli.ErrorMessages.CONFIG_FILE_NOT_FOUND.format(file=str(path))
            )
        suffix = path.suffix.lower()
        if suffix not in {".json", ".yaml", ".yml"}:
            return r[FlextCliSettings].fail(
                c.Cli.ErrorMessages.UNSUPPORTED_CONFIG_FORMAT.format(suffix=suffix)
            )
        try:
            raw = path.read_text(encoding="utf-8")
            if suffix == ".json":
                parsed: object = json.loads(raw)
            else:
                parsed = yaml.safe_load(raw)
            if not isinstance(parsed, dict):
                return r[FlextCliSettings].fail(c.Cli.CmdErrorMessages.CONFIG_NOT_DICT)
            mapping_adapter: TypeAdapter[t.ConfigurationMapping] = TypeAdapter(
                t.ConfigurationMapping
            )
            data: t.ConfigurationMapping = mapping_adapter.validate_python(parsed)
            instance = cls.model_validate(data)
            return r[FlextCliSettings].ok(instance)
        except (
            json.JSONDecodeError,
            yaml.YAMLError,
            ValidationError,
            ValueError,
            TypeError,
        ) as e:
            return r[FlextCliSettings].fail(
                c.Cli.ErrorMessages.FAILED_LOAD_CONFIG_FROM_FILE.format(
                    file=str(path), error=e
                )
            )


__all__ = ["FlextCliSettings", "logger"]
