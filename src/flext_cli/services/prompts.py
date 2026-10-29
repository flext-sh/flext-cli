"""User interaction tools for CLI applications.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_cli import c, p, r, u
from flext_cli.services import FlextCliServicesPromptsSupport


class FlextCliPrompts(FlextCliServicesPromptsSupport):
    """Interactive CLI prompt surface exposed through the CLI service runtime."""

    @override
    def execute(self) -> p.Result[p.Cli.RuntimeStatus]:
        """Return the current CLI runtime status.

        Returns:
            The current CLI runtime status.

        """
        return r[p.Cli.RuntimeStatus].ok(u.Cli.cmd_status())

    def confirm(self, message: str, *, default: bool = False) -> p.Result[bool]:
        """Read a yes/no confirmation or return the configured default.

        Args:
            message: Confirmation question shown to the user.
            default: Value returned when input is unavailable or empty.

        Returns:
            The resulting ``p.Result[bool]``.

        """
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
        """Read one text value or return the configured default.

        Args:
            message: Prompt text shown to the user.
            default: Value returned when input is unavailable or empty.

        Returns:
            The resulting ``p.Result[str]``.

        """
        if self.state.quiet or not self.state.interactive:
            return r[str].ok(default)
        return r[str].ok(self._read_prompt_value(message, default))

    def prompt_password(
        self,
        message: str = "Password:",
        min_length: int = c.Cli.PROMPT_MIN_PASSWORD_LENGTH,
    ) -> p.Result[str]:
        """Read a password and enforce the minimum length.

        Args:
            message: Prompt text shown before reading the password.
            min_length: Minimum accepted password length.

        Returns:
            The resulting ``p.Result[str]``.

        """
        if not self.state.interactive:
            return r[str].fail(c.Cli.ERR_INTERACTIVE_MODE_DISABLED)
        return u.Cli.prompts_password_result(
            self.password_reader(f"{message}{c.Cli.PROMPT_SPACE}"),
            min_length=min_length,
        )

    def _read_prompt_value(self, message: str, default: str) -> str:
        """Read one prompt value and record the canonical prompt log.

        Returns:
            The resulting ``str``.

        """
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
