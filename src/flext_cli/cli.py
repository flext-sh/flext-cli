"""FLEXT CLI - Unified CLI abstraction layer following ZERO TOLERANCE policy.

This module provides the ONLY allowed Click abstraction in the entire FLEXT ecosystem.
All Click functionality is contained within this single module to maintain proper
domain separation and ZERO TOLERANCE enforcement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import click

from flext_cli.constants import FlextCliConstants
from flext_cli.core import FlextCliService
from flext_cli.typings import FlextCliTypes
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextUtilities,
)


class FlextCli(FlextService[FlextCliTypes.Data.CliDataDict]):
    """Main CLI application service using domain-specific types.

    Provides the primary CLI interface for FLEXT applications with enhanced
    type safety using FlextCliTypes instead of generic FlextTypes.Core types.
    Extends FlextService with CLI-specific data dictionary types.
    """

    def __init__(
        self,
        name: str = "flext-cli",
        version: str = "2.0.0",
        description: str = "FLEXT CLI Application",
        **data: object,
    ) -> None:
        """Initialize CLI application with enhanced configuration.

        Args:
            name: CLI application name
            version: Application version
            description: Application description
            **data: Additional initialization data

        """
        super().__init__(**data)
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()

        # CLI-specific initialization
        self._name = name
        self._version = version
        self._description = description

        # Initialize CLI service as dependency
        self._cli_service = FlextCliService()

        # Initialize Click group for CLI interface
        self._click_group = click.Group(
            name=self._name,
            help=self._description,
            context_settings={"help_option_names": ["-h", "--help"]},
        )

    @property
    def name(self) -> str:
        """Get CLI application name.

        Returns:
            str: Application name

        """
        return self._name

    @property
    def version(self) -> str:
        """Get CLI application version.

        Returns:
            str: Application version

        """
        return self._version

    @property
    def description(self) -> str:
        """Get CLI application description.

        Returns:
            str: Application description

        """
        return self._description

    @property
    def cli_service(self) -> FlextCliService:
        """Get underlying CLI service.

        Returns:
            FlextCliService: CLI service instance

        """
        return self._cli_service

    @property
    def main(self) -> FlextCli:
        """Get main CLI interface for external access.

        Returns:
            FlextCli: Main CLI instance

        """
        return self

    def get_click_group(self) -> click.Group:
        """Get the underlying Click group for CLI operations.

        Returns:
            click.Group: Click command group

        """
        return self._click_group

    def run_cli(self) -> None:
        """Run the CLI application using Click."""
        try:
            self._click_group()
        except Exception:
            self._logger.exception("CLI execution failed")
            raise

    def execute(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute CLI application using CLI-specific data types.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: CLI execution result with enhanced type safety

        """
        return FlextResult[FlextCliTypes.Data.CliDataDict].ok({
            "cli_name": self._name,
            "version": self._version,
            "description": self._description,
            "status": FlextCliConstants.OPERATIONAL,
            "service": FlextCliConstants.FLEXT_CLI,
            "timestamp": FlextUtilities.Generators.generate_timestamp(),
            "components": {
                "api": "available",
                "auth": "available",
                "config": "available",
                "debug": "available",
                "formatters": "available",
                "main": "available",
            },
        })

    def get_application_info(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Get comprehensive CLI application information.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: Application information

        """
        try:
            # Get service statistics for comprehensive info
            service_stats = self._cli_service.execute()

            app_info: FlextCliTypes.Data.CliDataDict = {
                "application_name": self._name,
                "application_version": self._version,
                "application_description": self._description,
                "service_ready": service_stats.is_success,
                "commands_available": 0,  # Default value
                "session_support": True,
                "timestamp": FlextUtilities.Generators.generate_timestamp(),
            }

            # Add service information if available
            if service_stats.is_success and service_stats.value:
                service_data = service_stats.value
                if isinstance(service_data, dict):
                    commands_available_value = service_data.get(
                        "commands_registered", 0
                    )
                    if isinstance(commands_available_value, int):
                        app_info["commands_available"] = commands_available_value
                    # Store service_data as object to satisfy type checker
                    app_info["service_info"] = service_data  # type: ignore[assignment]

            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(app_info)

        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                f"Application info collection failed: {e}",
            )

    async def execute_async(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute CLI application asynchronously using CLI-specific data types.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: Async CLI execution result

        """
        return FlextResult[FlextCliTypes.Data.CliDataDict].ok({
            "cli_name": self._name,
            "version": self._version,
            "description": self._description,
            "status": FlextCliConstants.OPERATIONAL,
            "service": FlextCliConstants.FLEXT_CLI,
            "async_execution": True,
            "timestamp": FlextUtilities.Generators.generate_timestamp(),
            "components": {
                "api": "available",
                "auth": "available",
                "config": "available",
                "debug": "available",
                "formatters": "available",
                "main": "available",
            },
        })


__all__ = [
    "FlextCli",
]
