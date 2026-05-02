"""CLI command helpers shared through ``u.Cli``."""

from __future__ import annotations

import click

from flext_cli import FlextCliUtilitiesOutput as uo, c, p, r, t
from flext_core import u


class FlextCliUtilitiesCommands:
    """Helpers for normalizing command-handler outputs."""

    @staticmethod
    def commands_normalize_handler_result(
        result: p.Result[t.JsonPayload] | None,
        command_name: str,
    ) -> p.Result[t.JsonValue]:
        """Normalize command execution output into canonical JSON result."""
        if result is None:
            payload: t.JsonValue = {
                "status": c.Cli.CommandStatus.SUCCESS,
                "command": command_name,
            }
            return r[t.JsonValue].ok(payload)
        if result.success:
            result_value: t.JsonValue = u.normalize_to_json_value(
                result.value,
            )
            return r[t.JsonValue].ok(result_value)
        error_value = result.error
        return r[t.JsonValue].fail(
            error_value or "Command failed",
        )

    @staticmethod
    def commands_resolve_success_message[TResult: t.Cli.ResultValue](
        *,
        result_value: TResult,
        success_message: str | None,
        success_formatter: p.Cli.SuccessMessageFormatter[TResult] | None,
    ) -> str | None:
        """Resolve success message using formatter/value fallback order."""
        if success_formatter is not None:
            formatted: str = success_formatter(result_value)
            return formatted if isinstance(formatted, str) else str(formatted)
        if hasattr(result_value, "message"):
            candidate = getattr(result_value, "message", None)
            if isinstance(candidate, str) and candidate:
                return candidate
        if isinstance(result_value, str) and result_value:
            return result_value
        return success_message

    @staticmethod
    def commands_emit_success_message(
        message: str,
        success_type: c.Cli.MessageTypes,
    ) -> None:
        """Emit success output as raw payload or styled CLI message."""
        if message.lstrip().startswith(("{", "[")):
            click.echo(message)
            return
        payload, _ = uo.output_message_payload(
            message,
            success_type,
        )
        uo.emit_raw(f"{payload}\n")

    @staticmethod
    def commands_emit_error_message(error: str) -> None:
        """Emit standardized CLI error output."""
        payload, _ = uo.output_message_payload(
            error,
            c.Cli.MessageTypes.ERROR,
        )
        uo.emit_raw(f"{payload}\n")


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesCommands"]
