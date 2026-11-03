# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_08
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Protocol, runtime_checkable

from flext_core import FlextProtocols

from flext_cli import t


class FlextCliProtocolsBaseFlextclimodelsbasePart08:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class AtomicDirectoryChainPlan(FlextProtocols.Model, Protocol):
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

        @property
        def queries(
            self,
        ) -> tuple[tuple[str, Literal["exists", "isfile", "isdir"]], ...]:
            """Native candidate queries beneath an absent parent."""
            ...

        @property
        def membership_queried(self) -> bool:
            """Whether native planning consumed the absent parent's membership."""
            ...

        @property
        def membership_queries(self) -> tuple[t.StrTuple, ...]:
            """Consumed absent-parent membership selections."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart08",
]
