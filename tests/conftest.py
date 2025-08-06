"""Pytest configuration and fixtures for FLEXT CLI Library tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from flext_cli.core import (
    FlextCliCommand,
    FlextCliConfig,
    FlextCliContext,
    FlextCliPlugin,
    FlextCliSession,
)
from flext_cli.core.typedefs import FlextCliCommandType
from flext_core import FlextResult
from rich.console import Console

if TYPE_CHECKING:
    from collections.abc import Generator


# =============================================================================
# PYTEST CONFIGURATION - Early Hook to Prevent HTTP Initialization
# =============================================================================


def pytest_configure(config):
    """Early pytest hook to patch HTTP functionality before any imports."""
    # Apply patches at the earliest possible stage to prevent HTTP calls
    from unittest.mock import MagicMock, patch

    # Global patches that must be applied before modules are imported
    patches = [
        patch("flext_cli.flext_api_integration.FLEXT_API_AVAILABLE", False),
        patch("flext_cli.commands.debug.FLEXT_API_AVAILABLE", False),
        patch("aiohttp.ClientSession", return_value=MagicMock()),
        patch("httpx.AsyncClient", return_value=MagicMock()),
    ]

    # Store patches in pytest namespace for cleanup
    if not hasattr(config, "_api_patches"):
        config._api_patches = []
        for patch_obj in patches:
            patcher = patch_obj
            patcher.start()
            config._api_patches.append(patcher)


def pytest_unconfigure(config):
    """Cleanup patches after test session."""
    if hasattr(config, "_api_patches"):
        for patcher in config._api_patches:
            patcher.stop()
        config._api_patches.clear()


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def cli_config() -> FlextCliConfig:
    """Create a test CLI configuration."""
    return FlextCliConfig(
        api_url="http://localhost:8000",
        output_format="json",
        timeout=30,
        profile="test",
        debug=True,
        quiet=False,
        verbose=True,
        no_color=True,
    )


@pytest.fixture
def cli_settings() -> FlextCliConfig:
    """Create test CLI settings."""
    return FlextCliConfig(
        debug=True,
        profile="test",
        output_format="json",
        project_name="test-cli",
        project_description="Test CLI Library",
        log_level="DEBUG",
    )


@pytest.fixture
def cli_context(cli_config: FlextCliConfig) -> FlextCliContext:
    """Create a test CLI context."""
    from rich.console import Console

    return FlextCliContext(
        config=cli_config,
        console=Console(),
    )


@pytest.fixture
def console() -> Console:
    """Create a Rich console for testing."""
    return Console(width=80, height=24, force_terminal=False)


@pytest.fixture
def sample_command() -> FlextCliCommand:
    """Create a sample CLI command for testing."""
    return FlextCliCommand(
        id="test_cmd_001",
        name="test-command",
        description="A test command",
        command_type=FlextCliCommandType.SYSTEM,
        command_line="echo hello",
        arguments={"arg1": "value1"},
        options={"--verbose": True},
    )


@pytest.fixture
def sample_plugin() -> FlextCliPlugin:
    """Create a sample CLI plugin for testing."""
    return FlextCliPlugin(
        id="test_plugin_001",
        name="test-plugin",
        plugin_version="0.9.0",
        description="A test plugin",
        entry_point="test_plugin.main",
        commands=["test-cmd"],
        dependencies=["click"],
        author="Test Author",
        license="MIT",
    )


@pytest.fixture
def sample_session() -> FlextCliSession:
    """Create a sample CLI session for testing."""
    return FlextCliSession(
        id="test_session_001",
        session_id="test-session-123",
        working_directory=tempfile.gettempdir(),
        environment={"TEST": "true"},
        active=True,
    )


@pytest.fixture
def mock_context() -> tuple[object, object]:
    """Create mock Click context with console for testing commands."""
    from unittest.mock import MagicMock

    console = MagicMock(spec=Console)
    ctx = MagicMock()
    ctx.obj = {"console": console}
    return ctx, console


@pytest.fixture
def mock_data() -> dict[str, object]:
    """Mock data for testing."""
    return {
        "commands": [
            {"name": "cmd1", "status": "completed"},
            {"name": "cmd2", "status": "running"},
        ],
        "plugins": [
            {"name": "plugin1", "enabled": True},
            {"name": "plugin2", "enabled": False},
        ],
        "sessions": [
            {"id": "session1", "active": True},
            {"id": "session2", "active": False},
        ],
    }


# =============================================================================
# FLEXT-API INTEGRATION MOCKING (SOLID Dependency Inversion Pattern)
# =============================================================================


@pytest.fixture(autouse=True)
def disable_real_api_calls():
    """Additional API call prevention for test isolation.

    This fixture provides additional patches beyond the session-level ones
    applied in pytest_configure, ensuring complete test isolation.
    """
    # Additional patches for complete API isolation during individual tests
    with (
        patch("flext_api.create_flext_api", return_value=None),
        patch("flext_api.FlextApiClient", return_value=None),
    ):
        yield


@pytest.fixture
def mock_flext_api_client():
    """Create a mock FLEXT API client with consistent test behavior.

    Provides a fully mocked client that returns predictable FlextResult
    responses without making real HTTP calls.
    """
    mock_client = MagicMock()
    mock_client.base_url = "http://localhost:8000"

    # Setup async methods to return FlextResult objects
    async def mock_test_connection_success():
        return FlextResult.ok(True)

    async def mock_test_connection_failure():
        return FlextResult.fail("Connection failed")

    async def mock_get_system_status_success():
        return FlextResult.ok(
            {"version": "1.0.0", "status": "healthy", "uptime": "24h"}
        )

    async def mock_get_system_status_failure():
        return FlextResult.fail("Status unavailable")

    async def mock_list_services_success():
        return FlextResult.ok(
            [
                {
                    "name": "FlexCore",
                    "url": "http://localhost:8080",
                    "status": "healthy",
                    "response_time": 0.05,
                },
                {
                    "name": "FLEXT Service",
                    "url": "http://localhost:8081",
                    "status": "healthy",
                    "response_time": 0.03,
                },
            ]
        )

    # Default to successful responses - tests can override as needed
    mock_client.test_connection = mock_test_connection_success
    mock_client.get_system_status = mock_get_system_status_success
    mock_client.list_services = mock_list_services_success

    return mock_client


@pytest.fixture
def mock_flext_api_client_with_patches():
    """Mock API client with comprehensive patching to prevent real HTTP calls.

    This fixture provides complete isolation from flext-api HTTP functionality
    while maintaining the expected API interface for tests.
    """
    from tests.test_mocks import MockFlextApiClient, mock_create_flext_api

    # Create mock client instance
    mock_client = MockFlextApiClient()

    # Comprehensive patching to prevent any real HTTP calls
    with (
        patch("flext_cli.flext_api_integration.FLEXT_API_AVAILABLE", True),
        patch("flext_cli.commands.debug.FLEXT_API_AVAILABLE", True),
        patch("flext_api.create_flext_api", side_effect=mock_create_flext_api),
        patch(
            "flext_cli.flext_api_integration.create_flext_api",
            side_effect=mock_create_flext_api,
        ),
        patch(
            "flext_cli.flext_api_integration.FlextApiClient", return_value=MagicMock()
        ),
        patch(
            "flext_cli.flext_api_integration.get_default_cli_client",
            return_value=mock_client,
        ),
        patch(
            "flext_cli.flext_api_integration.create_cli_api_client",
            return_value=mock_client,
        ),
    ):
        yield mock_client


@pytest.fixture
def mock_failing_api_client():
    """Mock API client that simulates connection failures for error testing."""
    from tests.test_mocks import MockFailingApiClient, mock_create_flext_api

    # Create failing mock client instance
    mock_client = MockFailingApiClient()

    # Patch with failing client
    with (
        patch("flext_cli.flext_api_integration.FLEXT_API_AVAILABLE", True),
        patch("flext_cli.commands.debug.FLEXT_API_AVAILABLE", True),
        patch("flext_api.create_flext_api", side_effect=mock_create_flext_api),
        patch(
            "flext_cli.flext_api_integration.create_flext_api",
            side_effect=mock_create_flext_api,
        ),
        patch(
            "flext_cli.flext_api_integration.FlextApiClient", return_value=MagicMock()
        ),
        patch(
            "flext_cli.flext_api_integration.get_default_cli_client",
            return_value=mock_client,
        ),
        patch(
            "flext_cli.flext_api_integration.create_cli_api_client",
            return_value=mock_client,
        ),
    ):
        yield mock_client


@pytest.fixture
def mock_container():
    """Create a mock CLI container for dependency injection testing."""
    from flext_cli.infrastructure.container import create_cli_container

    container = create_cli_container()

    # Mock the API client factory to return test clients
    def mock_api_factory(**kwargs: object) -> object:
        """Mock API client factory that returns test-friendly clients."""
        mock_client = MagicMock()
        mock_client.base_url = kwargs.get("base_url", "http://localhost:8000")
        mock_client.timeout = kwargs.get("timeout", 30.0)
        mock_client.token = kwargs.get("token")

        # Mock async methods
        async def mock_test_connection():
            return FlextResult.ok(True)

        async def mock_get_system_status():
            return FlextResult.ok({"version": "1.0.0", "status": "healthy"})

        mock_client.test_connection = mock_test_connection
        mock_client.get_system_status = mock_get_system_status
        mock_client.is_available = MagicMock(return_value=True)

        return mock_client

    # Replace the API client factory in the container
    container._container.register_instance("api_client_factory", mock_api_factory)

    return container


@pytest.fixture
def isolated_config():
    """Create isolated config for tests without singleton contamination."""
    from flext_cli.config import FlextCliConfig

    # Return fresh config instance for each test
    return FlextCliConfig(
        api_url="http://localhost:8000",
        timeout=30,
        debug=True,
        profile="test",
        output_format="json",
        no_color=True,
    )
