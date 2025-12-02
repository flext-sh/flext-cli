"""Pytest configuration and fixtures for unit tests."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from flext_core import FlextConfig

from flext_cli import FlextCliConfig, FlextCliServiceBase


@pytest.fixture(autouse=True)
def reset_config_singleton(request: pytest.FixtureRequest) -> Generator[None]:
    """Reset FlextCliConfig singleton before and after each test.

    This ensures test isolation and prevents one test from contaminating
    the state for other tests.
    """
    # Clean up BEFORE test
    if hasattr(FlextCliConfig, "_instance"):
        FlextCliConfig._instance = None  # type: ignore[attr-defined]
    if hasattr(FlextCliConfig, "_instances"):
        FlextCliConfig._instances.clear()  # type: ignore[attr-defined]
    if hasattr(FlextCliServiceBase, "_config_instance"):
        FlextCliServiceBase._config_instance = None  # type: ignore[attr-defined]

    # Also reset the global instance from FlextConfig
    if hasattr(FlextConfig, "_instance"):
        FlextConfig._instance = None  # type: ignore[attr-defined]
    if hasattr(FlextConfig, "_instances"):
        FlextConfig._instances.clear()  # type: ignore[attr-defined]

    yield

    # Clean up AFTER test
    if hasattr(FlextCliConfig, "_instance"):
        FlextCliConfig._instance = None  # type: ignore[attr-defined]
    if hasattr(FlextCliConfig, "_instances"):
        FlextCliConfig._instances.clear()  # type: ignore[attr-defined]
    if hasattr(FlextCliServiceBase, "_config_instance"):
        FlextCliServiceBase._config_instance = None  # type: ignore[attr-defined]

    # Also reset the global instance from FlextConfig
    if hasattr(FlextConfig, "_instance"):
        FlextConfig._instance = None  # type: ignore[attr-defined]
    if hasattr(FlextConfig, "_instances"):
        FlextConfig._instances.clear()  # type: ignore[attr-defined]
