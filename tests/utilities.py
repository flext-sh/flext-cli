"""Test utilities for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

import typer
from flext_tests import FlextTestsUtilities

from flext_cli import (
    FlextCliCmd,
    FlextCliCommands,
    FlextCliCommonParams,
    FlextCliSettings,
    u,
)
from flext_core import r
from tests import t


class TestsFlextCliUtilities(FlextTestsUtilities, u):
    """Test utilities for flext-cli."""

    class Cli(u.Cli):
        """Cli domain test utilities."""

        class Tests:
            """Test-specific utilities for flext-cli."""

            @staticmethod
            def create_test_config() -> r[FlextCliSettings]:
                """Create test config using Railway pattern."""
                try:
                    config = FlextCliSettings()
                    return r[FlextCliSettings].ok(config)
                except Exception as e:
                    return r[FlextCliSettings].fail(
                        f"Failed to create test config: {e}"
                    )

            @staticmethod
            def create_cli_app() -> r[typer.Typer]:
                """Create CLI app using Railway pattern."""
                try:
                    app = typer.Typer()
                    return r[typer.Typer].ok(app)
                except Exception as e:
                    return r[typer.Typer].fail(f"Failed to create CLI app: {e}")

            @staticmethod
            def create_decorated_command(
                app: typer.Typer,
                command_name: str = "test",
            ) -> r[Callable[..., None]]:
                """Create decorated command using Railway pattern."""

                @app.command(name=command_name)
                def typer_command(
                    verbose: Annotated[
                        bool,
                        FlextCliCommonParams.create_option("verbose"),
                    ] = False,
                    debug: Annotated[
                        bool,
                        FlextCliCommonParams.create_option("debug"),
                    ] = False,
                    log_level: Annotated[
                        str,
                        FlextCliCommonParams.create_option("cli_log_level"),
                    ] = "INFO",
                    output_format: Annotated[
                        str,
                        FlextCliCommonParams.create_option("output_format"),
                    ] = "table",
                ) -> None:
                    """Test command with Railway-oriented parameter handling."""
                    typer.echo(f"Command: {command_name}")
                    if verbose:
                        typer.echo("Verbose: enabled")
                    if debug:
                        typer.echo("Debug: enabled")
                    typer.echo(f"Log level: {log_level}")
                    typer.echo(f"Output format: {output_format}")

                return r[Callable[..., None]].ok(typer_command)

            @staticmethod
            def create_cmd_instance() -> FlextCliCmd:
                """Create FlextCliCmd instance for testing."""
                return FlextCliCmd()

            class CommandsFactory:
                """Factory for creating test commands with high automation."""

                @staticmethod
                def create_commands() -> FlextCliCommands:
                    """Create a FlextCliCommands instance for testing."""
                    return FlextCliCommands()

                @staticmethod
                def register_simple_command(
                    commands: FlextCliCommands,
                    command_name: str,
                    result_value: str = "success",
                ) -> r[bool]:
                    """Register a simple test command that returns a fixed value."""

                    def handler(
                        *args: t.ContainerValue,
                        **kwargs: t.ContainerValue,
                    ) -> r[t.RecursiveValue]:
                        return r[t.RecursiveValue].ok(result_value)

                    return commands.register_handler(command_name, handler)

                @staticmethod
                def register_command_with_args(
                    commands: FlextCliCommands,
                    command_name: str,
                ) -> r[bool]:
                    """Register a command that accepts arguments."""

                    def handler(
                        *args: t.ContainerValue,
                        **kwargs: t.ContainerValue,
                    ) -> r[t.RecursiveValue]:
                        return r[t.RecursiveValue].ok(f"args: {len(args)}")

                    return commands.register_handler(command_name, handler)

                @staticmethod
                def register_failing_command(
                    commands: FlextCliCommands,
                    command_name: str,
                    error_message: str = "Test error",
                ) -> r[bool]:
                    """Register a command that fails with a specific error."""

                    def handler(
                        *args: t.ContainerValue,
                        **kwargs: t.ContainerValue,
                    ) -> r[t.RecursiveValue]:
                        return r[t.RecursiveValue].fail(error_message)

                    return commands.register_handler(command_name, handler)


u = TestsFlextCliUtilities
__all__ = ["TestsFlextCliUtilities", "u"]
