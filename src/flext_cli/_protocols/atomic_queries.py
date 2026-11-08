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

        files: tuple[
            tuple[
                FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState,
                FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState,
            ],
            ...,
        ]
        membership_policy: t.StrTuple | None
        directories: tuple[
            FlextCliProtocolsBaseFlextclimodelsbasePart03.AtomicDirectoryState, ...
        ]
        directory_observations: MutableMapping[
            Path, FlextCliProtocolsBaseFlextclimodelsbasePart09.AtomicDirectoryInventory
        ]
        topology_observations: MutableMapping[
            Path, FlextCliProtocolsBaseFlextclimodelsbasePart08.AtomicDirectoryChainPlan
        ]

    @runtime_checkable
    class AtomicDirectoryQueryBoundary(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        published: Mapping[
            Path,
            tuple[
                FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState,
                FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState,
            ],
        ]
        created: Mapping[
            Path, FlextCliProtocolsBaseFlextclimodelsbasePart03.AtomicDirectoryState
        ]
        ancestors: Mapping[Path, None]
        directory_observations: MutableMapping[
            Path, FlextCliProtocolsBaseFlextclimodelsbasePart09.AtomicDirectoryInventory
        ]
        topology_observations: MutableMapping[
            Path, FlextCliProtocolsBaseFlextclimodelsbasePart08.AtomicDirectoryChainPlan
        ]


__all__: list[str] = [
    "FlextCliProtocolsAtomicQueries",
]
