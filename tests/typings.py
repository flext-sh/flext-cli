"""Type system foundation for flext-cli tests.

Provides TestsCliTypes, extending FlextTestsTypes with flext-cli-specific types.
All generic test types come from flext_tests, only flext-cli-specific additions here.

Architecture:
- FlextTestsTypes (flext_tests) = Generic types for all FLEXT projects
- TestsCliTypes (tests/) = flext-cli-specific types extending FlextTestsTypes

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TypedDict

from flext_cli.typings import FlextCliTypes, t as cli_t
from flext_core.typings import T, T_co, T_contra, t as core_t
from flext_tests.typings import FlextTestsTypes


class TestsCliTypes(FlextTestsTypes, FlextCliTypes):
    """Type system foundation for flext-cli tests - extends FlextTestsTypes and FlextCliTypes.

    Architecture: Multiple inheritance provides both generic test types AND CLI-specific types.
    All types from both FlextTestsTypes and FlextCliTypes are available through inheritance.

    Hierarchy:
    - FlextTestsTypes.Tests.* (generic test types from flext_tests)
    - FlextCliTypes.Cli.* (source types from flext_cli - INHERITED)
    - TestsCliTypes.Tests.* (flext-cli-specific test types)

    Rules:
    - NEVER redeclare types from FlextTestsTypes or FlextCliTypes
    - Only flext-cli-specific types allowed (not generic for other projects)
    - All generic types come from FlextTestsTypes
    - CLI types come from FlextCliTypes via inheritance
    """

    class Tests(FlextTestsTypes.Tests):
        """flext-cli-specific test type definitions namespace.

        Use tt.Tests.* for flext-cli-specific test types.
        Use t.Tests.* for generic test types from FlextTestsTypes.
        """

        class Cli:
            """Flext-cli-specific type definitions for testing.

            Uses composition of cli_t and t for type safety and consistency.
            Only defines types that are truly flext-cli-specific.
            Dict type aliases were removed in Pydantic v2 migration - use models instead.
            """

            # Import remaining types from FlextCliTypes.Cli for test access
            ResultFormatter = cli_t.Cli.ResultFormatter
            FormatableResult = cli_t.Cli.FormatableResult
            TabularData = cli_t.Cli.TabularData

            type CliConfigMapping = Mapping[
                str,
                core_t.JsonValue | Sequence[str] | Mapping[str, str | int] | None,
            ]
            """CLI configuration mapping specific to flext-cli."""

            type CommandArgsMapping = Mapping[str, cli_t.GeneralValueType]
            """Command arguments mapping for CLI operations."""

        class Fixtures:
            """TypedDict definitions for test fixtures."""

            class CliCommandDict(TypedDict, total=False):
                """CLI command test data."""

                name: str
                args: list[str]
                format: str
                status: str

            class CliOutputDict(TypedDict, total=False):
                """CLI output test data."""

                format: str
                data: dict[str, str | int | bool]
                success: bool


# Short aliases
t = TestsCliTypes
tt = TestsCliTypes

__all__ = [
    "T",
    "TTestModel",
    "TTestResult",
    "TTestService",
    "T_co",
    "T_contra",
    "TestsCliTypes",
    "t",
    "tt",
]
