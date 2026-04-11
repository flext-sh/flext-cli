"""User interaction tools for CLI applications."""

from __future__ import annotations

import getpass
from typing import Self, override

from pydantic import PrivateAttr

from flext_cli import (
    c,
    m,
    r,
    s,
    t,
    u,
)


class FlextCliPrompts(s):
    """CLI prompts service with validation, history, and non-interactive fallbacks."""

    _state: m.Cli.PromptRuntimeState = PrivateAttr(
        default_factory=m.Cli.PromptRuntimeState,
    )
    _input_reader: t.Cli.PromptTextReader = PrivateAttr(default_factory=lambda: input)
    _password_reader: t.Cli.PromptTextReader = PrivateAttr(
        default_factory=lambda: getpass.getpass
    )
    _test_env_override: bool | None = PrivateAttr(default=None)

    def configure(self, state: m.Cli.PromptRuntimeState) -> Self:
        """Replace prompt runtime state using the canonical CLI model."""
        self._state = state
        return self

    def confirm(self, message: str, *, default: bool = False) -> r[bool]:
        try:
            if self._state.quiet or not self._state.interactive:
                return r[bool].ok(default)
            prompt_text = u.Cli.prompts_confirmation_text(
                message,
                default=default,
            )
            return self._read_confirmation_input(message, prompt_text, default=default)
        except KeyboardInterrupt:
            return r[bool].fail(c.Cli.ERR_USER_CANCELLED_CONFIRMATION)
        except EOFError:
            return r[bool].fail(c.Cli.ERR_INPUT_STREAM_ENDED)
        except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
            self._fatal("confirm", message, exc, "Confirmation failed completely")
            return r[bool].fail(
                c.Cli.ERR_CONFIRMATION_FAILED_FMT.format(error=exc),
            )

    @override
    def execute(self) -> r[t.Cli.JsonMapping]:
        try:
            self._log(
                c.LogLevel.DEBUG,
                "Prompt service execution completed",
                operation="execute",
            )
            empty_result: t.Cli.JsonMapping = {}
            return r[t.Cli.JsonMapping].ok(empty_result)
        except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
            self._fatal(
                "execute",
                "execute",
                exc,
                "Prompt service execution failed completely",
            )
            return r[t.Cli.JsonMapping].fail(
                f"Prompt service execution failed: {exc}",
            )

    def print_error(self, message: str) -> r[bool]:
        return self._print_message(
            message,
            c.LogLevel.ERROR,
            c.Cli.PROMPT_ERROR_FMT,
            "Print error failed: {error}",
        )

    def print_success(self, message: str) -> r[bool]:
        return self._print_message(
            message,
            c.LogLevel.INFO,
            c.Cli.PROMPT_SUCCESS_FMT,
            "Print success failed: {error}",
        )

    def print_warning(self, message: str) -> r[bool]:
        return self._print_message(
            message,
            c.LogLevel.WARNING,
            c.Cli.PROMPT_WARNING_FMT,
            "Print warning failed: {error}",
        )

    def prompt(self, message: str, default: str = "") -> r[str]:
        try:
            if self._state.quiet or not self._state.interactive:
                return r[str].ok(default)
            display_message = u.Cli.prompts_display_message(message, default)
            raw = self._input_reader(f"{display_message}{c.Cli.PROMPT_SEP}")
            value = u.Cli.prompts_effective_text(raw, default)
            if not self._is_test_env():
                self._log(
                    c.LogLevel.INFO,
                    c.Cli.PROMPT_LOG_FMT.format(message=message, input=value),
                )
            return r[str].ok(value)
        except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
            self._fatal("prompt", message, exc, "Prompt failed completely")
            return r[str].fail(c.Cli.ERR_PROMPT_FAILED_FMT.format(error=exc))

    def prompt_choice(
        self,
        message: str,
        choices: t.StrSequence,
        default: str | None = None,
    ) -> r[str]:
        try:
            return u.Cli.prompts_choice_result(
                interactive=self._state.interactive,
                choices=choices,
                default=default,
            )
        except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
            self._fatal(
                "prompt_choice",
                message,
                exc,
                "Choice prompt failed completely",
            )
            return r[str].fail(
                c.Cli.ERR_CHOICE_PROMPT_FAILED_FMT.format(error=exc),
            )

    def prompt_password(
        self,
        message: str = "Password:",
        min_length: int = c.Cli.PROMPT_MIN_PASSWORD_LENGTH,
    ) -> r[str]:
        if not self._state.interactive:
            return r[str].fail(c.Cli.ERR_INTERACTIVE_PASSWORD_DISABLED)
        try:
            password = self._password_reader(f"{message}{c.Cli.PROMPT_SPACE}")
            return u.Cli.prompts_password_result(password, min_length=min_length)
        except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
            self._fatal(
                "prompt_password",
                message,
                exc,
                "Password prompt failed completely",
            )
            return r[str].fail(
                c.Cli.ERR_PASSWORD_PROMPT_FAILED_FMT.format(error=exc),
            )

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
        return u.Cli.prompts_is_test_env(test_override=self._test_env_override)

    def _log(
        self,
        log_level: str,
        message: str,
        **context: t.RuntimeData | Exception,
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
    ) -> r[bool]:
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
    ) -> r[bool]:
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


__all__ = ["FlextCliPrompts"]
