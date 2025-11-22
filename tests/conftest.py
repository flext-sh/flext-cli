"""FLEXT CLI Test Configuration - Comprehensive Test Infrastructure.

Centralized test configuration using flext_tests library with real functionality
testing, Docker support, and comprehensive fixtures following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Callable, Generator
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner
from flext_core import FlextContainer, FlextUtilities
from flext_tests import FlextTestDocker, FlextTestsFactories
from pydantic import TypeAdapter

from flext_cli import (
    FlextCli,
    FlextCliCmd,
    FlextCliCommands,
    FlextCliConfig,
    FlextCliConstants,
    FlextCliContext,
    FlextCliCore,
    FlextCliDebug,
    FlextCliFileTools,
    FlextCliMixins,
    FlextCliModels,
    FlextCliOutput,
    FlextCliPrompts,
    FlextCliProtocols,
    FlextCliServiceBase,
    FlextCliTypes,
)


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create Click CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


# Factory for creating temporary files with different formats
def _create_temp_file(
    temp_dir: Path,
    filename: str,
    content: str,
) -> Path:
    """Factory helper for creating temporary files with custom content.

    Args:
        temp_dir: Temporary directory path
        filename: Target filename with extension
        content: File content as string

    Returns:
        Path to created file

    """
    file_path = temp_dir / filename
    file_path.write_text(content)
    return file_path


@pytest.fixture
def temp_file(temp_dir: Path) -> Path:
    """Create temporary text file for tests."""
    return _create_temp_file(temp_dir, "test_file.txt", "test content")


@pytest.fixture
def temp_json_file(temp_dir: Path) -> Path:
    """Create temporary JSON file for tests."""
    test_data: dict[str, str | int | list[int]] = {
        "key": "value",
        "number": 42,
        "list": [1, 2, 3],
    }
    return _create_temp_file(temp_dir, "test_file.json", json.dumps(test_data))


@pytest.fixture
def temp_yaml_file(temp_dir: Path) -> Path:
    """Create temporary YAML file for tests."""
    test_data: dict[str, str | int | list[int]] = {
        "key": "value",
        "number": 42,
        "list": [1, 2, 3],
    }
    return _create_temp_file(temp_dir, "test_file.yaml", yaml.dump(test_data))


@pytest.fixture
def temp_csv_file(temp_dir: Path) -> Path:
    """Create temporary CSV file for tests."""
    csv_content = "name,age,city\nJohn,30,New York\nJane,25,London\nBob,35,Paris"
    return _create_temp_file(temp_dir, "test_file.csv", csv_content)


# ============================================================================
# FLEXT CLI SERVICE FIXTURES
# ============================================================================


@pytest.fixture
def flext_cli_api(tmp_path: Path, request: pytest.FixtureRequest) -> FlextCli:
    """Create isolated FlextCli instance with test-specific config.

    Each test gets a fresh FlextCli instance with configuration pointing
    to a unique temporary directory, ensuring complete isolation between tests.
    Uses real configuration with test paths, no monkeypatch.
    """
    # Create unique subdirectory for this specific test
    # This ensures complete isolation even if pytest reuses tmp_path
    test_dir = tmp_path / f"test_{id(request)}"
    test_dir.mkdir(exist_ok=True)

    # Reset singleton to ensure clean state
    FlextCliConfig._reset_instance()

    # Create config with test paths using real API
    # The config will be used by FlextCli when it's created
    FlextCliConfig(
        config_dir=test_dir,
        token_file=test_dir / "token.json",
        refresh_token_file=test_dir / "refresh_token.json",
    )

    # Create FlextCli instance - it will use the configured instance
    return FlextCli()


# ============================================================================
# MODEL FACTORY FIXTURES
# ============================================================================
# Consolidated model creation fixtures to reduce test code duplication
# Tests receive these as parameters - no imports needed, follows pytest patterns


@pytest.fixture
def cli_command_factory() -> Callable[..., FlextCliModels.CliCommand]:
    """Factory fixture for creating CliCommand models with defaults using FlextTestsFactories."""

    def _create(
        name: str = "test_command",
        command_line: str = "flext test",
        description: str = "Test command",
        status: str = "pending",
        **kwargs: object,
    ) -> FlextCliModels.CliCommand:
        # Use FlextTestsFactories for generating base data, then merge with CLI-specific fields
        base_data = FlextTestsFactories.create_service(
            service_type="cli_command",
            service_id=name,
        )

        # Override with CLI-specific data
        cli_data = {
            "command_line": command_line,
            "args": [],  # Default empty args
            "status": status,
            "exit_code": None,
            "output": "",
            "error_output": "",
            "execution_time": None,
            "working_directory": None,
            "environment": {},
            "metadata": {},
        }

        # Merge base data with CLI data and kwargs
        final_data = {**base_data, **cli_data, **kwargs}
        return FlextCliModels.CliCommand(**final_data)  # type: ignore[arg-type]

    return _create


@pytest.fixture
def cli_session_factory() -> Callable[..., FlextCliModels.CliSession]:
    """Factory fixture for creating CliSession models with defaults using FlextTestsFactories."""

    def _create(
        session_id: str = "test-session",
        user_id: str = "test_user",
        status: str = "active",
        **kwargs: object,
    ) -> FlextCliModels.CliSession:
        # Use FlextTestsFactories for user data as base
        base_data = FlextTestsFactories.create_user(
            user_id=user_id,
            name=f"Session {session_id}",
        )

        # Add session-specific fields
        session_data = {
            "session_id": session_id,
            "status": status,
            "commands": [],
            "start_time": None,
            "end_time": None,
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0,
        }

        # Merge all data
        final_data = {**base_data, **session_data, **kwargs}
        return FlextCliModels.CliSession(**final_data)  # type: ignore[arg-type]

    return _create


@pytest.fixture
def debug_info_factory() -> Callable[..., FlextCliModels.DebugInfo]:
    """Factory fixture for creating DebugInfo models with defaults using FlextTestsFactories."""

    def _create(
        service: str = "TestService",
        status: str = "operational",
        level: str = "INFO",
        message: str = "Test message",
        **kwargs: object,
    ) -> FlextCliModels.DebugInfo:
        # Use FlextTestsFactories for config data as base
        base_data = FlextTestsFactories.create_config(
            service_type="debug",
            environment="test",
            debug=True,
            log_level=level,
        )

        # Add debug-specific fields
        debug_data = {
            "service": service,
            "status": status,
            "level": level,
            "message": message,
            "timestamp": None,
            "context": {},
            "stack_trace": None,
            "metadata": {},
        }

        # Merge all data
        final_data = {**base_data, **debug_data, **kwargs}
        return FlextCliModels.DebugInfo(**final_data)  # type: ignore[arg-type]

    return _create


@pytest.fixture
def logging_config_factory() -> Callable[..., FlextCliModels.LoggingConfig]:
    """Factory fixture for creating LoggingConfig models with defaults using FlextTestsFactories."""

    def _create(
        log_level: str = "INFO",
        log_format: str = "%(asctime)s - %(message)s",
        **kwargs: object,
    ) -> FlextCliModels.LoggingConfig:
        # Use FlextTestsFactories for config data as base
        base_data = FlextTestsFactories.create_config(
            service_type="logging",
            environment="test",
            log_level=log_level,
        )

        # Add logging-specific fields
        logging_data = {
            "log_level": log_level,
            "log_format": log_format,
            "handlers": [],
            "file_path": None,
            "max_file_size": None,
            "backup_count": None,
        }

        # Merge all data
        final_data = {**base_data, **logging_data, **kwargs}
        return FlextCliModels.LoggingConfig(**final_data)  # type: ignore[arg-type]

    return _create


# ============================================================================
# SERVICE FIXTURE FACTORY
# ============================================================================
# Consolidated service fixtures using factory pattern to reduce code duplication


def _create_service_instance(service_class: type) -> object:
    """Factory helper for creating service instances.

    Args:
        service_class: The service class to instantiate

    Returns:
        New instance of the service class

    """
    # Special handling for FlextCliConfig singleton
    if service_class is FlextCliConfig:
        return FlextCliServiceBase.get_cli_config()

    return service_class()


# Mapping of service names to classes - consolidates 14 services
_SERVICE_CLASSES: dict[str, type] = {
    "cmd": FlextCliCmd,
    "commands": FlextCliCommands,
    "config": FlextCliConfig,
    "constants": FlextCliConstants,
    "context": FlextCliContext,
    "core": FlextCliCore,
    "debug": FlextCliDebug,
    "file_tools": FlextCliFileTools,
    "mixins": FlextCliMixins,
    "models": FlextCliModels,
    "output": FlextCliOutput,
    "prompts": FlextCliPrompts,
    "protocols": FlextCliProtocols,
    "types": FlextCliTypes,
}


# Generate service fixtures from mapping - each fixture uses factory
@pytest.fixture
def flext_cli_cmd() -> FlextCliCmd:
    """Create FlextCliCmd instance for testing."""
    return _create_service_instance(FlextCliCmd)  # type: ignore[return-value]


@pytest.fixture
def flext_cli_commands() -> FlextCliCommands:
    """Create FlextCliCommands instance for testing."""
    return _create_service_instance(FlextCliCommands)  # type: ignore[return-value]


@pytest.fixture
def flext_cli_config() -> FlextCliConfig:
    """Create FlextCliConfig instance for testing via FlextCliServiceBase."""
    return _create_service_instance(FlextCliConfig)  # type: ignore[return-value]


@pytest.fixture
def flext_cli_constants() -> FlextCliConstants:
    """Create FlextCliConstants instance for testing."""
    return _create_service_instance(FlextCliConstants)  # type: ignore[return-value]


@pytest.fixture
def flext_cli_context() -> FlextCliContext:
    """Create FlextCliContext instance for testing."""
    return _create_service_instance(FlextCliContext)  # type: ignore[return-value]


@pytest.fixture
def flext_cli_core() -> FlextCliCore:
    """Create FlextCliCore instance for testing."""
    return _create_service_instance(FlextCliCore)  # type: ignore[return-value]


@pytest.fixture
def flext_cli_debug() -> FlextCliDebug:
    """Create FlextCliDebug instance for testing."""
    return _create_service_instance(FlextCliDebug)  # type: ignore[return-value]


@pytest.fixture
def flext_cli_file_tools() -> FlextCliFileTools:
    """Create FlextCliFileTools instance for testing."""
    return _create_service_instance(FlextCliFileTools)  # type: ignore[return-value]


@pytest.fixture
def flext_cli_mixins() -> FlextCliMixins:
    """Create FlextCliMixins instance for testing."""
    return _create_service_instance(FlextCliMixins)  # type: ignore[return-value]


@pytest.fixture
def flext_cli_models() -> FlextCliModels:
    """Create FlextCliModels instance for testing."""
    return _create_service_instance(FlextCliModels)  # type: ignore[return-value]


@pytest.fixture
def flext_cli_output() -> FlextCliOutput:
    """Create FlextCliOutput instance for testing."""
    return _create_service_instance(FlextCliOutput)  # type: ignore[return-value]


@pytest.fixture
def flext_cli_prompts() -> FlextCliPrompts:
    """Create FlextCliPrompts instance for testing."""
    return _create_service_instance(FlextCliPrompts)  # type: ignore[return-value]


@pytest.fixture
def flext_cli_protocols() -> FlextCliProtocols:
    """Create FlextCliProtocols instance for testing."""
    return _create_service_instance(FlextCliProtocols)  # type: ignore[return-value]


@pytest.fixture
def flext_cli_types() -> FlextCliTypes:
    """Create FlextCliTypes instance for testing."""
    return _create_service_instance(FlextCliTypes)  # type: ignore[return-value]


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
def sample_config_data() -> FlextCliTypes.Data.CliDataDict:
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
def sample_file_data(temp_dir: Path) -> FlextCliTypes.Data.CliDataDict:
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
def sample_command_data() -> FlextCliTypes.Data.CliDataDict:
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
def load_fixture_config() -> FlextCliTypes.Data.CliDataDict:
    """Load configuration data from fixtures directory."""
    fixture_path = Path("tests/fixtures/configs/test_config.json")
    with fixture_path.open(encoding="utf-8") as f:
        data = json.load(f)
    adapter: TypeAdapter[FlextCliTypes.Data.CliDataDict] = TypeAdapter(
        FlextCliTypes.Data.CliDataDict
    )
    return adapter.validate_python(data)


@pytest.fixture
def load_fixture_data() -> FlextCliTypes.Data.CliDataDict:
    """Load test data from fixtures directory."""
    fixture_path = Path("tests/fixtures/data/test_data.json")
    with fixture_path.open(encoding="utf-8") as f:
        data = json.load(f)
    adapter: TypeAdapter[FlextCliTypes.Data.CliDataDict] = TypeAdapter(
        FlextCliTypes.Data.CliDataDict
    )
    return adapter.validate_python(data)


# ============================================================================
# DOCKER TEST SUPPORT (CENTRALIZED FIXTURES)
# ============================================================================

@pytest.fixture(scope="session")
def flext_test_docker(tmp_path_factory: pytest.TempPathFactory) -> FlextTestDocker:
    """FlextTestDocker instance for managing test containers.

    Container stays alive after tests for debugging, only recreated on real infra failures.
    Tests are idempotent with cleanup at start/end. Uses session scope to persist
    containers across tests but clean up at session end.
    """
    # Use the flext-cli directory as workspace root
    workspace_root = Path(__file__).parent.parent
    docker_manager = FlextTestDocker(workspace_root=workspace_root)

    # Clean up any existing test containers at start
    try:
        docker_manager.cleanup_test_containers()
    except Exception:
        # Ignore cleanup errors at startup
        pass

    yield docker_manager

    # Keep containers alive after tests for debugging (don't clean up)
    # Only clean up on explicit failures or when requested
    pass


# ============================================================================
# UTILITY FIXTURES
# ============================================================================


@pytest.fixture
def mock_env_vars(tmp_path: Path) -> Generator[dict[str, str]]:
    """Set up environment variables for tests using real .env file."""
    # Create .env file with test environment variables
    env_file = tmp_path / ".env"
    env_content = """FLEXT_CLI_DEBUG=true
FLEXT_CLI_OUTPUT_FORMAT=json
FLEXT_CLI_NO_COLOR=false
FLEXT_CLI_PROFILE=test
FLEXT_CLI_TIMEOUT=30
FLEXT_CLI_RETRIES=3
"""
    env_file.write_text(env_content)

    # Store which env vars were originally set (only track existing ones)
    original_env: dict[str, str] = {}
    env_vars = {
        "FLEXT_CLI_DEBUG": "true",
        "FLEXT_CLI_OUTPUT_FORMAT": "json",
        "FLEXT_CLI_NO_COLOR": "false",
        "FLEXT_CLI_PROFILE": "test",
        "FLEXT_CLI_TIMEOUT": "30",
        "FLEXT_CLI_RETRIES": "3",
    }

    for key, value in env_vars.items():
        # Only store if the variable was already set
        if key in os.environ:
            original_env[key] = os.environ[key]
        os.environ[key] = value

    yield env_vars

    # Restore original environment
    for key in env_vars:
        if key in original_env:
            # Restore the original value
            os.environ[key] = original_env[key]
        else:
            # Variable was not set before, remove it
            os.environ.pop(key, None)


@pytest.fixture(autouse=True)
def reset_singletons() -> Generator[None]:
    """Reset all FlextConfig singletons between tests for isolation.

    CRITICAL: This fixture runs automatically before EACH test to ensure
    no state leaks between tests regardless of pytest-randomly order.
    """
    # Reset BEFORE test to ensure clean state
    FlextCliConfig._reset_instance()
    yield
    # Reset after test to clean up any state
    FlextCliConfig._reset_instance()


@pytest.fixture
def clean_flext_container() -> Generator[None]:
    """Ensure clean FlextContainer state for tests."""
    # Store original state
    FlextContainer.get_global()

    # Create fresh container - use configure_container instead of set_global
    FlextContainer()
    container = FlextContainer()
    container.configure_container({})

    yield

    # Restore original state - reset to original configuration
    container.configure_container({})


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
        "markers",
        "real_functionality: marks tests that test real functionality",
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
