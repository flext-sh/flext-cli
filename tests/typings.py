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

from enum import StrEnum, unique

from flext_tests import FlextTestsTypes

from flext_cli import t


class FlextCliTestTypes(FlextTestsTypes, t):
    """Type system foundation for flext-cli tests - extends FlextTestsTypes and t.

    Architecture: Multiple inheritance provides both generic test types AND CLI-specific types.
    All types from both FlextTestsTypes and t are available through inheritance.

    Hierarchy:
    - FlextTestsTypes.Tests.* (generic test types from flext_tests)
    - t.Cli.* (source types from flext_cli - INHERITED)

    Rules:
    - NEVER redeclare types from FlextTestsTypes or t
    - Only flext-cli-specific types allowed (not generic for other projects)
    - All generic types come from FlextTestsTypes
    - CLI types come from t via inheritance
    """

    class Cli(t.Cli):
        """Flext-cli-specific type definitions for testing."""

        class Tests:
            """Test-specific type definitions for flext-cli."""

            @unique
            class ValidationType(StrEnum):
                """Types of version validation."""

                STRING = "string_validation"
                INFO = "info_validation"
                CONSISTENCY = "consistency"

            @unique
            class ConfigTestType(StrEnum):
                """Config test types."""

                INITIALIZATION = "initialization"
                SERIALIZATION = "serialization"
                VALIDATION = "validation"
                INTEGRATION = "integration"
                EDGE_CASES = "edge_cases"

            @unique
            class ConfigParam(StrEnum):
                """Test configuration parameters for parametrized tests."""

                VERBOSE = "verbose"
                QUIET = "quiet"
                DEBUG = "debug"
                NO_COLOR = "no_color"
                LOG_LEVEL = "log_level"
                LOG_FORMAT = "log_format"
                OUTPUT_FORMAT = "output_format"


t = FlextCliTestTypes

__all__ = ["FlextCliTestTypes", "t"]
