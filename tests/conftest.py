"""Production-ready pytest configuration with FlextTests* utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

import pytest

# Import FlextResult directly to avoid circular imports
# Import individual modules to avoid circular imports
from flext_cli.api import FlextCliApi
from flext_cli.auth import FlextCliAuth
from flext_cli.commands import FlextCliCommands
from flext_cli.config import FlextCliConfig
from flext_cli.context import FlextCliContext
from flext_cli.models import FlextCliModels
from tests.test_utils import FlextTestsBuilders, FlextTestsDomains, FlextTestsMatchers


# Test Configuration and Constants
class FlextCliTestData:
    """Centralized test data and constants for flext-cli tests."""

    # Auth Test Data
    AUTH_TOKENS: ClassVar[dict[str, str]] = {
        "valid": "test_auth_token_12345",
        "special_chars": "token_with_!@#$%^&*()_+-={}[]|\\:;\"'<>,.?/",
        "long": "x" * 1000,
        "empty": "",
        "integration": "integration_test_token_xyz789",
        "workflow": "workflow_integration_token_123",
    }

    # User Test Data
    TEST_USERS: ClassVar[dict[str, dict[str, object]]] = {
        "default": {
            "user_id": "test_user_factory",
            "name": "Test User",
            "email": "test@example.com",
            "age": 25,
            "is_active": True,
            "created_at": datetime.fromisoformat("2024-01-01T00:00:00"),
            "metadata": {"source": "factory"},
        },
        "REDACTED_LDAP_BIND_PASSWORD": {
            "user_id": "REDACTED_LDAP_BIND_PASSWORD_user_id",
            "name": "Admin User",
            "email": "REDACTED_LDAP_BIND_PASSWORD@example.com",
            "age": 35,
            "is_active": True,
            "created_at": datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            "metadata": {"role": "REDACTED_LDAP_BIND_PASSWORD"},
        },
    }

    # Test Messages and Outputs
    TEST_MESSAGES: ClassVar[dict[str, str]] = {
        "auth_success": "Successfully authenticated",
        "auth_failure": "Authentication failed",
        "token_expired": "Token expired",
        "logout_success": "Successfully logged out",
        "not_authenticated": "Not authenticated",
    }


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "auth: marks tests as auth-related")
    config.addinivalue_line("markers", "cli: marks tests as CLI-related")
    config.addinivalue_line("markers", "real: marks tests using real functionality")


# FlextTests* Utility Fixtures - Commented out due to import issues


@pytest.fixture
def flext_builders() -> FlextTestsBuilders:
    """Provide FlextTestsBuilders for test data creation."""
    return FlextTestsBuilders()


@pytest.fixture
def flext_domains() -> FlextTestsDomains:
    """Provide FlextTestsDomains for test data creation."""
    return FlextTestsDomains()


@pytest.fixture
def flext_matchers() -> FlextTestsMatchers:
    """Provide FlextTestsMatchers for test assertions."""
    return FlextTestsMatchers()


@pytest.fixture
def cli_api() -> FlextCliApi:
    """Provide FlextCliApi instance for tests."""
    return FlextCliApi()


@pytest.fixture
def cli_auth() -> FlextCliAuth:
    """Provide FlextCliAuth instance for tests."""
    return FlextCliAuth()


@pytest.fixture
def cli_main() -> FlextCliCommands:
    """Provide FlextCliCommands instance for tests."""
    return FlextCliCommands()


@pytest.fixture
def cli_context() -> FlextCliContext:
    """Provide FlextCliContext instance for tests."""
    config = FlextCliConfig.MainConfig(
        profile="test", output_format="json", debug=True, no_color=True
    )
    return FlextCliContext.create(config=config, debug=True, verbose=True)


@pytest.fixture
def auth_tokens() -> dict[str, str]:
    """Provide auth tokens for testing."""
    return {
        "valid": "test_auth_token_12345",
        "invalid": "invalid_token",
        "expired": "expired_token_12345",
        "special_chars": "token_with_!@#$%^&*()_+-={}[]|\\:;\"'<>,.?/",
        "long": "x" * 1000,
        "empty": "",
        "integration": "integration_test_token_xyz789",
        "workflow": "workflow_integration_token_123",
    }


@pytest.fixture
def test_messages() -> dict[str, str]:
    """Provide test messages for testing."""
    return {
        "success": "Operation completed successfully",
        "error": "An error occurred",
        "warning": "Warning message",
        "auth_failure": "Authentication failed",
        "token_expired": "Token expired",
        "info": "Information message",
    }


@pytest.fixture
def auth_commands() -> dict[str, FlextCliModels.CliCommand]:
    """Provide auth commands for testing."""
    return {
        "login": FlextCliModels.CliCommand(
            command_line="auth login", name="login", entry_point="auth.login"
        ),
        "logout": FlextCliModels.CliCommand(
            command_line="auth logout", name="logout", entry_point="auth.logout"
        ),
        "status": FlextCliModels.CliCommand(
            command_line="auth status", name="status", entry_point="auth.status"
        ),
        "token": FlextCliModels.CliCommand(
            command_line="auth token", name="token", entry_point="auth.token"
        ),
    }


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """Provide temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)
