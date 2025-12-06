"""Test models for flext-cli tests.

Extends FlextTestsModels and FlextCliModels with test-specific models using inheritance.
Centralizes test model objects without duplicating parent class models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self

from flext_tests import m as flext_tests_m
from pydantic import ConfigDict, Field

from flext_cli import m as flext_cli_m
from flext_cli.typings import t as flext_cli_t


class TestsCliModels(flext_cli_m):
    """Test models extending FlextCliModels with FlextTestsModels via composition.

    Business Rules:
    ───────────────
    1. Extends FlextCliModels via inheritance (primary hierarchy)
    2. Uses FlextTestsModels via composition to avoid MRO conflicts with Entity/Value
    3. Only contains test-specific models not in src
    4. Reuses parent models through inheritance hierarchy
    5. All methods returning self use Self for namespace compatibility
    6. Uses Python 3.13+ syntax and patterns
    7. Uses composition and override to reduce duplication
    """

    # Expose FlextTestsModels via composition to avoid MRO conflicts
    # Both FlextTestsModels and FlextCliModels define Entity/Value, causing mypy errors
    # Solution: inherit from flext_cli_m (primary) and expose flext_tests_m via composition
    _tests_models = flext_tests_m

    class _TestModelBase(flext_cli_m.Entity):
        """Base class for test models with shared functionality.

        Extends Entity via inheritance to expose full hierarchy through TestsCliModels.
        """

        model_config = ConfigDict(frozen=True, extra="forbid")

        def _copy_with_update(self, **updates: object) -> Self:
            """Helper method for model_copy with updates - reduces repetition."""
            return self.model_copy(update=updates)

        def model_post_init(self, __context: object, /) -> None:
            """Override to prevent frozen instance errors from TimestampableMixin."""
            # Do nothing - timestamp fields are handled by Core

    class TestCommand(_TestModelBase):
        """Test-specific command model for testing."""

        test_id: str = Field(..., description="Test identifier")
        test_data: flext_cli_t.Json.JsonDict = Field(
            default_factory=dict,
            description="Test-specific data",
        )

        def with_test_data(self, data: flext_cli_t.Json.JsonDict) -> Self:
            """Return copy with new test data."""
            return self._copy_with_update(test_data=data)

    class TestSession(_TestModelBase):
        """Test-specific session model for testing."""

        test_session_id: str = Field(..., description="Test session identifier")
        test_metadata: flext_cli_t.Json.JsonDict = Field(
            default_factory=dict,
            description="Test metadata",
        )

        def with_metadata(self, metadata: flext_cli_t.Json.JsonDict) -> Self:
            """Return copy with new metadata."""
            return self._copy_with_update(test_metadata=metadata)


# Standardized short name - matches src pattern (m = FlextCliModels)
# TestsCliModels extends FlextTestsModels and FlextCliModels, so use same short name 'm'
# Type annotation needed for mypy compatibility
m: type[TestsCliModels] = TestsCliModels

__all__ = [
    "TestsCliModels",
    "m",
]
