"""Test protocols for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from flext_tests import FlextTestsProtocols

from flext_cli import FlextCliProtocols

if TYPE_CHECKING:
    from tests import m, t


class TestsFlextCliProtocols(FlextTestsProtocols, FlextCliProtocols):
    """Test protocols for flext-cli."""

    class Tests(FlextTestsProtocols.Tests):
        """Test-specific protocols."""

        class Prompts(Protocol):
            """Public prompt service surface exercised by the prompt tests."""

            @staticmethod
            def execute() -> p.Result[m.Cli.RuntimeStatus]:
                """Define the execute test contract."""
                ...

            @staticmethod
            def prompt(message: str, default: str = "") -> p.Result[str]:
                """Define the prompt test contract."""
                ...

            @staticmethod
            def confirm(message: str, *, default: bool = False) -> p.Result[bool]:
                """Define the confirm test contract."""
                ...

            @staticmethod
            def prompt_choice(
                choices: t.StrSequence,
                default: str | None = None,
            ) -> p.Result[str]:
                """Define the prompt choice test contract."""
                ...

            @staticmethod
            def prompt_password(
                message: str,
                min_length: int = 8,
            ) -> p.Result[str]:
                """Define the prompt password test contract."""
                ...

            @staticmethod
            def print_success(message: str) -> p.Result[bool]:
                """Define the print success test contract."""
                ...

            @staticmethod
            def print_error(message: str) -> p.Result[bool]:
                """Define the print error test contract."""
                ...

            @staticmethod
            def print_warning(message: str) -> p.Result[bool]:
                """Define the print warning test contract."""
                ...


p = TestsFlextCliProtocols
__all__: list[str] = ["TestsFlextCliProtocols", "p"]
