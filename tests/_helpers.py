"""Enhanced test helpers for 100% coverage with real automated tests."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime

import pytest
from flext_core import r

from flext_cli import FlextCliCommands, m, t
from tests.models import CliCommandInput, CliSessionInput


def create_test_cli_command(**overrides: t.ContainerValue) -> m.Cli.CliCommand:
    """Factory for real CliCommand instances with sensible defaults."""
    now = datetime.now(UTC)
    payload: dict[str, t.JsonValue] = {
        "unique_id": f"test-cmd-{now.timestamp()}",
        "name": "test_command",
        "description": "Test command description",
        "status": "pending",
        "created_at": now,
        "command_line": "test_command",
    }
    if "command_id" in overrides and isinstance(overrides["command_id"], str):
        payload["unique_id"] = overrides["command_id"]
    if "arguments" in overrides and isinstance(overrides["arguments"], (list, tuple)):
        args_val = overrides["arguments"]
        payload["args"] = [str(x) for x in args_val if isinstance(x, str)]
    merged = {**payload, **overrides}
    _ = merged.pop("command_id", None)
    _ = merged.pop("arguments", None)
    filtered = {k: v for k, v in merged.items() if k in CliCommandInput.model_fields}
    inp = CliCommandInput.model_validate(filtered)
    cmd = m.Cli.CliCommand.model_construct(
        _fields_set=None, **inp.model_dump(exclude_none=True)
    )
    object.__setattr__(cmd, "command_id", cmd.unique_id)
    return cmd


def create_test_cli_session(**overrides: t.ContainerValue) -> m.Cli.CliSession:
    """Factory for real CliSession instances with sensible defaults."""
    now = datetime.now(UTC)
    payload: dict[str, t.JsonValue] = {
        "session_id": f"test-session-{now.timestamp()}",
        "status": "active",
        "created_at": now,
    }
    filtered = {
        k: v
        for k, v in {**payload, **overrides}.items()
        if k in CliSessionInput.model_fields
    }
    inp = CliSessionInput.model_validate(filtered)
    session = m.Cli.CliSession.model_construct(
        _fields_set=None, **inp.model_dump(exclude_none=True)
    )
    if getattr(session, "environment", None) is None:
        object.__setattr__(session, "environment", overrides.get("environment", "test"))
    return session


class AuthHelpers:
    """Authentication test helpers."""

    @staticmethod
    def create_test_token(user_id: str = "test_user") -> str:
        """Create a test JWT token."""
        now = datetime.now(UTC)
        return f"test_token_{user_id}_{now.timestamp()}"

    @staticmethod
    def create_test_credentials(
        **overrides: t.ContainerValue,
    ) -> Mapping[str, t.ContainerValue]:
        """Create test credentials dict."""
        defaults: dict[str, t.ContainerValue] = {
            "username": "test_user",
            "password": "test_pass",
            "token": AuthHelpers.create_test_token(),
        }
        return {**defaults, **overrides}

    @staticmethod
    def create_auth_test_data() -> dict[str, t.ContainerValue]:
        """Create authentication test data."""
        return {
            "valid_credentials": {"username": "test_user", "password": "test_pass"},
            "invalid_credentials": {"username": "wrong_user", "password": "wrong_pass"},
            "expected_token": "valid_token",
        }

    @staticmethod
    def create_auth_operations_test_data() -> dict[str, t.ContainerValue]:
        """Create authentication operations test data."""
        return {
            "login_success": {
                "username": "test_user",
                "password": "test_pass",
                "expected_token": "valid_token",
            },
            "login_failure": {
                "username": "wrong_user",
                "password": "wrong_pass",
                "expected_error": "Invalid credentials",
            },
            "token_validation": {
                "valid_token": "valid_token",
                "invalid_token": "invalid_token",
            },
        }


class CommandHelpers:
    """Command execution test helpers."""

    @staticmethod
    def create_command_model(**overrides: t.ContainerValue) -> r[m.Cli.CliCommand]:
        """Create a command model wrapped in r.

        Args:
            **overrides: Optional field overrides

        Returns:
            r[m.Cli.CliCommand]: Success result with command model

        """
        cmd = create_test_cli_command(**overrides)
        return r[m.Cli.CliCommand].ok(cmd)

    @staticmethod
    def create_test_command_data(
        **overrides: t.ContainerValue,
    ) -> Mapping[str, t.ContainerValue]:
        """Create test command data."""
        defaults: dict[str, t.ContainerValue] = {
            "name": "test_command",
            "args": ["--test"],
            "timeout": 30.0,
            "working_dir": "/tmp",
        }
        return {**defaults, **overrides}

    @staticmethod
    def create_command_execution_test_data() -> dict[str, t.ContainerValue]:
        """Create command execution test data."""
        return {
            "basic_command": {"name": "echo", "args": ["hello world"], "timeout": 10.0},
            "complex_command": {
                "name": "python",
                "args": ["-c", "print('test')"],
                "timeout": 30.0,
                "working_dir": "/tmp",
            },
            "expected_result": {"success": True, "exit_code": 0},
        }

    @staticmethod
    def simulate_command_execution(
        command_data: dict[str, t.ContainerValue],
    ) -> Mapping[str, t.ContainerValue]:
        """Simulate command execution result."""
        return {
            "success": True,
            "output": f"Executed {command_data.get('name', 'unknown')}",
            "exit_code": 0,
            "duration": 1.5,
        }


class OutputHelpers:
    """Output formatting test helpers."""

    @staticmethod
    def create_test_output_data(
        **overrides: t.ContainerValue,
    ) -> Mapping[str, t.ContainerValue]:
        """Create test output data."""
        defaults: dict[str, t.ContainerValue] = {
            "format": "json",
            "data": {"test": "data"},
            "headers": ["col1", "col2"],
            "rows": [["val1", "val2"]],
        }
        return {**defaults, **overrides}

    @staticmethod
    def create_format_test_data() -> dict[str, t.ContainerValue]:
        """Create format test data for output formatting tests."""
        return {
            "json": {"test": "data", "number": 42},
            "table": {"headers": ["Name", "Value"], "rows": [["Test", "42"]]},
            "plain": "Plain text output",
        }

    @staticmethod
    def create_table_test_data() -> dict[str, t.ContainerValue]:
        """Create table test data for output formatting tests."""
        return {
            "simple": {
                "headers": ["Name", "Age", "City"],
                "rows": [["Alice", "25", "NYC"], ["Bob", "30", "LA"]],
            },
            "with_none": {
                "headers": ["Name", "Age", "City"],
                "rows": [["Alice", "25", None], ["Bob", None, "LA"]],
            },
            "empty": {"headers": [], "rows": []},
        }

    @staticmethod
    def format_test_output(data: dict[str, t.ContainerValue]) -> str:
        """Format test output."""
        if data.get("format") == "json":
            return json.dumps(data.get("data", {}))
        return str(data.get("data", {}))


class CommandsFactory:
    """Factory for creating test commands with high automation."""

    @staticmethod
    def create_basic_command(**overrides: t.ContainerValue) -> m.Cli.CliCommand:
        """Create basic test command."""
        return create_test_cli_command(**overrides)

    @staticmethod
    def create_command_chain(count: int = 3) -> list[m.Cli.CliCommand]:
        """Create a chain of related commands."""
        commands: list[m.Cli.CliCommand] = []
        for i in range(count):
            cmd = create_test_cli_command(
                command_id=f"chain_cmd_{i}",
                name=f"command_{i}",
                arguments=[f"--step={i}"],
            )
            commands.append(cmd)
        return commands

    @staticmethod
    def create_commands_with_dependencies() -> list[m.Cli.CliCommand]:
        """Create commands with dependency relationships."""
        cmd1 = create_test_cli_command(
            command_id="dep_cmd_1", name="prepare_data", arguments=["--prepare"]
        )
        cmd2 = create_test_cli_command(
            command_id="dep_cmd_2",
            name="process_data",
            arguments=["--process", "--input=dep_cmd_1"],
        )
        return [cmd1, cmd2]

    @staticmethod
    def create_commands() -> FlextCliCommands:
        """Create a FlextCliCommands instance for testing."""
        return FlextCliCommands()

    @staticmethod
    def register_simple_command(
        commands: FlextCliCommands, command_name: str, result_value: str = "success"
    ) -> r[bool]:
        """Register a simple test command that returns a fixed value."""

        def handler(*args: t.JsonValue, **kwargs: t.JsonValue) -> r[t.JsonValue]:
            return r[t.JsonValue].ok(result_value)

        return commands.register_command(command_name, handler)

    @staticmethod
    def register_command_with_args(
        commands: FlextCliCommands, command_name: str
    ) -> r[bool]:
        """Register a command that accepts arguments."""

        def handler(*args: t.JsonValue, **kwargs: t.JsonValue) -> r[t.JsonValue]:
            return r[t.JsonValue].ok(f"args: {len(args)}")

        return commands.register_command(command_name, handler)

    @staticmethod
    def register_failing_command(
        commands: FlextCliCommands, command_name: str, error_message: str = "Test error"
    ) -> r[bool]:
        """Register a command that fails with a specific error."""

        def handler(*args: t.JsonValue, **kwargs: t.JsonValue) -> r[t.JsonValue]:
            return r[t.JsonValue].fail(error_message)

        return commands.register_command(command_name, handler)


def generate_edge_case_data() -> list[dict[str, t.JsonValue]]:
    """Generate comprehensive edge case test data for CliCommand.

    Only uses valid CliCommand fields: name, description, command_line, usage,
    entry_point, plugin_version, args, status, exit_code, output.
    """
    return [
        {"name": "a", "description": "Minimum name length"},
        {"name": "a" * 100, "description": "Maximum name length"},
        {"name": "test_123", "description": "Underscores"},
        {"name": "test-123", "description": "Hyphens"},
        {"name": "test.123", "description": "Dots"},
        {"name": "测试命令", "description": "Chinese characters"},
        {"name": "café", "description": "Accented characters"},
        {
            "name": "test",
            "command_line": "test --verbose --debug",
            "description": "With flags",
        },
        {"name": "test", "command_line": "", "description": "Empty command line"},
        {"name": "test", "args": [], "description": "Empty args"},
        {
            "name": "test",
            "args": ["--verbose", "--debug"],
            "description": "Multiple args",
        },
        {"name": "test", "status": "pending", "description": "Pending status"},
        {"name": "test", "status": "running", "description": "Running status"},
        {"name": "test", "status": "completed", "description": "Completed status"},
    ]


@pytest.fixture
def test_cli_command() -> m.Cli.CliCommand:
    """Fixture providing test CliCommand instance."""
    return create_test_cli_command()


@pytest.fixture
def test_cli_session() -> m.Cli.CliSession:
    """Fixture providing test CliSession instance."""
    return create_test_cli_session()


@pytest.fixture
def edge_case_commands() -> list[m.Cli.CliCommand]:
    """Fixture providing edge case command instances."""
    return [create_test_cli_command(**data) for data in generate_edge_case_data()]
