# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/atomic_queries
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli import t
    from flext_cli._protocols._base import (
        FlextCliProtocolsBaseFlextclimodelsbasePart02,
        FlextCliProtocolsBaseFlextclimodelsbasePart03,
        FlextCliProtocolsBaseFlextclimodelsbasePart08,
        FlextCliProtocolsBaseFlextclimodelsbasePart09,
    )


class FlextCliProtocolsAtomicQueries:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class AtomicDirectoryWorkingSelectors(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        queries: Mapping[int, set[tuple[str, Literal["exists", "isfile", "isdir"]]]]
        membership_queries: Mapping[int, set[t.StrTuple]]

    @runtime_checkable
    class AtomicDirectorySelection(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def queries(
            self,
        ) -> tuple[tuple[str, Literal["exists", "isfile", "isdir"]], ...]:
            """Sorted native predicates consumed by the caller."""
            ...

        @property
        def membership_queried(self) -> bool:
            """Whether the complete direct membership was consumed."""
            ...

        @property
        def membership_queries(self) -> tuple[t.StrTuple, ...]:
            """Sorted membership exclusions consumed by the caller."""
            ...

    @runtime_checkable
    class AtomicDirectoryQueryProof(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def files(
            self,
        ) -> tuple[
            tuple[
                FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState,
                FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState,
            ],
            ...,
        ]:
            """Authenticated file effects as before and after states."""
            ...

        membership_policy: t.StrTuple | None

        @property
        def directories(
            self,
        ) -> tuple[
            FlextCliProtocolsBaseFlextclimodelsbasePart03.AtomicDirectoryState, ...
        ]:
            """Own directory creations published in the boundary."""
            ...

        @property
        def directory_observations(
            self,
        ) -> MutableMapping[
            Path, FlextCliProtocolsBaseFlextclimodelsbasePart09.AtomicDirectoryInventory
        ]:
            """Directory observations shared by reference in the boundary."""
            ...

        @property
        def topology_observations(
            self,
        ) -> MutableMapping[
            Path, FlextCliProtocolsBaseFlextclimodelsbasePart08.AtomicDirectoryChainPlan
        ]:
            """Ancestry observations shared by reference in the boundary."""
            ...

    @runtime_checkable
    class AtomicDirectoryQueryBoundary(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def published(
            self,
        ) -> Mapping[
            Path,
            tuple[
                FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState,
                FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState,
            ],
        ]:
            """Authenticated file effects keyed by their destination."""
            ...

        @property
        def created(
            self,
        ) -> Mapping[
            Path, FlextCliProtocolsBaseFlextclimodelsbasePart03.AtomicDirectoryState
        ]:
            """Own directory creations keyed by their path."""
            ...

        ancestors: Mapping[Path, None]

        @property
        def directory_observations(
            self,
        ) -> MutableMapping[
            Path, FlextCliProtocolsBaseFlextclimodelsbasePart09.AtomicDirectoryInventory
        ]:
            """Directory observations shared by reference in the boundary."""
            ...

        @property
        def topology_observations(
            self,
        ) -> MutableMapping[
            Path, FlextCliProtocolsBaseFlextclimodelsbasePart08.AtomicDirectoryChainPlan
        ]:
            """Ancestry observations shared by reference in the boundary."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsAtomicQueries",
]
