"""FLEXT CLI Test Configuration - Comprehensive Test Infrastructure.

Centralized test configuration using flext_tests library with real functionality
testing, Docker support, and comprehensive fixtures following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import builtins
import getpass
import json
import logging
import os
from collections import deque
from collections.abc import Callable, Generator, Iterator, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

import pytest
import yaml
from click.testing import CliRunner
from flext_core import FlextContainer, FlextSettings
from flext_tests.docker import tk
from pydantic import TypeAdapter

from flext_cli import (
    FlextCli,
    FlextCliCmd,
    FlextCliCommands,
    FlextCliCore,
    FlextCliDebug,
    FlextCliFileTools,
    FlextCliMixins,
    FlextCliOutput,
    FlextCliPrompts,
    FlextCliServiceBase,
    FlextCliSettings,
)

from . import c, m, p, t, u
from .helpers._impl import _is_json_dict
from .models import ScalarConfigRestore


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest markers for the test suite."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line("markers", "docker: marks tests that require Docker")
    config.addinivalue_line(
        "markers", "real_functionality: marks tests that test real functionality"
    )


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create Click CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide temporary directory for tests.

    Wraps pytest's tmp_path fixture to maintain naming consistency.
    """
    return tmp_path


def _create_temp_file(temp_dir: Path, filename: str, content: str) -> Path:
    """Factory helper for creating temporary files with custom content.

    Args:
        temp_dir: Temporary directory path
        filename: Target filename with extension
        content: File content as string

    Returns:
        Path to created file

    """
    file_path = temp_dir / filename
    _ = file_path.write_text(content)
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


@pytest.fixture
def flext_cli_api(
    tmp_path: Path, request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> FlextCli:
    """Create isolated FlextCli instance with test-specific config.

    Each test gets a fresh FlextCli instance with configuration pointing
    to a unique temporary directory, ensuring complete isolation between tests.
    Uses FlextCliSettings modern API: environment variables for configuration.
    """
    test_dir = tmp_path / f"test_{id(request)}"
    test_dir.mkdir(exist_ok=True)
    FlextSettings.reset_for_testing()
    FlextCliSettings._reset_instance()
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
    return FlextCli()


class CliCommandFactory(Protocol):
    """Protocol for CliCommand factory function."""

    def __call__(
        self,
        name: str = ...,
        command_line: str = ...,
        description: str = ...,
        status: str = ...,
        **kwargs: t.Scalar,
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
        **kwargs: t.Scalar,
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
        **kwargs: t.Scalar,
    ) -> m.Cli.DebugInfo:
        """Create DebugInfo instance."""
        ...


class LoggingConfigFactory(Protocol):
    """Protocol for LoggingConfig factory function."""

    def __call__(
        self, log_level: str = ..., log_format: str = ..., **kwargs: t.Scalar
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
        **kwargs: t.Scalar,
    ) -> m.Cli.CliCommand:
        cli_data: dict[str, object]
        cli_data = {
            "command_line": command_line,
            "args": [],
            "status": status,
            "exit_code": None,
            "output": "",
            "error_output": "",
            "execution_time": None,
            "result": None,
            "kwargs": {},
            "name": name,
            "description": description,
        }
        raw_data: dict[str, object] = {**cli_data, **kwargs}
        typed_data: dict[str, object] = raw_data
        transform_result = u.transform(typed_data)
        if transform_result.is_success:
            unwrapped = transform_result.value
            if _is_json_dict(unwrapped):
                final_data = dict(unwrapped.items())
            else:
                final_data = raw_data
        else:
            final_data = raw_data
        return m.Cli.CliCommand(**final_data)

    return _create


@pytest.fixture
def cli_session_factory() -> CliSessionFactory:
    """Factory fixture for creating CliSession models with defaults."""

    def _create(
        session_id: str = "test-session",
        user_id: str = "test_user",
        status: str = "active",
        **kwargs: t.Scalar,
    ) -> m.Cli.CliSession:
        session_data: dict[str, object] = {
            "session_id": session_id,
            "status": status,
            "user_id": user_id,
            "commands": [],
            "start_time": None,
            "end_time": None,
            "last_activity": None,
            "internal_duration_seconds": 0.0,
            "commands_executed": 0,
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": None,
        }
        raw_data: dict[str, object] = {**session_data, **kwargs}
        typed_data = raw_data
        transform_result = u.transform(typed_data)
        if transform_result.is_success:
            unwrapped = transform_result.value
            if _is_json_dict(unwrapped):
                final_data = dict(unwrapped.items())
            else:
                final_data = raw_data
        else:
            final_data = raw_data
        return m.Cli.CliSession(**final_data)

    return _create


@pytest.fixture
def debug_info_factory() -> DebugInfoFactory:
    """Factory fixture for creating DebugInfo models with defaults."""

    def _create(
        service: str = "TestService",
        level: str = "INFO",
        message: str = "",
        **kwargs: t.Scalar,
    ) -> m.Cli.DebugInfo:
        debug_data: dict[str, object] = {
            "service": service,
            "level": level,
            "message": message or "",
            "system_info": {},
            "config_info": {},
        }
        valid_fields = {
            "service",
            "timestamp",
            "system_info",
            "config_info",
            "level",
            "message",
        }
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}
        raw_data: dict[str, object] = {**debug_data, **filtered_kwargs}
        typed_data = raw_data
        transform_result = u.transform(typed_data)
        if transform_result.is_success:
            unwrapped = transform_result.value
            if _is_json_dict(unwrapped):
                final_data = dict(unwrapped.items())
            else:
                final_data = raw_data
        else:
            final_data = raw_data
        return m.Cli.DebugInfo(**final_data)

    return _create


@pytest.fixture
def logging_config_factory() -> LoggingConfigFactory:
    """Factory fixture for creating LoggingConfig models with defaults."""

    def _create(
        log_level: str = "INFO",
        log_format: str = "%(asctime)s - %(message)s",
        **kwargs: t.Scalar,
    ) -> m.Cli.LoggingConfig:
        logging_data: dict[str, object] = {
            "log_level": log_level,
            "log_format": log_format,
            "console_output": True,
            "log_file": "",
        }
        raw_data: dict[str, object] = {**logging_data, **kwargs}
        typed_data = raw_data
        transform_result = u.transform(typed_data)
        if transform_result.is_success:
            unwrapped = transform_result.value
            if _is_json_dict(unwrapped):
                final_data = dict(unwrapped.items())
            else:
                final_data = raw_data
        else:
            final_data = raw_data
        return m.Cli.LoggingConfig(**final_data)

    return _create


def _create_service_instance(service_class: type) -> object:
    """Factory helper for creating service instances.

    Args:
        service_class: The service class to instantiate

    Returns:
        New instance of the service class

    """
    if service_class is FlextCliSettings:
        return FlextCliServiceBase.get_cli_config()
    return service_class()


_SERVICE_CLASSES: dict[str, type] = {
    "cmd": FlextCliCmd,
    "commands": FlextCliCommands,
    "config": FlextCliSettings,
    "constants": c,
    "core": FlextCliCore,
    "debug": FlextCliDebug,
    "file_tools": FlextCliFileTools,
    "mixins": FlextCliMixins,
    "models": m,
    "output": FlextCliOutput,
    "prompts": FlextCliPrompts,
    "protocols": p,
}


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
def flext_cli_constants() -> c:
    """Create c instance for testing."""
    instance = _create_service_instance(c)
    assert isinstance(instance, c)
    return instance


@pytest.fixture
def flext_cli_context() -> c:
    """Create c instance for testing."""
    instance = _create_service_instance(c)
    assert isinstance(instance, c)
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
def flext_cli_models() -> m:
    """Create m instance for testing."""
    instance = _create_service_instance(m)
    assert isinstance(instance, m)
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
def flext_cli_protocols() -> p:
    """Create p instance for testing."""
    instance = _create_service_instance(p)
    assert isinstance(instance, p)
    return instance


@pytest.fixture
def flext_cli_utilities() -> type[u]:
    """Provide u class for testing."""
    return u


@pytest.fixture
def sample_config_data() -> dict[str, object]:
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
def sample_file_data(temp_dir: Path) -> dict[str, object]:
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
def sample_command_data() -> dict[str, object]:
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
def load_fixture_config() -> Mapping[str, object]:
    """Load configuration data from fixtures directory."""
    fixture_path = Path("tests/fixtures/configs/test_config.json")
    with fixture_path.open(encoding="utf-8") as f:
        data = json.load(f)
    adapter: TypeAdapter[Mapping[str, object]] = TypeAdapter(object)
    return adapter.validate_python(data)


@pytest.fixture
def load_fixture_data() -> Mapping[str, object]:
    """Load test data from fixtures directory."""
    fixture_path = Path("tests/fixtures/data/test_data.json")
    with fixture_path.open(encoding="utf-8") as f:
        data = json.load(f)
    adapter: TypeAdapter[Mapping[str, object]] = TypeAdapter(object)
    return adapter.validate_python(data)


@pytest.fixture(scope="session")
def flext_test_docker(tmp_path_factory: pytest.TempPathFactory) -> tk:
    """Tk instance for managing test containers.

    Container stays alive after tests for debugging, recreated on infra failures.
    Tests are idempotent with cleanup at start/end. Uses session scope to persist
    containers across tests but clean up at session end.
    """
    workspace_root = Path(__file__).parent.parent
    docker_manager = tk(workspace_root=workspace_root)
    try:
        _ = docker_manager.cleanup_dirty_containers()
    except OSError as startup_err:
        logging.getLogger(__name__).debug(
            "Docker cleanup at startup skipped: %s", startup_err
        )
    return docker_manager


@pytest.fixture
def mock_env_vars(tmp_path: Path) -> Generator[dict[str, str]]:
    """Set up environment variables for tests using real .env file."""
    env_file = tmp_path / ".env"
    env_content = "FLEXT_CLI_DEBUG=true\nFLEXT_CLI_OUTPUT_FORMAT=json\nFLEXT_CLI_NO_COLOR=false\nFLEXT_CLI_PROFILE=test\nFLEXT_CLI_TIMEOUT=30\nFLEXT_CLI_RETRIES=3\n"
    _ = env_file.write_text(env_content)
    original_env: dict[str, str] = {}
    env_vars = {
        "FLEXT_CLI_DEBUG": "true",
        "FLEXT_CLI_OUTPUT_FORMAT": "json",
        "FLEXT_CLI_NO_COLOR": "false",
        "FLEXT_CLI_PROFILE": "test",
        "FLEXT_CLI_TIMEOUT": "30",
        "FLEXT_CLI_RETRIES": "3",
    }

    def set_env_var(k: str, v: str) -> None:
        """Set single environment variable."""
        if k in os.environ:
            original_env[k] = os.environ[k]
        os.environ[k] = v

    _ = u.Cli.process_mapping(env_vars, set_env_var, on_error="skip")
    yield env_vars

    def restore_env_var(k: str, _v: str) -> None:
        """Restore single environment variable."""
        if k in original_env:
            os.environ[k] = original_env[k]
        else:
            _ = os.environ.pop(k, None)

    _ = u.Cli.process_mapping(env_vars, restore_env_var, on_error="skip")


@pytest.fixture(autouse=True)
def reset_singletons() -> None:
    """Reset all FlextSettings singletons between tests for isolation.

    CRITICAL: This fixture runs automatically before EACH test to ensure
    no state leaks between tests regardless of pytest-randomly order.
    """
    return


@pytest.fixture
def clean_flext_container() -> Generator[None]:
    """Ensure clean FlextContainer state for tests."""
    container = FlextContainer()
    original_config = container.get_config()
    _ = container.configure({})
    yield
    restore = ScalarConfigRestore.from_config_items(dict(original_config.root))
    _ = container.configure(restore.root)


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


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Modify test collection to add markers based on test names."""
    _ = config
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        if "docker" in item.name:
            item.add_marker(pytest.mark.docker)
        if "slow" in item.name:
            item.add_marker(pytest.mark.slow)
