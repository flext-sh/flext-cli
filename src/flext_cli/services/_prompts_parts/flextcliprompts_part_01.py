"""User interaction tools for CLI applications."""

from __future__ import annotations

from typing import override

from flext_cli import (
    c,
    p,
    r,
    t,
    u,
)
from flext_cli.services._prompts_parts.flextcliprompts_support import (
    FlextCliPromptsSupport,
)


class FlextCliPrompts(FlextCliPromptsSupport):
    """Implementation part for FlextCliPrompts."""

    def confirm(self, message: str, *, default: bool = False) -> p.Result[bool]:
        try:
            if self.state.quiet or not self.state.interactive:
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
    def execute(self) -> p.Result[t.JsonMapping]:
        return r[t.JsonMapping].ok(u.Cli.cmd_status_payload())

    def print_error(self, message: str) -> p.Result[bool]:
        return self._print_message(
            message,
            c.LogLevel.ERROR,
            c.Cli.PROMPT_ERROR_FMT,
            "Print error failed: {error}",
        )

    def print_success(self, message: str) -> p.Result[bool]:
        return self._print_message(
            message,
            c.LogLevel.INFO,
            c.Cli.PROMPT_SUCCESS_FMT,
            "Print success failed: {error}",
        )

    def print_warning(self, message: str) -> p.Result[bool]:
        return self._print_message(
            message,
            c.LogLevel.WARNING,
            c.Cli.PROMPT_WARNING_FMT,
            "Print warning failed: {error}",
        )

    def _read_prompt_value(self, message: str, default: str) -> str:
        """Read one prompt value and record the canonical prompt log."""
        display_message = u.Cli.prompts_display_message(message, default)
        raw = self._input_reader(f"{display_message}{c.Cli.PROMPT_SEP}")
        value: str = u.Cli.prompts_effective_text(raw, default)
        if not self._is_test_env():
            self._log(
                c.LogLevel.INFO,
                c.Cli.PROMPT_LOG_FMT.format(message=message, input=value),
            )
        return value

    def prompt(self, message: str, default: str = "") -> p.Result[str]:
        if self.state.quiet or not self.state.interactive:
            return r[str].ok(default)
        try:
            return r[str].ok(self._read_prompt_value(message, default))
        except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
            self._fatal("prompt", message, exc, "Prompt failed completely")
            return r[str].fail(c.Cli.ERR_PROMPT_FAILED_FMT.format(error=exc))


__all__: list[str] = ["FlextCliPrompts"]
