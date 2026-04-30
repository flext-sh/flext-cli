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

import re
from collections.abc import Mapping
from enum import StrEnum
from re import Pattern
from types import MappingProxyType
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
    - c.Tests.* (project-specific test data)

    Rules:
    - NEVER duplicate constants from FlextTestsConstants or c
    - Only flext-cli-specific constants allowed (not generic for other projects)
    - All generic constants come from FlextTestsConstants
    - All production constants come from c
    """

    class Tests(FlextTestsConstants.Tests):
        """Test-specific constant values for flext-cli."""

        SEMVER_RE: Final[Pattern[str]] = re.compile(
            r"^\d+\.\d+\.\d+(?:[-.][\w\.]+)?(?:\+[\w\.]+)?$"
        )

        VERSION_EMPTY_MSG: Final[str] = "Version must be non-empty string"
        VERSION_INFO_TOO_SHORT_MSG: Final[str] = (
            "Version info must have at least 3 parts"
        )

        PROMPT_LONG: Final[str] = (
            "This is a very long message that tests how the system handles extended text input"
        )
        PROMPT_SPECIAL: Final[str] = "!@#$%^&*()"
        PROMPT_UNICODE: Final[str] = "你好世界🌍"
        PROMPT_EDGE_MESSAGES: Final[tuple[str, ...]] = (
            "",
            PROMPT_LONG,
            PROMPT_SPECIAL,
            PROMPT_UNICODE,
        )

        class VersionStringCase(StrEnum):
            """Named version-string fixtures for scenario builders."""

            VALID_SEMVER = "1.2.3"
            VALID_SEMVER_COMPLEX = "1.2.3-alpha.1+build.123"
            INVALID_NO_DOTS = "version"
            INVALID_NON_NUMERIC = "a.b.c"

        VERSION_INFO_VALID_TUPLE: Final[tuple[int, int, int]] = (1, 2, 3)
        VERSION_INFO_VALID_COMPLEX_TUPLE: Final[tuple[int | str, ...]] = (
            1,
            2,
            3,
            "alpha",
            1,
        )
        VERSION_INFO_SHORT_TUPLE: Final[tuple[int, int]] = (1, 2)
        VERSION_INFO_EMPTY_TUPLE: Final[tuple[()]] = ()

        class Environment(StrEnum):
            """Canonical environment names used by CLI settings tests."""

            DEVELOPMENT = "development"
            STAGING = "staging"
            PRODUCTION = "production"
            TEST = "test"

        ENVIRONMENTS: Final[t.StrSequence] = (
            Environment.DEVELOPMENT,
            Environment.STAGING,
            Environment.PRODUCTION,
            Environment.TEST,
        )
        ENVIRONMENT_SET: Final[frozenset[str]] = frozenset(ENVIRONMENTS)

        LOG_LEVEL_SET: Final[frozenset[str]] = frozenset({
            c.LogLevel.DEBUG,
            c.LogLevel.INFO,
            c.LogLevel.WARNING,
            c.LogLevel.ERROR,
            c.LogLevel.CRITICAL,
        })
        LOG_LEVEL_TO_EXPECTED: Final[Mapping[str, str]] = MappingProxyType({
            c.LogLevel.DEBUG: c.LogLevel.DEBUG,
            c.LogLevel.INFO: c.LogLevel.INFO,
            c.LogLevel.WARNING: c.LogLevel.WARNING,
            c.LogLevel.ERROR: c.LogLevel.ERROR,
            c.LogLevel.CRITICAL: c.LogLevel.CRITICAL,
        })
        LOG_LEVEL_SCENARIOS: Final[tuple[tuple[str, str], ...]] = (
            (c.LogLevel.DEBUG, c.LogLevel.DEBUG),
            (c.LogLevel.INFO, c.LogLevel.INFO),
            (c.LogLevel.WARNING, c.LogLevel.WARNING),
            (c.LogLevel.ERROR, c.LogLevel.ERROR),
            (c.LogLevel.CRITICAL, c.LogLevel.CRITICAL),
        )

        CONVERSION_STR_CASES: Final[
            tuple[tuple[t.Cli.TypeKind, t.JsonValue | None, t.JsonValue], ...]
        ] = (
            (c.Cli.TypeKind.STR, "hello", "hello"),
            (c.Cli.TypeKind.STR, None, ""),
            (c.Cli.TypeKind.STR, 42, ""),
        )
        CONVERSION_BOOL_CASES: Final[
            tuple[tuple[t.Cli.TypeKind, t.JsonValue | None, t.JsonValue], ...]
        ] = (
            (c.Cli.TypeKind.BOOL, True, True),
            (c.Cli.TypeKind.BOOL, False, False),
            (c.Cli.TypeKind.BOOL, None, False),
            (c.Cli.TypeKind.BOOL, "x", False),
        )
        CONVERSION_DICT_CASES: Final[
            tuple[tuple[t.Cli.TypeKind, t.JsonValue | None, t.JsonValue], ...]
        ] = (
            (c.Cli.TypeKind.DICT, {"k": "v"}, {"k": "v"}),
            (c.Cli.TypeKind.DICT, None, {}),
            (c.Cli.TypeKind.DICT, "str", {}),
        )

        FILES_DETECT_FORMAT_CASES: Final[tuple[tuple[str, str], ...]] = (
            ("data.json", c.Cli.OutputFormats.JSON),
            ("data.yaml", c.Cli.OutputFormats.YAML),
            ("data.yml", c.Cli.OutputFormats.YAML),
            ("data.csv", c.Cli.OutputFormats.CSV),
            ("data.txt", c.Cli.OutputFormats.TEXT),
            ("data.log", c.Cli.OutputFormats.TEXT),
        )
        FILES_DETECT_FORMAT_FAIL_CASES: Final[tuple[str, ...]] = (
            "data.xml",
            "data.parquet",
            "data",
        )


c = TestsFlextCliConstants

__all__: list[str] = ["TestsFlextCliConstants", "c"]
