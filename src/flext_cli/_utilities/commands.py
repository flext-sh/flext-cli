"""CLI command helpers shared through ``u.Cli``."""

from __future__ import annotations

from collections.abc import (
    Callable,
)

import click

from flext_cli import FlextCliUtilitiesJson as uj, c, p, r, t
from flext_cli._utilities.output import FlextCliUtilitiesOutput


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
            result_value: t.JsonValue = uj.normalize_json_value(
                result.value,
            )
            return r[t.JsonValue].ok(result_value)
        error_value = result.error
        return r[t.JsonValue].fail(
            str(error_value) if error_value else "Command failed",
        )

    @staticmethod
    def commands_execute_handler(
        *,
        command_name: str,
        handler: t.Cli.JsonCommandFn,
        args: t.StrSequence | None,
        kwargs: t.ScalarMapping,
        on_signature_mismatch: Callable[[str], None] | None = None,
    ) -> p.Result[t.JsonValue]:
        """Execute one command handler with optional args fallback and normalize output."""
        try:
            result: p.Result[t.JsonPayload] | None = None
            execution_attempted = False
            if args or kwargs:
                try:
                    result = handler(*args, **kwargs) if args else handler(**kwargs)
                    execution_attempted = True
                except TypeError as exc:
                    if on_signature_mismatch is not None:
                        on_signature_mismatch(str(exc))
            if not execution_attempted:
                result = handler()
            return FlextCliUtilitiesCommands.commands_normalize_handler_result(
                result,
                command_name,
            )
        except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
            return r[t.JsonValue].fail(
                c.Cli.ERR_COMMAND_EXECUTION_FAILED.format(error=exc),
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
            formatted: object = success_formatter(result_value)
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
        payload, _ = FlextCliUtilitiesOutput.output_message_payload(
            message,
            success_type,
        )
        FlextCliUtilitiesOutput.emit_raw(f"{payload}\n")

    @staticmethod
    def commands_emit_error_message(error: str) -> None:
        """Emit standardized CLI error output."""
        payload, _ = FlextCliUtilitiesOutput.output_message_payload(
            error,
            c.Cli.MessageTypes.ERROR,
        )
        FlextCliUtilitiesOutput.emit_raw(f"{payload}\n")


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesCommands"]
