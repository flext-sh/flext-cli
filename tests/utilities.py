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
    FlextCliSettings,
    cli,
    u,
)
from tests import c, p, r, t


class TestsFlextCliUtilities(FlextTestsUtilities, u):
    """Test utilities for flext-cli."""

    class Tests(FlextTestsUtilities.Tests):
        """Test-specific utilities for flext-cli."""

        class VersionTestFactory:
            """Version validation helpers exposed through the canonical `u` namespace."""

            @staticmethod
            def validate_version_string(version: str) -> p.Result[str]:
                """Validate version string against semver pattern."""
                if not version:
                    return r[str].fail(c.Tests.VERSION_EMPTY_MSG)
                pattern = c.PATTERN_SEMVER_RE
                if not pattern.match(version):
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
                        c.Tests.VERSION_INFO_TOO_SHORT_MSG,
                    )
                for index, part in enumerate(version_info):
                    match part:
                        case int() if part < 0:
                            return r[tuple[int | str, ...]].fail(
                                f"Version part {index} must be non-negative int",
                            )
                        case str() if not part:
                            return r[tuple[int | str, ...]].fail(
                                f"Version part {index} must be non-empty string",
                            )
                        case int() | str():
                            pass
                return r[tuple[int | str, ...]].ok(version_info)

            @classmethod
            def validate_consistency(
                cls,
                version_string: str,
                version_info: tuple[int | str, ...],
            ) -> p.Result[tuple[str, tuple[int | str, ...]]]:
                """Validate consistency between version string and version info."""
                string_result = cls.validate_version_string(
                    version_string,
                )
                if string_result.failure:
                    return r[tuple[str, tuple[int | str, ...]]].fail(
                        f"Invalid version string: {string_result.error}",
                    )
                info_result = cls.validate_version_info(
                    version_info,
                )
                if info_result.failure:
                    return r[tuple[str, tuple[int | str, ...]]].fail(
                        f"Invalid version info: {info_result.error}",
                    )
                version_parts = [
                    int(part) if part.isdigit() else part
                    for part in version_string
                    .split("+", maxsplit=1)[0]
                    .replace("-", ".")
                    .split(".")
                ]
                for index, (version_part, info_part) in enumerate(
                    zip(version_parts, version_info, strict=False)
                ):
                    if type(version_part) is not type(info_part):
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
        def create_test_settings() -> p.Result[p.Cli.Settings]:
            """Create test settings using Railway pattern."""
            return r[p.Cli.Settings].create_from_callable(FlextCliSettings)

        @staticmethod
        def create_cli_app() -> p.Result[t.Cli.CliApp]:
            """Create CLI app using Railway pattern."""
            return r[t.Cli.CliApp].create_from_callable(typer.Typer)

        @staticmethod
        def create_decorated_command(
            app: t.Cli.CliApp,
            command_name: str = "test",
        ) -> p.Result[Callable[..., None]]:
            """Create decorated command using Railway pattern."""

            @app.command(name=command_name)
            def typer_command(
                verbose: Annotated[
                    bool,
                    cli.create_option("verbose"),
                ] = False,
                debug: Annotated[
                    bool,
                    cli.create_option("debug"),
                ] = False,
                log_level: Annotated[
                    str,
                    cli.create_option("cli_log_level"),
                ] = c.LogLevel.INFO,
                output_format: Annotated[
                    str,
                    cli.create_option("output_format"),
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

        class CommandsFactory:
            """Factory for creating test commands with high automation."""

            @staticmethod
            def create_commands() -> p.Cli.CommandRegistry:
                """Create an isolated public cli facade for command testing."""
                return cli.create(name=c.Cli.COMMANDS_DEFAULT_NAME)

            @staticmethod
            def register_command(
                commands: p.Cli.CommandRegistry,
                command_name: str,
                *,
                result_value: str = "success",
                error_message: str | None = None,
                reflect_args: bool = False,
            ) -> p.Result[bool]:
                """Register a test command with fixed success, arg reflection, or failure."""

                def handler(
                    *args: t.JsonValue,
                    **kwargs: t.JsonValue,
                ) -> p.Result[t.JsonPayload]:
                    _ = kwargs
                    if error_message is not None:
                        return r[t.JsonPayload].fail(error_message)
                    if reflect_args:
                        return r[t.JsonPayload].ok(f"args: {len(args)}")
                    return r[t.JsonPayload].ok(result_value)

                return commands.register_handler(command_name, handler)


u = TestsFlextCliUtilities

__all__: list[str] = ["TestsFlextCliUtilities", "u"]
