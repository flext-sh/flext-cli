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

from flext_core import FlextProtocols

if TYPE_CHECKING:
    from flext_cli import t
    from flext_cli._protocols._base import (
        FlextCliProtocolsBaseFlextclimodelsbasePart02,
        FlextCliProtocolsBaseFlextclimodelsbasePart08,
        FlextCliProtocolsBaseFlextclimodelsbasePart09,
    )


class FlextCliProtocolsBaseFlextclimodelsbasePart10:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class AtomicDirectoryObservations(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        directories: MutableMapping[
            Path, FlextCliProtocolsBaseFlextclimodelsbasePart09.AtomicDirectoryInventory
        ]
        topology: MutableMapping[
            Path, FlextCliProtocolsBaseFlextclimodelsbasePart08.AtomicDirectoryChainPlan
        ]

    @runtime_checkable
    class AtomicDirectoryQueryEffects(FlextProtocols.BaseModel, Protocol):
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
            """Authenticated file effects in this boundary."""
            ...

        membership_policy: t.StrTuple

    @runtime_checkable
    class AtomicFilePublication(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def before(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState:
            """Exact destination state observed during preflight."""
            ...

        @property
        def replacement(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState:
            """Exact caller-owned staged replacement state."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart10",
]
