"""Prompt service support primitives.

Input-port failures are not caught here: the reader's exception escapes the
prompt method with its cause. Only declared prompt outcomes return ``r``.
"""

from __future__ import annotations

import getpass
from typing import Annotated, Self

from flext_cli import c, m, p, r, s, settings, t, u


class _PromptInputReaderDefault:
    """Resolve the built-in input reader without storing a method descriptor."""

    def __call__(self, prompt: str) -> str:
        return input(prompt)


class _PromptPasswordReaderDefault:
    """Resolve the password reader without storing a method descriptor."""

    def __call__(self, prompt: str) -> str:
        return getpass.getpass(prompt)


class FlextCliPromptsSupport(s[m.Cli.RuntimeStatus]):
    """Support owner for prompt runtime state, logging, and input readers."""

    state: Annotated[
        m.Cli.PromptRuntimeState,
        m.Field(description="Prompt runtime state for interaction behavior."),
    ] = m.Field(m.Cli.PromptRuntimeState(), validate_default=True)

    input_reader: Annotated[
        t.Cli.PromptTextReader,
        m.Field(
            description=(
                "Text input port; reads the process stdin unless the embedding "
                "application injects its own source."
            ),
            exclude=True,
        ),
    ] = m.Field(default_factory=_PromptInputReaderDefault, validate_default=True)

    password_reader: Annotated[
        t.Cli.PromptTextReader,
        m.Field(
            description=(
                "Secret input port; reads the terminal without echo unless the "
                "embedding application injects its own source."
            ),
            exclude=True,
        ),
    ] = m.Field(default_factory=_PromptPasswordReaderDefault, validate_default=True)

    def configure(self, state: m.Cli.PromptRuntimeState) -> Self:
        """Replace prompt runtime state using the canonical CLI model."""
        self.state = state
        return self

    def _is_test_env(self) -> bool:
        """Whether prompt logging must use test-safe behavior.

        Delegates to the canonical ``u.Cli.cli_test_env`` utility — settings
        stay pure flat data (§2.6), detection logic lives in the utilities
        layer, never reimplemented here.
        """
        return u.Cli.cli_test_env(settings)

    def _log(self, log_level: str, message: str, **context: t.LogValue) -> None:
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
        self, message: str, log_level: str, message_format: str
    ) -> p.Result[bool]:
        # Fail loud: a logger failure propagates with its cause.
        self._log(log_level, message_format.format(message=message))
        return r[bool].ok(True)

    def _read_confirmation_input(
        self, message: str, prompt_text: str, *, default: bool
    ) -> p.Result[bool]:
        while True:
            input_text = self.input_reader(prompt_text)
            parsed = u.Cli.prompts_parse_confirmation(input_text, default=default)
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
