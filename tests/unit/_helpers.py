"""Enhanced test helpers for 100% coverage with real automated tests."""

from __future__ import annotations

from flext_cli import FlextCliCommands
from tests import p, r, t


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
    ) -> p.Result[bool]:
        """Register a simple test command that returns a fixed value."""

        def handler(
            *args: t.JsonValue,
            **kwargs: t.JsonValue,
        ) -> p.Result[t.JsonPayload]:
            return r[t.JsonPayload].ok(result_value)

        return commands.register_handler(command_name, handler)

    @staticmethod
    def register_command_with_args(
        commands: FlextCliCommands,
        command_name: str,
    ) -> p.Result[bool]:
        """Register a command that accepts arguments."""

        def handler(
            *args: t.JsonValue,
            **kwargs: t.JsonValue,
        ) -> p.Result[t.JsonPayload]:
            return r[t.JsonPayload].ok(f"args: {len(args)}")

        return commands.register_handler(command_name, handler)

    @staticmethod
    def register_failing_command(
        commands: FlextCliCommands,
        command_name: str,
        error_message: str = "Test error",
    ) -> p.Result[bool]:
        """Register a command that fails with a specific error."""

        def handler(
            *args: t.JsonValue,
            **kwargs: t.JsonValue,
        ) -> p.Result[t.JsonPayload]:
            return r[t.JsonPayload].fail(error_message)

        return commands.register_handler(command_name, handler)
