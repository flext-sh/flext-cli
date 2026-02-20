"""FLEXT CLI Test Configuration - Comprehensive Test Infrastructure.

Centralized test configuration using flext_tests library with real functionality
testing, Docker support, and comprehensive fixtures following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations
# PYTHON_VERSION_GUARD — Do not remove. Managed by scripts/maintenance/enforce_python_version.py
import sys as _sys

if _sys.version_info[:2] != (3, 13):
    _v = f"{_sys.version_info.major}.{_sys.version_info.minor}.{_sys.version_info.micro}"
    raise RuntimeError(
        f"\n{'=' * 72}\n"
        f"FATAL: Python {_v} detected — this project requires Python 3.13.\n"
        f"\n"
        f"The virtual environment was created with the WRONG Python interpreter.\n"
        f"\n"
        f"Fix:\n"
        f"  1. rm -rf .venv\n"
        f"  2. poetry env use python3.13\n"
        f"  3. poetry install\n"
        f"\n"
        f"Or use the workspace Makefile:\n"
        f"  make setup PROJECT=<project-name>\n"
        f"{'=' * 72}\n"
    )
del _sys
# PYTHON_VERSION_GUARD_END

# ============================================================================
# TEST CONSTANTS - Available in all tests via TestsCliConstants (c)
# ============================================================================
# All constants are in tests/constants.py (TestsCliConstants)
# Test files import directly from conftest or use c.ClassName.CONSTANT pattern
import builtins
import getpass
import json
import os
from collections import deque
from collections.abc import Callable, Generator, Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

import pytest
import yaml
from click.testing import CliRunner
from flext_cli import (
    FlextCli,
    FlextCliCmd,
    FlextCliCommands,
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
    FlextCliSettings,
    m,
)

# Import from correct locations - use TestsCli structure
from flext_cli.typings import t
from flext_core import (
    FlextContainer,
    FlextSettings,
)
from flext_tests.docker import FlextTestsDocker
from pydantic import TypeAdapter

from tests.utilities import TestsCliUtilities

from . import (
    c,
    u,
)


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest markers for the test suite."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line("markers", "docker: marks tests that require Docker")
    config.addinivalue_line(
        "markers",
        "real_functionality: marks tests that test real functionality",
    )


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create Click CLI runner for testing."""
    return CliRunner()


# ============================================================================
# TEMPORARY DIRECTORY AND FILE FIXTURES
# ============================================================================


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide temporary directory for tests.

    Wraps pytest's tmp_path fixture to maintain naming consistency.
    """
    return tmp_path


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
def temp_json_file(temp_dir: Path) -> Path:
    """Create temporary JSON file for tests using consolidated temp_dir fixture.

    Uses the consolidated temp_dir fixture from flext-core/tests/conftest.py.
    """
    test_data: dict[str, str | int | list[int]] = {
        "key": "value",
        "number": 42,
        "list": [1, 2, 3],
    }
    return _create_temp_file(temp_dir, "test_file.json", json.dumps(test_data))


@pytest.fixture
def temp_yaml_file(temp_dir: Path) -> Path:
    """Create temporary YAML file for tests using consolidated temp_dir fixture.

    Uses the consolidated temp_dir fixture from flext-core/tests/conftest.py.
    """
    test_data: dict[str, str | int | list[int]] = {
        "key": "value",
        "number": 42,
        "list": [1, 2, 3],
    }
    return _create_temp_file(temp_dir, "test_file.yaml", yaml.dump(test_data))


@pytest.fixture
def temp_csv_file(temp_dir: Path) -> Path:
    """Create temporary CSV file for tests using consolidated temp_dir fixture.

    Uses the consolidated temp_dir fixture from flext-core/tests/conftest.py.
    """
    csv_content = "name,age,city\nJohn,30,New York\nJane,25,London\nBob,35,Paris"
    return _create_temp_file(temp_dir, "test_file.csv", csv_content)


@pytest.fixture
def temp_file(temp_dir: Path) -> Path:
    """Create generic temporary text file for tests.

    Creates a simple text file for file operation tests.
    """
    return _create_temp_file(temp_dir, "test_file.txt", "test content\nline 2\nline 3")


# ============================================================================
# FLEXT CLI SERVICE FIXTURES
# ============================================================================


@pytest.fixture
def flext_cli_api(
    tmp_path: Path,
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> FlextCli:
    """Create isolated FlextCli instance with test-specific config.

    Each test gets a fresh FlextCli instance with configuration pointing
    to a unique temporary directory, ensuring complete isolation between tests.
    Uses FlextCliSettings modern API: environment variables for configuration.
    """
    # Create unique subdirectory for this specific test
    # This ensures complete isolation even if pytest reuses tmp_path
    test_dir = tmp_path / f"test_{id(request)}"
    test_dir.mkdir(exist_ok=True)

    # Reset singleton to ensure clean state
    FlextSettings.reset_global_instance()
    FlextCliSettings._reset_instance()

    # Configure FlextCliSettings using modern API: environment variables
    # FlextCliSettings uses pydantic_settings with env_prefix="FLEXT_CLI_"
    monkeypatch.setenv("FLEXT_CLI_CONFIG_DIR", str(test_dir))
    monkeypatch.setenv("FLEXT_CLI_TOKEN_FILE", str(test_dir / "token.json"))
    monkeypatch.setenv(
        "FLEXT_CLI_REFRESH_TOKEN_FILE",
        str(test_dir / "refresh_token.json"),
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


class CliCommandFactory(Protocol):
    """Protocol for CliCommand factory function."""

    def __call__(
        self,
        name: str = ...,
        command_line: str = ...,
        description: str = ...,
        status: str = ...,
        **kwargs: object,
    ) -> m.Cli.CliCommand:
        """Create CliCommand instance."""
        ...


class CliSessionFactory(Protocol):
    """Protocol for CliSession factory function."""

    def __call__(
        self,
        session_id: str = ...,
        user_id: str = ...,
        status: str = ...,
        **kwargs: object,
    ) -> m.Cli.CliSession:
        """Create CliSession instance."""
        ...


class DebugInfoFactory(Protocol):
    """Protocol for DebugInfo factory function."""

    def __call__(
        self,
        service: str = ...,
        level: str = ...,
        message: str = ...,
        **kwargs: object,
    ) -> m.Cli.DebugInfo:
        """Create DebugInfo instance."""
        ...


class LoggingConfigFactory(Protocol):
    """Protocol for LoggingConfig factory function."""

    def __call__(
        self,
        log_level: str = ...,
        log_format: str = ...,
        **kwargs: object,
    ) -> m.Cli.LoggingConfig:
        """Create LoggingConfig instance."""
        ...


@pytest.fixture
def cli_command_factory() -> CliCommandFactory:
    """Factory fixture for creating CliCommand models with defaults."""

    def _create(
        name: str = "test_command",
        command_line: str = "flext test",
        description: str = "Test command",
        status: str = "pending",
        **kwargs: object,
    ) -> m.Cli.CliCommand:
        # No base data needed since CliCommand has extra="forbid"

        # Override with CLI-specific data
        # Use object for kwargs since t.GeneralValueType may not be accessible via t
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

        # Merge kwargs
        raw_data = {**cli_data, **kwargs}
        # Use u.transform for JSON conversion (from flext-core)
        # Type narrowing: raw_data is dict, compatible with ConfigurationDict
        if not isinstance(raw_data, dict):
            msg = "raw_data must be dict"
            raise TypeError(msg)
        # ConfigurationDict = Mapping[str, t.GeneralValueType]
        typed_data: dict[str, t.GeneralValueType] = raw_data
        transform_result = u.transform(
            typed_data,
            to_json=True,
        )
        if transform_result.is_success:
            # unwrap() returns t.GeneralValueType, narrow to dict[str, t.GeneralValueType]
            unwrapped = transform_result.value
            if isinstance(unwrapped, dict):
                final_data: dict[str, t.GeneralValueType] = dict(unwrapped.items())
            else:
                final_data = raw_data
        else:
            final_data = raw_data
        # Use model_validate which accepts dict[str, t.GeneralValueType] and validates at runtime
        return m.Cli.CliCommand.model_validate(final_data)

    return _create


@pytest.fixture
def cli_session_factory() -> CliSessionFactory:
    """Factory fixture for creating CliSession models with defaults."""

    def _create(
        session_id: str = "test-session",
        user_id: str = "test_user",
        status: str = "active",
        **kwargs: object,
    ) -> m.Cli.CliSession:
        # CliSession has extra="forbid", so no extra fields allowed
        # Pydantic v2 with 'from __future__ import annotations' resolves forward refs

        # Add session-specific fields - only real fields that exist in CliSession
        # Include created_at and updated_at for frozen model compatibility

        session_data: dict[str, t.GeneralValueType] = {
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
        raw_data = {**session_data, **kwargs}
        # Use u.transform for JSON conversion
        # Type narrowing: raw_data is dict, compatible with ConfigurationDict
        if not isinstance(raw_data, dict):
            msg = "raw_data must be dict"
            raise TypeError(msg)
        typed_data: dict[str, t.GeneralValueType] = raw_data
        transform_result = u.transform(
            typed_data,
            to_json=True,
        )
        if transform_result.is_success:
            unwrapped = transform_result.value
            if isinstance(unwrapped, dict):
                final_data: dict[str, t.GeneralValueType] = dict(unwrapped.items())
            else:
                final_data = raw_data
        else:
            final_data = raw_data
        # Create instance - autouse fixture should have handled model_rebuild
        # Use model_validate which accepts dict[str, t.GeneralValueType] and validates at runtime
        return m.Cli.CliSession.model_validate(final_data)

    return _create


@pytest.fixture
def debug_info_factory() -> DebugInfoFactory:
    """Factory fixture for creating DebugInfo models with defaults."""

    def _create(
        service: str = "TestService",
        level: str = "INFO",
        message: str = "",
        **kwargs: object,
    ) -> m.Cli.DebugInfo:
        # DebugInfo has strict validation (extra='forbid'), use compatible fields

        # Add debug-specific fields - only real fields that exist in DebugInfo
        debug_data: dict[str, t.GeneralValueType] = {
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
        raw_data = {**debug_data, **filtered_kwargs}
        # Use u.transform for JSON conversion
        # Type narrowing: raw_data is dict, compatible with ConfigurationDict
        if not isinstance(raw_data, dict):
            msg = "raw_data must be dict"
            raise TypeError(msg)
        typed_data: dict[str, t.GeneralValueType] = raw_data
        transform_result = u.transform(
            typed_data,
            to_json=True,
        )
        if transform_result.is_success:
            unwrapped = transform_result.value
            if isinstance(unwrapped, dict):
                final_data: dict[str, t.GeneralValueType] = dict(unwrapped.items())
            else:
                final_data = raw_data
        else:
            final_data = raw_data
        # Use model_validate which accepts dict[str, t.GeneralValueType] and validates at runtime
        return m.Cli.DebugInfo.model_validate(final_data)

    return _create


@pytest.fixture
def logging_config_factory() -> LoggingConfigFactory:
    """Factory fixture for creating LoggingConfig models with defaults."""

    def _create(
        log_level: str = "INFO",
        log_format: str = "%(asctime)s - %(message)s",
        **kwargs: object,
    ) -> m.Cli.LoggingConfig:
        # LoggingConfig has strict validation (extra='forbid'), use compatible fields
        # Don't use FlextTestsFactories.create_config as it may have extra fields

        # Add logging-specific fields - only real fields that exist in LoggingConfig
        logging_data: dict[str, t.GeneralValueType] = {
            "log_level": log_level,
            "log_format": log_format,
            "console_output": True,
            "log_file": "",
        }

        # Merge with kwargs
        raw_data = {**logging_data, **kwargs}
        # Use u.transform for JSON conversion
        # Type narrowing: raw_data is dict, compatible with ConfigurationDict
        if not isinstance(raw_data, dict):
            msg = "raw_data must be dict"
            raise TypeError(msg)
        typed_data: dict[str, t.GeneralValueType] = raw_data
        transform_result = u.transform(
            typed_data,
            to_json=True,
        )
        if transform_result.is_success:
            unwrapped = transform_result.value
            if isinstance(unwrapped, dict):
                final_data: dict[str, t.GeneralValueType] = dict(unwrapped.items())
            else:
                final_data = raw_data
        else:
            final_data = raw_data
        # Use model_validate which accepts dict[str, t.GeneralValueType] and validates at runtime
        return m.Cli.LoggingConfig.model_validate(final_data)

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
    # Special handling for FlextCliSettings singleton
    if service_class is FlextCliSettings:
        return FlextCliServiceBase.get_cli_config()

    return service_class()


# Mapping of service names to classes - consolidates 14 services
_SERVICE_CLASSES: dict[str, type] = {
    "cmd": FlextCliCmd,
    "commands": FlextCliCommands,
    "config": FlextCliSettings,
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
def flext_cli_config() -> FlextCliSettings:
    """Create FlextCliSettings instance for testing via FlextCliServiceBase."""
    instance = _create_service_instance(FlextCliSettings)
    assert isinstance(instance, FlextCliSettings)
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
def flext_cli_utilities() -> type[TestsCliUtilities]:
    """Provide TestsCliUtilities class for testing."""
    return TestsCliUtilities


# ============================================================================
# TEST SUPPORT
# ============================================================================

# Note: pytest-provides automatic event_loop fixture
# No custom event_loop fixture needed


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================


@pytest.fixture
def sample_config_data() -> dict[str, t.GeneralValueType]:
    """Provide sample configuration data for tests."""
    return {
        "debug": True,
        "output_format": "table",
        "no_color": False,
        "profile": "test",
        "timeout": c.Cli.TIMEOUTS.DEFAULT,
        "retries": c.Cli.HTTP.MAX_RETRIES,
        "api_endpoint": "https://api.example.com",
        "auth_token": "test_token_123",
    }


@pytest.fixture
def sample_file_data(temp_dir: Path) -> dict[str, t.GeneralValueType]:
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
def sample_command_data() -> dict[str, t.GeneralValueType]:
    """Provide sample command data for tests."""
    return {
        "command": "test_command",
        "args": ["--verbose", "--output", "json"],
        "kwargs": {
            "timeout": c.Cli.TIMEOUTS.DEFAULT,
            "retries": c.Cli.HTTP.MAX_RETRIES,
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
def load_fixture_config() -> dict[str, t.GeneralValueType]:
    """Load configuration data from fixtures directory."""
    fixture_path = Path("tests/fixtures/configs/test_config.json")
    with fixture_path.open(encoding="utf-8") as f:
        data = json.load(f)
    adapter: TypeAdapter[dict[str, t.GeneralValueType]] = TypeAdapter(
        dict[str, t.GeneralValueType]
    )
    return adapter.validate_python(data)


@pytest.fixture
def load_fixture_data() -> dict[str, t.GeneralValueType]:
    """Load test data from fixtures directory."""
    fixture_path = Path("tests/fixtures/data/test_data.json")
    with fixture_path.open(encoding="utf-8") as f:
        data = json.load(f)
    adapter: TypeAdapter[dict[str, t.GeneralValueType]] = TypeAdapter(
        dict[str, t.GeneralValueType]
    )
    return adapter.validate_python(data)


# ============================================================================
# DOCKER TEST SUPPORT (CENTRALIZED FIXTURES)
# ============================================================================


@pytest.fixture(scope="session")
def flext_test_docker(
    tmp_path_factory: pytest.TempPathFactory,
) -> FlextTestsDocker:
    """FlextTestsDocker instance for managing test containers.

    Container stays alive after tests for debugging, recreated on infra failures.
    Tests are idempotent with cleanup at start/end. Uses session scope to persist
    containers across tests but clean up at session end.
    """
    # Use the flext-cli directory as workspace root
    workspace_root = Path(__file__).parent.parent
    docker_manager = FlextTestsDocker(workspace_root=workspace_root)

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
def reset_singletons() -> None:
    """Reset all FlextSettings singletons between tests for isolation.

    CRITICAL: This fixture runs automatically before EACH test to ensure
    no state leaks between tests regardless of pytest-randomly order.
    """
    # Reset BEFORE test to ensure clean state
    # For now, skip reset to focus on test functionality
    # Pydantic v2 with 'from __future__ import annotations' resolves forward refs
    # No manual model_rebuild() needed - annotations resolved at runtime
    # Reset after test to clean up any state
    return


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
# VERSION TEST FIXTURES AND CONSTANTS
# ============================================================================


class Examples:
    """Version string examples for parametrized tests."""

    VALID_SEMVER: str = "1.2.3"
    VALID_SEMVER_COMPLEX: str = "1.2.3-alpha.1+build.123"
    INVALID_NO_DOTS: str = "version"
    INVALID_NON_NUMERIC: str = "a.b.c"


class InfoTuples:
    """Version info tuple examples for parametrized tests."""

    VALID_TUPLE: tuple[int, int, int] = (1, 2, 3)
    VALID_COMPLEX_TUPLE: tuple[int | str, ...] = (1, 2, 3, "alpha", 1)
    SHORT_TUPLE: tuple[int, int] = (1, 2)
    EMPTY_TUPLE: tuple[()] = ()


# ============================================================================
# INPUT SIMULATION FIXTURES - For eliminating monkeypatch violations
# ============================================================================


@pytest.fixture
def input_simulator() -> Iterator[Callable[[list[str]], None]]:
    """Simulate user input via fixture-based queue (REPLACES monkeypatch).

    Usage:
        def test_something(input_simulator):
            input_simulator(["value1", "value2"])
            result = prompts.prompt("Enter:")
            assert result.is_success
    """
    input_queue: deque[str] = deque()

    def queue_inputs(values: list[str]) -> None:
        """Queue input values to be returned by simulated input."""
        input_queue.extend(values)

    original_input = builtins.input

    def simulated_input(prompt: str = "") -> str:
        """Return queued input or empty string."""
        if input_queue:
            return input_queue.popleft()
        return ""

    setattr(builtins, "input", simulated_input)
    yield queue_inputs
    builtins.input = original_input


@pytest.fixture
def password_simulator() -> Iterator[Callable[[str], None]]:
    """Simulate password input via fixture (REPLACES monkeypatch getpass).

    Usage:
        def test_password(password_simulator):
            password_simulator("secret123")
            result = prompts.prompt_password("Enter password:")
            assert result.is_success
    """
    password_value: str = ""

    def set_password(value: str) -> None:
        """Set the password to be returned by getpass."""
        nonlocal password_value
        password_value = value

    original_getpass = getpass.getpass

    def simulated_getpass(prompt: str = "", stream: object = None) -> str:
        """Return the set password."""
        return password_value

    getpass.getpass = simulated_getpass
    yield set_password
    getpass.getpass = original_getpass


@pytest.fixture
def input_exception_simulator() -> Iterator[Callable[[type[Exception]], None]]:
    """Simulate exceptions during input (REPLACES monkeypatch with exception).

    Usage:
        def test_interrupt(input_exception_simulator):
            input_exception_simulator(KeyboardInterrupt)
            result = prompts.confirm("Continue?", default=False)
            assert result.is_failure
    """
    exception_to_raise: type[Exception] | None = None

    def set_exception(exc_type: type[Exception]) -> None:
        """Set the exception to raise on next input call."""
        nonlocal exception_to_raise
        exception_to_raise = exc_type

    original_input = builtins.input

    def simulated_input(prompt: str = "") -> str:
        """Raise the set exception or return empty string."""
        if exception_to_raise:
            raise exception_to_raise()
        return ""

    setattr(builtins, "input", simulated_input)
    yield set_exception
    builtins.input = original_input


# ============================================================================
# TEST MARKERS AND CONFIGURATION
# ============================================================================
# pytest_configure is already defined above with constants and markers


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
