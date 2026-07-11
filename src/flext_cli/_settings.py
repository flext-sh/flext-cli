"""FLEXT CLI settings — flat, env-sourceable scalars only (§2.6).

Settings carry ONLY simple scalars (``str | int | bool | float``) loadable
from ``.env`` / environment / CLI flags. Composed, nested, or validated
structures belong in ``config`` (``_config.py``); behavior (such as
test-runtime detection) lives in ``_utilities/settings.py`` behind ``u.Cli``
— never on the settings model.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from flext_core import FlextSettings


class FlextCliSettings(FlextSettings):
    """CLI settings: flat scalars under the ``FLEXT_CLI_`` env prefix."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="FLEXT_CLI_",
        extra="ignore",
    )

    cli_verbose: Annotated[bool, Field(description="Verbose output")] = False
    cli_quiet: Annotated[bool, Field(description="Quiet output")] = False
    cli_app_name: Annotated[str, Field(description="CLI application name")] = (
        "flext-cli"
    )
    cli_log_verbosity: Annotated[
        str,
        Field(description="Log format (compact, detailed, full)"),
    ] = "compact"
    cli_log_level: Annotated[str, Field(description="CLI log level")] = "info"
    cli_no_color: Annotated[bool, Field(description="Disable colored output")] = False
    cli_output_format: Annotated[
        str,
        Field(description="Output format (table, json, yaml, csv, plain)"),
    ] = "table"
    cli_config_file: Annotated[
        str | None,
        Field(description="Path to settings file"),
    ] = None
    cli_token_file: Annotated[
        str | None,
        Field(description="Path to auth token file"),
    ] = None
    cli_ci: Annotated[
        bool,
        Field(description="Whether the current runtime is a CI environment."),
    ] = False
    cli_pytest_current_test: Annotated[
        str | None,
        Field(description="Current pytest test identifier."),
    ] = None
    cli_shell_command: Annotated[
        str | None,
        Field(description="Current shell command propagated by the runtime."),
    ] = None


settings: FlextCliSettings = FlextCliSettings.fetch_global()


__all__: list[str] = ["FlextCliSettings", "settings"]
