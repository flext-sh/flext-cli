"""Pytest configuration and fixtures for FLEXT CLI Library tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from flext_cli import (
    CLICommand,
    CLIConfig,
    CLIExecutionContext as CLIContext,  # alias acceptable from root
    CommandType,
    FlextConstants,
    create_cli_container,
)
from tests.test_mocks import (
    MockFailingApiClient,
    MockFlextApiClient,
)

# =============================================================================
# PYTEST CONFIGURATION - Early Hook to Prevent HTTP Initialization
# =============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Early pytest hook to patch HTTP functionality before any imports."""
    # Apply patches at the earliest possible stage to prevent HTTP calls

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


def pytest_unconfigure(config: pytest.Config) -> None:
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
def cli_config() -> CLIConfig:
    """Create a test CLI configuration."""
    return CLIConfig(
      api_url=f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}",
      output_format="json",
      timeout=30,
      profile="test",
      debug=True,
      quiet=False,
      verbose=True,
      no_color=True,
    )


@pytest.fixture
def cli_settings() -> CLIConfig:
    """Create test CLI settings."""
    return CLIConfig(
      debug=True,
      profile="test",
      output_format="json",
      project_name="test-cli",
      project_description="Test CLI Library",
      log_level="DEBUG",
    )


@pytest.fixture
def cli_context(cli_config: CLIConfig) -> CLIContext:
    """Create a test CLI context."""
    return CLIContext(
      config=cli_config,
      console=Console(),
    )


@pytest.fixture
def console() -> Console:
    """Create a Rich console for testing."""
    return Console(width=80, height=24, force_terminal=False)


@pytest.fixture
def sample_command() -> CLICommand:
    """Create a sample CLI command for testing."""
    return CLICommand(
      id="test_cmd_001",
      name="test-command",
      description="A test command",
      command_type=CommandType.SYSTEM,
      command_line="echo hello",
      arguments={"arg1": "value1"},
      options={"--verbose": True},
    )


@pytest.fixture
def mock_context() -> tuple[object, object]:
    """Create mock Click context with console for testing commands."""
    console = MagicMock(spec=Console)
    ctx = MagicMock()
    ctx.obj = {"console": console}
    return ctx, console


@pytest.fixture(autouse=True)
def disable_real_api_calls() -> None:
    """Additional API call prevention for test isolation.

    This fixture runs automatically for all tests to ensure no real HTTP calls
    are made during testing.
    """
    # Additional patches for comprehensive API call prevention
    patches = [
      patch("flext_cli.flext_api_integration.FLEXT_API_AVAILABLE", False),
      patch("flext_cli.commands.debug.FLEXT_API_AVAILABLE", False),
      # patch("flext_cli.commands.projects.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.sessions.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.plugins.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.config.FLEXT_API_AVAILABLE", False),  # Attribute does not exist
      # patch("flext_cli.commands.auth.FLEXT_API_AVAILABLE", False),  # Attribute does not exist
      # patch("flext_cli.commands.help.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.version.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.init.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.run.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.status.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.clean.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.reset.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.export.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.import_cmd.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.validate.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.test.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.benchmark.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.profile.FLEXT_API_AVAILABLE", False),  # Module does not exist
      patch("flext_cli.commands.debug.FLEXT_API_AVAILABLE", False),
      # patch("flext_cli.commands.logs.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.metrics.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.health.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.info.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.about.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.help.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.version.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.init.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.run.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.status.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.clean.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.reset.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.export.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.import_cmd.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.validate.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.test.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.benchmark.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.profile.FLEXT_API_AVAILABLE", False),  # Module does not exist
      patch("flext_cli.commands.debug.FLEXT_API_AVAILABLE", False),
      # patch("flext_cli.commands.logs.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.metrics.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.health.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.info.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.about.FLEXT_API_AVAILABLE", False),  # Module does not exist
    ]

    # Apply patches
    for patch_obj in patches:
      patch_obj.start()

    yield

    # Cleanup patches
    for patch_obj in patches:
      patch_obj.stop()


@pytest.fixture
def mock_flext_api_client() -> MockFlextApiClient:
    """Create a mock FLEXT API client with consistent test behavior.

    This fixture provides a mock client that simulates successful API responses
    for testing CLI command behavior without making real HTTP calls.
    """
    return MockFlextApiClient()


@pytest.fixture
def mock_flext_api_client_with_patches() -> MockFlextApiClient:
    """Mock API client with comprehensive patching to prevent real HTTP calls.

    This fixture creates a mock client and applies patches to ensure no real
    HTTP calls are made, while maintaining the expected API interface for tests.
    """
    # Create mock client instance
    client = MockFlextApiClient()

    # Apply additional patches for comprehensive isolation
    patches = [
      patch("flext_cli.flext_api_integration.FLEXT_API_AVAILABLE", False),
      patch("flext_cli.commands.debug.FLEXT_API_AVAILABLE", False),
      # patch("flext_cli.commands.projects.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.sessions.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.plugins.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.config.FLEXT_API_AVAILABLE", False),  # Attribute does not exist
      # patch("flext_cli.commands.auth.FLEXT_API_AVAILABLE", False),  # Attribute does not exist
      # patch("flext_cli.commands.help.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.version.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.init.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.run.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.status.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.clean.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.reset.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.export.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.import_cmd.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.validate.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.test.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.benchmark.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.profile.FLEXT_API_AVAILABLE", False),  # Module does not exist
      patch("flext_cli.commands.debug.FLEXT_API_AVAILABLE", False),
      # patch("flext_cli.commands.logs.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.metrics.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.health.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.info.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.about.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.help.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.version.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.init.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.run.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.status.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.clean.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.reset.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.export.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.import_cmd.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.validate.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.test.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.benchmark.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.profile.FLEXT_API_AVAILABLE", False),  # Module does not exist
      patch("flext_cli.commands.debug.FLEXT_API_AVAILABLE", False),
      # patch("flext_cli.commands.logs.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.metrics.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.health.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.info.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.about.FLEXT_API_AVAILABLE", False),  # Module does not exist
    ]

    # Apply patches
    for patch_obj in patches:
      patch_obj.start()

    yield client

    # Cleanup patches
    for patch_obj in patches:
      patch_obj.stop()


@pytest.fixture
def mock_failing_api_client() -> MockFailingApiClient:
    """Mock API client that simulates connection failures for error testing."""
    # Create failing mock client instance
    client = MockFailingApiClient()

    # Apply patches to ensure no real HTTP calls
    patches = [
      patch("flext_cli.flext_api_integration.FLEXT_API_AVAILABLE", False),
      patch("flext_cli.commands.debug.FLEXT_API_AVAILABLE", False),
      # patch("flext_cli.commands.projects.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.sessions.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.plugins.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.config.FLEXT_API_AVAILABLE", False),  # Attribute does not exist
      # patch("flext_cli.commands.auth.FLEXT_API_AVAILABLE", False),  # Attribute does not exist
      # patch("flext_cli.commands.help.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.version.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.init.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.run.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.status.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.clean.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.reset.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.export.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.import_cmd.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.validate.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.test.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.benchmark.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.profile.FLEXT_API_AVAILABLE", False),  # Module does not exist
      patch("flext_cli.commands.debug.FLEXT_API_AVAILABLE", False),
      # patch("flext_cli.commands.logs.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.metrics.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.health.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.info.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.about.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.help.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.version.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.init.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.run.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.status.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.clean.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.reset.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.export.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.import_cmd.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.validate.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.test.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.benchmark.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.profile.FLEXT_API_AVAILABLE", False),  # Module does not exist
      patch("flext_cli.commands.debug.FLEXT_API_AVAILABLE", False),
      # patch("flext_cli.commands.logs.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.metrics.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.health.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.info.FLEXT_API_AVAILABLE", False),  # Module does not exist
      # patch("flext_cli.commands.about.FLEXT_API_AVAILABLE", False),  # Module does not exist
    ]

    # Apply patches
    for patch_obj in patches:
      patch_obj.start()

    yield client

    # Cleanup patches
    for patch_obj in patches:
      patch_obj.stop()


@pytest.fixture
def mock_container() -> object:
    """Create a mock CLI container for dependency injection testing."""
    return create_cli_container()


@pytest.fixture
def isolated_config() -> CLIConfig:
    """Create isolated config for tests without singleton contamination."""
    # Return fresh config instance for each test
    return CLIConfig(
      profile="test",
      debug=True,
      output_format="json",
      project_name="test-cli",
      project_description="Test CLI Library",
      log_level="DEBUG",
    )
