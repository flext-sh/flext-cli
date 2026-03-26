"""Constants for flext-cli tests.

Provides FlextCliTestConstants, extending FlextTestsConstants with flext-cli-specific
constants using COMPOSITION INHERITANCE.

Inheritance hierarchy:
- FlextTestsConstants (flext_tests) - Provides .Tests.* namespace
- FlextCliConstants (production) - Provides .Cli.* namespace

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final

from flext_tests import FlextTestsConstants

from flext_cli import FlextCliConstants
from tests import t


class FlextCliTestConstants(FlextTestsConstants, FlextCliConstants):
    """Constants for flext-cli tests using COMPOSITION INHERITANCE.

    MANDATORY: Inherits from BOTH:
    1. FlextTestsConstants - for test infrastructure (.Tests.*)
    2. FlextCliConstants - for domain constants (.Cli.*)

    Access patterns:
    - c.Tests.Docker.* (container testing)
    - c.Tests.Matcher.* (assertion messages)
    - c.Tests.Factory.* (test data generation)
    - c.Cli.* (domain constants from production)
    - c.Cli.Test.TestData.* (project-specific test data)

    Rules:
    - NEVER duplicate constants from FlextTestsConstants or FlextCliConstants
    - Only flext-cli-specific constants allowed (not generic for other projects)
    - All generic constants come from FlextTestsConstants
    - All production constants come from FlextCliConstants
    """

    class Cli(FlextCliConstants.Cli):
        """CLI constants with test-specific extensions."""

        class Test:
            """Test-specific constant values."""

            TWO: Final[t.StrSequence] = ["item1", "item2"]

            class PasswordDefaults:
                """Password validation constants."""

                MIN_LENGTH_STRICT: Final[int] = 8

            class TestData:
                """Test data constants for test modules."""

                TWO: Final[int] = 2
                PASSWORD: Final[str] = "test_password_123"
                LONG: Final[str] = (
                    "This is a very long message that tests how the system handles extended text input"
                )
                SPECIAL: Final[str] = "!@#$%^&*()"
                UNICODE: Final[str] = "你好世界🌍"


c = FlextCliTestConstants

__all__ = ["FlextCliTestConstants", "c"]
