"""Test protocols for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from flext_tests import FlextTestsProtocols

from flext_cli import FlextCliProtocols

if TYPE_CHECKING:
    from types import EllipsisType

    from tests import m, t


class TestsFlextCliProtocols(FlextTestsProtocols, FlextCliProtocols):
    """Test protocols for flext-cli."""

    class Tests(FlextTestsProtocols.Tests):
        """Test-specific protocols."""

        class Prompts(Protocol):
            """Public prompt service surface exercised by the prompt tests."""

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

            def print_success(self, message: str) -> p.Result[bool]:
                """Define the print success test contract."""
                ...

            def print_error(self, message: str) -> p.Result[bool]:
                """Define the print error test contract."""
                ...

            def print_warning(self, message: str) -> p.Result[bool]:
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


p = TestsFlextCliProtocols
__all__: list[str] = ["TestsFlextCliProtocols", "p"]
