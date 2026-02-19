"""Enhanced test helpers for 100% coverage with real automated tests."""

import json
from datetime import UTC, datetime
from typing import Any

import pytest
from flext_cli import FlextCliCommands

# Direct imports to avoid forward reference issues
from flext_cli.models import m
from flext_cli.typings import FlextCliTypes as t
from flext_core.result import FlextResult as r


# Factory functions using direct model instantiation (no forward refs)
def create_test_cli_command(
    **overrides: dict[str, t.GeneralValueType],
) -> m.Cli.CliCommand:
    """Factory for real CliCommand instances with sensible defaults."""
    now = datetime.now(UTC)
    defaults = {
        "unique_id": f"test-cmd-{now.timestamp()}",
        "name": "test_command",
        "description": "Test command description",
        "status": "pending",
        "created_at": now,
    }
    defaults.update(overrides)
    # Use model_construct to avoid DomainEvent forward reference issue during model_rebuild
    cmd = m.Cli.CliCommand.model_construct(**defaults)
    # Add command_id as an alias to unique_id for backward compatibility with tests
    object.__setattr__(cmd, "command_id", cmd.unique_id)
    return cmd


def create_test_cli_session(
    **overrides: dict[str, t.GeneralValueType],
) -> m.Cli.CliSession:
    """Factory for real CliSession instances with sensible defaults."""
    now = datetime.now(UTC)
    defaults = {
        "session_id": f"test-session-{now.timestamp()}",
        "status": "active",
        "created_at": now,
    }
    defaults.update(overrides)
    # Use model_construct to avoid DomainEvent forward reference issue during model_rebuild
    session = m.Cli.CliSession.model_construct(**defaults)
    # Add environment as an alias for backward compatibility with tests
    if not hasattr(session, "environment") or session.environment is None:
        object.__setattr__(session, "environment", overrides.get("environment", "test"))
    return session


# Test Helper Classes
class AuthHelpers:
    """Authentication test helpers."""

    @staticmethod
    def create_test_token(user_id: str = "test_user") -> str:
        """Create a test JWT token."""
        now = datetime.now(UTC)
        return f"test_token_{user_id}_{now.timestamp()}"

    @staticmethod
    def create_test_credentials(
        **overrides: dict[str, t.GeneralValueType],
    ) -> dict[str, t.GeneralValueType]:
        """Create test credentials dict."""
        defaults = {
            "username": "test_user",
            "password": "test_pass",
            "token": AuthHelpers.create_test_token(),
        }
        defaults.update(overrides)
        return defaults

    @staticmethod
    def create_auth_test_data() -> dict[str, t.GeneralValueType]:
        """Create authentication test data."""
        return {
            "valid_credentials": {
                "username": "test_user",
                "password": "test_pass",
            },
            "invalid_credentials": {
                "username": "wrong_user",
                "password": "wrong_pass",
            },
            "expected_token": "valid_token",
        }

    @staticmethod
    def create_auth_operations_test_data() -> dict[str, t.GeneralValueType]:
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
    def create_command_model(
        **overrides: dict[str, t.GeneralValueType],
    ) -> "r[m.Cli.CliCommand]":
        """Create a command model wrapped in FlextResult.

        Args:
            **overrides: Optional field overrides

        Returns:
            r[m.Cli.CliCommand]: Success result with command model

        """
        cmd = create_test_cli_command(**overrides)
        return r[m.Cli.CliCommand].ok(cmd)

    @staticmethod
    def create_test_command_data(
        **overrides: dict[str, t.GeneralValueType],
    ) -> dict[str, t.GeneralValueType]:
        """Create test command data."""
        defaults = {
            "name": "test_command",
            "args": ["--test"],
            "timeout": 30.0,
            "working_dir": "/tmp",
        }
        defaults.update(overrides)
        return defaults

    @staticmethod
    def create_command_execution_test_data() -> dict[str, t.GeneralValueType]:
        """Create command execution test data."""
        return {
            "basic_command": {
                "name": "echo",
                "args": ["hello world"],
                "timeout": 10.0,
            },
            "complex_command": {
                "name": "python",
                "args": ["-c", "print('test')"],
                "timeout": 30.0,
                "working_dir": "/tmp",
            },
            "expected_result": {
                "success": True,
                "exit_code": 0,
            },
        }

    @staticmethod
    def simulate_command_execution(
        command_data: dict[str, t.GeneralValueType],
    ) -> dict[str, t.GeneralValueType]:
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
        **overrides: dict[str, t.GeneralValueType],
    ) -> dict[str, t.GeneralValueType]:
        """Create test output data."""
        defaults = {
            "format": "json",
            "data": {"test": "data"},
            "headers": ["col1", "col2"],
            "rows": [["val1", "val2"]],
        }
        defaults.update(overrides)
        return defaults

    @staticmethod
    def create_format_test_data() -> dict[str, t.GeneralValueType]:
        """Create format test data for output formatting tests."""
        return {
            "json": {"test": "data", "number": 42},
            "table": {"headers": ["Name", "Value"], "rows": [["Test", "42"]]},
            "plain": "Plain text output",
        }

    @staticmethod
    def create_table_test_data() -> dict[str, t.GeneralValueType]:
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
            "empty": {
                "headers": [],
                "rows": [],
            },
        }

    @staticmethod
    def format_test_output(data: dict[str, t.GeneralValueType]) -> str:
        """Format test output."""
        if data.get("format") == "json":
            return json.dumps(data.get("data", {}))
        return str(data.get("data", {}))


class CommandsFactory:
    """Factory for creating test commands with high automation."""

    @staticmethod
    def create_basic_command(
        **overrides: dict[str, t.GeneralValueType],
    ) -> m.Cli.CliCommand:
        """Create basic test command."""
        return create_test_cli_command(**overrides)

    @staticmethod
    def create_command_chain(count: int = 3) -> list[m.Cli.CliCommand]:
        """Create a chain of related commands."""
        commands = []
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
            command_id="dep_cmd_1",
            name="prepare_data",
            arguments=["--prepare"],
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
        commands: FlextCliCommands,
        command_name: str,
        result_value: str = "success",
    ) -> r[bool]:
        """Register a simple test command that returns a fixed value."""

        def handler() -> r[str]:
            return r.ok(result_value)

        return commands.register_command(command_name, handler)

    @staticmethod
    def register_command_with_args(
        commands: FlextCliCommands,
        command_name: str,
    ) -> r[bool]:
        """Register a command that accepts arguments."""

        def handler(*args: str, **kwargs: t.GeneralValueType) -> str:
            # Return formatted string with args count (expected by test)
            return f"args: {len(args)}"

        return commands.register_command(command_name, handler)

    @staticmethod
    def register_failing_command(
        commands: FlextCliCommands,
        command_name: str,
        error_message: str = "Test error",
    ) -> r[bool]:
        """Register a command that fails with a specific error."""

        def handler() -> r[Any]:
            return r.error(error_message)

        return commands.register_command(command_name, handler)


# Aliases for backward compatibility
def create_real_cli_command(
    **overrides: dict[str, t.GeneralValueType],
) -> m.Cli.CliCommand:
    """Alias for create_test_cli_command - creates a real Pydantic model instance."""
    return create_test_cli_command(**overrides)


def create_real_cli_session(
    **overrides: dict[str, t.GeneralValueType],
) -> m.Cli.CliSession:
    """Alias for create_test_cli_session - creates a real Pydantic model instance."""
    return create_test_cli_session(**overrides)


def generate_edge_case_data() -> list[dict[str, t.GeneralValueType]]:
    """Generate comprehensive edge case test data for CliCommand.

    Only uses valid CliCommand fields: name, description, command_line, usage,
    entry_point, plugin_version, args, status, exit_code, output.
    """
    return [
        # Boundary name lengths
        {"name": "a", "description": "Minimum name length"},
        {"name": "a" * 100, "description": "Maximum name length"},
        # Special characters in name
        {"name": "test_123", "description": "Underscores"},
        {"name": "test-123", "description": "Hyphens"},
        {"name": "test.123", "description": "Dots"},
        # Unicode names
        {"name": "测试命令", "description": "Chinese characters"},
        {"name": "café", "description": "Accented characters"},
        # Command line variations
        {
            "name": "test",
            "command_line": "test --verbose --debug",
            "description": "With flags",
        },
        {"name": "test", "command_line": "", "description": "Empty command line"},
        # Args variations
        {"name": "test", "args": [], "description": "Empty args"},
        {
            "name": "test",
            "args": ["--verbose", "--debug"],
            "description": "Multiple args",
        },
        # Status variations
        {"name": "test", "status": "pending", "description": "Pending status"},
        {"name": "test", "status": "running", "description": "Running status"},
        {"name": "test", "status": "completed", "description": "Completed status"},
    ]


# Parametrized test data generators
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
