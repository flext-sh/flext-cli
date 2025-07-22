"""Pytest configuration and shared fixtures for FLEXT-CLI.

Modern test configuration for CLI with Click testing support.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from click.testing import CliRunner

# Import CLI command - real import required for tests
from flext_cli.cli import cli as main_cli_command

if TYPE_CHECKING:
    from collections.abc import Iterator
    from unittest.mock import Mock

    import pytest_mock
    from _pytest.config import Config
    from _pytest.nodes import Item
    from click import Command


# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config: Config) -> None:
    """Configure pytest with custom markers and settings.

    Args:
        config: Pytest configuration object.

    """
    # Register custom markers
    config.addinivalue_line(
        "markers",
        "unit: Unit tests that don't require external dependencies",
    )
    config.addinivalue_line(
        "markers",
        "integration: Integration tests that may require external services",
    )
    config.addinivalue_line(
        "markers",
        "slow: Tests that take more than 1 second to run",
    )
    config.addinivalue_line(
        "markers",
        "smoke: Quick smoke tests for CI/CD",
    )
    config.addinivalue_line(
        "markers",
        "e2e: End-to-end tests",
    )
    config.addinivalue_line(
        "markers",
        "cli: CLI command tests",
    )
    config.addinivalue_line(
        "markers",
        "interactive: Interactive CLI tests",
    )


def pytest_collection_modifyitems(config: Config, items: list[Item]) -> None:
    """Automatically mark tests based on their location.

    Args:
        config: Pytest configuration object.
        items: List of collected test items.

    """
    for item in items:
        # Auto-mark based on test location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


# ============================================================================
# CLI Testing Fixtures
# ============================================================================


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Click CLI runner for testing commands.

    Returns:
        CliRunner instance configured for testing.

    """
    return CliRunner()


@pytest.fixture
def isolated_cli_runner() -> Iterator[CliRunner]:
    """Provide a CLI runner with isolated filesystem.

    Yields:
        CliRunner instance with isolated filesystem for testing.

    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner


@pytest.fixture
def cli() -> Command:
    """Provide the main CLI command for testing.

    Returns:
        Main CLI command instance.

    """
    return main_cli_command


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    """Create a temporary configuration file for testing.

    Args:
        tmp_path: Pytest temporary path fixture.

    Returns:
        Path to the created configuration file.

    """
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
api:
  url: http://localhost:8000
  timeout: 30

auth:
  token: test-token-123

defaults:
  output_format: json
  color: true
  verbose: false
""",
    )
    return config_path


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    """Create a temporary environment file for testing.

    Args:
        tmp_path: Pytest temporary path fixture.

    Returns:
        Path to the created environment file.

    """
    env_path = tmp_path / ".env"
    env_path.write_text(
        """
FLEXT_API_URL=http://localhost:8000
FLEXT_API_TOKEN=test-token-123
FLEXT_DEBUG=true
""",
    )
    return env_path


# ============================================================================
# Mock API Fixtures
# ============================================================================


@pytest.fixture
def mock_api_client(mocker: pytest_mock.MockerFixture) -> Any:
    """Create a mock API client for testing.

    Args:
        mocker: Pytest mock fixture.

    Returns:
        Mock API client with predefined responses.

    """
    mock = mocker.Mock()

    # Mock pipeline operations
    mock.list_pipelines.return_value = {
        "items": [
            {
                "id": "pipeline-1",
                "name": "test-pipeline-1",
                "status": "active",
            },
            {
                "id": "pipeline-2",
                "name": "test-pipeline-2",
                "status": "inactive",
            },
        ],
        "total": 2,
    }

    mock.get_pipeline.return_value = {
        "id": "pipeline-1",
        "name": "test-pipeline-1",
        "status": "active",
        "config": {"source": "postgres", "destination": "snowflake"},
    }

    mock.create_pipeline.return_value = {
        "id": "pipeline-new",
        "name": "new-pipeline",
        "status": "active",
    }

    return mock


# ============================================================================
# Output Fixtures
# ============================================================================


@pytest.fixture
def json_output() -> str:
    """Provide sample JSON output for testing.

    Returns:
        JSON string for testing output parsing.

    """
    return """{
  "id": "pipeline-1",
  "name": "test-pipeline",
  "status": "active"
}"""


@pytest.fixture
def table_output() -> str:
    """Provide sample table output for testing.

    Returns:
        Table string for testing table formatting.

    """
    return """┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ ID         ┃ Name          ┃ Status  ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ pipeline-1 │ test-pipeline │ active  │
└────────────┴───────────────┴─────────┘"""


# ============================================================================
# Interactive Testing Fixtures
# ============================================================================


@pytest.fixture
def mock_prompt(mocker: pytest_mock.MockerFixture) -> Mock:
    """Create a mock prompt for interactive testing.

    Args:
        mocker: Pytest mock fixture.

    Returns:
        Mock prompt with predefined responses.

    """
    mock = mocker.patch("questionary.prompt")
    mock.return_value = {
        "name": "test-pipeline",
        "description": "Test pipeline description",
        "source": "postgres",
        "destination": "snowflake",
    }
    return mock


@pytest.fixture
def mock_confirm(mocker: pytest_mock.MockerFixture) -> Mock:
    """Create a mock confirmation prompt for testing.

    Args:
        mocker: Pytest mock fixture.

    Returns:
        Mock confirmation prompt that returns True.

    """
    mock = mocker.patch("questionary.confirm")
    mock.return_value = True
    return mock


# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
def pipeline_config() -> dict[str, Any]:
    """Provide sample pipeline configuration for testing.

    Returns:
        Dictionary containing pipeline configuration data.

    """
    return {
        "name": "test-pipeline",
        "description": "Test pipeline for CLI",
        "config": {
            "source": {
                "type": "postgres",
                "connection": "postgresql://localhost/test",
            },
            "destination": {
                "type": "snowflake",
                "account": "test_account",
            },
            "schedule": "@daily",
        },
    }


@pytest.fixture
def command_args() -> list[str]:
    return ["--debug", "--output", "json", "--no-color"]


# ============================================================================
# Environment Fixtures
# ============================================================================


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clean environment variables for testing.

    Args:
        monkeypatch: Pytest monkeypatch fixture.

    """
    env_vars = [
        "FLEXT_API_URL",
        "FLEXT_API_TOKEN",
        "FLEXT_CONFIG_FILE",
        "FLEXT_DEBUG",
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up test environment variables.

    Args:
        monkeypatch: Pytest monkeypatch fixture.

    """
    monkeypatch.setenv("FLEXT_API_URL", "http://test-api:8000")
    monkeypatch.setenv("FLEXT_API_TOKEN", "test-token-env")
    monkeypatch.setenv("FLEXT_DEBUG", "true")
