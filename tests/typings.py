"""Test type definitions for flext-cli tests.

Extends FlextTestsTypes and FlextCliTypes with test-specific type aliases using inheritance.
Centralizes test type objects without duplicating parent class types.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from flext_tests import FlextTestsTypes

from flext_cli import FlextCliTypes, r

# TypeVars for test-specific types
TTestCommand = TypeVar("TTestCommand")
TTestSession = TypeVar("TTestSession")
TTestResult = TypeVar("TTestResult")


class TestsCliTypes(FlextTestsTypes, FlextCliTypes):
    """Test type definitions extending FlextTestsTypes and FlextCliTypes.

    Business Rules:
    ───────────────
    1. Extends FlextTestsTypes and FlextCliTypes via inheritance (not aliases)
    2. Only contains test-specific types not in src
    3. Reuses parent types through inheritance hierarchy
    4. Uses PEP 695 type aliases for Python 3.13+ syntax
    """

    # Test-specific type aliases
    type TestDataDict = FlextCliTypes.JsonDict
    type TestResultDict = FlextCliTypes.JsonDict
    type TestFixtureData = FlextCliTypes.JsonDict

    class Test:
        """Test-related type aliases."""

        type Handler[T] = Callable[[FlextCliTypes.GeneralValueType], r[T]]
        type Validator = Callable[[FlextCliTypes.GeneralValueType], bool]
        type Fixture = Callable[[], FlextCliTypes.GeneralValueType]

    class Assertion:
        """Assertion-related type aliases."""

        type AssertionFunction = Callable[[object, object], None]
        type ComparisonFunction = Callable[[object, object], bool]

    class TestFactory:
        """Factory-related type aliases for tests."""

        type ModelFactory[T] = Callable[[FlextCliTypes.JsonDict], r[T]]
        type CommandFactory = Callable[[str], r[FlextCliTypes.GeneralValueType]]


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
