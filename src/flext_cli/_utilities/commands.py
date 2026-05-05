"""CLI command helpers shared through ``u.Cli``."""

from __future__ import annotations

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
        match result:
            case None:
                return r[t.JsonValue].ok({
                    c.Cli.DICT_KEY_STATUS: c.Cli.CommandStatus.SUCCESS,
                    c.Cli.DICT_KEY_COMMAND: command_name,
                })
            case _ if result.success:
                return r[t.JsonValue].ok(u.normalize_to_json_value(result.value))
            case _:
                return r[t.JsonValue].fail(result.error or c.Cli.ERR_COMMAND_FAILED)

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
        normalized_value: t.JsonValue = u.normalize_to_json_value(result_value)
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
        """Emit success output as raw payload or styled CLI message."""
        rendered = (
            message
            if message.lstrip().startswith(("{", "["))
            else uo.output_message_payload(message, success_type)[0]
        )
        uo.emit_raw(f"{rendered}\n")

    @staticmethod
    def commands_emit_error_message(error: str) -> None:
        """Emit standardized CLI error output."""
        uo.emit_raw(
            f"{uo.output_message_payload(error, c.Cli.MessageTypes.ERROR)[0]}\n"
        )


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesCommands"]
