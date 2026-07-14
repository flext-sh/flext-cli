"""Test protocols for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Self

from flext_tests import FlextTestsProtocols

from flext_cli import p

from flext_cli import m
from tests import t



class TestsFlextCliProtocols(FlextTestsProtocols, p):
    """Test protocols for flext-cli."""

    class Tests(FlextTestsProtocols.Tests):
        """Test-specific protocols."""

        class ScriptedPrompts(Protocol):
            """Prompt test double contract exposed through the canonical `p`."""

            def override_test_env(self, *, enabled: bool | None = True) -> Self:
                """Override test-environment detection for the prompt instance."""
                ...

            def use_input_values(self, values: t.StrSequence) -> Self:
                """Queue text values returned by subsequent prompt calls."""
                ...

            def use_input_error(self, error: Exception) -> Self:
                """Configure the next text prompt to raise the supplied error."""
                ...

            def use_password(self, password: str) -> Self:
                """Configure the password returned by the prompt boundary."""
                ...

            def use_password_error(self, error: Exception) -> Self:
                """Configure the next password prompt to raise an error."""
                ...

            def configure_state(
                self, *, interactive: bool = True, quiet: bool = False
            ) -> Self:
                """Set the observable interactive and quiet prompt state."""
                ...

            def execute(self) -> p.Result[m.Cli.RuntimeStatus]:
                """Return the canonical typed CLI runtime status."""
                ...

            def prompt(self, message: str, default: str = "") -> p.Result[str]:
                """Read a text value or return the configured default."""
                ...

            def confirm(self, message: str, *, default: bool = False) -> p.Result[bool]:
                """Read a yes-or-no confirmation through the public result contract."""
                ...

            def prompt_choice(
                self, message: str, choices: t.StrSequence, default: str | None = None
            ) -> p.Result[str]:
                """Read one validated value from the available choices."""
                ...

            def prompt_password(
                self, message: str, min_length: int = 8
            ) -> p.Result[str]:
                """Read a password satisfying the minimum length."""
                ...

            def print_success(self, message: str) -> p.Result[None]:
                """Emit a success message through the prompt service."""
                ...

            def print_error(self, message: str) -> p.Result[None]:
                """Emit an error message through the prompt service."""
                ...

            def print_warning(self, message: str) -> p.Result[None]:
                """Emit a warning message through the prompt service."""
                ...

        class CaptureLogPrompts(ScriptedPrompts, Protocol):
            """Prompt test double that exposes captured log records."""

            @property
            def records(self) -> list[tuple[str, str]]:
                """Captured log-level and message pairs."""
                ...

        class FailingLogPrompts(ScriptedPrompts, Protocol):
            """Prompt test double that can fail a selected log call."""

            def fail_on_log(self, *, level: str, message: str) -> Self:
                """Configure one matching log emission to fail."""
                ...


p = TestsFlextCliProtocols
__all__: list[str] = ["TestsFlextCliProtocols", "p"]
