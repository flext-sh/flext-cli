"""Pytest configuration and fixtures for unit tests."""

from __future__ import annotations  # @vulture_ignore

from collections.abc import Generator  # @vulture_ignore - used in fixture return type

import pytest  # @vulture_ignore - pytest is used by pytest decorators
from flext_cli import FlextCliSettings  # @vulture_ignore - used in fixture
from flext_core import FlextSettings  # @vulture_ignore - used in fixture


@pytest.fixture(autouse=True)  # @vulture_ignore - pytest fixture
def reset_config_singleton(request: pytest.FixtureRequest) -> Generator[None]:
    """Reset FlextCliSettings singleton before and after each test.

    This ensures test isolation and prevents one test from contaminating
    the state for other tests.
    """
    # Clean up BEFORE test - use public reset methods
    # Business Rule: Use public reset methods for singleton cleanup
    # These methods are designed for test isolation and are safe to use
    FlextCliSettings._reset_instance()
    FlextSettings.reset_global_instance()
    # Note: FlextCliServiceBase._config_instance is reset via FlextCliSettings reset

    yield

    # Clean up AFTER test - use public reset methods
    # Business Rule: Use public reset methods for singleton cleanup
    # These methods are designed for test isolation and are safe to use
    FlextCliSettings._reset_instance()
    FlextSettings.reset_global_instance()
    # Note: FlextCliServiceBase._config_instance is reset via FlextCliSettings reset
