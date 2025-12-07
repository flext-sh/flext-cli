"""Test protocol definitions for flext-cli tests.

Extends FlextTestsProtocols and FlextCliProtocols with test-specific protocols using inheritance.
Centralizes test protocol objects without duplicating parent class protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, Self, runtime_checkable

from flext_tests import p as flext_tests_p

from flext_cli import p as flext_cli_p
from flext_cli.typings import t as flext_cli_t


class TestsCliProtocols(flext_tests_p, flext_cli_p):
    """Test protocol definitions extending FlextTestsProtocols and FlextCliProtocols.

    Business Rules:
    ───────────────
    1. Extends FlextTestsProtocols and FlextCliProtocols via inheritance (not aliases)
    2. Only contains test-specific protocols not in src
    3. Reuses parent protocols through inheritance hierarchy
    4. Uses @runtime_checkable for isinstance() checks
    5. Uses Self for methods returning the same instance
    """

    class Test:
        """Test-specific protocols."""

        @runtime_checkable
        class TestFixtureProtocol(Protocol):
            """Protocol for test fixtures."""

            def setup(self) -> flext_cli_p.Result[bool]:
                """Setup test fixture."""
                ...

            def teardown(self) -> flext_cli_p.Result[bool]:
                """Teardown test fixture."""
                ...

            def reset(self) -> Self:
                """Reset fixture state."""
                ...

        @runtime_checkable
        class TestValidatorProtocol(Protocol):
            """Protocol for test validators."""

            def validate(
                self, data: flext_cli_t.GeneralValueType
            ) -> flext_cli_p.Result[bool]:
                """Validate test data."""
                ...

            def validate_all(
                self,
                data: Sequence[flext_cli_t.GeneralValueType],
            ) -> flext_cli_p.Result[bool]:
                """Validate all test data."""
                ...

        @runtime_checkable
        class TestFactoryProtocol(Protocol):
            """Protocol for test factories."""

            def create(
                self, **kwargs: flext_cli_t.GeneralValueType
            ) -> flext_cli_p.Result[object]:
                """Create test object."""
                ...

            def create_batch(
                self,
                count: int,
                **kwargs: flext_cli_t.GeneralValueType,
            ) -> flext_cli_p.Result[Sequence[object]]:
                """Create batch of test objects."""
                ...


# Standardized short name - matches src pattern (p = FlextCliProtocols)
# TestsCliProtocols extends FlextTestsProtocols and FlextCliProtocols, so use same short name 'p'
# Type annotation needed for mypy compatibility
p: type[TestsCliProtocols] = TestsCliProtocols

__all__ = [
    "TestsCliProtocols",
    "p",
]
