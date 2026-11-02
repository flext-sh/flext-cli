# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/atomic_publication
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_cli import c

if TYPE_CHECKING:
    from flext_cli.protocols import p


class FlextCliProtocolsAtomicPublication:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class StagedFile(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def path(self) -> Path: ...
        @property
        def content(self) -> bytes: ...
        @property
        def mode(self) -> int: ...
        @property
        def identity(self) -> tuple[int, int]: ...

    @runtime_checkable
    class ObservedFile(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def path(self) -> Path: ...
        @property
        def state(self) -> os.stat_result: ...

    @runtime_checkable
    class AtomicWriteOptions(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def expected_state(self) -> p.Cli.AtomicFileState | None: ...
        @property
        def permission_mode(self) -> int | None: ...
        @property
        def durability(self) -> c.Cli.WriteDurability: ...
        @property
        def owner_uid(self) -> int | None: ...

    @runtime_checkable
    class TreeEntryDetails(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["directory", "file", "symlink"]: ...
        @property
        def parent_mount_id(self) -> int: ...
        @property
        def mount_id(self) -> int: ...
        @property
        def size(self) -> int | None: ...
        @property
        def digest(self) -> str | None: ...
        @property
        def link_target(self) -> str | None: ...


__all__: list[str] = [
    "FlextCliProtocolsAtomicPublication",
]
