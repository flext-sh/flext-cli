"""CLI command helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import FlextRuntime, u

from flext_cli import c, r, t
from flext_cli._utilities import FlextCliUtilitiesOutput

if TYPE_CHECKING:
    from flext_cli import p


class FlextCliUtilitiesCommands:
    """Helpers for result-command messaging in the public Typer DSL."""

    @staticmethod
    def commands_resolve_success_message[TResult: t.JsonPayload](
        *,
        result_value: TResult,
        success_message: str | None,
        success_formatter: t.Cli.SuccessMessageFormatter[TResult] | None,
    ) -> str | None:
        """Resolve success message using formatter/value fallback order.

        The explicit formatter wins; otherwise a message key or string payload
        supplies the text, and the configured message is the final fallback.

        Args:
            result_value: Command result value inspected for embedded text.
            success_message: Configured fallback message when the value carries none.
            success_formatter: Optional formatter applied to the result value first.

        Returns:
            The resolved success message, or None when no source supplies one.

        """
        if success_formatter is not None:
            formatted: str = success_formatter(result_value)
            return formatted
        normalized_value: t.JsonValue = FlextRuntime.normalize_to_json_value(
            result_value
        )
        match normalized_value:
            case {c.Cli.DICT_KEY_MESSAGE: str() as candidate} if candidate:
                return candidate
            case str() as candidate if candidate:
                return candidate
            case _:
                return success_message

    @staticmethod
    def commands_emit_success_message(
        message: str,
        success_type: c.Cli.MessageTypes,
    ) -> None:
        """Emit success output as raw payload or styled CLI message.

        JSON-shaped payloads print verbatim; every other message renders
        through the canonical styled message payload.

        Args:
            message: Success text or raw JSON payload to emit.
            success_type: Canonical message style for non-JSON messages.

        """
        rendered = (
            message
            if message.lstrip().startswith(("{", "["))
            else FlextCliUtilitiesOutput.output_message_payload(message, success_type)[
                0
            ]
        )
        FlextCliUtilitiesOutput.emit_raw(f"{rendered}\n")

    @staticmethod
    def commands_emit_failure_cause[TResult](
        result: p.Result[TResult],
    ) -> None:
        """Render rejected-input diagnostics without contaminating result stdout."""
        error = r.require_error(result)
        FlextCliUtilitiesOutput.emit_raw(
            "{}\n".format(
                FlextCliUtilitiesOutput.output_message_payload(
                    error,
                    c.Cli.MessageTypes.ERROR,
                )[0],
            ),
            error=True,
        )

    @staticmethod
    def commands_emit_result_error[TResult](
        result: p.Result[TResult],
    ) -> None:
        """Finalize one failed Result through structured logging and CLI output.

        Args:
            result: Failed result whose error is logged and rendered.

        """
        # NOTE (multi-agent): keep the canonical Result intact through every
        # service layer; only this outer CLI boundary exposes its failure state.
        error = r.require_error(result)
        u.failure(
            error,
            exception=result.exception,
            error_code=result.error_code,
            error_data=result.error_data,
        )
        FlextCliUtilitiesOutput.emit_raw(
            "{}\n".format(
                FlextCliUtilitiesOutput.output_message_payload(
                    error,
                    c.Cli.MessageTypes.ERROR,
                )[0],
            ),
            error=True,
        )
        if result.error_code:
            FlextCliUtilitiesOutput.emit_raw(f"   [{result.error_code}]\n", error=True)


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesCommands"]
