"""Coverage tests for flext_cli._utilities.commands."""

from __future__ import annotations

from tests.constants import c
from tests.utilities import u


class TestsFlextCliCommandsUtilsCov:
    """Data-driven coverage for u.Cli."""

    def test_commands_resolve_success_message_with_formatter(self) -> None:
        result = u.Cli.commands_resolve_success_message(
            result_value=7,
            success_message="fallback",
            success_formatter=lambda value: str(value * 2),
        )
        assert result == "14"

    def test_commands_resolve_success_message_from_string(self) -> None:
        result = u.Cli.commands_resolve_success_message(
            result_value="direct",
            success_message="fallback",
            success_formatter=None,
        )
        assert result == "direct"

    def test_commands_resolve_success_message_from_mapping_message_key(self) -> None:
        result = u.Cli.commands_resolve_success_message(
            result_value={c.Cli.DICT_KEY_MESSAGE: "mapped"},
            success_message="fallback",
            success_formatter=None,
        )
        assert result == "mapped"

    def test_commands_resolve_success_message_fallback(self) -> None:
        result = u.Cli.commands_resolve_success_message(
            result_value=False,
            success_message="fallback",
            success_formatter=None,
        )
        assert result == "fallback"

    def test_commands_emit_success_message_does_not_raise(self) -> None:
        """Test that emit_success_message completes without exceptions."""
        u.Cli.commands_emit_success_message(
            '{"ok": true}',
            c.Cli.MessageTypes.SUCCESS,
        )

    def test_commands_emit_error_message_does_not_raise(self) -> None:
        """Test that emit_error_message completes without exceptions."""
        u.Cli.commands_emit_error_message("bad")


__all__: list[str] = ["TestsFlextCliCommandsUtilsCov"]
