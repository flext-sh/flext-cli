"""CLI command helpers shared through ``u.Cli``."""

from __future__ import annotations

import traceback

# mro-j47u (codex): formatter contracts are owned once by the t facade.
from flext_cli import c, t
from flext_cli._utilities.output import FlextCliUtilitiesOutput as uo
from flext_core import u


class FlextCliUtilitiesCommands:
    """Helpers for result-command messaging in the public Typer DSL."""

    @staticmethod
    def commands_resolve_success_message[TResult: t.Cli.ResultValue](
        *,
        result_value: TResult,
        success_message: str | None,
        success_formatter: t.Cli.SuccessMessageFormatter[TResult] | None,
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
        message: str, success_type: c.Cli.MessageTypes
    ) -> None:
        """Emit success output as raw payload or styled CLI message."""
        rendered = (
            message
            if message.lstrip().startswith(("{", "["))
            else uo.output_message_payload(message, success_type)[0]
        )
        uo.emit_raw(f"{rendered}\n")

    @staticmethod
    def commands_emit_error_message(
        error: str,
        *,
        error_code: str | None = None,
        exception: BaseException | None = None,
        verbose: bool = False,
    ) -> None:
        """Emit standardized CLI error output and log it via flext-core."""
        logger = u.fetch_logger(__name__)
        if isinstance(exception, Exception):
            logger.exception(error, error_code=error_code, exception=exception)
        else:
            logger.error(error, error_code=error_code)
        uo.emit_raw(
            f"{uo.output_message_payload(error, c.Cli.MessageTypes.ERROR)[0]}\n"
        )
        if error_code:
            uo.emit_raw(f"   [{error_code}]\n")
        if verbose and exception is not None:
            detail = "".join(
                traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                )
            )
            uo.emit_raw(detail if detail.endswith("\n") else f"{detail}\n")


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesCommands"]
