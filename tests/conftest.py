"""Pytest configuration and fixtures for FLEXT CLI Library tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from flext_cli import (
    CLICommand,
    CLIConfig,
    CLIContext,
    CLIPlugin,
    CLISession,
    CLISettings,
    CommandType,
)
from rich.console import Console

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def cli_config() -> CLIConfig:
    """Create a test CLI configuration."""
    return CLIConfig(
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
def cli_settings() -> CLISettings:
    """Create test CLI settings."""
    return CLISettings(
        project_name="test-cli",
        project_version="1.0.0",
        project_description="Test CLI Library",
        debug=True,
        log_level="DEBUG",
    )


@pytest.fixture
def cli_context(cli_config: CLIConfig, cli_settings: CLISettings) -> CLIContext:
    """Create a test CLI context."""
    return CLIContext(
        profile="test",
        output_format="json",
        debug=True,
        quiet=False,
        verbose=True,
        no_color=True,
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
def sample_plugin() -> CLIPlugin:
    """Create a sample CLI plugin for testing."""
    return CLIPlugin(
        id="test_plugin_001",
        name="test-plugin",
        version="0.8.0",
        description="A test plugin",
        entry_point="test_plugin.main",
        commands=["test-cmd"],
        dependencies=["click"],
        author="Test Author",
        license="MIT",
    )


@pytest.fixture
def sample_session() -> CLISession:
    """Create a sample CLI session for testing."""
    return CLISession(
        id="test_session_001",
        session_id="test-session-123",
        working_directory=tempfile.gettempdir(),
        environment={"TEST": "true"},
        active=True,
    )


@pytest.fixture
def mock_data() -> dict[str, Any]:
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
