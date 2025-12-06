"""Test type definitions for flext-cli tests.

Extends FlextTestsTypes and FlextCliTypes with test-specific type aliases using inheritance.
Centralizes test type objects without duplicating parent class types.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from flext_tests import t as flext_tests_t

from flext_cli import r, t as flext_cli_t

# TypeVars for test-specific types
TTestCommand = TypeVar("TTestCommand")
TTestSession = TypeVar("TTestSession")
TTestResult = TypeVar("TTestResult")


class TestsCliTypes(flext_tests_t, flext_cli_t):
    """Test type definitions extending FlextTestsTypes and FlextCliTypes.

    Business Rules:
    ───────────────
    1. Extends FlextTestsTypes and FlextCliTypes via inheritance (not aliases)
    2. Only contains test-specific types not in src
    3. Reuses parent types through inheritance hierarchy
    4. Uses PEP 695 type aliases for Python 3.13+ syntax
    """

    # Expose GeneralValueType from parent hierarchy for direct access
    type GeneralValueType = flext_cli_t.GeneralValueType

    # Test-specific type aliases
    type TestDataDict = flext_cli_t.Json.JsonDict
    type TestResultDict = flext_cli_t.Json.JsonDict
    type TestFixtureData = flext_cli_t.Json.JsonDict

    class Test:
        """Test-related type aliases."""

        type Handler[T] = Callable[[flext_cli_t.GeneralValueType], r[T]]
        type Validator = Callable[[flext_cli_t.GeneralValueType], bool]
        type Fixture = Callable[[], flext_cli_t.GeneralValueType]

    class Assertion:
        """Assertion-related type aliases."""

        type AssertionFunction = Callable[[object, object], None]
        type ComparisonFunction = Callable[[object, object], bool]

    class TestFactory:
        """Factory-related type aliases for tests."""

        type ModelFactory[T] = Callable[[flext_cli_t.Json.JsonDict], r[T]]
        type CommandFactory = Callable[[str], r[flext_cli_t.GeneralValueType]]


# Standardized short name - matches src pattern (t = FlextCliTypes)
# TestsCliTypes extends FlextTestsTypes and FlextCliTypes, so use same short name 't'
# Type annotation needed for mypy compatibility
t: type[TestsCliTypes] = TestsCliTypes

__all__ = [
    "TTestCommand",
    "TTestResult",
    "TTestSession",
    "TestsCliTypes",
    "t",
]
