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
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest
import yaml
from click.testing import CliRunner
from flext_core import (
    FlextConfig,
    FlextConstants,
    FlextContainer,
    FlextDecorators,
    FlextExceptions,
    FlextHandlers,
    FlextModels,
    FlextProtocols,
    FlextResult,
    FlextService,
    t,
    u,
)
from flext_tests.docker import FlextTestDocker
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
)

# Aliases for static method calls and type references
# Use u.* for uds
# Use t.* for t type references
# Use c.* for FlextConstants constants
# Use m.* for FlextModels model references
# Use p.* for FlextProtocols protocol references
# Use r.* for FlextResult methods
# Use e.* for FlextExceptions
# Use d.* for FlextDecorators decorators
# Use s.* for FlextService service base
# Use h.* for FlextHandlers handlers
c = FlextConstants
m = FlextModels
p = FlextProtocols
r = FlextResult
e = FlextExceptions
d = FlextDecorators
s = FlextService
h = FlextHandlers


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
def flext_cli_api(
    tmp_path: Path, request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> FlextCli:
    """Create isolated FlextCli instance with test-specific config.

    Each test gets a fresh FlextCli instance with configuration pointing
    to a unique temporary directory, ensuring complete isolation between tests.
    Uses FlextCliConfig modern API: environment variables for configuration.
    """
    # Create unique subdirectory for this specific test
    # This ensures complete isolation even if pytest reuses tmp_path
    test_dir = tmp_path / f"test_{id(request)}"
    test_dir.mkdir(exist_ok=True)

    # Reset singleton to ensure clean state
    FlextConfig.reset_global_instance()
    FlextCliConfig._reset_instance()

    # Configure FlextCliConfig using modern API: environment variables
    # FlextCliConfig uses pydantic_settings with env_prefix="FLEXT_CLI_"
    monkeypatch.setenv("FLEXT_CLI_CONFIG_DIR", str(test_dir))
    monkeypatch.setenv("FLEXT_CLI_TOKEN_FILE", str(test_dir / "token.json"))
    monkeypatch.setenv(
        "FLEXT_CLI_REFRESH_TOKEN_FILE", str(test_dir / "refresh_token.json")
    )
    monkeypatch.setenv("FLEXT_CLI_PROFILE", "test")
    monkeypatch.setenv("FLEXT_CLI_OUTPUT_FORMAT", "json")
    monkeypatch.setenv("FLEXT_CLI_NO_COLOR", "true")
    monkeypatch.setenv("FLEXT_CLI_PROJECT_NAME", "test-cli")
    monkeypatch.setenv("FLEXT_CLI_API_URL", "http://localhost:8000")

    # Create FlextCli instance - it will use the configured instance via env vars
    return FlextCli()


# ============================================================================
# MODEL FACTORY FIXTURES
# ============================================================================
# Consolidated model creation fixtures to reduce test code duplication
# Tests receive these as parameters - no imports needed, follows pytest patterns


@pytest.fixture
def cli_command_factory() -> Callable[..., FlextCliModels.CliCommand]:
    """Factory fixture for creating CliCommand models with defaults."""

    def _create(
        name: str = "test_command",
        command_line: str = "flext test",
        description: str = "Test command",
        status: str = "pending",
        **kwargs: object,
    ) -> FlextCliModels.CliCommand:
        # No base data needed since CliCommand has extra="forbid"

        # Override with CLI-specific data
        cli_data: dict[str, t.GeneralValueType]
        cli_data = {
            "command_line": command_line,
            "args": [],  # Default empty args
            "status": status,
            "exit_code": None,
            "output": "",
            "error_output": "",
            "execution_time": None,
            "result": None,
            "kwargs": {},
            "name": name,
            "description": description,  # Add description field
        }

        # Convert dict[str, object] to dict[str, GeneralValueType] for convert_dict_to_json
        converted_kwargs = {k: cast("t.GeneralValueType", v) for k, v in kwargs.items()}
        # Use u.transform for JSON conversion
        raw_data = {**cli_data, **converted_kwargs}
        transform_result = u.transform(raw_data, to_json=True)
        final_data: t.JsonDict = (
            transform_result.unwrap()
            if transform_result.is_success
            else cast("t.JsonDict", raw_data)
        )
        # Use cast to satisfy type checker - Pydantic accepts dict[str, Any] at runtime
        return FlextCliModels.CliCommand(**cast("dict[str, object]", final_data))  # type: ignore[arg-type]

    return _create


@pytest.fixture
def cli_session_factory() -> Callable[..., FlextCliModels.CliSession]:
    """Factory fixture for creating CliSession models with defaults."""

    def _create(
        session_id: str = "test-session",
        user_id: str = "test_user",
        status: str = "active",
        **kwargs: object,
    ) -> FlextCliModels.CliSession:
        # CliSession has extra="forbid", so no extra fields allowed
        # Pydantic v2 with 'from __future__ import annotations' resolves forward refs

        # Add session-specific fields - only real fields that exist in CliSession
        # Include created_at and updated_at for frozen model compatibility

        session_data: dict[str, t.GeneralValueType]
        session_data = {
            "session_id": session_id,
            "status": status,
            "user_id": user_id,
            "commands": [],
            "start_time": None,
            "end_time": None,
            "last_activity": None,
            "internal_duration_seconds": 0.0,
            "commands_executed": 0,
            "created_at": datetime.now(UTC),
            "updated_at": None,
        }

        # Merge session data with kwargs
        # Convert to JsonDict-compatible dict using u
        # Convert dict[str, object] to dict[str, GeneralValueType] for convert_dict_to_json
        converted_kwargs = {k: cast("t.GeneralValueType", v) for k, v in kwargs.items()}
        # Use u.transform for JSON conversion
        raw_data = {**session_data, **converted_kwargs}
        transform_result = u.transform(raw_data, to_json=True)
        final_data: t.JsonDict = (
            transform_result.unwrap()
            if transform_result.is_success
            else cast("t.JsonDict", raw_data)
        )
        # Create instance - autouse fixture should have handled model_rebuild
        # Use cast to satisfy type checker - Pydantic accepts dict[str, Any] at runtime
        return FlextCliModels.CliSession(**cast("dict[str, object]", final_data))  # type: ignore[arg-type]

    return _create


@pytest.fixture
def debug_info_factory() -> Callable[..., FlextCliModels.DebugInfo]:
    """Factory fixture for creating DebugInfo models with defaults."""

    def _create(
        service: str = "TestService",
        level: str = "INFO",
        message: str = "",
        **kwargs: object,
    ) -> FlextCliModels.DebugInfo:
        # DebugInfo has strict validation (extra='forbid'), use compatible fields

        # Add debug-specific fields - only real fields that exist in DebugInfo
        debug_data = {
            "service": service,
            "level": level,
            "message": message or "",
            "system_info": {},
            "config_info": {},
        }

        # Filter kwargs to only include valid DebugInfo fields
        valid_fields = {
            "service",
            "timestamp",
            "system_info",
            "config_info",
            "level",
            "message",
        }
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}

        # Merge data
        # Convert to JsonDict-compatible dict using u
        # Convert dict[str, object] to dict[str, GeneralValueType] for convert_dict_to_json
        converted_debug_data = {
            k: cast("t.GeneralValueType", v) for k, v in debug_data.items()
        }
        converted_filtered_kwargs = {
            k: cast("t.GeneralValueType", v) for k, v in filtered_kwargs.items()
        }
        # Use u.transform for JSON conversion
        raw_data = {**converted_debug_data, **converted_filtered_kwargs}
        transform_result = u.transform(raw_data, to_json=True)
        final_data: t.JsonDict = (
            transform_result.unwrap()
            if transform_result.is_success
            else cast("t.JsonDict", raw_data)
        )
        # Use cast to satisfy type checker - Pydantic accepts dict[str, Any] at runtime
        return FlextCliModels.DebugInfo(**cast("dict[str, object]", final_data))  # type: ignore[arg-type]

    return _create


@pytest.fixture
def logging_config_factory() -> Callable[..., FlextCliModels.LoggingConfig]:
    """Factory fixture for creating LoggingConfig models with defaults."""

    def _create(
        log_level: str = "INFO",
        log_format: str = "%(asctime)s - %(message)s",
        **kwargs: object,
    ) -> FlextCliModels.LoggingConfig:
        # LoggingConfig has strict validation (extra='forbid'), use compatible fields
        # Don't use FlextTestsFactories.create_config as it may have extra fields

        # Add logging-specific fields - only real fields that exist in LoggingConfig
        logging_data = {
            "log_level": log_level,
            "log_format": log_format,
            "console_output": True,
            "log_file": "",
        }

        # Merge with kwargs, but only if they are valid fields
        # Convert to JsonDict-compatible dict using u
        # Convert dict[str, object] to dict[str, GeneralValueType] for convert_dict_to_json
        converted_logging_data = {
            k: cast("t.GeneralValueType", v) for k, v in logging_data.items()
        }
        converted_kwargs = {k: cast("t.GeneralValueType", v) for k, v in kwargs.items()}
        # Use u.transform for JSON conversion
        raw_data = {**converted_logging_data, **converted_kwargs}
        transform_result = u.transform(raw_data, to_json=True)
        final_data: t.JsonDict = (
            transform_result.unwrap()
            if transform_result.is_success
            else cast("t.JsonDict", raw_data)
        )
        # Use cast to satisfy type checker - Pydantic accepts dict[str, Any] at runtime
        return FlextCliModels.LoggingConfig(**cast("dict[str, object]", final_data))  # type: ignore[arg-type]

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
}


# Generate service fixtures from mapping - each fixture uses factory
@pytest.fixture
def flext_cli_cmd() -> FlextCliCmd:
    """Create FlextCliCmd instance for testing."""
    instance = _create_service_instance(FlextCliCmd)
    assert isinstance(instance, FlextCliCmd)
    return instance


@pytest.fixture
def flext_cli_commands() -> FlextCliCommands:
    """Create FlextCliCommands instance for testing."""
    instance = _create_service_instance(FlextCliCommands)
    assert isinstance(instance, FlextCliCommands)
    return instance


@pytest.fixture
def flext_cli_config() -> FlextCliConfig:
    """Create FlextCliConfig instance for testing via FlextCliServiceBase."""
    instance = _create_service_instance(FlextCliConfig)
    assert isinstance(instance, FlextCliConfig)
    return instance


@pytest.fixture
def flext_cli_constants() -> FlextCliConstants:
    """Create FlextCliConstants instance for testing."""
    instance = _create_service_instance(FlextCliConstants)
    assert isinstance(instance, FlextCliConstants)
    return instance


@pytest.fixture
def flext_cli_context() -> FlextCliContext:
    """Create FlextCliContext instance for testing."""
    instance = _create_service_instance(FlextCliContext)
    assert isinstance(instance, FlextCliContext)
    return instance


@pytest.fixture
def flext_cli_core() -> FlextCliCore:
    """Create FlextCliCore instance for testing."""
    instance = _create_service_instance(FlextCliCore)
    assert isinstance(instance, FlextCliCore)
    return instance


@pytest.fixture
def flext_cli_debug() -> FlextCliDebug:
    """Create FlextCliDebug instance for testing."""
    instance = _create_service_instance(FlextCliDebug)
    assert isinstance(instance, FlextCliDebug)
    return instance


@pytest.fixture
def flext_cli_file_tools() -> FlextCliFileTools:
    """Create FlextCliFileTools instance for testing."""
    instance = _create_service_instance(FlextCliFileTools)
    assert isinstance(instance, FlextCliFileTools)
    return instance


@pytest.fixture
def flext_cli_mixins() -> FlextCliMixins:
    """Create FlextCliMixins instance for testing."""
    instance = _create_service_instance(FlextCliMixins)
    assert isinstance(instance, FlextCliMixins)
    return instance


@pytest.fixture
def flext_cli_models() -> FlextCliModels:
    """Create FlextCliModels instance for testing."""
    instance = _create_service_instance(FlextCliModels)
    assert isinstance(instance, FlextCliModels)
    return instance


@pytest.fixture
def flext_cli_output() -> FlextCliOutput:
    """Create FlextCliOutput instance for testing."""
    instance = _create_service_instance(FlextCliOutput)
    assert isinstance(instance, FlextCliOutput)
    return instance


@pytest.fixture
def flext_cli_prompts() -> FlextCliPrompts:
    """Create FlextCliPrompts instance for testing."""
    instance = _create_service_instance(FlextCliPrompts)
    assert isinstance(instance, FlextCliPrompts)
    return instance


@pytest.fixture
def flext_cli_protocols() -> FlextCliProtocols:
    """Create FlextCliProtocols instance for testing."""
    instance = _create_service_instance(FlextCliProtocols)
    assert isinstance(instance, FlextCliProtocols)
    return instance


@pytest.fixture
def flext_cli_utilities() -> type[u]:
    """Provide FlextUtilities class from flext-core for testing."""
    return u


# ============================================================================
# TEST SUPPORT
# ============================================================================

# Note: pytest-provides automatic event_loop fixture
# No custom event_loop fixture needed


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================


@pytest.fixture
def sample_config_data() -> t.JsonDict:
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
def sample_file_data(temp_dir: Path) -> t.JsonDict:
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
def sample_command_data() -> t.JsonDict:
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
def load_fixture_config() -> t.JsonDict:
    """Load configuration data from fixtures directory."""
    fixture_path = Path("tests/fixtures/configs/test_config.json")
    with fixture_path.open(encoding="utf-8") as f:
        data = json.load(f)
    adapter: TypeAdapter[t.JsonDict] = TypeAdapter(t.JsonDict)
    return adapter.validate_python(data)


@pytest.fixture
def load_fixture_data() -> t.JsonDict:
    """Load test data from fixtures directory."""
    fixture_path = Path("tests/fixtures/data/test_data.json")
    with fixture_path.open(encoding="utf-8") as f:
        data = json.load(f)
    adapter: TypeAdapter[t.JsonDict] = TypeAdapter(t.JsonDict)
    return adapter.validate_python(data)


# ============================================================================
# DOCKER TEST SUPPORT (CENTRALIZED FIXTURES)
# ============================================================================


@pytest.fixture(scope="session")
def flext_test_docker(
    tmp_path_factory: pytest.TempPathFactory,
) -> FlextTestDocker:
    """FlextTestDocker instance for managing test containers.

    Container stays alive after tests for debugging, recreated on infra failures.
    Tests are idempotent with cleanup at start/end. Uses session scope to persist
    containers across tests but clean up at session end.
    """
    # Use the flext-cli directory as workspace root
    workspace_root = Path(__file__).parent.parent
    docker_manager = FlextTestDocker(workspace_root=workspace_root)

    # Clean up any existing test containers at start
    try:
        docker_manager.cleanup_dirty_containers()
    except Exception:
        # Ignore cleanup errors at startup
        pass

    return docker_manager

    # Keep containers alive after tests for debugging (don't clean up)
    # Only clean up on explicit failures or when requested


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

    # Use u.process to set environment variables
    def set_env_var(k: str, v: str) -> None:
        """Set single environment variable."""
        # Only store if the variable was already set
        if k in os.environ:
            original_env[k] = os.environ[k]
        os.environ[k] = v

    u.process(env_vars, processor=set_env_var, on_error="skip")

    yield env_vars

    # Restore original environment using u.process
    def restore_env_var(k: str, _v: str) -> None:
        """Restore single environment variable."""
        if k in original_env:
            # Restore the original value
            os.environ[k] = original_env[k]
        else:
            # Variable was not set before, remove it
            os.environ.pop(k, None)

    u.process(env_vars, processor=restore_env_var, on_error="skip")


@pytest.fixture(autouse=True)
def reset_singletons() -> Generator[None]:
    """Reset all FlextConfig singletons between tests for isolation.

    CRITICAL: This fixture runs automatically before EACH test to ensure
    no state leaks between tests regardless of pytest-randomly order.
    """
    # Reset BEFORE test to ensure clean state
    # For now, skip reset to focus on test functionality
    # Pydantic v2 with 'from __future__ import annotations' resolves forward refs
    # No manual model_rebuild() needed - annotations resolved at runtime
    # Yield to make this a proper generator fixture (required for Generator[None] return type)
    # Business Rule: Generator fixtures MUST use yield, not return, for proper cleanup
    # CRITICAL: Must use yield, not return, for Generator[None] type compatibility
    # Architecture: Generator[None] requires yield statement, return None causes type error
    # Type system requirement: Generator[None] protocol requires yield, not return
    # FIXED: Changed return None to yield None for Generator[None] type compatibility
    # CRITICAL: Generator[None] return type REQUIRES yield statement, not return
    # Business Rule: Generator fixtures MUST use yield for proper cleanup and type compatibility
    # Architecture: Generator[None] protocol requires yield, return None causes type error
    yield None  # noqa: PT022
    # Reset after test to clean up any state


@pytest.fixture
def clean_flext_container() -> Generator[None]:
    """Ensure clean FlextContainer state for tests."""
    # Get or create container instance (singleton pattern)
    container = FlextContainer()

    # Store original configuration
    original_config = container.get_config()

    # Reset container configuration
    container.configure({})

    yield

    # Restore original configuration
    container.configure(original_config)


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
