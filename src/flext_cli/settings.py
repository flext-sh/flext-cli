"""FLEXT CLI Configuration Module.

CLI-specific settings extending FlextSettings. All Pydantic v2; no compatibility layers.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated

from flext_cli import c
from flext_core import FlextSettingsBase, m, u


class FlextCliSettings(FlextSettingsBase):
    """CLI-specific configuration; extends FlextSettings with profile and CLI fields."""

    model_config = m.SettingsConfigDict(
        env_prefix="FLEXT_CLI_",
        extra="ignore",
    )

    # Common application identification (post-rule-3 isolation: project owns
    # its own copies of root-style fields).
    app_name: Annotated[str, m.Field(description="Application name")] = "flext-cli"
    debug: Annotated[bool, m.Field(description="Enable debug mode")] = False
    trace: Annotated[bool, m.Field(description="Enable trace mode")] = False

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
    ci: Annotated[
        bool,
        u.Field(
            default=c.Cli.ENV_DEFAULT_CI,
            validation_alias=c.Cli.ENV_VAR_CI,
            description="Whether the current runtime is a CI environment.",
        ),
    ]
    pytest_current_test: Annotated[
        str | None,
        u.Field(
            default=None,
            validation_alias=c.Cli.ENV_VAR_PYTEST_CURRENT_TEST,
            description="Current pytest test identifier when running under pytest.",
        ),
    ] = None
    shell_command: Annotated[
        str | None,
        u.Field(
            default=None,
            validation_alias=c.Cli.ENV_VAR_SHELL_COMMAND,
            description="Current shell command propagated by the runtime environment.",
        ),
    ] = None

    @u.computed_field()
    @property
    def test_env(self) -> bool:
        """Whether prompts should treat the current runtime as test/CI mode."""
        normalized_shell = (self.shell_command or "").strip().lower()
        return (
            self.pytest_current_test is not None
            or "pytest" in normalized_shell
            or self.ci
        )
