# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_08
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Protocol, runtime_checkable

from flext_cli import t


class FlextCliProtocolsBaseFlextclimodelsbasePart08:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class AtomicDirectoryChainPlan(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def target(self) -> Path: ...
        @property
        def anchor_path(self) -> Path: ...
        @property
        def anchor_device(self) -> int: ...
        @property
        def anchor_inode(self) -> int: ...
        @property
        def anchor_ancestry(self) -> tuple[tuple[int, int], ...]: ...
        @property
        def directories(self) -> tuple[Path, ...]: ...
        @property
        def queries(
            self,
        ) -> tuple[tuple[str, Literal["exists", "isfile", "isdir"]], ...]: ...
        @property
        def membership_queried(self) -> bool: ...
        @property
        def membership_queries(self) -> tuple[t.StrTuple, ...]: ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart08",
]
