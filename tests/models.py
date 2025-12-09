"""Test models for flext-cli tests.

Provides TestsCliModels using composition with FlextTestsModels and FlextCliModels.
All generic test models come from flext_tests.

Architecture:
- FlextTestsModels (flext_tests) = Generic models for all FLEXT projects
- FlextCliModels (flext_cli) = CLI domain models
- TestsCliModels (tests/) = flext-cli-specific models using composition

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self

from flext_tests import m as flext_tests_m
from pydantic import ConfigDict, Field

from flext_cli import m as flext_cli_m
from flext_cli.typings import t as flext_cli_t


class TestsCliModels:
    """Models for flext-cli tests - uses composition with FlextCliModels.

    Architecture: Uses composition (not inheritance) with FlextTestsModels and FlextCliModels
    for flext-cli-specific model definitions.

    Access patterns:
    - TestsCliModels.Tests.* = flext_tests test models (via composition)
    - TestsCliModels.Cli.* = flext_cli domain models (via composition)
    - TestsCliModels.CliTests.* = flext-cli-specific test models

    Rules:
    - Use composition, not inheritance (FlextCliModels deprecates subclassing)
    - flext-cli-specific test models go in CliTests namespace
    - Generic models accessed via Tests namespace
    - CLI models accessed via Cli namespace
    """

    # Composition: expose FlextTestsModels namespaces
    Tests = flext_tests_m.Tests

    # Composition: expose FlextCliModels namespaces
    Cli = flext_cli_m.Cli
    Entity = flext_cli_m.Entity
    Value = flext_cli_m.Value

    class CliTests:
        """flext-cli-specific test models namespace."""

        class _TestModelBase(flext_cli_m.Entity):
            """Base class for test models with shared functionality.

            Extends Entity via FlextCliModels.Entity for CLI test models.
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

    # Backward compatibility: expose CliTests classes at root level
    TestCommand = CliTests.TestCommand
    TestSession = CliTests.TestSession


# Standardized short name - matches src pattern (m = FlextCliModels)
# TestsCliModels uses composition with FlextTestsModels and FlextCliModels
# Type annotation needed for mypy compatibility
m: type[TestsCliModels] = TestsCliModels

__all__ = [
    "TestsCliModels",
    "m",
]
