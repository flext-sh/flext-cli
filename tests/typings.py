"""Type system foundation for flext-cli tests.

Provides TestsFlextCliTypes, extending TestsFlextTypes with flext-cli-specific types.
All generic test types come from flext_tests, only flext-cli-specific additions here.

Architecture:
- TestsFlextTypes (flext_tests) = Generic types for all FLEXT projects
- TestsFlextCliTypes (tests/) = flext-cli-specific types extending TestsFlextTypes

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum, unique

from flext_tests import FlextTestsTypes

from flext_cli import t


class TestsFlextCliTypes(FlextTestsTypes, t):
    """Type system foundation for flext-cli tests - extends TestsFlextTypes and t.

    Architecture: Multiple inheritance provides both generic test types AND CLI-specific types.
    All types from both TestsFlextTypes and t are available through inheritance.

    Hierarchy:
    - TestsFlextTypes.Tests.* (generic test types from flext_tests)
    - t.Cli.* (source types from flext_cli - INHERITED)

    Rules:
    - NEVER redeclare types from TestsFlextTypes or t
    - Only flext-cli-specific types allowed (not generic for other projects)
    - All generic types come from TestsFlextTypes
    - CLI types come from t via inheritance
    """

    class Tests(FlextTestsTypes.Tests):
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


t = TestsFlextCliTypes

__all__: list[str] = ["TestsFlextCliTypes", "t"]
