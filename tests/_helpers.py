"""Enhanced test helpers for 100% coverage with real automated tests."""

from __future__ import annotations

from collections.abc import Sequence

from flext_core import r

from flext_cli import FlextCliCommands, t


class CommandsFactory:
    """Factory for creating test commands with high automation."""

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

        def handler(
            *args: t.ContainerValue,
            **kwargs: t.ContainerValue,
        ) -> r[t.Cli.JsonValue]:
            return r[t.Cli.JsonValue].ok(result_value)

        return commands.register_command(command_name, handler)

    @staticmethod
    def register_command_with_args(
        commands: FlextCliCommands,
        command_name: str,
    ) -> r[bool]:
        """Register a command that accepts arguments."""

        def handler(
            *args: t.ContainerValue,
            **kwargs: t.ContainerValue,
        ) -> r[t.Cli.JsonValue]:
            return r[t.Cli.JsonValue].ok(f"args: {len(args)}")

        return commands.register_command(command_name, handler)

    @staticmethod
    def register_failing_command(
        commands: FlextCliCommands,
        command_name: str,
        error_message: str = "Test error",
    ) -> r[bool]:
        """Register a command that fails with a specific error."""

        def handler(
            *args: t.ContainerValue,
            **kwargs: t.ContainerValue,
        ) -> r[t.Cli.JsonValue]:
            return r[t.Cli.JsonValue].fail(error_message)

        return commands.register_command(command_name, handler)


def generate_edge_case_data() -> Sequence[dict[str, t.ContainerValue]]:
    """Generate comprehensive edge case test data."""
    return [
        {"name": "a"},
        {"name": "a" * 100},
        {"name": "test_123"},
    ]
