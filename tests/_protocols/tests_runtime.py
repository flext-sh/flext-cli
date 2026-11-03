# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
tests/_protocols/tests_runtime
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_tests import FlextTestsProtocols

if TYPE_CHECKING:
    from tests import t


class TestsFlextCliProtocolsTestsRuntime:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class ApiResponse(FlextTestsProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        status: str
        data: t.JsonMapping | None
        message: str
        error: str | None

    @runtime_checkable
    class ModelCommandSample(FlextTestsProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        name: str
        value: int

    @runtime_checkable
    class ModelCommandNullable(FlextTestsProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        name: str
        optional: str | None

    @runtime_checkable
    class ModelCommandRequired(FlextTestsProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        key: str
        count: int

    @runtime_checkable
    class RuntimeCommandCase(FlextTestsProtocols.BaseModel, Protocol):
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
