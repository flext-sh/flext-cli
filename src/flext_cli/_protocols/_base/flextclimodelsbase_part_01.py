# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_01
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli import t

if TYPE_CHECKING:
    from flext_cli.protocols import p


class FlextCliProtocolsBaseFlextclimodelsbasePart01:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class ProcessOutcome(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def raw_return_code(self) -> int: ...
        @property
        def timed_out(self) -> bool: ...
        @property
        def forwarded_signal(self) -> int | None: ...

    @runtime_checkable
    class CommandOutputEnvelope(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def outcome(self) -> p.Cli.ProcessOutcome: ...
        @property
        def duration(self) -> t.NonNegativeFloat: ...

    @runtime_checkable
    class CommandOutput(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def outcome(self) -> p.Cli.ProcessOutcome: ...
        @property
        def duration(self) -> t.NonNegativeFloat: ...
        @property
        def stdout(self) -> str: ...
        @property
        def stderr(self) -> str: ...

    @runtime_checkable
    class CommandBytesOutput(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def outcome(self) -> p.Cli.ProcessOutcome: ...
        @property
        def duration(self) -> t.NonNegativeFloat: ...
        @property
        def stdout(self) -> bytes: ...
        @property
        def stderr(self) -> bytes: ...

    @runtime_checkable
    class ProcessDeadline(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def expires_at_monotonic(self) -> t.PositiveFloat: ...
        @property
        def termination_grace_seconds(self) -> t.PositiveFloat: ...

    @runtime_checkable
    class RuntimeComponents(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def settings(self) -> str: ...
        @property
        def formatters(self) -> str: ...
        @property
        def prompts(self) -> str: ...
        @property
        def rules(self) -> str: ...

    @runtime_checkable
    class RuntimeStatus(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def status(self) -> str: ...
        @property
        def service(self) -> str: ...
        @property
        def timestamp(self) -> str: ...
        @property
        def version(self) -> str: ...
        @property
        def components(self) -> p.Cli.RuntimeComponents: ...

    @runtime_checkable
    class DisplayData(Protocol):
        """Structural data contract projected from the owning model."""

        data: t.JsonMapping

    @runtime_checkable
    class LoadedConfig(Protocol):
        """Structural data contract projected from the owning model."""

        content: t.JsonMapping

    @runtime_checkable
    class CliNormalizedJson(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def root(self) -> t.JsonValue: ...

    @runtime_checkable
    class NormalizedJsonList(Protocol):
        """Structural data contract projected from the owning model."""

        value: t.JsonValue
        default: t.JsonMapping

    @runtime_checkable
    class SuccessSummaryDetails(Protocol):
        """Structural data contract projected from the owning model."""

        root: Mapping[str, str]


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart01",
]
