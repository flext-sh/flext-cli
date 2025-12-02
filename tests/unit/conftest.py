"""Pytest configuration and fixtures for unit tests."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from flext_core import FlextConfig

from flext_cli import FlextCliConfig


@pytest.fixture(autouse=True)
def reset_config_singleton(request: pytest.FixtureRequest) -> Generator[None]:
    """Reset FlextCliConfig singleton before and after each test.

    This ensures test isolation and prevents one test from contaminating
    the state for other tests.
    """
    # Clean up BEFORE test - use public reset methods
    # Business Rule: Use public reset methods for singleton cleanup
    # These methods are designed for test isolation and are safe to use
    FlextCliConfig._reset_instance()
    FlextConfig.reset_global_instance()
    # Note: FlextCliServiceBase._config_instance is reset via FlextCliConfig reset

    yield

    # Clean up AFTER test - use public reset methods
    # Business Rule: Use public reset methods for singleton cleanup
    # These methods are designed for test isolation and are safe to use
    FlextCliConfig._reset_instance()
    FlextConfig.reset_global_instance()
    # Note: FlextCliServiceBase._config_instance is reset via FlextCliConfig reset
