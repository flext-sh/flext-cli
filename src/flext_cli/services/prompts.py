"""User interaction tools for CLI applications."""

from __future__ import annotations

import getpass
import os
from collections.abc import Mapping
from typing import override

from flext_core import r
from pydantic import PrivateAttr
from rich.errors import ConsoleError, LiveError, StyleError

from flext_cli import (
    FlextCliConstants,
    FlextCliServiceBase,
    FlextCliTypes,
    m,
    t,
)

PD, EM = (FlextCliConstants.Cli.PromptsDefaults, FlextCliConstants.Cli.ErrorMessages)
PM, PEM = (
    FlextCliConstants.Cli.PromptsMessages,
    FlextCliConstants.Cli.PromptsErrorMessages,
)
SOURCE_PATH = "flext-cli/src/flext_cli/prompts.py"


class FlextCliPrompts(FlextCliServiceBase):
    """CLI prompts service with validation, history, and non-interactive fallbacks."""

    _interactive_mode: bool = PrivateAttr(default=True)
    _quiet: bool = PrivateAttr(default=False)
    _default_timeout: int = PrivateAttr(
        default=FlextCliConstants.Cli.TIMEOUTS.DEFAULT,
    )

    def __init__(
        self,
        default_timeout: int = FlextCliConstants.Cli.TIMEOUTS.DEFAULT,
        *,
        interactive_mode: bool = True,
        quiet: bool = False,
        **data: t.Scalar,
    ) -> None:
        data["interactive_mode"] = interactive_mode and (not quiet)
        data["quiet"] = quiet
        data["default_timeout"] = default_timeout
        super().__init__(
            config_type=None,
            config_overrides=None,
            initial_context=None,
        )
        self._interactive_mode = bool(data.get("interactive_mode", True))
        self._quiet = bool(data.get("quiet"))
        timeout_raw = data.get("default_timeout")
        resolved_timeout_raw = (
            timeout_raw if isinstance(timeout_raw, int | str) else None
        )
        self._default_timeout = m.Cli.PromptTimeoutResolved(
            raw=resolved_timeout_raw,
            default=default_timeout,
        ).resolve()
        self.logger.debug(
            "Initialized CLI prompts service",
            operation="__init__",
            interactive_mode=self._interactive_mode,
            quiet=self._quiet,
            default_timeout=self._default_timeout,
        )

    def confirm(self, message: str, *, default: bool = False) -> r[bool]:
        try:
            if self._quiet or not self._interactive_mode:
                return r[bool].ok(default)
            prompt_text = (
                f"{message}{PD.CONFIRMATION_YES_PROMPT}"
                if default
                else f"{message}{PD.CONFIRMATION_NO_PROMPT}"
            )
            return self._read_confirmation_input(message, prompt_text, default=default)
        except KeyboardInterrupt:
            return r[bool].fail(PM.USER_CANCELLED_CONFIRMATION)
        except EOFError:
            return r[bool].fail(PM.INPUT_STREAM_ENDED)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as exc:
            self._fatal("confirm", message, exc, "Confirmation failed completely")
            return r[bool].fail(PEM.CONFIRMATION_FAILED.format(error=exc))

    @override
    def execute(self) -> r[Mapping[str, FlextCliTypes.Cli.JsonValue]]:
        try:
            self.logger.debug("Prompt service execution completed", operation="execute")
            empty_result: Mapping[str, FlextCliTypes.Cli.JsonValue] = {}
            return r[Mapping[str, FlextCliTypes.Cli.JsonValue]].ok(empty_result)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as exc:
            self._fatal(
                "execute",
                "execute",
                exc,
                "Prompt service execution failed completely",
            )
            return r[Mapping[str, FlextCliTypes.Cli.JsonValue]].fail(
                PEM.PROMPT_SERVICE_EXECUTION_FAILED.format(error=exc),
            )

    def print_error(self, message: str) -> r[bool]:
        return self._print_message(
            message,
            "error",
            PD.ERROR_FORMAT,
            PEM.PRINT_ERROR_FAILED,
        )

    def print_success(self, message: str) -> r[bool]:
        return self._print_message(
            message,
            "info",
            PD.SUCCESS_FORMAT,
            PEM.PRINT_SUCCESS_FAILED,
        )

    def print_warning(self, message: str) -> r[bool]:
        return self._print_message(
            message,
            "warning",
            PD.WARNING_FORMAT,
            PEM.PRINT_WARNING_FAILED,
        )

    def prompt(self, message: str, default: str = "") -> r[str]:
        try:
            if self._quiet or not self._interactive_mode:
                return r[str].ok(default)
            display_message = (
                f"{message}{PD.PROMPT_DEFAULT_FORMAT.format(default=default)}"
                if default
                else message
            )
            raw = input(f"{display_message}{PD.PROMPT_INPUT_SEPARATOR}").strip()
            value = raw or default
            if not self._is_test_env():
                self.logger.info(
                    PD.PROMPT_LOG_FORMAT.format(message=message, input=value),
                )
            return r[str].ok(value)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as exc:
            self._fatal("prompt", message, exc, "Prompt failed completely")
            return r[str].fail(PEM.PROMPT_FAILED.format(error=exc))

    def prompt_choice(
        self,
        message: str,
        choices: t.StrSequence,
        default: str | None = None,
    ) -> r[str]:
        if not choices:
            return r[str].fail(EM.NO_CHOICES_PROVIDED)
        if not self._interactive_mode:
            if default and default in choices:
                return r[str].ok(default)
            return r[str].fail(EM.INTERACTIVE_MODE_DISABLED_CHOICE)
        try:
            if default is None:
                return r[str].fail(
                    PEM.CHOICE_REQUIRED.format(choices=", ".join(choices)),
                )
            if default not in choices:
                return r[str].fail(EM.INVALID_CHOICE.format(selected=default))
            return r[str].ok(default)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as exc:
            self._fatal(
                "prompt_choice",
                message,
                exc,
                "Choice prompt failed completely",
            )
            return r[str].fail(EM.CHOICE_PROMPT_FAILED.format(error=exc))

    def prompt_password(
        self,
        message: str = "Password:",
        min_length: int = FlextCliConstants.Cli.FormattingDefaults.MIN_FIELD_LENGTH,
    ) -> r[str]:
        if not self._interactive_mode:
            return r[str].fail(EM.INTERACTIVE_MODE_DISABLED_PASSWORD)
        try:
            password = getpass.getpass(prompt=f"{message}{PD.PROMPT_SPACE_SUFFIX}")
            if len(password) < min_length:
                return r[str].fail(
                    EM.PASSWORD_TOO_SHORT_MIN.format(min_length=min_length),
                )
            return r[str].ok(password)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as exc:
            self._fatal(
                "prompt_password",
                message,
                exc,
                "Password prompt failed completely",
            )
            return r[str].fail(EM.PASSWORD_PROMPT_FAILED.format(error=exc))

    def _fatal(
        self,
        operation: str,
        message: str,
        exc: Exception,
        consequence: str,
    ) -> None:
        self.logger.error(
            "FATAL ERROR during %s - operation aborted",
            operation,
            operation=operation,
            prompt_message=message,
            error=str(exc),
            error_type=type(exc).__name__,
            consequence=consequence,
            severity="critical",
        )

    def _is_test_env(self) -> bool:
        env_underscore = os.environ.get("_", "")
        return (
            os.environ.get("PYTEST_CURRENT_TEST") is not None
            or "pytest" in env_underscore.lower()
            or os.environ.get("CI") == "true"
        )

    def _print_message(
        self,
        message: str,
        log_level: str,
        message_format: str,
        error_message_template: str,
    ) -> r[bool]:
        try:
            formatted_message = message_format.format(message=message)
            match log_level:
                case "error":
                    self.logger.error(formatted_message)
                case "warning":
                    self.logger.warning(formatted_message)
                case _:
                    self.logger.info(formatted_message)
            return r[bool].ok(value=True)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as exc:
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
        yes_values = {"y", "yes"}
        no_values = {"n", "no"}
        while True:
            text = input(prompt_text).strip().lower()
            if not text:
                return r[bool].ok(default)
            if text in yes_values:
                return r[bool].ok(value=True)
            if text in no_values:
                return r[bool].ok(False)
            self.logger.warning(
                "Invalid confirmation input - please enter yes or no",
                operation="confirm",
                prompt_message=message,
                user_input=text,
                consequence="Prompting again",
            )


__all__ = ["FlextCliPrompts"]
