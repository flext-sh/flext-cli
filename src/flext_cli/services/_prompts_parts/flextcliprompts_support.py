"""Prompt service support primitives."""

from __future__ import annotations

import getpass
from typing import Annotated, Self

from flext_cli import c, m, p, r, s, t, u
from flext_cli._protocols.base import FlextCliProtocolsBase


class FlextCliPromptsSupport(s):
    """Support owner for prompt runtime state, logging, and input readers."""

    state: Annotated[
        m.Cli.PromptRuntimeState,
        m.Field(description="Prompt runtime state for interaction behavior."),
    ] = m.Field(default_factory=m.Cli.PromptRuntimeState)

    _input_reader: t.Cli.PromptTextReader = m.PrivateAttr(default_factory=lambda: input)

    _password_reader: t.Cli.PromptTextReader = m.PrivateAttr(
        default_factory=lambda: getpass.getpass
    )

    _test_env_override: bool | None = m.PrivateAttr(default_factory=lambda: None)

    def configure(self, state: m.Cli.PromptRuntimeState) -> Self:
        """Replace prompt runtime state using the canonical CLI model."""
        self.state = state
        return self

    def _fatal(
        self,
        operation: str,
        message: str,
        exc: Exception,
        consequence: str,
    ) -> None:
        self._log(
            c.LogLevel.ERROR,
            f"FATAL ERROR during {operation} - operation aborted",
            operation=operation,
            prompt_message=message,
            error=str(exc),
            error_type=type(exc).__name__,
            consequence=consequence,
            severity="critical",
        )

    def _is_test_env(self) -> bool:
        if self._test_env_override is not None:
            return self._test_env_override
        cli_settings: FlextCliProtocolsBase.CliSettings = self.settings.Cli
        return cli_settings.test_env

    def _log(
        self,
        log_level: str,
        message: str,
        **context: t.LogValue,
    ) -> None:
        match log_level:
            case c.LogLevel.DEBUG:
                self.logger.debug(message, **context)
            case c.LogLevel.ERROR:
                self.logger.error(message, **context)
            case c.LogLevel.WARNING:
                self.logger.warning(message, **context)
            case _:
                self.logger.info(message, **context)

    def _print_message(
        self,
        message: str,
        log_level: str,
        message_format: str,
        error_message_template: str,
    ) -> p.Result[bool]:
        try:
            formatted_message = message_format.format(message=message)
            self._log(log_level, formatted_message)
            return r[bool].ok(True)
        except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
            self.logger.exception(
                "FAILED to print message - operation aborted",
                operation="_print_message",
                log_level=log_level,
                prompt_message=message,
                error=str(exc),
                error_type=type(exc).__name__,
                consequence="Message not displayed",
            )
            return r[bool].fail(error_message_template.format(error=exc))

    def _read_confirmation_input(
        self,
        message: str,
        prompt_text: str,
        *,
        default: bool,
    ) -> p.Result[bool]:
        while True:
            input_text = self._input_reader(prompt_text)
            parsed = u.Cli.prompts_parse_confirmation(
                input_text,
                default=default,
            )
            if parsed is not None:
                return r[bool].ok(parsed)
            self._log(
                c.LogLevel.WARNING,
                c.Cli.ERR_INVALID_CONFIRM_INPUT,
                operation="confirm",
                prompt_message=message,
                user_input=input_text,
                consequence="Prompting again",
            )


__all__: list[str] = ["FlextCliPromptsSupport"]
