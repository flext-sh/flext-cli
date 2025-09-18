"""Production-ready pytest configuration with FlextTests* utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from collections.abc import Callable, Generator
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

import pytest
from flext_core import FlextResult, FlextTypes
from flext_tests import (
    FlextTestsBuilders,
    FlextTestsDomains,
    FlextTestsFactories,
    FlextTestsFixtures,
    FlextTestsMatchers,
    FlextTestsUtilities,
)

from flext_cli import (
    FlextCliApi,
    FlextCliAuth,
    FlextCliConfig,
    FlextCliContext,
    FlextCliMain,
)
from flext_cli.models import FlextCliModels


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


# FlextTests* Utility Fixtures
@pytest.fixture
def flext_builders() -> FlextTestsBuilders:
    """Provide FlextTestsBuilders for test data creation."""
    return FlextTestsBuilders()


@pytest.fixture
def flext_factories() -> FlextTestsFactories:
    """Provide FlextTestsFactories for realistic test data."""
    return FlextTestsFactories()


@pytest.fixture
def flext_fixtures() -> FlextTestsFixtures:
    """Provide FlextTestsFixtures for comprehensive test utilities."""
    return FlextTestsFixtures()


@pytest.fixture
def flext_matchers() -> FlextTestsMatchers:
    """Provide FlextTestsMatchers for assertions and validations."""
    return FlextTestsMatchers()


@pytest.fixture
def flext_domains() -> FlextTestsDomains:
    """Provide FlextTestsDomains for domain-specific test data."""
    return FlextTestsDomains()


@pytest.fixture
def flext_utilities() -> FlextTestsUtilities:
    """Provide FlextTestsUtilities for advanced test operations."""
    return FlextTestsUtilities()


# File System Fixtures
@pytest.fixture
def temp_dir() -> Generator[Path]:
    """Provide temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp:
        yield Path(temp)


# CLI Core Fixtures
@pytest.fixture
def cli_api() -> FlextCliApi:
    """Provide FlextCliApi for testing."""
    return FlextCliApi()


@pytest.fixture
def cli_main() -> FlextCliMain:
    """Provide FlextCliMain for testing."""
    return FlextCliMain(name="test-cli", description="Test CLI interface")


@pytest.fixture
def cli_auth() -> FlextCliAuth:
    """Provide FlextCliAuth for testing."""
    return FlextCliAuth()


@pytest.fixture
def cli_context(flext_factories: FlextTestsFactories) -> FlextCliContext:
    """Provide real CLI context using FlextTests factories."""
    # Use FlextTestsFactories to create realistic test config
    config_data = flext_factories.ConfigFactory.create(
        profile="test",
        debug=True,
        output_format="json",
        timeout_seconds=30,
        no_color=True,
    )

    config = FlextCliConfig(**config_data)
    return FlextCliContext(
        config=config,
        debug=True,
        verbose=True,
        quiet=False,
        user_id="test_user",
        session_id="test_session",
    )


# Configuration Fixtures
@pytest.fixture
def test_config(flext_factories: FlextTestsFactories) -> FlextCliConfig:
    """Provide test configuration using FlextTestsFactories."""
    config_data = flext_factories.ConfigFactory.create(
        profile="test",
        debug=True,
        timeout_seconds=30,
        output_format="table",
    )
    return FlextCliConfig(**config_data)


# User and Domain Fixtures
@pytest.fixture
def test_user(flext_domains: FlextTestsDomains) -> FlextTypes.Core.Dict:
    """Provide test user using FlextTestsDomains."""
    return flext_domains.create_user(**FlextCliTestData.TEST_USERS["default"])


@pytest.fixture
def REDACTED_LDAP_BIND_PASSWORD_user(flext_domains: FlextTestsDomains) -> FlextTypes.Core.Dict:
    """Provide REDACTED_LDAP_BIND_PASSWORD user using FlextTestsDomains."""
    return flext_domains.create_user(**FlextCliTestData.TEST_USERS["REDACTED_LDAP_BIND_PASSWORD"])


@pytest.fixture
def test_user_batch(flext_domains: FlextTestsDomains) -> list[FlextTypes.Core.Dict]:
    """Provide batch of test users using FlextTestsDomains."""
    return flext_domains.batch_users(count=5)


# FlextResult Fixtures
@pytest.fixture
def success_result(flext_builders: FlextTestsBuilders) -> FlextResult[object]:
    """Provide successful FlextResult using FlextTestsBuilders."""
    return flext_builders.success_result("test_success")


@pytest.fixture
def failure_result(flext_builders: FlextTestsBuilders) -> FlextResult[object]:
    """Provide failed FlextResult using FlextTestsBuilders."""
    return flext_builders.failure_result("test_failure")


@pytest.fixture
def auth_success_result(flext_builders: FlextTestsBuilders) -> FlextResult[object]:
    """Provide successful auth result using FlextTestsBuilders."""
    auth_data = {
        "token": FlextCliTestData.AUTH_TOKENS["valid"],
        "status": "authenticated",
    }
    return flext_builders.success_result(auth_data)


@pytest.fixture
def auth_failure_result(flext_builders: FlextTestsBuilders) -> FlextResult[object]:
    """Provide failed auth result using FlextTestsBuilders."""
    return flext_builders.failure_result("Authentication failed")


# Repository and Service Fixtures
@pytest.fixture
def real_repositories(_flext_fixtures: FlextTestsFixtures) -> FlextTypes.Core.Dict:
    """Provide collection of real repository implementations using FlextTestsFixtures."""
    return {
        "user_repo": {},  # Placeholder for in-memory repo
        "auth_service": FlextCliAuth(),
        "config": FlextCliConfig(profile="test"),
    }


# Command and CLI Fixtures
@pytest.fixture
def auth_commands() -> dict[str, FlextCliModels.CliCommand]:
    """Provide auth command definitions."""
    return {
        "login": FlextCliModels.CliCommand(
            name="login",
            entry_point="auth.login:run",
            command_line="auth login",
        ),
        "logout": FlextCliModels.CliCommand(
            name="logout",
            entry_point="auth.logout:run",
            command_line="auth logout",
        ),
        "status": FlextCliModels.CliCommand(
            name="status",
            entry_point="auth.status:run",
            command_line="auth status",
        ),
    }


@pytest.fixture
def cli_models() -> type[FlextCliModels]:
    """Provide FlextCliModels for command creation."""
    return FlextCliModels


# Test Data Fixtures
@pytest.fixture
def auth_tokens() -> dict[str, str]:
    """Provide auth token test data."""
    return FlextCliTestData.AUTH_TOKENS.copy()


@pytest.fixture
def test_messages() -> dict[str, str]:
    """Provide test message constants."""
    return FlextCliTestData.TEST_MESSAGES.copy()


# Validation and Assertion Helpers
@pytest.fixture
def assert_success(
    flext_matchers: FlextTestsMatchers,
) -> Callable[[FlextResult[object], object], None]:
    """Provide success assertion helper."""

    def _assert_success(
        result: FlextResult[object], expected_data: object = None
    ) -> None:
        flext_matchers.assert_result_success(result)
        if expected_data is not None:
            assert result.value == expected_data

    return _assert_success


@pytest.fixture
def assert_failure(
    flext_matchers: FlextTestsMatchers,
) -> Callable[[FlextResult[object], str | None], None]:
    """Provide failure assertion helper."""

    def _assert_failure(
        result: FlextResult[object], expected_error: str | None = None
    ) -> None:
        flext_matchers.assert_result_failure(result)
        if expected_error is not None:
            assert expected_error in str(result.error or "")

    return _assert_failure


# Performance and Benchmarking Fixtures
@pytest.fixture
def benchmark_fixture(_flext_fixtures: FlextTestsFixtures) -> object:
    """Provide benchmark fixture for performance tests."""
    return {}  # Placeholder for benchmark fixture


# Clean Test Environment
@pytest.fixture(autouse=True)
def clean_auth_environment(cli_auth: FlextCliAuth) -> Generator[None]:
    """Automatically clean auth environment before each test."""
    # Clean up before test
    cli_auth.clear_auth_tokens()
    yield
    # Clean up after test
    cli_auth.clear_auth_tokens()


# Legacy compatibility fixtures (DEPRECATED - use FlextTests* directly)
@pytest.fixture
def test_flext_result_success(
    success_result: FlextResult[object],
) -> FlextResult[object]:
    """DEPRECATED: Use success_result fixture directly."""
    return success_result


@pytest.fixture
def test_flext_result_failure(
    failure_result: FlextResult[object],
) -> FlextResult[object]:
    """DEPRECATED: Use failure_result fixture directly."""
    return failure_result
