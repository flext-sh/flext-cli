"""Test utilities for flext-cli.

Composes ``FlextTestsUtilities + u`` via MRO. Hosts only flext-cli-specific
helpers; everything generic comes from the parent namespaces.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from flext_tests import FlextTestsUtilities, r

from flext_cli import cli, u
from tests import c
from tests import p
from tests.settings import TestsFlextCliSettings
from tests import t


class TestsFlextCliUtilities(FlextTestsUtilities, u):
    """Test utilities for flext-cli."""

    class Tests(FlextTestsUtilities.Tests):
        """flext-cli-specific test utilities."""

        class VersionTestFactory:
            """Version validation helpers exposed through ``u``."""

            @staticmethod
            def validate_version_string(version: str) -> p.Result[str]:
                if not version:
                    return r[str].fail(c.Tests.VERSION_EMPTY_MSG)
                if not c.PATTERN_SEMVER_RE.match(version):
                    return r[str].fail(
                        f"Version '{version}' does not match semver pattern"
                    )
                return r[str].ok(version)

            @staticmethod
            def validate_version_info(
                version_info: tuple[int | str, ...],
            ) -> p.Result[tuple[int | str, ...]]:
                if len(version_info) < 3:
                    return r[tuple[int | str, ...]].fail(
                        c.Tests.VERSION_INFO_TOO_SHORT_MSG
                    )
                for index, part in enumerate(version_info):
                    if isinstance(part, bool):
                        return r[tuple[int | str, ...]].fail(
                            f"Version part {index} must not be bool"
                        )
                    if isinstance(part, int) and part < 0:
                        return r[tuple[int | str, ...]].fail(
                            f"Version part {index} must be non-negative int"
                        )
                    if isinstance(part, str) and not part:
                        return r[tuple[int | str, ...]].fail(
                            f"Version part {index} must be non-empty string"
                        )
                return r[tuple[int | str, ...]].ok(version_info)

            @classmethod
            def validate_consistency(
                cls, version_string: str, version_info: tuple[int | str, ...]
            ) -> p.Result[tuple[str, tuple[int | str, ...]]]:
                pair_t = tuple[str, tuple[int | str, ...]]
                string_check = cls.validate_version_string(version_string)
                if string_check.failure:
                    return r[pair_t].fail(
                        f"Invalid version string: {string_check.error}"
                    )
                info_check = cls.validate_version_info(version_info)
                if info_check.failure:
                    return r[pair_t].fail(f"Invalid version info: {info_check.error}")
                version_parts = [
                    int(part) if part.isdigit() else part
                    for part in version_string
                    .split("+", maxsplit=1)[0]
                    .replace("-", ".")
                    .split(".")
                ]
                for index, (vs_part, vi_part) in enumerate(
                    zip(version_parts, version_info, strict=False)
                ):
                    if isinstance(vs_part, int) != isinstance(vi_part, int):
                        return r[pair_t].fail(
                            f"Type mismatch at position {index}: "
                            f"{vs_part.__class__.__name__} != {vi_part.__class__.__name__}"
                        )
                    if vs_part != vi_part:
                        return r[pair_t].fail(
                            f"Mismatch at position {index}: {vs_part} != {vi_part}"
                        )
                return r[pair_t].ok((version_string, version_info))

        @staticmethod
        def create_test_settings() -> p.Result[p.Cli.Settings]:
            """Create test settings via Railway pattern."""
            return r[p.Cli.Settings].ok(TestsFlextCliSettings())

        @staticmethod
        def create_cli_app() -> p.Result[t.Cli.CliApp]:
            """Create CLI app via Railway pattern."""
            # NOTE (multi-agent, mro-wkii.19.4): the CLI owns global settings.
            return r[t.Cli.CliApp].ok(
                cli.create_app_with_common_params(
                    name="tests-cli", help_text="Test CLI app"
                )
            )

        @staticmethod
        def create_decorated_command(
            app: t.Cli.CliApp, command_name: str = "test"
        ) -> p.Result[Callable[..., None]]:
            """Register a real flag-driven command on ``app`` for tests."""

            def command(
                verbose: Annotated[bool, cli.create_option("verbose")] = False,
                debug: Annotated[bool, cli.create_option("debug")] = False,
                log_level: Annotated[
                    str, cli.create_option("cli_log_level")
                ] = c.LogLevel.INFO,
                output_format: Annotated[
                    str, cli.create_option("output_format")
                ] = c.Cli.OutputFormats.TABLE,
            ) -> None:
                cli.print(f"Command: {command_name}")
                if verbose:
                    cli.print("Verbose: enabled")
                if debug:
                    cli.print("Debug: enabled")
                cli.print(f"Log level: {log_level}")
                cli.print(f"Output format: {output_format}")

            cli.register_command(
                app, name=command_name, help_text=f"Run {command_name}", command=command
            )
            return r[Callable[..., None]].ok(command)


u = TestsFlextCliUtilities

__all__: list[str] = ["TestsFlextCliUtilities", "u"]
