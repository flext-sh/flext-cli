# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_10
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import MutableMapping
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli import t

if TYPE_CHECKING:
    from flext_cli.protocols import p


class FlextCliProtocolsBaseFlextclimodelsbasePart10:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class AtomicDirectoryObservations(Protocol):
        """Structural data contract projected from the owning model."""

        directories: MutableMapping[Path, p.Cli.AtomicDirectoryInventory]
        topology: MutableMapping[Path, p.Cli.AtomicDirectoryChainPlan]

    @runtime_checkable
    class AtomicDirectoryQueryEffects(Protocol):
        """Structural data contract projected from the owning model."""

        files: tuple[tuple[p.Cli.AtomicFileState, p.Cli.AtomicFileState], ...]
        membership_policy: t.StrTuple

    @runtime_checkable
    class AtomicFilePublication(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def before(self) -> p.Cli.AtomicFileState: ...
        @property
        def replacement(self) -> p.Cli.AtomicFileState: ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart10",
]
