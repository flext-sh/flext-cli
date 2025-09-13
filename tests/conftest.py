"""Production-ready pytest configuration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from click.testing import CliRunner
from flext_core import FlextResult, FlextTypes
from rich.console import Console

from flext_cli import FlextCliConfig, FlextCliContext


class MockUser:
    """Simple test user class for testing purposes."""

    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        age: int,
        is_active: bool,
        created_at: datetime,
        metadata: dict[str, object],
    ) -> None:
        """Initialize test user."""
        self.id = user_id
        self.name = name
        self.email = email
        self.age = age
        self.is_active = is_active
        self.created_at = created_at
        self.metadata = metadata


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


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
        timeout_seconds=30,
    )
    return FlextCliContext(
        config=config,
        debug=True,
        verbose=True,
        quiet=False,
        user_id="test_user",
        session_id="test_session",
    )


@pytest.fixture
def test_config() -> FlextCliConfig:
    """Provide test configuration using flext_tests."""
    return FlextCliConfig(
        profile="test",
        debug=True,
        timeout_seconds=30,
        output_format="table",
    )


@pytest.fixture
def test_user() -> MockUser:
    """Provide real test user using factory."""
    return MockUser(
        user_id="test_user_factory",
        name="Test User",
        email="test@example.com",
        age=25,
        is_active=True,
        created_at=datetime.fromisoformat("2024-01-01T00:00:00"),
        metadata={"source": "factory_fallback"},
    )


@pytest.fixture
def real_test_user() -> MockUser:
    """Provide real User instance for testing."""
    return MockUser(
        user_id="test_user_id",  # Required: id
        name="test_user",  # Required: name
        email="test@example.com",  # Required: email
        age=25,  # Required: age
        is_active=True,  # Required: is_active
        created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
        metadata={},  # Required: metadata
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
        "user_repo": MockUser,  # Test user class
        "config": FlextCliConfig(profile="test"),
    }


@pytest.fixture
def success_result() -> FlextResult[str]:
    """Provide successful FlextResult."""
    return FlextResult[str].ok("test_data")


@pytest.fixture
def failure_result() -> FlextResult[str]:
    """Provide failed FlextResult."""
    return FlextResult[str].fail("test_error")
