"""Coverage tests for flext_cli._utilities.commands."""

from __future__ import annotations

from dataclasses import dataclass

from flext_cli import c, t
from flext_cli._utilities.commands import FlextCliUtilitiesCommands
from flext_core import r
from tests import c as test_c


@dataclass
class MessageCarrier:
    """Simple carrier exposing a message attribute."""

    message: str


class TestsFlextCliCommandsUtilsCov:
    """Data-driven coverage for FlextCliUtilitiesCommands."""

    def test_commands_normalize_handler_result_none(self) -> None:
        result = FlextCliUtilitiesCommands.commands_normalize_handler_result(
            None,
            test_c.Tests.CMD_NAMES_VALID[0],
        )
        assert result.success
        assert isinstance(result.value, dict)
        assert result.value["command"] == test_c.Tests.CMD_NAMES_VALID[0]

    def test_commands_normalize_handler_result_success(self) -> None:
        result = FlextCliUtilitiesCommands.commands_normalize_handler_result(
            r[t.JsonPayload].ok({"items": ["a", "b"]}),
            test_c.Tests.CMD_NAMES_VALID[1],
        )
        assert result.success
        assert result.value == {"items": ["a", "b"]}

    def test_commands_normalize_handler_result_failure_with_error(self) -> None:
        result = FlextCliUtilitiesCommands.commands_normalize_handler_result(
            r[t.JsonPayload].fail("boom"),
            test_c.Tests.CMD_NAMES_VALID[2],
        )
        assert result.failure
        assert result.error == "boom"

    def test_commands_normalize_handler_result_failure_without_error(self) -> None:
        result = FlextCliUtilitiesCommands.commands_normalize_handler_result(
            r[t.JsonPayload].fail(""),
            test_c.Tests.CMD_NAMES_VALID[0],
        )
        assert result.failure
        assert result.error == "Command failed"

    def test_commands_resolve_success_message_with_formatter(self) -> None:
        result = FlextCliUtilitiesCommands.commands_resolve_success_message(
            result_value=7,
            success_message="fallback",
            success_formatter=lambda value: value * 2,
        )
        assert result == "14"

    def test_commands_resolve_success_message_from_attribute(self) -> None:
        result = FlextCliUtilitiesCommands.commands_resolve_success_message(
            result_value=MessageCarrier(message="done"),
            success_message="fallback",
            success_formatter=None,
        )
        assert result == "done"

    def test_commands_resolve_success_message_from_string(self) -> None:
        result = FlextCliUtilitiesCommands.commands_resolve_success_message(
            result_value="direct",
            success_message="fallback",
            success_formatter=None,
        )
        assert result == "direct"

    def test_commands_resolve_success_message_fallback(self) -> None:
        result = FlextCliUtilitiesCommands.commands_resolve_success_message(
            result_value=False,
            success_message="fallback",
            success_formatter=None,
        )
        assert result == "fallback"

    def test_commands_emit_success_message_does_not_raise(self) -> None:
        """Test that emit_success_message completes without exceptions."""
        FlextCliUtilitiesCommands.commands_emit_success_message(
            '{"ok": true}',
            c.Cli.MessageTypes.SUCCESS,
        )

    def test_commands_emit_error_message_does_not_raise(self) -> None:
        """Test that emit_error_message completes without exceptions."""
        FlextCliUtilitiesCommands.commands_emit_error_message("bad")


__all__: list[str] = ["TestsFlextCliCommandsUtilsCov"]
