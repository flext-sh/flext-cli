"""CLI command helpers shared through ``u.Cli``."""

from __future__ import annotations

from flext_cli import c, p, t
from flext_cli._utilities.output import FlextCliUtilitiesOutput as uo
from flext_core import u


class FlextCliUtilitiesCommands:
    """Helpers for result-command messaging in the public Typer DSL."""

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
