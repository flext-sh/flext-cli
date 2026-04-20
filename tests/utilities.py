"""Test utilities for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from collections.abc import (
    Callable,
)
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
from tests import c, p, r, t


class TestsFlextCliUtilities(FlextTestsUtilities, u):
    """Test utilities for flext-cli."""

    class Cli(u.Cli):
        """Cli domain test utilities."""

        class Tests:
            """Test-specific utilities for flext-cli."""

            class VersionTestFactory:
                """Version validation helpers exposed through the canonical `u` namespace."""

                @staticmethod
                def validate_version_string(version: str) -> p.Result[str]:
                    """Validate version string against semver pattern."""
                    if not version:
                        return r[str].fail(c.Cli.Tests.VersionErrors.EMPTY_STRING)
                    pattern = c.Cli.Tests.VersionExamples.SEMVER_PATTERN
                    if not re.match(pattern, version):
                        return r[str].fail(
                            f"Version '{version}' does not match semver pattern"
                        )
                    return r[str].ok(version)

                @staticmethod
                def validate_version_info(
                    version_info: tuple[int | str, ...],
                ) -> p.Result[tuple[int | str, ...]]:
                    """Validate version info tuple structure."""
                    if len(version_info) < 3:
                        return r[tuple[int | str, ...]].fail(
                            c.Cli.Tests.VersionErrors.INFO_TOO_SHORT,
                        )
                    for index, part in enumerate(version_info):
                        if isinstance(part, int) and part < 0:
                            return r[tuple[int | str, ...]].fail(
                                f"Version part {index} must be non-negative int",
                            )
                        if isinstance(part, str) and not part:
                            return r[tuple[int | str, ...]].fail(
                                f"Version part {index} must be non-empty string",
                            )
                    return r[tuple[int | str, ...]].ok(version_info)

                @staticmethod
                def validate_consistency(
                    version_string: str,
                    version_info: tuple[int | str, ...],
                ) -> p.Result[tuple[str, tuple[int | str, ...]]]:
                    """Validate consistency between version string and version info."""
                    string_result = TestsFlextCliUtilities.Cli.Tests.VersionTestFactory.validate_version_string(
                        version_string,
                    )
                    if string_result.failure:
                        return r[tuple[str, tuple[int | str, ...]]].fail(
                            f"Invalid version string: {string_result.error}",
                        )
                    info_result = TestsFlextCliUtilities.Cli.Tests.VersionTestFactory.validate_version_info(
                        version_info,
                    )
                    if info_result.failure:
                        return r[tuple[str, tuple[int | str, ...]]].fail(
                            f"Invalid version info: {info_result.error}",
                        )
                    version_without_metadata = version_string.split("+", maxsplit=1)[0]
                    version_base_and_prerelease = version_without_metadata.split("-")
                    base_parts = version_base_and_prerelease[0].split(".")
                    prerelease_parts = (
                        version_base_and_prerelease[1].split(".")
                        if len(version_base_and_prerelease) > 1
                        else []
                    )
                    version_parts: list[int | str] = []
                    for part in [*base_parts, *prerelease_parts]:
                        try:
                            version_parts.append(int(part))
                        except ValueError:
                            u.fetch_logger(__name__).debug(
                                f"version part non-int, keep as str: {part}"
                            )
                            version_parts.append(part)
                    for index, info_part in enumerate(version_info):
                        if index >= len(version_parts):
                            break
                        version_part = version_parts[index]
                        same_kind = (
                            isinstance(info_part, int) and isinstance(version_part, int)
                        ) or (
                            isinstance(info_part, str) and isinstance(version_part, str)
                        )
                        if not same_kind:
                            return r[tuple[str, tuple[int | str, ...]]].fail(
                                f"Type mismatch at position {index}: {type(version_part).__name__} != {type(info_part).__name__}",
                            )
                        if version_part != info_part:
                            return r[tuple[str, tuple[int | str, ...]]].fail(
                                f"Mismatch at position {index}: {version_part} != {info_part}",
                            )
                    return r[tuple[str, tuple[int | str, ...]]].ok((
                        version_string,
                        version_info,
                    ))

            @staticmethod
            def create_test_settings() -> p.Result[FlextCliSettings]:
                """Create test settings using Railway pattern."""
                try:
                    settings = FlextCliSettings()
                    return r[FlextCliSettings].ok(settings)
                except Exception as e:
                    return r[FlextCliSettings].fail(
                        f"Failed to create test settings: {e}"
                    )

            @staticmethod
            def create_cli_app() -> p.Result[typer.Typer]:
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
            ) -> p.Result[Callable[..., None]]:
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
                    ] = c.LogLevel.INFO,
                    output_format: Annotated[
                        str,
                        FlextCliCommonParams.create_option("output_format"),
                    ] = c.Cli.OutputFormats.TABLE,
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
                ) -> p.Result[bool]:
                    """Register a simple test command that returns a fixed value."""

                    def handler(
                        *args: t.Cli.JsonValue,
                        **kwargs: t.Cli.JsonValue,
                    ) -> p.Result[t.Cli.JsonValue]:
                        return r[t.Cli.JsonValue].ok(result_value)

                    return commands.register_handler(command_name, handler)

                @staticmethod
                def register_command_with_args(
                    commands: FlextCliCommands,
                    command_name: str,
                ) -> p.Result[bool]:
                    """Register a command that accepts arguments."""

                    def handler(
                        *args: t.Cli.JsonValue,
                        **kwargs: t.Cli.JsonValue,
                    ) -> p.Result[t.Cli.JsonValue]:
                        return r[t.Cli.JsonValue].ok(f"args: {len(args)}")

                    return commands.register_handler(command_name, handler)

                @staticmethod
                def register_failing_command(
                    commands: FlextCliCommands,
                    command_name: str,
                    error_message: str = "Test error",
                ) -> p.Result[bool]:
                    """Register a command that fails with a specific error."""

                    def handler(
                        *args: t.Cli.JsonValue,
                        **kwargs: t.Cli.JsonValue,
                    ) -> p.Result[t.Cli.JsonValue]:
                        return r[t.Cli.JsonValue].fail(error_message)

                    return commands.register_handler(command_name, handler)


u = TestsFlextCliUtilities

__all__: list[str] = ["TestsFlextCliUtilities", "u"]
