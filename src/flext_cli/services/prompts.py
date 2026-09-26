"""User interaction tools for CLI applications."""

from __future__ import annotations

from typing import override

from flext_cli import c, m, p, r, t, u

from ._prompts_support import FlextCliPromptsSupport


class FlextCliPrompts(FlextCliPromptsSupport):
    """Interactive CLI prompt surface exposed through the CLI service runtime."""

    @override
    def execute(self) -> p.Result[m.Cli.RuntimeStatus]:
        """Return the current CLI runtime status."""
        return r[m.Cli.RuntimeStatus].ok(u.Cli.cmd_status())

    def confirm(self, message: str, *, default: bool = False) -> p.Result[bool]:
        """Read a yes/no confirmation or return the configured default."""
        try:
            if self.state.quiet or not self.state.interactive:
                return r[bool].ok(default)
            prompt_text = u.Cli.prompts_confirmation_text(message, default=default)
            return self._read_confirmation_input(message, prompt_text, default=default)
        except KeyboardInterrupt as exc:
            return r[bool].fail(c.Cli.ERR_USER_CANCELLED_CONFIRMATION, exception=exc)
        except EOFError as exc:
            return r[bool].fail(c.Cli.ERR_INPUT_STREAM_ENDED, exception=exc)

    def prompt(self, message: str, default: str = "") -> p.Result[str]:
        """Read one text value or return the configured default."""
        if self.state.quiet or not self.state.interactive:
            return r[str].ok(default)
        return r[str].ok(self._read_prompt_value(message, default))

    def prompt_choice(
        self, choices: t.StrSequence, default: str | None = None
    ) -> p.Result[str]:
        """Resolve one value constrained to the supplied choices."""
        return u.Cli.prompts_choice_result(
            interactive=self.state.interactive, choices=choices, default=default
        )

    def prompt_password(
        self,
        message: str = "Password:",
        min_length: int = c.Cli.PROMPT_MIN_PASSWORD_LENGTH,
    ) -> p.Result[str]:
        """Read a password and enforce the minimum length."""
        if not self.state.interactive:
            return r[str].fail(c.Cli.ERR_INTERACTIVE_PASSWORD_DISABLED)
        return u.Cli.prompts_password_result(
            self.password_reader(f"{message}{c.Cli.PROMPT_SPACE}"),
            min_length=min_length,
        )

    def print_error(self, message: str) -> p.Result[bool]:
        """Render an error message through the canonical prompt output path."""
        return self._print_message(message, c.LogLevel.ERROR, c.Cli.PROMPT_ERROR_FMT)

    def print_success(self, message: str) -> p.Result[bool]:
        """Render a success message through the canonical prompt output path."""
        return self._print_message(message, c.LogLevel.INFO, c.Cli.PROMPT_SUCCESS_FMT)

    def print_warning(self, message: str) -> p.Result[bool]:
        """Render a warning message through the canonical prompt output path."""
        return self._print_message(
            message, c.LogLevel.WARNING, c.Cli.PROMPT_WARNING_FMT
        )

    def _read_prompt_value(self, message: str, default: str) -> str:
        """Read one prompt value and record the canonical prompt log."""
        display_message = u.Cli.prompts_display_message(message, default)
        raw = self.input_reader(f"{display_message}{c.Cli.PROMPT_SEP}")
        value: str = u.Cli.prompts_effective_text(raw, default)
        if not self._is_test_env():
            self._log(
                c.LogLevel.INFO,
                c.Cli.PROMPT_LOG_FMT.format(message=message, input=value),
            )
        return value


__all__: list[str] = ["FlextCliPrompts"]
