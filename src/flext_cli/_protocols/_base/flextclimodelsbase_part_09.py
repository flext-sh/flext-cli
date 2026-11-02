# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/_base/flextclimodelsbase_part_09
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_cli import t

if TYPE_CHECKING:
    from flext_cli.protocols import p


class FlextCliProtocolsBaseFlextclimodelsbasePart09:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class AtomicPhysicalTreeEntry(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def path(self) -> Path: ...
        @property
        def kind(self) -> Literal["directory", "file", "symlink"]: ...
        @property
        def parent_device(self) -> int: ...
        @property
        def parent_inode(self) -> int: ...
        @property
        def parent_mount_id(self) -> int: ...
        @property
        def mode(self) -> int: ...
        @property
        def device(self) -> int: ...
        @property
        def inode(self) -> int: ...
        @property
        def mount_id(self) -> int: ...
        @property
        def link_count(self) -> int: ...
        @property
        def uid(self) -> int: ...
        @property
        def gid(self) -> int: ...
        @property
        def mtime_ns(self) -> int: ...
        @property
        def ctime_ns(self) -> int: ...
        @property
        def file_attributes(self) -> int | None: ...
        @property
        def link_target(self) -> str | None: ...
        @property
        def reparse_tag(self) -> int | None: ...
        @property
        def size(self) -> int | None: ...
        @property
        def sha256(self) -> str | None: ...

    @runtime_checkable
    class AtomicDirectoryName(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str: ...
        @property
        def kind(self) -> Literal["directory", "file", "symlink", "other"]: ...
        @property
        def version_key(self) -> tuple[int, ...]: ...
        @property
        def link_target(self) -> str | None: ...

    @runtime_checkable
    class AtomicDirectoryInventory(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def root(self) -> p.Cli.AtomicPhysicalTreeEntry: ...
        @property
        def entries(self) -> tuple[p.Cli.AtomicDirectoryName, ...]: ...
        @property
        def queries(
            self,
        ) -> tuple[tuple[str, Literal["exists", "isfile", "isdir"]], ...]: ...
        @property
        def membership_queried(self) -> bool: ...
        @property
        def membership_queries(self) -> tuple[t.StrTuple, ...]: ...

    @runtime_checkable
    class AtomicPhysicalTreeManifest(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def root(self) -> p.Cli.AtomicPhysicalTreeEntry: ...
        @property
        def entries(self) -> tuple[p.Cli.AtomicPhysicalTreeEntry, ...]: ...


__all__: list[str] = [
    "FlextCliProtocolsBaseFlextclimodelsbasePart09",
]
