"""Structural protocols for the generic TOML operation domain (``p.Cli.Toml*``).

Field-level contracts mirroring the ``m.Cli.Toml*`` operation models. Consumers
type against these protocols (``p.Cli.TomlPhaseConfig`` etc.) and never against
the concrete ``m`` classes (DIP). No project imports — foundation purity.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, runtime_checkable

from flext_cli._constants.enums import FlextCliConstantsEnums as ce
from flext_core import t


class FlextCliProtocolsToml:
    """TOML operation protocol namespace (structural; flat in ``p.Cli.Toml*``)."""

    @runtime_checkable
    class TomlSetOp(Protocol):
        """Set one TOML key to one JSON-compatible value."""

        @property
        def kind(self) -> ce.TomlOperationKind:
            """Operation kind."""
            ...

        @property
        def key(self) -> str:
            """TOML key name."""
            ...

        @property
        def value(self) -> t.JsonValue:
            """JSON-compatible value."""
            ...

    @runtime_checkable
    class TomlListOp(Protocol):
        """Set or merge one TOML string list."""

        @property
        def kind(self) -> ce.TomlOperationKind:
            """Operation kind."""
            ...

        @property
        def key(self) -> str:
            """TOML key name."""
            ...

        @property
        def values(self) -> t.StrSequence:
            """Expected values."""
            ...

        @property
        def strategy(self) -> ce.TomlMergeMode:
            """Merge strategy."""
            ...

        @property
        def sort(self) -> bool:
            """Sort values before sync."""
            ...

    @runtime_checkable
    class TomlRemoveOp(Protocol):
        """Remove one TOML key, optionally from a nested relative table."""

        @property
        def kind(self) -> ce.TomlOperationKind:
            """Operation kind."""
            ...

        @property
        def key(self) -> str:
            """Key to remove."""
            ...

        @property
        def table_path(self) -> t.StrSequence:
            """Relative sub-table path."""
            ...

    type TomlOperation = TomlSetOp | TomlListOp | TomlRemoveOp

    @runtime_checkable
    class TomlPhaseConfig(Protocol):
        """Declarative TOML phase surface."""

        @property
        def name(self) -> str:
            """Phase name."""
            ...

        @property
        def root_path(self) -> t.StrSequence:
            """Root path before table_path."""
            ...

        @property
        def table_path(self) -> t.StrSequence:
            """Primary table path."""
            ...

        @property
        def operations(self) -> t.SequenceOf[FlextCliProtocolsToml.TomlOperation]:
            """Declarative TOML operations."""
            ...

        @property
        def nested_tables(
            self,
        ) -> t.SequenceOf[FlextCliProtocolsToml.TomlPhaseConfig]:
            """Nested TOML phase configs."""
            ...

        @property
        def custom_handler(self) -> Callable[..., t.StrSequence] | None:
            """Custom handler."""
            ...


__all__: list[str] = ["FlextCliProtocolsToml"]
