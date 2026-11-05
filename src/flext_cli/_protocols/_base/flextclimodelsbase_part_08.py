# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_08
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliProtocolsBaseFlextclimodelsbasePart08:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class AtomicNativeSelections(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def queries(
            self,
        ) -> tuple[tuple[str, Literal["exists", "isfile", "isdir"]], ...]:
            """Consumed native candidate predicates."""
            ...

        @property
        def membership_queried(self) -> bool:
            """Whether native planning consumed direct membership."""
            ...

        @property
        def membership_queries(self) -> tuple[t.StrTuple, ...]:
            """Consumed membership selections, each excluding named children."""
            ...

        def validate_native_selections(self) -> None:
            """Require ordered, unique, lexical child names in every selection."""
            ...

    @runtime_checkable
    class AtomicDirectoryChainPlan(AtomicNativeSelections, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def target(self) -> Path:
            """Requested directory path."""
            ...

        @property
        def anchor_path(self) -> Path:
            """Deepest physical existing ancestor."""
            ...

        @property
        def anchor_device(self) -> int:
            """Anchor device."""
            ...

        @property
        def anchor_inode(self) -> int:
            """Anchor inode."""
            ...

        @property
        def anchor_ancestry(self) -> tuple[tuple[int, int], ...]:
            """Root-to-anchor physical identities."""
            ...

        @property
        def directories(self) -> tuple[Path, ...]:
            """Ordered contiguous paths observed absent."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart08",
]
