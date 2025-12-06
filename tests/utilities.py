"""Test utilities for flext-cli tests.

Extends FlextTestsUtilities and FlextCliUtilities with test-specific utilities using inheritance.
Centralizes test utility objects without duplicating parent class utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from flext_tests import u as flext_tests_u

from flext_cli import r, u as flext_cli_u
from flext_cli.typings import t as flext_cli_t


class TestsCliUtilities(flext_tests_u, flext_cli_u):
    """Test utilities extending FlextTestsUtilities and FlextCliUtilities.

    Business Rules:
    ───────────────
    1. Extends FlextTestsUtilities and FlextCliUtilities via inheritance (not aliases)
    2. Only contains test-specific utilities not in src
    3. Reuses parent utilities through inheritance hierarchy
    4. All methods returning self use Self for namespace compatibility
    5. Uses Python 3.13+ syntax and patterns
    """

    class TestValidation:
        """Test-specific validation operations."""

        @staticmethod
        def validate_test_data(data: flext_cli_t.Json.JsonDict | None) -> r[bool]:
            """Validate test data structure."""
            if data is None:
                return r[bool].fail("Test data cannot be None")
            if not isinstance(data, dict):
                return r[bool].fail("Test data must be a dictionary")
            return r[bool].ok(True)

        @staticmethod
        def validate_fixture(fixture: object) -> r[bool]:
            """Validate test fixture."""
            if fixture is None:
                return r[bool].fail("Fixture cannot be None")
            if not callable(fixture):
                return r[bool].fail("Fixture must be callable")
            return r[bool].ok(True)

    class TestFactory:
        """Test-specific factory operations."""

        @staticmethod
        def create_test_model(
            model_class: type,
            data: Mapping[str, flext_cli_t.GeneralValueType],
        ) -> r[object]:
            """Create test model instance."""
            try:
                if not hasattr(model_class, "model_validate"):
                    return r[object].fail(f"{model_class} is not a Pydantic model")
                instance = model_class.model_validate(dict(data))
                return r[object].ok(instance)
            except Exception as e:
                return r[object].fail(f"Failed to create model: {e}")

        @staticmethod
        def create_test_command(
            name: str,
            handler: Callable[..., flext_cli_t.GeneralValueType],
        ) -> r[dict[str, object]]:
            """Create test command data."""
            try:
                command_data: dict[str, object] = {
                    "name": name,
                    "handler": handler,
                    "test": True,
                }
                return r[dict[str, object]].ok(command_data)
            except Exception as e:
                return r[dict[str, object]].fail(f"Failed to create command: {e}")


# Standardized short name - matches src pattern (u = FlextCliUtilities)
# TestsCliUtilities extends FlextTestsUtilities and FlextCliUtilities, so use same short name 'u'
# Type annotation needed for mypy compatibility
u: type[TestsCliUtilities] = TestsCliUtilities

__all__ = [
    "TestsCliUtilities",
    "u",
]
