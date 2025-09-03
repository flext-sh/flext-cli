"""Pytest configuration and fixtures for FLEXT CLI Library - REAL FUNCTIONALITY TESTS.

This conftest provides minimal fixtures for REAL testing without excessive mocking.
Follows user requirement: "melhore bem os tests para executar codigo de verdade e validar
a funcionalidade requerida, pare de ficar mockando tudo!"

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import click
import pytest
from flext_core import FlextContainer
from rich.console import Console

from flext_cli import FlextCliModels
from flext_cli import FlextCliConfig
from flext_cli import FlextCliContext

# =============================================================================
# PYTEST CONFIGURATION - REAL FUNCTIONALITY TESTING
# =============================================================================

# NO MOCKING - Tests should execute real code!
# Only isolation: use temporary directories and test data


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """Create a temporary directory for REAL file operations in tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def cli_config() -> object:
    """Create REAL CLI configuration for testing actual functionality."""
    if FlextCliConfig is None:
        pytest.skip("FlextCliConfig not available")
    return FlextCliConfig(
        profile="test",
        debug=True,
        log_level="DEBUG",
        project_name="test-cli",
    )


@pytest.fixture
def cli_settings() -> object:
    """Create REAL CLI settings for testing actual functionality."""
    if FlextCliConfig is None:
        pytest.skip("FlextCliConfig not available")
    return FlextCliConfig.CliSettings(
        debug=True,
        project_name="test-cli",
        project_description="Test CLI Library",
        log_level="DEBUG",
    )


@pytest.fixture
def cli_context(cli_config: object) -> object:
    """Create REAL CLI context for testing actual functionality."""
    if FlextCliContext is None:
        pytest.skip("FlextCliContext not available")
    return FlextCliContext(
        config=cli_config,
        console=Console(),
    )


@pytest.fixture
def console() -> Console:
    """Create REAL Rich console for testing actual output formatting."""
    return Console(width=80, height=24, force_terminal=False)


@pytest.fixture
def sample_command() -> object:
    """Create REAL sample CLI command for testing actual execution."""
    # Use getattr to safely access the Command class
    command_class = getattr(FlextCliModels, "Command", None)
    if command_class is None:
        pytest.skip("FlextCliModels.Command not available")
    if callable(command_class):
        return command_class(
            command_line="echo hello",
            id="test-command",
        )
    pytest.skip("FlextCliModels.Command is not callable")
    return None  # This line will never be reached, but satisfies type checker


@pytest.fixture
def real_click_context(console: Console) -> tuple[object, Console]:
    """Create REAL Click context for testing actual CLI command execution.

    This provides real Click context without mocking for testing actual command behavior.
    """
    ctx = click.Context(click.Command("test"))
    ctx.obj = {"console": console}
    return ctx, console


@pytest.fixture
def cli_container() -> object:
    """Create REAL CLI container for testing actual dependency injection."""
    # Use getattr to safely access the create_container method
    create_container = getattr(FlextContainer, "create_container", None)
    if create_container is None:
        pytest.skip("FlextContainer.create_container not available")
    # Call the method if it exists
    if callable(create_container):
        return create_container()
    pytest.skip("FlextContainer.create_container is not callable")
    return None  # This line will never be reached, but satisfies type checker


@pytest.fixture
def isolated_config() -> object:
    """Create REAL isolated config for testing without state contamination."""
    if FlextCliConfig is None:
        pytest.skip("FlextCliConfig not available")
    # Return fresh config instance for each test
    config = FlextCliConfig(
        profile="test",
        debug=True,
        log_level="DEBUG",
        project_name="test-cli",
    )
    # Set output format via nested config if available
    if hasattr(config, "output") and hasattr(config.output, "format"):
        config.output.format = "json"
    return config


@pytest.fixture
def sample_data() -> dict[str, object]:
    """Sample data for REAL testing of data processing functions."""
    return {
        "users": [
            {"id": 1, "name": "Alice", "age": 30, "department": "Engineering"},
            {"id": 2, "name": "Bob", "age": 25, "department": "Sales"},
            {"id": 3, "name": "Carol", "age": 35, "department": "Engineering"},
        ],
        "config": {
            "version": "1.0.0",
            "debug": True,
            "features": ["auth", "api", "cli"],
        },
    }


# =============================================================================
# REAL TEST DATA - No Mocks, Just Data
# =============================================================================


@pytest.fixture
def test_config_dict() -> dict[str, object]:
    """Real configuration dictionary for testing."""
    return {
        "project_name": "flext-cli-test",
        "project_version": "0.9.0",
        "debug": True,
        "output_format": "json",
        "log_level": "DEBUG",
        "timeout": 30,
        "profile": "test",
    }


@pytest.fixture
def test_command_data() -> dict[str, object]:
    """Real command data for testing."""
    return {
        "name": "test-command",
        "command_line": "echo 'Hello, World!'",
        "description": "Test command for real execution",
        "timeout": 60,
        "command_type": "system",
    }
