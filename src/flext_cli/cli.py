"""FLEXT CLI - Unified facade class for direct CLI access.

Single FlextCli class providing unified access to all CLI functionality.
Follows FLEXT pattern of one class per module with direct access.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime

import click

from flext_cli.api import FlextCliApi
from flext_cli.auth import FlextCliAuth
from flext_cli.commands import FlextCliCommands
from flext_cli.config import FlextCliConfig
from flext_cli.debug import FlextCliDebug
from flext_cli.output import FlextCliOutput
from flext_core import FlextResult


class FlextCli:
    """Unified CLI facade providing direct access to all CLI functionality.

    Single entry point for the FLEXT CLI ecosystem, aggregating all CLI services
    without wrappers or aliases, following FLEXT domain patterns.
    """

    def __init__(self) -> None:
        """Initialize unified CLI facade."""
        # Direct access to CLI components
        self.api = FlextCliApi()
        self.auth = FlextCliAuth()
        self.config = FlextCliConfig.MainConfig()
        self.debug = FlextCliDebug()
        self.formatters = FlextCliOutput()
        self.main = FlextCliCommands()

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute the main domain service operation - required by FlextService."""
        return FlextResult[dict[str, object]].ok({
            "status": "operational",
            "service": "flext-cli",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "2.0.0",
            "components": {
                "api": "available",
                "auth": "available",
                "config": "available",
                "debug": "available",
                "formatters": "available",
                "main": "available",
            },
        })

    def run_cli(self) -> None:
        """Run the CLI interface."""

        # Create Click group
        @click.group()
        @click.version_option(version="0.9.0")
        def cli() -> None:
            """FLEXT CLI - Enterprise Data Integration Platform."""

        # Add basic commands
        @cli.command()
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

        @cli.command()
        def version() -> None:
            """Show version information."""
            click.echo("FLEXT CLI version 0.9.0")

        # Register commands
        cli.add_command(status)
        cli.add_command(version)

        # Run the CLI
        cli()


__all__ = [
    "FlextCli",
]
