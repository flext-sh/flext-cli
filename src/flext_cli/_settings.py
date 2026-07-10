"""FLEXT CLI Configuration Module.

CLI-specific settings extending FlextSettings. All Pydantic v2; no compatibility layers.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import BaseModel, Field, computed_field
from pydantic_settings import SettingsConfigDict

from flext_core import FlextSettings


class FlextCliSettings(FlextSettings):
    """CLI-specific configuration; extends FlextSettings with profile and CLI fields."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="FLEXT_CLI_",
        extra="ignore",
    )

    class CliSettings(BaseModel):
        """Namespaced CLI runtime settings."""

        verbose: Annotated[bool, Field(description="Verbose output")] = False
        quiet: Annotated[bool, Field(description="Quiet output")] = False
        app_name: Annotated[str, Field(description="CLI application name")] = (
            "flext-cli"
        )
        log_verbosity: Annotated[
            str,
            Field(description="Log format (compact, detailed, full)"),
        ] = "compact"
        cli_log_level: Annotated[
            str,
            Field(description="CLI log level"),
        ] = "info"
        no_color: Annotated[bool, Field(description="Disable colored output")] = False
        output_format: Annotated[
            str,
            Field(description="Output format (table, json, yaml, csv, plain)"),
        ] = "table"
        config_file: Annotated[
            str | None,
            Field(description="Path to settings file"),
        ] = None
        token_file: Annotated[
            str | None,
            Field(description="Path to auth token file"),
        ] = None
        ci: Annotated[
            bool,
            Field(description="Whether the current runtime is a CI environment."),
        ] = False
        pytest_current_test: Annotated[
            str | None,
            Field(description="Current pytest test identifier."),
        ] = None
        shell_command: Annotated[
            str | None,
            Field(description="Current shell command propagated by the runtime."),
        ] = None

        @computed_field
        @property
        def test_env(self) -> bool:
            """Whether prompts should treat the current runtime as test/CI mode."""
            normalized_shell = (self.shell_command or "").strip().lower()
            return (
                self.pytest_current_test is not None
                or "pytest" in normalized_shell
                or self.ci
            )

    Cli: CliSettings = Field(
        default_factory=CliSettings,
        description="Namespaced CLI settings branch.",
    )


settings: FlextCliSettings = FlextCliSettings.fetch_global()


__all__: list[str] = ["FlextCliSettings", "settings"]
