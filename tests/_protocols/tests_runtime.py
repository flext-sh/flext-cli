# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
tests/_protocols/tests_runtime
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol, runtime_checkable

from flext_tests import FlextTestsProtocols

from tests import t


class TestsFlextCliProtocolsTestsRuntime:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class ApiResponse(FlextTestsProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def status(self) -> str:
            """Status."""
            ...

        @property
        def data(self) -> t.JsonMapping | None:
            """Payload."""
            ...

        @property
        def message(self) -> str:
            """Message."""
            ...

        @property
        def error(self) -> str | None:
            """Error."""
            ...

    @runtime_checkable
    class ModelCommandSample(FlextTestsProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str:
            """Required command name."""
            ...

        @property
        def value(self) -> int:
            """Command value with default."""
            ...

    @runtime_checkable
    class ModelCommandNullable(FlextTestsProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str:
            """Required command name."""
            ...

        @property
        def optional(self) -> str | None:
            """Optional value."""
            ...

    @runtime_checkable
    class ModelCommandRequired(FlextTestsProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def key(self) -> str:
            """Required key."""
            ...

        @property
        def count(self) -> int:
            """Required count."""
            ...

    @runtime_checkable
    class RuntimeCommandCase(FlextTestsProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def case_id(self) -> str:
            """Pytest case id."""
            ...

        @property
        def command(self) -> Sequence[str]:
            """Command argv."""
            ...

        @property
        def timeout(self) -> int | None:
            """Optional timeout in seconds."""
            ...

        @property
        def env(self) -> Mapping[str, str] | None:
            """Optional child environment overrides."""
            ...

        @property
        def use_tmp_path(self) -> bool:
            """Use pytest tmp_path as cwd."""
            ...

        @property
        def input_data(self) -> str | bytes | None:
            """Optional stdin payload (text or binary)."""
            ...

        @property
        def expect_success(self) -> bool:
            """Whether command should succeed."""
            ...

        @property
        def stdout_has(self) -> str:
            """Expected stdout substring."""
            ...

        @property
        def stderr_has(self) -> str:
            """Expected stderr substring."""
            ...

        @property
        def exit_code(self) -> int | None:
            """Expected exit code when applicable."""
            ...

        @property
        def expected(self) -> str:
            """Expected captured output."""
            ...

        @property
        def error_has(self) -> str:
            """Expected error substring."""
            ...

        @property
        def timed_out(self) -> bool:
            """Whether the run must end owned-timeout."""
            ...


__all__: list[str] = [
    "TestsFlextCliProtocolsTestsRuntime",
]
