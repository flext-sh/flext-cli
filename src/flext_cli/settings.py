"""FLEXT CLI Configuration Module.

CLI-specific settings extending FlextSettings. All Pydantic v2; no compatibility layers.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from flext_cli import c
from flext_core import FlextLogger, FlextSettings

logger = FlextLogger(__name__)


@FlextSettings.auto_register("cli")
class FlextCliSettings(FlextSettings):
    """CLI-specific configuration; extends FlextSettings with profile and CLI fields."""

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
    token_file: Annotated[
        str | None,
        Field(default=None, description="Path to auth token file"),
    ]


__all__ = ["FlextCliSettings", "logger"]
