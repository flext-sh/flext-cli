"""Pytest configuration and fixtures for unit tests."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from flext_core import FlextSettings

from flext_cli import FlextCliSettings


@pytest.fixture(autouse=True)
def reset_config_singleton(request: pytest.FixtureRequest) -> Generator[None]:
    """Reset FlextCliSettings singleton before and after each test.

    This ensures test isolation and prevents one test from contaminating
    the state for other tests.
    """
    FlextCliSettings._reset_instance()
    FlextSettings.reset_for_testing()
    yield
    FlextCliSettings._reset_instance()
    FlextSettings.reset_for_testing()
