"""FLEXT CLI Configuration Module.

CLI-specific settings extending FlextSettings. All Pydantic v2; no compatibility layers.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic_settings import SettingsConfigDict

from flext_cli import c
from flext_core import FlextSettings, m


@FlextSettings.auto_register("cli")
class FlextCliSettings(FlextSettings):
    """CLI-specific configuration; extends FlextSettings with profile and CLI fields."""

    model_config: ClassVar[SettingsConfigDict] = m.SettingsConfigDict(
        env_prefix="FLEXT_CLI_",
        extra="ignore",
    )

    verbose: Annotated[bool, m.Field(description="Verbose output")] = (
        c.Cli.CLI_DEFAULT_VERBOSE
    )
    quiet: Annotated[bool, m.Field(description="Quiet output")] = (
        c.Cli.CLI_DEFAULT_QUIET
    )
    log_verbosity: Annotated[
        str,
        m.Field(
            description="Log format (compact, detailed, full)",
        ),
    ] = c.Cli.LogVerbosity.COMPACT
    cli_log_level: Annotated[c.LogLevel, m.Field(description="CLI log level")] = (
        c.LogLevel.INFO
    )
    no_color: Annotated[
        bool,
        m.Field(
            description="Disable colored output",
        ),
    ] = c.Cli.CLI_DEFAULT_NO_COLOR
    output_format: Annotated[
        str,
        m.Field(
            description="Output format (table, json, yaml, csv, plain)",
        ),
    ] = c.Cli.OUTPUT_DEFAULT_FORMAT_TYPE
    config_file: Annotated[str | None, m.Field(description="Path to settings file")] = (
        None
    )
    token_file: Annotated[
        str | None, m.Field(description="Path to auth token file")
    ] = None
