"""FLEXT CLI Configuration Module.

CLI-specific settings extending FlextSettings. All Pydantic v2; no compatibility layers.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from flext_core import FlextLogger, FlextSettings
from pydantic import Field, TypeAdapter

from flext_cli import c, t

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
            description="CLI config directory",
        ),
    ] = Field(default_factory=lambda: FlextCliSettings._default_config_dir())
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


__all__ = ["FlextCliSettings", "logger"]
