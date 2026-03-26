"""FLEXT CLI Test Configuration - Comprehensive Test Infrastructure.

Centralized test configuration using flext_tests library with real functionality
testing, Docker support, and comprehensive fixtures following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest
from click.testing import CliRunner


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest markers for the test suite."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line("markers", "docker: marks tests that require Docker")
    config.addinivalue_line(
        "markers",
        "real_functionality: marks tests that test real functionality",
    )


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create Click CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide temporary directory for tests.

    Wraps pytest's tmp_path fixture to maintain naming consistency.
    """
    return tmp_path


@pytest.fixture(autouse=True)
def reset_singletons() -> None:
    """Reset all FlextSettings singletons between tests for isolation.

    CRITICAL: This fixture runs automatically before EACH test to ensure
    no state leaks between tests regardless of pytest-randomly order.
    """
    return


class Examples:
    """Version string examples for parametrized tests."""

    VALID_SEMVER: str = "1.2.3"
    VALID_SEMVER_COMPLEX: str = "1.2.3-alpha.1+build.123"
    INVALID_NO_DOTS: str = "version"
    INVALID_NON_NUMERIC: str = "a.b.c"


class InfoTuples:
    """Version info tuple examples for parametrized tests."""

    VALID_TUPLE: tuple[int, int, int] = (1, 2, 3)
    VALID_COMPLEX_TUPLE: tuple[int | str, ...] = (1, 2, 3, "alpha", 1)
    SHORT_TUPLE: tuple[int, int] = (1, 2)
    EMPTY_TUPLE: tuple[()] = ()


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: Sequence[pytest.Item],
) -> None:
    """Modify test collection to add markers based on test names."""
    _ = config
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        if "docker" in item.name:
            item.add_marker(pytest.mark.docker)
        if "slow" in item.name:
            item.add_marker(pytest.mark.slow)
