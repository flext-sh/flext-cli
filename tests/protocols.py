"""Test protocols for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Self

from flext_tests import FlextTestsProtocols

from flext_cli import p

if TYPE_CHECKING:
    from types import EllipsisType

    from tests import m, t


class TestsFlextCliProtocols(FlextTestsProtocols, p):
    """Test protocols for flext-cli."""

    class Tests(FlextTestsProtocols.Tests):
        """Test-specific protocols."""

        class ScriptedPrompts(Protocol):
            """Prompt test double contract exposed through the canonical `p`."""

            def override_test_env(self, *, enabled: bool | None = True) -> Self:
                """Define the override test env test contract."""
                ...

            def use_input_values(self, values: t.StrSequence) -> Self:
                """Define the use input values test contract."""
                ...

            def use_input_error(self, error: Exception) -> Self:
                """Define the use input error test contract."""
                ...

            def use_password(self, password: str) -> Self:
                """Define the use password test contract."""
                ...

            def use_password_error(self, error: Exception) -> Self:
                """Define the use password error test contract."""
                ...

            def configure_state(
                self, *, interactive: bool = True, quiet: bool = False
            ) -> Self:
                """Define the configure state test contract."""
                ...

            def execute(self) -> p.Result[m.Cli.RuntimeStatus]:
                """Define the execute test contract."""
                ...

            def prompt(self, message: str, default: str = "") -> p.Result[str]:
                """Define the prompt test contract."""
                ...

            def confirm(self, message: str, *, default: bool = False) -> p.Result[bool]:
                """Define the confirm test contract."""
                ...

            def prompt_choice(
                self, message: str, choices: t.StrSequence, default: str | None = None
            ) -> p.Result[str]:
                """Define the prompt choice test contract."""
                ...

            def prompt_password(
                self, message: str, min_length: int = 8
            ) -> p.Result[str]:
                """Define the prompt password test contract."""
                ...

            def print_success(self, message: str) -> p.Result[None]:
                """Define the print success test contract."""
                ...

            def print_error(self, message: str) -> p.Result[None]:
                """Define the print error test contract."""
                ...

            def print_warning(self, message: str) -> p.Result[None]:
                """Define the print warning test contract."""
                ...

        class FrameworkOption(Protocol):
            """Typed option metadata exposed in a generated command signature."""

            @property
            def param_decls(self) -> t.StrSequence | None:
                """Ordered framework option declarations."""
                ...

            @property
            def default(self) -> t.Cli.CliValue | EllipsisType | None:
                """Generated option default."""
                ...

        class CaptureLogPrompts(ScriptedPrompts, Protocol):
            """Prompt test double that exposes captured log records."""

            @property
            def records(self) -> list[tuple[str, str]]:
                """Define the records test contract."""
                ...

        class FailingLogPrompts(ScriptedPrompts, Protocol):
            """Prompt test double that can fail a selected log call."""

            def fail_on_log(self, *, level: str, message: str) -> Self:
                """Define the fail on log test contract."""
                ...


p = TestsFlextCliProtocols
__all__: list[str] = ["TestsFlextCliProtocols", "p"]
