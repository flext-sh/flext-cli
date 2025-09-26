"""FLEXT CLI - Unified CLI abstraction layer following ZERO TOLERANCE policy.

This module provides the ONLY allowed Click abstraction in the entire FLEXT ecosystem.
All Click functionality is contained within this single module to maintain proper
domain separation and ZERO TOLERANCE enforcement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import override

import click  # ONLY module allowed to import Click in entire ecosystem

from flext_cli.api import FlextCliApi
from flext_cli.auth import FlextCliAuth
from flext_cli.commands import FlextCliCommands
from flext_cli.config import FlextCliConfig, FlextCliConfigService
from flext_cli.constants import FlextCliConstants
from flext_cli.debug import FlextCliDebug
from flext_cli.output import FlextCliOutput
from flext_core import FlextLogger, FlextResult, FlextService, FlextTypes


class FlextCli(FlextService[FlextTypes.Core.Dict]):
    """Unified CLI abstraction layer following ZERO TOLERANCE policy.

    This class provides the ONLY allowed Click abstraction in the entire FLEXT ecosystem.
    All CLI functionality is properly abstracted to maintain domain separation.
    """

    @override
    def __init__(self) -> None:
        """Initialize unified CLI abstraction layer."""
        super().__init__()
        self._logger = FlextLogger(__name__)

        # Initialize CLI components
        self._api = FlextCliApi()
        self._auth = FlextCliAuth()
        self._config = FlextCliConfigService()
        self._debug = FlextCliDebug()
        self._output = FlextCliOutput()
        self._commands = FlextCliCommands()

        self._logger.info("FlextCli abstraction layer initialized")

    # Property accessors for test compatibility
    @property
    def api(self) -> FlextCliApi:
        """Get API component."""
        return self._api

    @property
    def auth(self) -> FlextCliAuth:
        """Get auth component."""
        return self._auth

    @property
    def config(self) -> FlextCliConfig:
        """Get config component."""
        return FlextCliConfig()

    @property
    def debug(self) -> FlextCliDebug:
        """Get debug component."""
        return self._debug

    @property
    def formatters(self) -> FlextCliOutput:
        """Get formatters component (aliased to output)."""
        return self._output

    @property
    def main(self) -> FlextCliCommands:
        """Get main component (aliased to commands)."""
        return self._commands

    @override
    def execute(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute the main CLI service operation - required by FlextService."""
        return FlextResult[FlextTypes.Core.Dict].ok({
            "status": FlextCliConstants.OPERATIONAL,
            "service": FlextCliConstants.FLEXT_CLI,
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "2.0.0",
            "components": {
                "api": FlextCliConstants.AVAILABLE,
                "auth": FlextCliConstants.AVAILABLE,
                "config": FlextCliConstants.AVAILABLE,
                "debug": FlextCliConstants.AVAILABLE,
                "formatters": FlextCliConstants.AVAILABLE,
                "main": FlextCliConstants.AVAILABLE,
            },
        })

    async def execute_async(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute the main CLI service operation asynchronously - required by FlextService."""
        return FlextResult[FlextTypes.Core.Dict].ok({
            "status": FlextCliConstants.OPERATIONAL,
            "service": FlextCliConstants.FLEXT_CLI,
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "2.0.0",
            "components": {
                "api": FlextCliConstants.AVAILABLE,
                "auth": FlextCliConstants.AVAILABLE,
                "config": FlextCliConstants.AVAILABLE,
                "debug": FlextCliConstants.AVAILABLE,
                "formatters": FlextCliConstants.AVAILABLE,
                "main": FlextCliConstants.AVAILABLE,
            },
        })

    def create_cli_group(self, name: str = "flext") -> FlextResult[click.Group]:
        """Create a Click CLI group with proper abstraction.

        Args:
            name: CLI group name

        Returns:
            FlextResult[click.Group]: Click group or error

        """
        try:

            @click.group(name=name)
            @click.version_option(version="0.9.0")
            def cli_group() -> None:
                """FLEXT CLI - Enterprise Data Integration Platform."""

            return FlextResult[click.Group].ok(cli_group)
        except Exception as e:
            return FlextResult[click.Group].fail(f"Failed to create CLI group: {e}")

    def add_status_command(self, cli_group: click.Group) -> FlextResult[None]:
        """Add status command to CLI group.

        Args:
            cli_group: Click group to add command to

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:

            @cli_group.command()
            def status() -> None:
                """Show CLI status."""
                result = self.execute()
                if result.is_success:
                    click.echo("FLEXT CLI is operational")
                    data = result.unwrap()
                    click.echo(f"Service: {data['service']}")
                    click.echo(f"Version: {data['version']}")
                else:
                    click.echo(f"Error: {result.error}")
                    raise click.Abort

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to add status command: {e}")

    def add_version_command(self, cli_group: click.Group) -> FlextResult[None]:
        """Add version command to CLI group.

        Args:
            cli_group: Click group to add command to

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:

            @cli_group.command()
            def version() -> None:
                """Show version information."""
                click.echo("FLEXT CLI version 0.9.0")

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to add version command: {e}")

    def run_cli(self) -> FlextResult[None]:
        """Run the CLI interface with proper error handling.

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            # Create CLI group
            group_result = self.create_cli_group()
            if group_result.is_failure:
                return FlextResult[None].fail(
                    f"Failed to create CLI group: {group_result.error}"
                )

            cli_group = group_result.unwrap()

            # Add commands
            status_result = self.add_status_command(cli_group)
            if status_result.is_failure:
                return FlextResult[None].fail(
                    f"Failed to add status command: {status_result.error}"
                )

            version_result = self.add_version_command(cli_group)
            if version_result.is_failure:
                return FlextResult[None].fail(
                    f"Failed to add version command: {version_result.error}"
                )

            # Run the CLI
            cli_group()
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"CLI execution failed: {e}")


__all__ = [
    "FlextCli",
]
