"""Test protocols for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from typing import Protocol

from flext_tests import FlextTestsProtocols

from flext_cli import FlextCliProtocols


class TestsFlextCliProtocols(FlextTestsProtocols, FlextCliProtocols):
    """Test protocols for flext-cli."""

    class Tests(FlextTestsProtocols.Tests):
        """Test-specific protocols."""

        class ServiceGreeting(Protocol):
            """Read-only greeting capabilities consumed by the service."""

            @property
            def name(self) -> str:
                """Greeting target name.

                Returns:
                    The configured greeting target name.

                """
                ...

            @property
            def times(self) -> int:
                """Greeting repeat count.

                Returns:
                    The configured number of greeting repeats.

                """
                ...

        class ServiceStatus(Protocol):
            """Read-only result capability of the service."""

            @property
            def ready(self) -> int:
                """Service readiness indicator.

                Returns:
                    The configured readiness indicator.

                """
                ...

        class Prompts(Protocol):
            """Public prompt service surface exercised by the prompt tests."""

            def execute(self) -> p.Result[p.Cli.RuntimeStatus]:
                """Define the execute test contract."""
                ...

            def prompt(self, message: str, default: str = "") -> p.Result[str]:
                """Define the prompt test contract."""
                ...

            def confirm(self, message: str, *, default: bool = False) -> p.Result[bool]:
                """Define the confirm test contract."""
                ...

            def prompt_password(
                self,
                message: str,
                min_length: int = 8,
            ) -> p.Result[str]:
                """Define the prompt password test contract."""
                ...


p = TestsFlextCliProtocols
__all__: list[str] = ["TestsFlextCliProtocols", "p"]
