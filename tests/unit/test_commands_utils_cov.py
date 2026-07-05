"""Behavioral tests for ``u.Cli`` command messaging helpers.

Public contract under test (``flext_cli._utilities.commands`` via ``u.Cli``):

- ``commands_resolve_success_message`` returns the resolved success message
  string following the order: formatter > string value > mapping ``message``
  key > provided fallback.
- ``commands_emit_success_message`` writes JSON/array payloads verbatim and
  styles plain text with a success glyph, always terminated by a newline.
- ``commands_emit_error_message`` writes the error styled with an error glyph
  and a trailing newline.

Assertions target observable return values and emitted stdout only.
"""

from __future__ import annotations

import pytest

from tests.constants import c
from tests.typings import t
from tests.utilities import u


class TestsFlextCliCommands:
    """Behavioral contract for the ``u.Cli`` command messaging helpers."""

    def test_formatter_result_wins_over_all_fallbacks(self) -> None:
        # Arrange
        def formatter(value: int) -> str:
            return str(value * 2)

        # Act
        resolved = u.Cli.commands_resolve_success_message(
            result_value=7,
            success_message="fallback",
            success_formatter=formatter,
        )

        # Assert
        assert resolved == "14"

    @pytest.mark.parametrize(
        ("result_value", "expected"),
        [
            pytest.param("direct", "direct", id="string-value-returned"),
            pytest.param({c.Cli.DICT_KEY_MESSAGE: "mapped"}, "mapped", id="mapping-message-key"),
            pytest.param(False, "fallback", id="bool-falls-back"),
            pytest.param("", "fallback", id="empty-string-falls-back"),
            pytest.param({c.Cli.DICT_KEY_MESSAGE: ""}, "fallback", id="empty-mapping-message-falls-back"),
            pytest.param({"other": "x"}, "fallback", id="mapping-without-message-key-falls-back"),
            pytest.param([1, 2, 3], "fallback", id="list-falls-back"),
            pytest.param(0, "fallback", id="zero-falls-back"),
        ],
    )
    def test_resolve_without_formatter_follows_value_then_fallback_order(
        self,
        result_value: t.Cli.ResultValue,
        expected: str,
    ) -> None:
        # Act
        resolved = u.Cli.commands_resolve_success_message(
            result_value=result_value,
            success_message="fallback",
            success_formatter=None,
        )

        # Assert
        assert resolved == expected

    def test_resolve_returns_none_fallback_when_message_is_none(self) -> None:
        # Act
        resolved = u.Cli.commands_resolve_success_message(
            result_value=0,
            success_message=None,
            success_formatter=None,
        )

        # Assert
        assert resolved is None

    @pytest.mark.parametrize(
        "payload",
        [
            pytest.param('{"ok": true}', id="json-object"),
            pytest.param("[1, 2, 3]", id="json-array"),
            pytest.param('   {"spaced": 1}', id="leading-whitespace-json"),
        ],
    )
    def test_structured_payload_is_emitted_verbatim_with_newline(
        self,
        payload: str,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        # Act
        u.Cli.commands_emit_success_message(payload, c.Cli.MessageTypes.SUCCESS)

        # Assert
        assert capsys.readouterr().out == f"{payload}\n"

    def test_plain_success_text_is_styled_and_newline_terminated(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        # Act
        u.Cli.commands_emit_success_message("all good", c.Cli.MessageTypes.SUCCESS)

        # Assert
        out = capsys.readouterr().out
        assert "all good" in out
        assert out != "all good\n"
        assert out.endswith("\n")

    def test_error_message_is_styled_and_newline_terminated(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        # Act
        u.Cli.commands_emit_error_message("boom")

        # Assert
        out = capsys.readouterr().out
        assert "boom" in out
        assert out != "boom\n"
        assert out.endswith("\n")


__all__: list[str] = ["TestsFlextCliCommands"]
