"""Type system foundation for flext-cli tests.

Provides FlextCliTestTypes, extending FlextTestsTypes with flext-cli-specific types.
All generic test types come from flext_tests, only flext-cli-specific additions here.

Architecture:
- FlextTestsTypes (flext_tests) = Generic types for all FLEXT projects
- FlextCliTestTypes (tests/) = flext-cli-specific types extending FlextTestsTypes

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from flext_tests import FlextTestsTypes

from flext_cli import FlextCliTypes


class FlextCliTestTypes(FlextTestsTypes, FlextCliTypes):
    """Type system foundation for flext-cli tests - extends FlextTestsTypes and FlextCliTypes.

    Architecture: Multiple inheritance provides both generic test types AND CLI-specific types.
    All types from both FlextTestsTypes and FlextCliTypes are available through inheritance.

    Hierarchy:
    - FlextTestsTypes.Tests.* (generic test types from flext_tests)
    - FlextCliTypes.Cli.* (source types from flext_cli - INHERITED)
    - FlextCliTestTypes.Tests.* (flext-cli-specific test types)

    Rules:
    - NEVER redeclare types from FlextTestsTypes or FlextCliTypes
    - Only flext-cli-specific types allowed (not generic for other projects)
    - All generic types come from FlextTestsTypes
    - CLI types come from FlextCliTypes via inheritance
    """

    class Cli(FlextCliTypes.Cli):
        """Flext-cli-specific type definitions for testing.

        Uses composition of FlextCliTypes and FlextTestsTypes for type safety and consistency.
        Only defines types that are truly flext-cli-specific.
        Dict type aliases were removed in Pydantic v2 migration - use models instead.
        """

        class Tests:
            """flext-cli-specific test type definitions namespace.

            Use t.Tests.* for flext-cli-specific test types.
            Use FlextTestsTypes.Tests.* for generic test types.
            """

            ResultFormatter = FlextCliTypes.Cli.ResultFormatter
            FormatableResult = FlextCliTypes.Cli.FormatableResult
            TabularData = FlextCliTypes.Cli.TabularData
            type CliConfigMapping = Mapping[
                str,
                t.NormalizedValue | Sequence[str] | Mapping[str, str | int] | None,
            ]
            "CLI configuration mapping specific to flext-cli."
            type CommandArgsMapping = t.ContainerMapping
            "Command arguments mapping for CLI operations."


t = FlextCliTestTypes

__all__ = ["FlextCliTestTypes", "t"]
