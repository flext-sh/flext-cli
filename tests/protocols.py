"""Test protocols for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Self

from flext_tests import FlextTestsProtocols

from flext_cli import p

if TYPE_CHECKING:
    from tests import t


class TestsFlextCliProtocols(FlextTestsProtocols, p):
    """Test protocols for flext-cli."""

    class Tests(FlextTestsProtocols.Tests):
        """Test-specific protocols."""

        class ScriptedPrompts(Protocol):
            """Prompt test double contract exposed through the canonical `p`."""

            def override_test_env(self, enabled: bool | None = True) -> Self: ...

            def use_input_values(self, values: t.StrSequence) -> Self: ...

            def use_input_error(self, error: Exception) -> Self: ...

            def use_password(self, password: str) -> Self: ...

            def use_password_error(self, error: Exception) -> Self: ...

            def configure_state(
                self, *, interactive: bool = True, quiet: bool = False
            ) -> Self: ...

            def execute(self) -> p.Result[t.MappingKV[str, t.JsonValue]]: ...

            def prompt(self, message: str, default: str = "") -> p.Result[str]: ...

            def confirm(
                self, message: str, *, default: bool = False
            ) -> p.Result[bool]: ...

            def prompt_choice(
                self, message: str, choices: t.StrSequence, default: str | None = None
            ) -> p.Result[str]: ...

            def prompt_password(
                self, message: str, min_length: int = 8
            ) -> p.Result[str]: ...

            def print_success(self, message: str) -> p.Result[None]: ...

            def print_error(self, message: str) -> p.Result[None]: ...

            def print_warning(self, message: str) -> p.Result[None]: ...

        class CaptureLogPrompts(ScriptedPrompts, Protocol):
            """Prompt test double that exposes captured log records."""

            @property
            def records(self) -> list[tuple[str, str]]: ...

        class FailingLogPrompts(ScriptedPrompts, Protocol):
            """Prompt test double that can fail a selected log call."""

            def fail_on_log(self, *, level: str, message: str) -> Self: ...


p = TestsFlextCliProtocols
__all__: list[str] = ["TestsFlextCliProtocols", "p"]
