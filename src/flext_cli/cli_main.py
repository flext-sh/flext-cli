"""CLI Main Service.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from typing import TypedDict

from pydantic import Field

from flext_cli.__version__ import __version__
from flext_cli.models import FlextCliModels
from flext_core import (
    FlextDomainService,
    FlextLogger,
    FlextResult,
    __version__ as core_version,
)


class FlextCliMain(FlextDomainService[str]):
    """Unified main CLI service class using FlextDomainService.

    Provides core CLI functionality expected by the ecosystem.
    Single responsibility with nested helpers pattern.
    """

    # CLI application metadata
    name: str = Field(default="flext-cli")
    description: str = Field(default="FLEXT CLI Application")

    class CliOptions(TypedDict):
        """CLI options type structure."""

        profile: str
        output_format: str
        debug: bool
        quiet: bool
        log_level: str | None

    class CliContext(TypedDict):
        """CLI execution context structure."""

        config: dict[str, object]
        debug_mode: bool
        quiet_mode: bool
        profile: str
        output_format: str

    class VersionInfo(TypedDict):
        """Version information structure."""

        cli_version: str
        core_version: str | None
        python_version: str
        platform: str

    def __init__(
        self, name: str | None = None, description: str | None = None, **_data: object
    ) -> None:
        """Initialize FlextCliMain.

        Args:
            name: CLI application name
            description: CLI application description
            **_data: Additional data for FlextDomainService (unused)

        """
        # Initialize Pydantic fields directly - no need to pass to super().__init__()
        # FlextDomainService inherits from TimestampedModel with default_factory fields
        super().__init__()

        # Set fields after initialization if provided
        if name is not None:
            object.__setattr__(self, "name", name)
        if description is not None:
            object.__setattr__(self, "description", description)
        self._logger = FlextLogger(__name__)
        self._command_groups: dict[str, dict[str, object]] = {}

    class _OptionsHelper:
        """Nested helper class for CLI options processing."""

        @staticmethod
        def create_cli_options(
            **options: object,
        ) -> FlextResult[FlextCliMain.CliOptions]:
            """Create CLI options from provided parameters."""
            try:
                cli_options: FlextCliMain.CliOptions = {
                    "profile": str(options.get("profile", "default")),
                    "output_format": str(options.get("output_format", "table")),
                    "debug": bool(options.get("debug")),
                    "quiet": bool(options.get("quiet")),
                    "log_level": str(options.get("log_level"))
                    if options.get("log_level")
                    else None,
                }
                return FlextResult[FlextCliMain.CliOptions].ok(cli_options)
            except Exception as e:
                return FlextResult[FlextCliMain.CliOptions].fail(
                    f"CLI options creation failed: {e}"
                )

    class _ContextHelper:
        """Nested helper class for CLI context management."""

        @staticmethod
        def create_cli_context(
            config: dict[str, object],
            options: FlextCliMain.CliOptions,
        ) -> FlextResult[FlextCliMain.CliContext]:
            """Create CLI execution context."""
            try:
                cli_context: FlextCliMain.CliContext = {
                    "config": config,
                    "debug_mode": options["debug"],
                    "quiet_mode": options["quiet"],
                    "profile": options["profile"],
                    "output_format": options["output_format"],
                }
                return FlextResult[FlextCliMain.CliContext].ok(cli_context)
            except Exception as e:
                return FlextResult[FlextCliMain.CliContext].fail(
                    f"CLI context creation failed: {e}"
                )

    class _VersionHelper:
        """Nested helper class for version management."""

        @staticmethod
        def get_version_info() -> FlextResult[FlextCliMain.VersionInfo]:
            """Get comprehensive version information."""
            try:
                version_info: FlextCliMain.VersionInfo = {
                    "cli_version": __version__,
                    "core_version": core_version,
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                    "platform": sys.platform,
                }
                return FlextResult[FlextCliMain.VersionInfo].ok(version_info)
            except Exception as e:
                return FlextResult[FlextCliMain.VersionInfo].fail(
                    f"Version info retrieval failed: {e}"
                )

    def execute(self) -> FlextResult[str]:
        """Execute CLI operation - FlextDomainService interface."""
        self._logger.info("Executing CLI operation")
        return FlextResult[str].ok("CLI executed successfully")

    def get_logger(self) -> FlextLogger:
        """Get logger instance - expected by tests."""
        return self._logger

    def create_options(self, **options: object) -> FlextResult[CliOptions]:
        """Create CLI options using nested helper."""
        return self._OptionsHelper.create_cli_options(**options)

    def create_context(
        self,
        config: dict[str, object],
        options: CliOptions,
    ) -> FlextResult[CliContext]:
        """Create CLI context using nested helper."""
        return self._ContextHelper.create_cli_context(config, options)

    def get_version(self) -> FlextResult[VersionInfo]:
        """Get version information using nested helper."""
        return self._VersionHelper.get_version_info()

    def register_command_group(
        self,
        name: str,
        commands: dict[str, FlextCliModels.CliCommand],
        description: str | None = None,
    ) -> FlextResult[None]:
        """Register a command group with the CLI.

        Args:
            name: Command group name
            commands: Dictionary of commands in the group
            description: Optional description for the group

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            if not name or not name.strip():
                return FlextResult[None].fail("Command group name cannot be empty")

            if not commands:
                return FlextResult[None].fail("Commands dictionary cannot be empty")

            # Store the command group
            self._command_groups[name] = {
                "commands": commands,
                "description": description or f"{name} commands",
            }

            self._logger.info(
                f"Registered command group: {name} with {len(commands)} commands"
            )
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Command group registration failed: {e}")


__all__ = ["FlextCliMain"]
