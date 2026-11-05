# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/atomic_symlink
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from flext_core import p


class FlextCliProtocolsAtomicSymlink:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class AtomicSymlinkIdentity(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def mode(self) -> int:
            """Exact link permission bits."""
            ...

        @property
        def device(self) -> int:
            """Link filesystem device."""
            ...

        @property
        def inode(self) -> int:
            """Link inode number."""
            ...

        @property
        def link_count(self) -> int:
            """Link inode reference count."""
            ...

        @property
        def uid(self) -> int:
            """Link owner user identifier."""
            ...

        @property
        def gid(self) -> int:
            """Link owner group identifier."""
            ...

        @property
        def mtime_ns(self) -> int:
            """Link modification timestamp."""
            ...

        @property
        def ctime_ns(self) -> int:
            """Link change timestamp."""
            ...

        @property
        def file_attributes(self) -> int | None:
            """Platform file attributes."""
            ...

        @property
        def reparse_tag(self) -> int | None:
            """Platform reparse tag."""
            ...

    @runtime_checkable
    class AtomicSymlinkState(p.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def path(self) -> Path:
            """Absolute lexical symbolic-link path."""
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
        def target(self) -> str | None:
            """Exact readlink text, or None when absent."""
            ...

        @property
        def identity(
            self,
        ) -> FlextCliProtocolsAtomicSymlink.AtomicSymlinkIdentity | None:
            """Complete physical link identity, or None when absent."""
            ...


__all__: list[str] = [
    "FlextCliProtocolsAtomicSymlink",
]
