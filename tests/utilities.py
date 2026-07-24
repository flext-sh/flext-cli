"""Test utilities for flext-cli.

Composes ``FlextTestsUtilities + u`` via MRO. Hosts only flext-cli-specific
helpers; everything generic comes from the parent namespaces.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from flext_cli import cli, u
from flext_tests import FlextTestsUtilities, r
from tests import c, p
from tests.settings import TestsFlextCliSettings


class TestsFlextCliUtilities(FlextTestsUtilities, u):
    """Test utilities for flext-cli."""

    class Tests(FlextTestsUtilities.Tests):
        """flext-cli-specific test utilities."""

        @staticmethod
        def create_test_settings() -> p.Result[p.Cli.Settings]:
            """Create test settings via Railway pattern."""
            return r[p.Cli.Settings].ok(TestsFlextCliSettings())

        @staticmethod
        def create_cli_app() -> p.Result[p.Cli.Application]:
            """Create CLI app via Railway pattern."""
            # NOTE (multi-agent, mro-wkii.19.4): the CLI owns global settings.
            return r[p.Cli.Application].ok(
                cli.create_app_with_common_params(
                    name="tests-cli", help_text="Test CLI app"
                )
            )

        @staticmethod
        def create_decorated_command(
            app: p.Cli.Application, command_name: str = "test"
        ) -> p.Result[Callable[..., None]]:
            """Register a real flag-driven command on ``app`` for tests."""

            def command(
                *,
                verbose: Annotated[bool, cli.create_option("verbose")] = False,
                debug: Annotated[bool, cli.create_option("debug")] = False,
                log_level: Annotated[
                    str, cli.create_option("cli_log_level")
                ] = c.LogLevel.INFO,
                output_format: Annotated[
                    str, cli.create_option("output_format")
                ] = c.Cli.OutputFormats.TABLE,
            ) -> None:
                cli.u.Cli.print(f"Command: {command_name}")
                if verbose:
                    cli.u.Cli.print("Verbose: enabled")
                if debug:
                    cli.u.Cli.print("Debug: enabled")
                cli.u.Cli.print(f"Log level: {log_level}")
                cli.u.Cli.print(f"Output format: {output_format}")

            cli.register_command(
                app, name=command_name, help_text=f"Run {command_name}", command=command
            )
            return r[Callable[..., None]].ok(command)


u = TestsFlextCliUtilities

__all__: list[str] = ["TestsFlextCliUtilities", "u"]
