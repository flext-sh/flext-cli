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

from flext_core import p

if TYPE_CHECKING:
    from flext_cli._constants import FlextCliConstantsFiles
    from flext_cli._protocols._base import FlextCliProtocolsBaseFlextclimodelsbasePart02


class FlextCliProtocolsAtomicPublication:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class StagedFile(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def path(self) -> Path:
            """Exact pathname of the staged file."""
            ...

        @property
        def content(self) -> bytes:
            """Authenticated staged file bytes."""
            ...

        @property
        def mode(self) -> int:
            """Native permission mode of the staged file."""
            ...

        @property
        def identity(self) -> tuple[int, int]:
            """Captured device and inode identity of the staged file."""
            ...

    @runtime_checkable
    class ObservedFile(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def path(self) -> Path:
            """Pathname of the observed file entry."""
            ...

        @property
        def state(self) -> os.stat_result:
            """Unchanged native stat observation of the file entry."""
            ...

    @runtime_checkable
    class AtomicWriteOptions(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def expected_state(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState | None:
            """Complete physical precondition, or None for none."""
            ...

        @property
        def permission_mode(self) -> int | None:
            """Permission mode to publish, or None to keep the current one."""
            ...

        @property
        def durability(self) -> FlextCliConstantsFiles.WriteDurability:
            """Whether staged inode and parent directory are synced."""
            ...

        @property
        def owner_uid(self) -> int | None:
            """Required owner uid of the parent and published file."""
            ...

    @runtime_checkable
    class TreeEntryDetails(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def kind(self) -> Literal["directory", "file", "symlink"]:
            """Measured filesystem kind of the tree entry."""
            ...

        @property
        def parent_mount_id(self) -> int:
            """Mount identity of the parent entry."""
            ...

        @property
        def mount_id(self) -> int:
            """Mount identity of the tree entry."""
            ...

        @property
        def size(self) -> int | None:
            """Measured file byte size."""
            ...

        @property
        def digest(self) -> str | None:
            """Authenticated content digest for a regular file."""
            ...

        @property
        def link_target(self) -> str | None:
            """Literal target of a symbolic link entry."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsAtomicPublication",
]
