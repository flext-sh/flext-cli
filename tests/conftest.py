"""Production-ready pytest configuration using flext_tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""


from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import cast

import pytest
from click.testing import CliRunner
from flext_core import FlextResult, FlextTypes
from flext_tests import (
    FlextTestsDomains,
    FlextTestsFactories,
)
from rich.console import Console

from flext_cli import FlextCliConfig, FlextCliContext

# =============================================================================
# PYTEST CONFIGURATION - MINIMAL SETUP
# =============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


# =============================================================================
# BASIC FIXTURES - MINIMAL DEPENDENCIES
# =============================================================================


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """Provide temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp:
        yield Path(temp)


@pytest.fixture
def console() -> Console:
    """Provide Rich console for testing."""
    return Console(file=None, width=80)


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide Click CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def cli_context() -> FlextCliContext:
    """Provide real CLI context using flext_tests factories."""
    # Create real configuration using factory
    config = FlextCliConfig(
        profile="test",
        debug=True,
        output_format="json",
        no_color=True,
        timeout_seconds=30
    )
    return FlextCliContext(
        config=config,
        debug=True,
        verbose=True,
        quiet=False,
        user_id="test_user",
        session_id="test_session"
    )


@pytest.fixture
def test_config() -> FlextCliConfig:
    """Provide test configuration using flext_tests."""
    return FlextCliConfig(
        profile="test",
        debug=True,
        timeout_seconds=30,
        output_format="table"
    )


@pytest.fixture
def test_user() -> FlextTestsDomains.TestUser:
    """Provide real test user using factory."""
    user_factory = FlextTestsFactories.UserFactory()
    return cast("FlextTestsDomains.TestUser", user_factory)


@pytest.fixture
def real_test_user() -> FlextTestsDomains.TestUser:
    """Provide real User instance from flext_tests."""
    return FlextTestsDomains.TestUser(
        id="test_user_id",
        username="test_user",
        email="test@example.com",
        age=25,
        is_admin=False
    )


@pytest.fixture
def test_flext_result_success() -> FlextResult[str]:
    """Provide successful FlextResult for testing."""
    return FlextResult[str].ok("test_success")


@pytest.fixture
def test_flext_result_failure() -> FlextResult[str]:
    """Provide failed FlextResult for testing."""
    return FlextResult[str].fail("test_failure")


@pytest.fixture
def real_repositories() -> FlextTypes.Core.Dict:
    """Provide collection of real repository implementations."""
    return {
        "user_repo": FlextTestsDomains.TestUserRepository(),
        "config": FlextCliConfig(profile="test")
    }


@pytest.fixture
def success_result() -> FlextResult[str]:
    """Provide successful FlextResult."""
    return FlextResult[str].ok("test_data")


@pytest.fixture
def failure_result() -> FlextResult[str]:
    """Provide failed FlextResult."""
    return FlextResult[str].fail("test_error")
