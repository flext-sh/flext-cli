"""FLEXT CLI Test Configuration - Comprehensive Test Infrastructure.

Centralized test configuration using flext_tests library with real functionality
testing, Docker support, and comprehensive fixtures following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner
from flext_core import FlextContainer, FlextTypes, FlextUtilities
from flext_tests import (
    FlextTestDocker,
    FlextTestsBuilders,
    FlextTestsUtilities,
)

from flext_cli.api import FlextCli
from flext_cli.auth import FlextCliAuth
from flext_cli.cmd import FlextCliCmd
from flext_cli.commands import FlextCliCommands
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.containers import FlextCliContainers
from flext_cli.context import FlextCliContext
from flext_cli.core import FlextCliService
from flext_cli.debug import FlextCliDebug
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.handlers import FlextCliHandlers
from flext_cli.mixins import FlextCliMixins
from flext_cli.models import FlextCliModels
from flext_cli.output import FlextCliOutput
from flext_cli.processors import FlextCliProcessors
from flext_cli.prompts import FlextCliPrompts
from flext_cli.protocols import FlextCliProtocols
from flext_cli.typings import FlextCliTypes

# ============================================================================
# CORE FLEXT TEST INFRASTRUCTURE
# ============================================================================


@pytest.fixture(scope="session")
def flext_test_utilities() -> FlextTestsUtilities:
    """Provide FlextTestsUtilities for test infrastructure."""
    return FlextTestsUtilities()


@pytest.fixture(scope="session")
def flext_test_builders() -> FlextTestsBuilders:
    """Provide FlextTestsBuilders for test data creation."""
    return FlextTestsBuilders()


@pytest.fixture(scope="session")
def flext_test_docker() -> FlextTestDocker:
    """Provide FlextTestDocker for containerized testing."""
    return FlextTestDocker()


# ============================================================================
# CLI TEST INFRASTRUCTURE
# ============================================================================


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create Click CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def temp_file(temp_dir: Path) -> Path:
    """Create temporary file for tests."""
    temp_file_path = temp_dir / "test_file.txt"
    temp_file_path.write_text("test content")
    return temp_file_path


@pytest.fixture
def temp_json_file(temp_dir: Path) -> Path:
    """Create temporary JSON file for tests."""
    temp_file_path = temp_dir / "test_file.json"
    test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
    temp_file_path.write_text(json.dumps(test_data))
    return temp_file_path


@pytest.fixture
def temp_yaml_file(temp_dir: Path) -> Path:
    """Create temporary YAML file for tests."""
    temp_file_path = temp_dir / "test_file.yaml"
    test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
    temp_file_path.write_text(yaml.dump(test_data))
    return temp_file_path


@pytest.fixture
def temp_csv_file(temp_dir: Path) -> Path:
    """Create temporary CSV file for tests."""
    temp_file_path = temp_dir / "test_file.csv"
    csv_content = "name,age,city\nJohn,30,New York\nJane,25,London\nBob,35,Paris"
    temp_file_path.write_text(csv_content)
    return temp_file_path


# ============================================================================
# FLEXT CLI SERVICE FIXTURES
# ============================================================================


@pytest.fixture
def flext_cli_api() -> FlextCli:
    """Create FlextCli instance for testing."""
    return FlextCli()


@pytest.fixture
def flext_cli_auth() -> FlextCliAuth:
    """Create FlextCliAuth instance for testing."""
    return FlextCliAuth()


@pytest.fixture
def flext_cli_cmd() -> FlextCliCmd:
    """Create FlextCliCmd instance for testing."""
    return FlextCliCmd()


@pytest.fixture
def flext_cli_commands() -> FlextCliCommands:
    """Create FlextCliCommands instance for testing."""
    return FlextCliCommands()


@pytest.fixture
def flext_cli_config() -> FlextCliConfig:
    """Create FlextCliConfig instance for testing."""
    return FlextCliConfig()


@pytest.fixture
def flext_cli_constants() -> FlextCliConstants:
    """Create FlextCliConstants instance for testing."""
    return FlextCliConstants()


@pytest.fixture
def flext_cli_containers() -> FlextCliContainers:
    """Create FlextCliContainers instance for testing."""
    return FlextCliContainers()


@pytest.fixture
def flext_cli_context() -> FlextCliContext:
    """Create FlextCliContext instance for testing."""
    return FlextCliContext()


@pytest.fixture
def flext_cli_core() -> FlextCliService:
    """Create FlextCliService instance for testing."""
    return FlextCliService()


@pytest.fixture
def flext_cli_debug() -> FlextCliDebug:
    """Create FlextCliDebug instance for testing."""
    return FlextCliDebug()


@pytest.fixture
def flext_cli_file_tools() -> FlextCliFileTools:
    """Create FlextCliFileTools instance for testing."""
    return FlextCliFileTools()


@pytest.fixture
def flext_cli_handlers() -> FlextCliHandlers:
    """Create FlextCliHandlers instance for testing."""
    return FlextCliHandlers()


@pytest.fixture
def flext_cli_mixins() -> FlextCliMixins:
    """Create FlextCliMixins instance for testing."""
    return FlextCliMixins()


@pytest.fixture
def flext_cli_models() -> FlextCliModels:
    """Create FlextCliModels instance for testing."""
    return FlextCliModels()


@pytest.fixture
def flext_cli_output() -> FlextCliOutput:
    """Create FlextCliOutput instance for testing."""
    return FlextCliOutput()


@pytest.fixture
def flext_cli_processors() -> FlextCliProcessors:
    """Create FlextCliProcessors instance for testing."""
    return FlextCliProcessors()


@pytest.fixture
def flext_cli_prompts() -> FlextCliPrompts:
    """Create FlextCliPrompts instance for testing."""
    return FlextCliPrompts()


@pytest.fixture
def flext_cli_protocols() -> FlextCliProtocols:
    """Create FlextCliProtocols instance for testing."""
    return FlextCliProtocols()


@pytest.fixture
def flext_cli_types() -> FlextCliTypes:
    """Create FlextCliTypes instance for testing."""
    return FlextCliTypes()


@pytest.fixture
def flext_cli_utilities() -> type[FlextUtilities]:
    """Provide FlextUtilities class from flext-core for testing."""
    return FlextUtilities


# ============================================================================
# TEST SUPPORT
# ============================================================================

# Note: pytest-provides automatic event_loop fixture
# No custom event_loop fixture needed


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================


@pytest.fixture
def sample_config_data() -> FlextTypes.Dict:
    """Provide sample configuration data for tests."""
    return {
        "debug": True,
        "output_format": "table",
        "no_color": False,
        "profile": "test",
        "timeout": FlextCliConstants.TIMEOUTS.DEFAULT,
        "retries": FlextCliConstants.HTTP.MAX_RETRIES,
        "api_endpoint": "https://api.example.com",
        "auth_token": "test_token_123",
    }


@pytest.fixture
def sample_file_data(temp_dir: Path) -> FlextTypes.Dict:
    """Provide sample file data for tests."""
    return {
        "content": "This is test content for file operations",
        "metadata": {
            "created": "2025-01-01T00:00:00Z",
            "modified": "2025-01-01T00:00:00Z",
            "size": 42,
            "type": "text/plain",
        },
        "path": str(temp_dir / "test_file.txt"),
    }


@pytest.fixture
def sample_command_data() -> FlextTypes.Dict:
    """Provide sample command data for tests."""
    return {
        "command": "test_command",
        "args": ["--verbose", "--output", "json"],
        "kwargs": {
            "timeout": FlextCliConstants.TIMEOUTS.DEFAULT,
            "retries": FlextCliConstants.HTTP.MAX_RETRIES,
        },
        "expected_result": {"status": "success", "data": "test_output"},
    }


@pytest.fixture
def fixture_config_file() -> Path:
    """Provide path to test configuration file from fixtures."""
    return Path("tests/fixtures/configs/test_config.json")


@pytest.fixture
def fixture_data_json() -> Path:
    """Provide path to test JSON data file from fixtures."""
    return Path("tests/fixtures/data/test_data.json")


@pytest.fixture
def fixture_data_csv() -> Path:
    """Provide path to test CSV data file from fixtures."""
    return Path("tests/fixtures/data/test_data.csv")


@pytest.fixture
def load_fixture_config() -> FlextTypes.Dict:
    """Load configuration data from fixtures directory."""
    fixture_path = Path("tests/fixtures/configs/test_config.json")
    with fixture_path.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def load_fixture_data() -> FlextTypes.Dict:
    """Load test data from fixtures directory."""
    fixture_path = Path("tests/fixtures/data/test_data.json")
    with fixture_path.open(encoding="utf-8") as f:
        return json.load(f)


# ============================================================================
# DOCKER TEST SUPPORT (CENTRALIZED FIXTURES)
# ============================================================================
#
# Docker fixtures are provided by flext_tests.fixtures.docker_fixtures:
#   - ldap_container: OpenLDAP container (port 3390)
#   - oracle_container: Oracle DB container (port 1522)
#   - algar_oud_container: ALGAR OUD container (port 3389)
#   - postgres_container: PostgreSQL container (port 5432)
#   - redis_container: Redis container (port 6379)
#
# For CLI-specific Docker testing, use FlextTestDocker directly:
#
# Example:
#   @pytest.fixture
#   def my_test_container(flext_test_docker):
#       result = flext_test_docker.start_shared_container("flext-openldap-test")
#       yield result.unwrap()
#       flext_test_docker.stop_shared_container("flext-openldap-test")
#


# ============================================================================
# UTILITY FIXTURES
# ============================================================================


@pytest.fixture
def mock_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up mock environment variables for tests."""
    monkeypatch.setenv("FLEXT_DEBUG", "true")
    monkeypatch.setenv("FLEXT_OUTPUT_FORMAT", "json")
    monkeypatch.setenv("FLEXT_NO_COLOR", "false")
    monkeypatch.setenv("FLEXT_PROFILE", "test")
    monkeypatch.setenv("FLEXT_TIMEOUT", "30")
    monkeypatch.setenv("FLEXT_RETRIES", "3")


@pytest.fixture
def clean_flext_container() -> Generator[None]:
    """Ensure clean FlextContainer state for tests."""
    # Store original state
    FlextContainer.get_global()

    # Create fresh container - use configure_global instead of set_global
    FlextContainer()
    FlextContainer.configure_global({})

    yield

    # Restore original state - reset to original configuration
    FlextContainer.configure_global({})


# ============================================================================
# TEST MARKERS AND CONFIGURATION
# ============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line("markers", "docker: marks tests that require Docker")
    config.addinivalue_line(
        "markers", "real_functionality: marks tests that test real functionality"
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Modify test collection to add markers based on test names."""
    # Use config to avoid unused argument warning
    _ = config  # Mark as used
    for item in items:
        # Add markers based on test file names
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Add markers based on test names
        # Note: pytest-auto-detects functions, no need to mark manually
        if "docker" in item.name:
            item.add_marker(pytest.mark.docker)
        if "slow" in item.name:
            item.add_marker(pytest.mark.slow)
