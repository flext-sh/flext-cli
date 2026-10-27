"""Behavioral tests for ``u.Cli`` command messaging helpers.

Public contract under test (``flext_cli._utilities.commands`` via ``u.Cli``):

- ``commands_resolve_success_message`` returns the resolved success message
  string following the order: formatter > string value > mapping ``message``
  key > provided fallback.
- ``commands_emit_success_message`` writes JSON/array payloads verbatim and
  styles plain text with a success glyph, always terminated by a newline.
- ``commands_emit_result_error`` finalizes the complete failed Result state
  and a trailing newline.

Assertions target returned values, stdout results, and stderr diagnostics.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Iterator
from io import StringIO

import pytest

from tests import c, m, p, r, t, tm, u


@pytest.mark.usefixtures("synchronous_logging")
class TestsFlextCliCommands:
    """Behavioral contract for the ``u.Cli`` command messaging helpers."""

    @staticmethod
    @pytest.fixture
    def synchronous_logging(
        capsys: pytest.CaptureFixture[str],
    ) -> Iterator[None]:
        """Restore the elected provider and composition after each test."""
        original_settings = u.logging_settings()
        original_options = u.logging_options()
        u.configure_structlog(
            settings=m.StructlogOptions(async_logging=False),
            runtime_settings=original_settings.clone(async_logging=False, trace=False),
        )
        try:
            yield
        finally:
            _ = capsys.readouterr()
            u.configure_structlog(
                settings=original_options,
                runtime_settings=original_settings,
            )

    @staticmethod
    def test_formatter_result_wins_over_all_fallbacks() -> None:
        # Arrange
        """Verify that formatter result wins over all fallbacks."""

        def formatter(value: int) -> str:
            return str(value * 2)

        # Act
        resolved = u.Cli.commands_resolve_success_message(
            result_value=7,
            success_message="fallback",
            success_formatter=formatter,
        )

        # Assert
        tm.that(resolved, eq="14")

    @staticmethod
    @pytest.mark.parametrize(
        ("result_value", "expected"),
        [
            pytest.param("direct", "direct", id="string-value-returned"),
            pytest.param(
                {c.Cli.DICT_KEY_MESSAGE: "mapped"},
                "mapped",
                id="mapping-message-key",
            ),
            pytest.param(False, "fallback", id="bool-falls-back"),
            pytest.param("", "fallback", id="empty-string-falls-back"),
            pytest.param(
                {c.Cli.DICT_KEY_MESSAGE: ""},
                "fallback",
                id="empty-mapping-message-falls-back",
            ),
            pytest.param(
                {"other": "x"},
                "fallback",
                id="mapping-without-message-key-falls-back",
            ),
            pytest.param([1, 2, 3], "fallback", id="list-falls-back"),
            pytest.param(0, "fallback", id="zero-falls-back"),
        ],
    )
    def test_resolve_without_formatter_follows_value_then_fallback_order(
        result_value: t.Cli.ResultValue,
        expected: str,
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

    @staticmethod
    def test_resolve_returns_none_fallback_when_message_is_none() -> None:
        # Act
        """Verify that resolve returns none fallback when message is none."""
        resolved = u.Cli.commands_resolve_success_message(
            result_value=0,
            success_message=None,
            success_formatter=None,
        )

        # Assert
        tm.that(resolved, none=True)

    @staticmethod
    @pytest.mark.parametrize(
        "payload",
        [
            pytest.param('{"ok": true}', id="json-object"),
            pytest.param("[1, 2, 3]", id="json-array"),
            pytest.param('   {"spaced": 1}', id="leading-whitespace-json"),
        ],
    )
    def test_structured_payload_is_emitted_verbatim_with_newline(
        payload: str,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        # Act
        """Verify that structured payload is emitted verbatim with newline."""
        u.Cli.commands_emit_success_message(payload, c.Cli.MessageTypes.SUCCESS)

        # Assert
        tm.that(capsys.readouterr().out, eq=f"{payload}\n")

    @staticmethod
    def test_plain_success_text_is_styled_and_newline_terminated(
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        # Act
        """Verify that plain success text is styled and newline terminated."""
        u.Cli.commands_emit_success_message("all good", c.Cli.MessageTypes.SUCCESS)

        # Assert
        out = capsys.readouterr().out
        tm.that(out, has="all good")
        tm.that(out, ne="all good\n")
        tm.ok(out.endswith("\n"))

    @staticmethod
    def test_error_message_is_styled_and_newline_terminated(
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        # Act
        """Verify that error message is styled and newline terminated."""
        u.Cli.commands_emit_result_error(r[str].fail("boom"))

        # Assert
        captured = capsys.readouterr()
        out = captured.err
        tm.that(out, has="boom")
        tm.that(out, ne="boom\n")
        tm.ok(out.endswith("\n"))
        tm.that(captured.out, eq="")

    @staticmethod
    def test_error_message_surfaces_code_without_traceback_in_normal_mode(
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        # Act
        """Verify that error message surfaces code without traceback in normal mode."""
        result = r[str].fail(
            "proposal config ausente: /x.yaml",
            error_code="missing_config",
            exception=FileNotFoundError("nope"),
        )
        u.Cli.commands_emit_result_error(result)

        # Assert
        captured = capsys.readouterr()
        out = captured.err
        tm.that(out, has="proposal config ausente: /x.yaml")
        tm.that(out, has="missing_config")
        tm.ok("Traceback" not in out)
        tm.ok("stack_trace" not in out)
        tm.that(captured.out, eq="")

    @staticmethod
    @pytest.mark.parametrize("trace", [False, True])
    @pytest.mark.parametrize(
        "exception",
        [FileNotFoundError("missing source.py"), KeyboardInterrupt("cancelled")],
    )
    def test_error_message_uses_core_detail_and_original_cause(
        capsys: pytest.CaptureFixture[str],
        exception: BaseException,
        *,
        trace: bool,
    ) -> None:
        """Core renders detail once and observers receive the original cause."""
        with pytest.raises(type(exception)) as caught:
            raise exception
        original_exception = caught.value
        native_stream = StringIO()
        records: t.MutableSequenceOf[p.LoggingRecord] = []

        def observe(event: p.LoggingRecord) -> None:
            records.append(event)

        u.configure_structlog(
            settings=m.StructlogOptions(
                handlers=(u.create_logging_handler(stream=native_stream),),
                observers=(observe,),
            ),
            runtime_settings=u.logging_settings().clone(
                log_level=c.LogLevel.ERROR,
                debug=False,
                trace=trace,
                async_logging=False,
            ),
        )
        result = r[str].fail(
            "source read failed",
            error_code="missing_config",
            exception=original_exception,
        )
        u.Cli.commands_emit_result_error(result)

        captured = capsys.readouterr()
        tm.that(captured.out, eq="")
        tm.that(captured.err, has="missing_config")
        tm.that(len(records), eq=1)
        tm.ok(records[0].exception is original_exception)
        tm.that("stack_trace" in records[0].context, eq=trace)
        native_event = m.ConfigMap.model_validate_json(native_stream.getvalue()).root
        tm.that(native_event[c.HandlerType.EVENT], eq=result.error)
        tm.that(native_event["exception_type"], eq=type(original_exception).__name__)
        tm.that("stack_trace" in native_event, eq=trace)
        serialized = m.LoggingRecord.model_validate(records[0], from_attributes=True)
        tm.fail("exception" in serialized.model_dump())
        tm.ok(result.exception is original_exception)
