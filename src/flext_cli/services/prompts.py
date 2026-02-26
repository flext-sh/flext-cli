"""User interaction tools for CLI applications."""

from __future__ import annotations

import getpass
import os
import re
from collections.abc import Mapping

from flext_core import r
from pydantic import Field, PrivateAttr
from rich.errors import ConsoleError, LiveError, StyleError

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import FlextCliConstants
from flext_cli.models import m
from flext_cli.typings import t
from flext_cli.utilities import FlextCliUtilities

CLI = FlextCliConstants.Cli
PD, EM = CLI.PromptsDefaults, CLI.ErrorMessages
PM, PEM = CLI.PromptsMessages, CLI.PromptsErrorMessages
SOURCE_PATH = "flext-cli/src/flext_cli/prompts.py"


class FlextCliPrompts(FlextCliServiceBase):
    """CLI prompts service with validation, history, and non-interactive fallbacks."""

    interactive_mode: bool = Field(
        default=True, description="Enable interactive prompts"
    )
    quiet: bool = Field(default=False, description="Enable quiet mode")
    default_timeout: int = Field(
        default=CLI.TIMEOUTS.DEFAULT,
        description="Default timeout for prompt operations in seconds",
    )
    _prompt_history: list[str] = PrivateAttr(default_factory=list)

    def __init__(
        self,
        default_timeout: int = CLI.TIMEOUTS.DEFAULT,
        *,
        interactive_mode: bool = True,
        quiet: bool = False,
        **data: t.JsonValue,
    ) -> None:
        data["interactive_mode"] = interactive_mode and not quiet
        data["quiet"] = quiet
        data["default_timeout"] = default_timeout
        super().__init__()
        self.interactive_mode = bool(data.get("interactive_mode", True))
        self.quiet = bool(data.get("quiet"))
        timeout_raw = data.get("default_timeout")
        resolved_timeout_raw = (
            timeout_raw if isinstance(timeout_raw, int | str) else None
        )
        self.default_timeout = m.Cli.PromptTimeoutResolved(
            raw=resolved_timeout_raw,
            default=default_timeout,
        ).resolved
        self.logger.debug(
            "Initialized CLI prompts service",
            operation="__init__",
            interactive_mode=self.interactive_mode,
            quiet=self.quiet,
            default_timeout=self.default_timeout,
        )

    @property
    def prompt_history(self) -> list[str]:
        return self._prompt_history.copy()

    def _record(self, value: str) -> None:
        self._prompt_history.append(value)

    def _is_test_env(self) -> bool:
        env_underscore = os.environ.get("_", "")
        return (
            os.environ.get("PYTEST_CURRENT_TEST") is not None
            or "pytest" in env_underscore.lower()
            or os.environ.get("CI") == "true"
        )

    def _fatal(
        self, operation: str, message: str, exc: Exception, consequence: str
    ) -> None:
        self.logger.error(
            f"FATAL ERROR during {operation} - operation aborted",
            operation=operation,
            prompt_message=message,
            error=str(exc),
            error_type=type(exc).__name__,
            consequence=consequence,
            severity="critical",
        )

    def prompt_text(
        self,
        message: str,
        default: str = "",
        validation_pattern: str | None = None,
    ) -> r[str]:
        if not self.interactive_mode:
            if not default:
                return r[str].fail(EM.INTERACTIVE_MODE_DISABLED)
            if validation_pattern and not re.match(validation_pattern, default):
                return r[str].fail(
                    EM.DEFAULT_PATTERN_MISMATCH.format(pattern=validation_pattern),
                )
            return r[str].ok(default)
        try:
            self._record(message)
            if (
                validation_pattern
                and default
                and not re.match(validation_pattern, default)
            ):
                return r[str].fail(
                    EM.INPUT_PATTERN_MISMATCH.format(pattern=validation_pattern)
                )
            return r[str].ok(default)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as exc:
            self._fatal("prompt_text", message, exc, "Text prompt failed completely")
            return r[str].fail(EM.TEXT_PROMPT_FAILED.format(error=exc))

    def prompt_confirmation(self, message: str, *, default: bool = False) -> r[bool]:
        if not self.interactive_mode:
            return r[bool].ok(default)
        try:
            self._record(f"{message}{PD.CONFIRMATION_SUFFIX}")
            return r[bool].ok(default)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as exc:
            self._fatal(
                "prompt_confirmation",
                message,
                exc,
                "Confirmation prompt failed completely",
            )
            return r[bool].fail(EM.CONFIRMATION_PROMPT_FAILED.format(error=exc))

    def prompt_choice(
        self,
        message: str,
        choices: list[str],
        default: str | None = None,
    ) -> r[str]:
        if not choices:
            return r[str].fail(EM.NO_CHOICES_PROVIDED)
        if not self.interactive_mode:
            if default and default in choices:
                return r[str].ok(default)
            return r[str].fail(EM.INTERACTIVE_MODE_DISABLED_CHOICE)
        try:
            options = ", ".join(
                PD.CHOICE_LIST_FORMAT.format(index=index + 1, choice=choice)
                for index, choice in enumerate(choices)
            )
            self._record(
                PD.CHOICE_HISTORY_FORMAT.format(
                    message=message,
                    separator=PD.CHOICE_PROMPT_SEPARATOR,
                    options=options,
                ),
            )
            if default is None:
                return r[str].fail(
                    PEM.CHOICE_REQUIRED.format(choices=", ".join(choices))
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
                "prompt_choice", message, exc, "Choice prompt failed completely"
            )
            return r[str].fail(EM.CHOICE_PROMPT_FAILED.format(error=exc))

    def prompt_password(
        self,
        message: str = "Password:",
        min_length: int = CLI.FormattingDefaults.MIN_FIELD_LENGTH,
    ) -> r[str]:
        if not self.interactive_mode:
            return r[str].fail(EM.INTERACTIVE_MODE_DISABLED_PASSWORD)
        try:
            self._record(f"{message} [password hidden]")
            password = getpass.getpass(prompt=f"{message}{PD.PROMPT_SPACE_SUFFIX}")
            if len(password) < min_length:
                return r[str].fail(
                    EM.PASSWORD_TOO_SHORT_MIN.format(min_length=min_length)
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
                "prompt_password", message, exc, "Password prompt failed completely"
            )
            return r[str].fail(EM.PASSWORD_PROMPT_FAILED.format(error=exc))

    def clear_prompt_history(self) -> r[bool]:
        try:
            self._prompt_history.clear()
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
                "FAILED to clear prompt history - operation aborted",
                operation="clear_prompt_history",
                error=str(exc),
                error_type=type(exc).__name__,
                consequence="History may still contain entries",
            )
            return r[bool].fail(EM.HISTORY_CLEAR_FAILED.format(error=exc))

    def get_prompt_statistics(self) -> r[Mapping[str, t.JsonValue]]:
        try:
            size = len(self._prompt_history)
            stats_model = m.Cli.PromptStatistics(
                prompts_executed=size,
                interactive_mode=self.interactive_mode,
                default_timeout=self.default_timeout,
                history_size=size,
                timestamp=FlextCliUtilities.generate("timestamp"),
            )
            stats_dict: Mapping[str, t.JsonValue] = stats_model.model_dump(mode="json")
            return r[Mapping[str, t.JsonValue]].ok(stats_dict)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as exc:
            self.logger.exception(
                "FAILED to collect prompt statistics - operation aborted",
                operation="get_prompt_statistics",
                error=str(exc),
                error_type=type(exc).__name__,
                consequence="Statistics unavailable",
            )
            return r[Mapping[str, t.JsonValue]].fail(
                PEM.STATISTICS_COLLECTION_FAILED.format(error=exc),
            )

    def execute(self) -> r[Mapping[str, t.JsonValue]]:
        try:
            self.logger.debug(
                "Prompt service execution completed",
                operation="execute",
            )
            empty_result: Mapping[str, t.JsonValue] = {}
            return r[Mapping[str, t.JsonValue]].ok(empty_result)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as exc:
            self._fatal(
                "execute", "execute", exc, "Prompt service execution failed completely"
            )
            return r[Mapping[str, t.JsonValue]].fail(
                PEM.PROMPT_SERVICE_EXECUTION_FAILED.format(error=exc),
            )

    def prompt(self, message: str, default: str = "") -> r[str]:
        try:
            self._record(message)
            if self.quiet or not self.interactive_mode:
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
                    PD.PROMPT_LOG_FORMAT.format(message=message, input=value)
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

    def confirm(self, message: str, *, default: bool = False) -> r[bool]:
        try:
            if self.quiet or not self.interactive_mode:
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

    def _read_selection(self, options: list[str]) -> r[str]:
        count = len(options)
        while True:
            try:
                choice = input(PD.CHOICE_PROMPT_PREFIX.format(count=count)).strip()
                if not choice:
                    continue
                index = int(choice)
                if 1 <= index <= count:
                    return r[str].ok(options[index - 1])
            except ValueError:
                continue
            except KeyboardInterrupt:
                return r[str].fail(PM.USER_CANCELLED_SELECTION)
            except EOFError:
                return r[str].fail(PM.INPUT_STREAM_ENDED)

    def select_from_options(
        self, options: list[str], message: str = PD.DEFAULT_CHOICE_MESSAGE
    ) -> r[str]:
        try:
            values = [str(option) for option in options]
            self._record(
                PD.CHOICE_HISTORY_FORMAT.format(
                    message=message,
                    separator=PD.PROMPT_INPUT_SEPARATOR,
                    options=values,
                ),
            )
            if not values:
                return r[str].fail(PM.NO_OPTIONS_PROVIDED)
            if self.quiet or not self.interactive_mode:
                return r[str].ok(values[0])

            self.logger.info(PD.SELECTION_PROMPT.format(message=message))
            for idx, value in enumerate(values, 1):
                self.logger.info(PD.CHOICE_DISPLAY_FORMAT.format(num=idx, option=value))
            result = self._read_selection(values)
            if result.is_success:
                self.logger.info(
                    PM.USER_SELECTION_LOG.format(message=message, choice=result.value)
                )
            return result
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as exc:
            self._fatal(
                "select_from_options", message, exc, "Selection failed completely"
            )
            return r[str].fail(PEM.SELECTION_FAILED.format(error=exc))

    def print_status(
        self, message: str, status: str = CLI.MessageTypes.INFO.value
    ) -> r[bool]:
        try:
            self.logger.info(
                PD.STATUS_FORMAT.format(status=status.upper(), message=message)
            )
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
                "FAILED to print status message - operation aborted",
                operation="print_status",
                prompt_message=message,
                status=status,
                error=str(exc),
                error_type=type(exc).__name__,
                consequence="Status message not displayed",
            )
            return r[bool].fail(PEM.PRINT_STATUS_FAILED.format(error=exc))

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

    def print_success(self, message: str) -> r[bool]:
        return self._print_message(
            message, "info", PD.SUCCESS_FORMAT, PEM.PRINT_SUCCESS_FAILED
        )

    def print_error(self, message: str) -> r[bool]:
        return self._print_message(
            message, "error", PD.ERROR_FORMAT, PEM.PRINT_ERROR_FAILED
        )

    def print_warning(self, message: str) -> r[bool]:
        return self._print_message(
            message, "warning", PD.WARNING_FORMAT, PEM.PRINT_WARNING_FAILED
        )

    def print_info(self, message: str) -> r[bool]:
        return self._print_message(
            message, "info", PD.INFO_FORMAT, PEM.PRINT_INFO_FAILED
        )

    def create_progress(
        self, description: str = PD.DEFAULT_PROCESSING_DESCRIPTION
    ) -> r[str]:
        try:
            self._record(f"Progress: {description}")
            self.logger.info("Starting progress operation")
            self.logger.info(PM.STARTING_PROGRESS.format(description=description))
            self.logger.info(PM.CREATED_PROGRESS.format(description=description))
            return r[str].ok(description)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as exc:
            self.logger.exception(
                "FAILED to create progress indicator - operation aborted",
                operation="create_progress",
                description=description,
                error=str(exc),
                error_type=type(exc).__name__,
                consequence="Progress indicator not created",
            )
            return r[str].fail(PEM.PROGRESS_CREATION_FAILED.format(error=exc))

    def with_progress(
        self,
        items: list[t.JsonValue],
        description: str = PD.DEFAULT_PROCESSING_DESCRIPTION,
    ) -> r[list[t.JsonValue]]:
        try:
            total = len(items)
            self.logger.info("Starting progress operation with items")
            self._record(
                PM.PROGRESS_OPERATION.format(description=description, count=total)
            )
            self.logger.info(PM.PROCESSING.format(description=description, count=total))

            threshold = CLI.ProgressDefaults.REPORT_THRESHOLD
            if total > threshold:
                interval = max(1, total // threshold)
                if total % interval == 0:
                    progress = (total / total) * 100
                    self.logger.info(
                        PD.PROGRESS_FORMAT.format(
                            progress=progress, current=total, total=total
                        ),
                    )

            self.logger.info(PM.PROGRESS_COMPLETED.format(description=description))
            self.logger.info(
                PM.PROGRESS_COMPLETED_LOG.format(
                    description=description, processed=total
                )
            )
            return r[list[t.JsonValue]].ok(items)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as exc:
            self._fatal(
                "with_progress",
                description,
                exc,
                "Progress operation failed completely",
            )
            return r[list[t.JsonValue]].fail(
                PEM.PROGRESS_PROCESSING_FAILED.format(error=exc)
            )


__all__ = ["FlextCliPrompts"]
