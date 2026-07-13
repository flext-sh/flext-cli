"""User interaction tools for CLI applications."""

from __future__ import annotations

from flext_cli import c, p, r, t, u
from flext_cli.services._prompts_parts.flextcliprompts_part_01 import (
    FlextCliPrompts as FlextCliPromptsPart01,
)


class FlextCliPrompts(FlextCliPromptsPart01):
    """Implementation part for FlextCliPrompts."""

    def prompt_choice(
        self, message: str, choices: t.StrSequence, default: str | None = None
    ) -> p.Result[str]:
        try:
            return u.Cli.prompts_choice_result(
                interactive=self.state.interactive, choices=choices, default=default
            )
        except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
            self._fatal(
                "prompt_choice", message, exc, "Choice prompt failed completely"
            )
            return r[str].fail(c.Cli.ERR_CHOICE_PROMPT_FAILED_FMT.format(error=exc))

    def prompt_password(
        self,
        message: str = "Password:",
        min_length: int = c.Cli.PROMPT_MIN_PASSWORD_LENGTH,
    ) -> p.Result[str]:
        if not self.state.interactive:
            return r[str].fail(c.Cli.ERR_INTERACTIVE_PASSWORD_DISABLED)
        try:
            password = self._password_reader(f"{message}{c.Cli.PROMPT_SPACE}")
            return u.Cli.prompts_password_result(password, min_length=min_length)
        except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
            self._fatal(
                "prompt_password", message, exc, "Password prompt failed completely"
            )
            return r[str].fail(c.Cli.ERR_PASSWORD_PROMPT_FAILED_FMT.format(error=exc))


__all__: list[str] = ["FlextCliPrompts"]
