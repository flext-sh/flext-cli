"""CLI command helpers shared through ``u.Cli``."""

from __future__ import annotations

from collections.abc import (
    Callable,
)

from flext_cli import FlextCliUtilitiesJson as uj, c, p, r, t


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


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesCommands"]
