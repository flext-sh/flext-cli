"""Constants for flext-cli tests.

Provides TestsFlextCliConstants, extending FlextTestsConstants with flext-cli-specific
constants using COMPOSITION INHERITANCE.

Inheritance hierarchy:
- FlextTestsConstants (flext_tests) - Provides .Tests.* namespace
- c (production) - Provides .Cli.* namespace

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Sequence,
)
from typing import Final

from flext_tests import FlextTestsConstants

from flext_cli import c
from tests import t


class TestsFlextCliConstants(FlextTestsConstants, c):
    """Constants for flext-cli tests using COMPOSITION INHERITANCE.

    MANDATORY: Inherits from BOTH:
    1. FlextTestsConstants - for test infrastructure (.Tests.*)
    2. c - for domain constants (.Cli.*)

    Access patterns:
    - c.Tests.* (generic test infrastructure)
    - c.Cli.* (domain constants from production)
    - c.Cli.Tests.* (project-specific test data)

    Rules:
    - NEVER duplicate constants from FlextTestsConstants or c
    - Only flext-cli-specific constants allowed (not generic for other projects)
    - All generic constants come from FlextTestsConstants
    - All production constants come from c
    """

    class Cli(c.Cli):
        """CLI constants with test-specific extensions."""

        class Tests(FlextTestsConstants.Tests):
            """Test-specific constant values for flext-cli."""

            LONG: Final[str] = (
                "This is a very long message that tests how the system handles extended text input"
            )
            SPECIAL: Final[str] = "!@#$%^&*()"
            UNICODE: Final[str] = "你好世界🌍"
            SEMVER_PATTERN: Final[str] = (
                "^\\d+\\.\\d+\\.\\d+(?:[-.][\\w\\.]+)?(?:\\+[\\w\\.]+)?$"
            )
            VALID_SEMVER: Final[str] = "1.2.3"
            VALID_SEMVER_COMPLEX: Final[str] = "1.2.3-alpha.1+build.123"
            INVALID_NO_DOTS: Final[str] = "version"
            INVALID_NON_NUMERIC: Final[str] = "a.b.c"
            EMPTY_STRING: Final[str] = "Version must be non-empty string"
            INFO_TOO_SHORT: Final[str] = "Version info must have at least 3 parts"
            VALID_TUPLE: Final[tuple[int, int, int]] = (1, 2, 3)
            VALID_COMPLEX_TUPLE: Final[tuple[int | str, ...]] = (
                1,
                2,
                3,
                "alpha",
                1,
            )
            SHORT_TUPLE: Final[tuple[int, int]] = (1, 2)
            EMPTY_TUPLE: Final[tuple[()]] = ()
            VALID_ENVIRONMENTS: Final[t.StrSequence] = (
                "development",
                "staging",
                "production",
                "test",
            )
            VALID_LOGGING_LEVELS: Final[t.StrSequence] = (
                c.LogLevel.DEBUG,
                c.LogLevel.INFO,
                c.LogLevel.WARNING,
                c.LogLevel.ERROR,
                c.LogLevel.CRITICAL,
            )

            @classmethod
            def logging_scenarios(cls) -> Sequence[tuple[str, str]]:
                """Generate logging level scenarios."""
                return [(level, level) for level in cls.VALID_LOGGING_LEVELS]


c = TestsFlextCliConstants

__all__: list[str] = ["TestsFlextCliConstants", "c"]
