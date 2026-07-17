"""Test protocols for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, Self

from flext_tests import FlextTestsProtocols

from flext_cli import p


from tests import t


class TestsFlextCliProtocols(FlextTestsProtocols, p):
    """Test protocols for flext-cli."""

    class Tests(FlextTestsProtocols.Tests):
        """Test-specific protocols."""

        class SampleInput(p.BaseModel, Protocol):
            """Input capabilities consumed by result-route tests."""

            @property
            def name(self) -> str:
                """Requested target name."""
                ...

        class SampleOutput(p.BaseModel, Protocol):
            """Output capabilities returned by result-route tests."""

            @property
            def message(self) -> str:
                """Rendered success message."""
                ...

        class RuntimeCommandCase(Protocol):
            """Inputs and expectations consumed by runtime command tests."""

            @property
            def command(self) -> t.StrSequence:
                """Command argument vector."""
                ...

            @property
            def timeout(self) -> int | None:
                """Optional command timeout."""
                ...

            @property
            def env(self) -> t.StrMapping | None:
                """Optional child environment overrides."""
                ...

            @property
            def input_data(self) -> bytes | None:
                """Optional standard-input payload."""
                ...

            @property
            def use_tmp_path(self) -> bool:
                """Temporary-directory working-directory flag."""
                ...

            @property
            def expect_success(self) -> bool:
                """Expected command success flag."""
                ...

            @property
            def stdout_has(self) -> str:
                """Expected standard-output fragment."""
                ...

            @property
            def stderr_has(self) -> str:
                """Expected standard-error fragment."""
                ...

            @property
            def exit_code(self) -> int | None:
                """Expected process exit code."""
                ...

            @property
            def expected(self) -> str:
                """Expected captured output."""
                ...

            @property
            def error_has(self) -> str:
                """Expected failure fragment."""
                ...

        class ScriptedPrompts(Protocol):
            """Prompt test double contract exposed through the canonical `p`."""

            def override_test_env(self, *, enabled: bool | None = True) -> Self:
                """Select the explicit test-environment override."""
                ...

            def use_input_values(self, values: t.StrSequence) -> Self:
                """Script successive prompt input values."""
                ...

            def use_input_error(self, error: Exception) -> Self:
                """Script an input-reader failure."""
                ...

            def use_password(self, password: str) -> Self:
                """Script a password response."""
                ...

            def use_password_error(self, error: Exception) -> Self:
                """Script a password-reader failure."""
                ...

            def configure_state(
                self, *, interactive: bool = True, quiet: bool = False
            ) -> Self:
                """Configure the observable prompt runtime state."""
                ...

            def execute(self) -> p.Result[p.Cli.RuntimeStatus]:
                """Return the public CLI runtime status."""
                ...

            def prompt(self, message: str, default: str = "") -> p.Result[str]:
                """Read one scripted text prompt."""
                ...

            def confirm(self, message: str, *, default: bool = False) -> p.Result[bool]:
                """Read one scripted confirmation."""
                ...

            def prompt_choice(
                self, message: str, choices: t.StrSequence, default: str | None = None
            ) -> p.Result[str]:
                """Read one scripted choice."""
                ...

            def prompt_password(
                self, message: str, min_length: int = 8
            ) -> p.Result[str]:
                """Read one scripted password."""
                ...

            def print_success(self, message: str) -> p.Result[bool]:
                """Emit one success message."""
                ...

            def print_error(self, message: str) -> p.Result[bool]:
                """Emit one error message."""
                ...

            def print_warning(self, message: str) -> p.Result[bool]:
                """Emit one warning message."""
                ...

        class CaptureLogPrompts(ScriptedPrompts, Protocol):
            """Prompt test double that exposes captured log records."""

            @property
            def records(self) -> list[tuple[str, str]]:
                """Captured level/message pairs."""
                ...

        class FailingLogPrompts(ScriptedPrompts, Protocol):
            """Prompt test double that can fail a selected log call."""

            def fail_on_log(self, *, level: str, message: str) -> Self:
                """Select the log call that raises the scripted failure."""
                ...


p = TestsFlextCliProtocols
__all__: list[str] = ["TestsFlextCliProtocols", "p"]
