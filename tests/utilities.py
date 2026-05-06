"""Test utilities for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from flext_tests import FlextTestsUtilities

from flext_cli import (
    cli,
    u,
)
from tests import c, p, r, t
from tests.helpers._impl import (
    TestsFlextCliCaptureLogPrompts,
    TestsFlextCliFailingLogPrompts,
    TestsFlextCliScriptedPrompts,
)


class TestsFlextCliUtilities(FlextTestsUtilities, u):
    """Test utilities for flext-cli."""

    class Tests(FlextTestsUtilities.Tests):
        """Test-specific utilities for flext-cli."""

        ScriptedPrompts = TestsFlextCliScriptedPrompts
        CaptureLogPrompts = TestsFlextCliCaptureLogPrompts
        FailingLogPrompts = TestsFlextCliFailingLogPrompts

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
                    if isinstance(version_part, int) != isinstance(info_part, int):
                        return r[tuple[str, tuple[int | str, ...]]].fail(
                            "Type mismatch at position "
                            f"{index}: {version_part.__class__.__name__} != "
                            f"{info_part.__class__.__name__}",
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
            return r[p.Cli.Settings].create_from_callable(cli.new_settings)

        @staticmethod
        def create_cli_app() -> p.Result[t.Cli.CliApp]:
            """Create CLI app using Railway pattern."""
            return r[t.Cli.CliApp].ok(
                cli.create_app_with_common_params(
                    name="tests-cli",
                    help_text="Test CLI app",
                    settings=cli.settings,
                )
            )

        @staticmethod
        def create_decorated_command(
            app: t.Cli.CliApp,
            command_name: str = "test",
        ) -> p.Result[Callable[..., None]]:
            """Create registered command using only the public CLI facade."""

            def command(
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
                cli.print(f"Command: {command_name}")
                if verbose:
                    cli.print("Verbose: enabled")
                if debug:
                    cli.print("Debug: enabled")
                cli.print(f"Log level: {log_level}")
                cli.print(f"Output format: {output_format}")

            cli.register_command(
                app,
                name=command_name,
                help_text=f"Run {command_name}",
                command=command,
            )
            return r[Callable[..., None]].ok(command)


u = TestsFlextCliUtilities

__all__: list[str] = ["TestsFlextCliUtilities", "u"]
