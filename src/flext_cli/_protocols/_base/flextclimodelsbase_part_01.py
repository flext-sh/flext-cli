# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_01
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import p

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliProtocolsBaseFlextclimodelsbasePart01:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class ProcessOutcome(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def raw_return_code(self) -> int:
            """Raw operating-system process return code."""
            ...

        @property
        def timed_out(self) -> bool:
            """Whether the process deadline expired."""
            ...

        @property
        def forwarded_signal(self) -> int | None:
            """First operator signal forwarded to the process."""
            ...

    @runtime_checkable
    class CommandOutputEnvelope(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def outcome(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart01.ProcessOutcome:
            """Causal process completion state."""
            ...

        @property
        def duration(self) -> t.NonNegativeFloat:
            """Duration in seconds."""
            ...

        @property
        def exit_code(self) -> int:
            """Expose the process return code without duplicating stored state."""
            ...

    @runtime_checkable
    class CommandOutput(CommandOutputEnvelope, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def stdout(self) -> str:
            """Captured standard output."""
            ...

        @property
        def stderr(self) -> str:
            """Captured standard error."""
            ...

    @runtime_checkable
    class CommandBytesOutput(CommandOutputEnvelope, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def stdout(self) -> bytes:
            """Captured standard output as raw bytes."""
            ...

        @property
        def stderr(self) -> bytes:
            """Captured standard error as raw bytes."""
            ...

    @runtime_checkable
    class ProcessDeadline(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def expires_at_monotonic(self) -> t.PositiveFloat:
            """Absolute time.monotonic expiry in seconds."""
            ...

        @property
        def termination_grace_seconds(self) -> t.PositiveFloat:
            """Reserved graceful termination and drain budget."""
            ...

    @runtime_checkable
    class RuntimeComponents(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def settings(self) -> str:
            """Settings component state."""
            ...

        @property
        def formatters(self) -> str:
            """Formatters component state."""
            ...

        @property
        def prompts(self) -> str:
            """Prompts component state."""
            ...

        @property
        def rules(self) -> str:
            """Rules component state."""
            ...

    @runtime_checkable
    class RuntimeStatus(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def status(self) -> str:
            """Overall service state."""
            ...

        @property
        def service(self) -> str:
            """Service identifier."""
            ...

        @property
        def timestamp(self) -> str:
            """Status generation timestamp."""
            ...

        @property
        def version(self) -> str:
            """CLI version."""
            ...

        @property
        def components(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart01.RuntimeComponents:
            """Component availability states."""
            ...

    @runtime_checkable
    class DisplayData(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        data: t.JsonMapping

    @runtime_checkable
    class LoadedConfig(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        content: t.JsonMapping

    @runtime_checkable
    class CliNormalizedJson(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def root(self) -> t.JsonValue:
            """Structural member projected from the owning model."""
            ...

    @runtime_checkable
    class NormalizedJsonList(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        value: t.JsonValue
        default: t.JsonMapping

        @property
        def resolved(self) -> t.JsonMapping:
            """Resolve value to dict or return default."""
            ...

    @runtime_checkable
    class SuccessSummaryDetails(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        root: Mapping[str, str]


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart01",
]
