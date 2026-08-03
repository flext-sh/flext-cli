"""Behavioral tests for ``u.Cli`` command messaging helpers.

Public contract under test (``flext_cli._utilities.commands`` via ``u.Cli``):

- ``commands_resolve_success_message`` returns the resolved success message
  string following the order: formatter > string value > mapping ``message``
  key > provided fallback.
- ``commands_emit_success_message`` writes JSON/array payloads verbatim and
  styles plain text with a success glyph, always terminated by a newline.
- ``commands_emit_result_error`` finalizes the complete failed Result state
  and a trailing newline.

Assertions target observable return values and emitted stdout only.
"""

from __future__ import annotations

import pytest

from flext_cli import r
from flext_tests import tm
from tests import c, t, u


class TestsFlextCliCommands:
    """Behavioral contract for the ``u.Cli`` command messaging helpers."""

    def test_formatter_result_wins_over_all_fallbacks(self) -> None:
        # Arrange
        """Verify that formatter result wins over all fallbacks."""

        def formatter(value: int) -> str:
            return str(value * 2)

        # Act
        resolved = u.Cli.commands_resolve_success_message(
            result_value=7, success_message="fallback", success_formatter=formatter
        )

        # Assert
        tm.that(resolved, eq="14")

    @pytest.mark.parametrize(
        ("result_value", "expected"),
        [
            pytest.param("direct", "direct", id="string-value-returned"),
            pytest.param(
                {c.Cli.DICT_KEY_MESSAGE: "mapped"}, "mapped", id="mapping-message-key"
            ),
            pytest.param(False, "fallback", id="bool-falls-back"),
            pytest.param("", "fallback", id="empty-string-falls-back"),
            pytest.param(
                {c.Cli.DICT_KEY_MESSAGE: ""},
                "fallback",
                id="empty-mapping-message-falls-back",
            ),
            pytest.param(
                {"other": "x"}, "fallback", id="mapping-without-message-key-falls-back"
            ),
            pytest.param([1, 2, 3], "fallback", id="list-falls-back"),
            pytest.param(0, "fallback", id="zero-falls-back"),
        ],
    )
    def test_resolve_without_formatter_follows_value_then_fallback_order(
        self, result_value: t.Cli.ResultValue, expected: str
    ) -> None:
        # Act
        """Verify that resolve without formatter follows value then fallback order."""
        resolved = u.Cli.commands_resolve_success_message(
            result_value=result_value,
            success_message="fallback",
            success_formatter=None,
        )

        # Assert
        tm.that(resolved, eq=expected)

    def test_resolve_returns_none_fallback_when_message_is_none(self) -> None:
        # Act
        """Verify that resolve returns none fallback when message is none."""
        resolved = u.Cli.commands_resolve_success_message(
            result_value=0, success_message=None, success_formatter=None
        )

        # Assert
        tm.that(resolved, none=True)

    @pytest.mark.parametrize(
        "payload",
        [
            pytest.param('{"ok": true}', id="json-object"),
            pytest.param("[1, 2, 3]", id="json-array"),
            pytest.param('   {"spaced": 1}', id="leading-whitespace-json"),
        ],
    )
    def test_structured_payload_is_emitted_verbatim_with_newline(
        self, payload: str, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Act
        """Verify that structured payload is emitted verbatim with newline."""
        u.Cli.commands_emit_success_message(payload, c.Cli.MessageTypes.SUCCESS)

        # Assert
        tm.that(capsys.readouterr().out, eq=f"{payload}\n")

    def test_plain_success_text_is_styled_and_newline_terminated(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Act
        """Verify that plain success text is styled and newline terminated."""
        u.Cli.commands_emit_success_message("all good", c.Cli.MessageTypes.SUCCESS)

        # Assert
        out = capsys.readouterr().out
        tm.that(out, has="all good")
        tm.that(out, ne="all good\n")
        tm.that(out.endswith("\n"), eq=True)

    def test_error_message_is_styled_and_newline_terminated(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Act
        """Verify that error message is styled and newline terminated."""
        u.Cli.commands_emit_result_error(r[str].fail("boom"))

        # Assert
        out = capsys.readouterr().out
        tm.that(out, has="boom")
        tm.that(out, ne="boom\n")
        tm.that(out.endswith("\n"), eq=True)

    def test_error_message_surfaces_code_without_traceback_in_normal_mode(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Act
        """Verify that error message surfaces code without traceback in normal mode."""
        result: r[str] = r[str].fail(
            "proposal config ausente: /x.yaml",
            error_code="missing_config",
            exception=FileNotFoundError("nope"),
        )
        u.Cli.commands_emit_result_error(result, verbose=False)

        # Assert
        out = capsys.readouterr().out
        tm.that(out, has="proposal config ausente: /x.yaml")
        tm.that(out, has="missing_config")
        tm.that("Traceback" not in out, eq=True)
        tm.that("FileNotFoundError" not in out, eq=True)

    def test_error_message_adds_traceback_in_verbose_mode(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange
        """Verify that error message adds traceback in verbose mode."""
        try:
            error_message = "nope"
            raise FileNotFoundError(error_message)
        except FileNotFoundError as exc:
            captured_exception: BaseException = exc

        # Act
        result: r[str] = r[str].fail(
            "proposal config ausente: /x.yaml",
            error_code="missing_config",
            exception=captured_exception,
        )
        u.Cli.commands_emit_result_error(result, verbose=True)

        # Assert
        out = capsys.readouterr().out
        tm.that(out, has="missing_config")
        tm.that(out, has="FileNotFoundError")
        tm.that(out, has="Traceback (most recent call last)")


__all__: list[str] = ["TestsFlextCliCommands"]
