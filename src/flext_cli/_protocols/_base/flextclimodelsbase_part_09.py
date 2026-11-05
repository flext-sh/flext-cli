# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_09
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_core import FlextProtocols

from flext_cli._protocols._base import FlextCliProtocolsBaseFlextclimodelsbasePart08

if TYPE_CHECKING:
    pass


class FlextCliProtocolsBaseFlextclimodelsbasePart09:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class AtomicPhysicalTreeEntry(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def path(self) -> Path:
            """Absolute entry path."""
            ...

        @property
        def kind(self) -> Literal["directory", "file", "symlink"]:
            """Physical entry kind."""
            ...

        @property
        def parent_device(self) -> int:
            """Physical parent device."""
            ...

        @property
        def parent_inode(self) -> int:
            """Physical parent inode."""
            ...

        @property
        def parent_mount_id(self) -> int:
            """Physical parent mount ID."""
            ...

        @property
        def mode(self) -> int:
            """Permission bits."""
            ...

        @property
        def device(self) -> int:
            """Physical device."""
            ...

        @property
        def inode(self) -> int:
            """Physical inode."""
            ...

        @property
        def mount_id(self) -> int:
            """Physical mount ID."""
            ...

        @property
        def link_count(self) -> int:
            """Exact link count."""
            ...

        @property
        def uid(self) -> int:
            """Owner user ID."""
            ...

        @property
        def gid(self) -> int:
            """Owner group ID."""
            ...

        @property
        def mtime_ns(self) -> int:
            """Modification timestamp in ns."""
            ...

        @property
        def ctime_ns(self) -> int:
            """Metadata-change timestamp in ns."""
            ...

        @property
        def file_attributes(self) -> int | None:
            """Host attributes."""
            ...

        @property
        def link_target(self) -> str | None:
            """Exact symlink target text."""
            ...

        @property
        def reparse_tag(self) -> int | None:
            """Host reparse tag."""
            ...

        @property
        def size(self) -> int | None:
            """Regular-file size."""
            ...

        @property
        def sha256(self) -> str | None:
            """Regular-file SHA-256 digest."""
            ...

    @runtime_checkable
    class AtomicDirectoryName(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str:
            """Lexical child name."""
            ...

        @property
        def kind(self) -> Literal["directory", "file", "symlink", "other"]:
            """Native physical entry kind."""
            ...

        @property
        def version_key(self) -> tuple[int, ...]:
            """Descriptor-authenticated native entry version."""
            ...

        @property
        def link_target(self) -> str | None:
            """Literal target of a physical symlink."""
            ...

    @runtime_checkable
    class AtomicDirectoryInventory(
        FlextCliProtocolsBaseFlextclimodelsbasePart08.AtomicNativeSelections, Protocol
    ):
        """Structural data contract projected from the owning model."""

        @property
        def root(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart09.AtomicPhysicalTreeEntry:
            """Descriptor-authenticated physical directory identity."""
            ...

        @property
        def entries(
            self,
        ) -> tuple[
            FlextCliProtocolsBaseFlextclimodelsbasePart09.AtomicDirectoryName, ...
        ]:
            """Complete ordered immediate physical children."""
            ...

    @runtime_checkable
    class AtomicPhysicalTreeManifest(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def root(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart09.AtomicPhysicalTreeEntry:
            """Physical tree root."""
            ...

        @property
        def entries(
            self,
        ) -> tuple[
            FlextCliProtocolsBaseFlextclimodelsbasePart09.AtomicPhysicalTreeEntry, ...
        ]:
            """Lexically ordered descendants."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart09",
]
