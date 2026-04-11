"""User interaction tools for CLI applications."""

from __future__ import annotations

import getpass
import os
from typing import Self, override

from pydantic import PrivateAttr

from flext_cli import (
    c,
    m,
    r,
    s,
    t,
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
            prompt_text = (
                f"{message}{c.Cli.PROMPT_CONFIRM_YES}"
                if default
                else f"{message}{c.Cli.PROMPT_CONFIRM_NO}"
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
            display_message = (
                f"{message}{c.Cli.PROMPT_DEFAULT_FMT.format(default=default)}"
                if default
                else message
            )
            raw = self._input_reader(f"{display_message}{c.Cli.PROMPT_SEP}").strip()
            value = raw or default
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
        if not choices:
            return r[str].fail(c.Cli.ERR_NO_CHOICES)
        if not self._state.interactive:
            if default and default in choices:
                return r[str].ok(default)
            return r[str].fail(c.Cli.ERR_INTERACTIVE_CHOICE_DISABLED)
        try:
            if default is None:
                return r[str].fail(
                    c.Cli.ERR_CHOICE_REQUIRED_FMT.format(
                        choices=", ".join(choices),
                    ),
                )
            if default not in choices:
                return r[str].fail(
                    c.Cli.ERR_INVALID_CHOICE_FMT.format(choice=default),
                )
            return r[str].ok(default)
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
            if len(password) < min_length:
                return r[str].fail(
                    c.Cli.ERR_PASSWORD_TOO_SHORT_FMT.format(
                        min_length=min_length,
                    ),
                )
            return r[str].ok(password)
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
        if self._test_env_override is not None:
            return self._test_env_override
        env_underscore = os.environ.get("_", "")
        return (
            os.environ.get("PYTEST_CURRENT_TEST") is not None
            or "pytest" in env_underscore.lower()
            or os.environ.get("CI") == "true"
        )

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
        yes_values = c.Cli.PROMPT_YES_VALUES
        no_values = c.Cli.PROMPT_NO_VALUES
        while True:
            text = self._input_reader(prompt_text).strip().lower()
            if not text:
                return r[bool].ok(default)
            if text in yes_values:
                return r[bool].ok(True)
            if text in no_values:
                return r[bool].ok(False)
            self._log(
                c.LogLevel.WARNING,
                c.Cli.ERR_INVALID_CONFIRM_INPUT,
                operation="confirm",
                prompt_message=message,
                user_input=text,
                consequence="Prompting again",
            )


__all__ = ["FlextCliPrompts"]
