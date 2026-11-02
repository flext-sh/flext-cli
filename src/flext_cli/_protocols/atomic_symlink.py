# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_cli/_protocols/atomic_symlink
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_cli.protocols import p


class FlextCliProtocolsAtomicSymlink:
    """Own the structural model contracts declared by this module."""

    @runtime_checkable
    class AtomicSymlinkIdentity(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def mode(self) -> int: ...
        @property
        def device(self) -> int: ...
        @property
        def inode(self) -> int: ...
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
        def reparse_tag(self) -> int | None: ...

    @runtime_checkable
    class AtomicSymlinkState(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def path(self) -> Path: ...
        @property
        def parent_device(self) -> int: ...
        @property
        def parent_inode(self) -> int: ...
        @property
        def target(self) -> str | None: ...
        @property
        def identity(self) -> p.Cli.AtomicSymlinkIdentity | None: ...


__all__: list[str] = [
    "FlextCliProtocolsAtomicSymlink",
]
