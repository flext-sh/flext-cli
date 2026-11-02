# Copyright (c) 2026 FLEXT Team. All rights reserved.
# SPDX-License-Identifier: MIT
"""Structural contracts mirrored from model base part 09."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Protocol, runtime_checkable

from flext_cli._protocols._base import FlextCliProtocolsBasePart05


class FlextCliProtocolsBasePart09(FlextCliProtocolsBasePart05):
    """Runtime-checkable physical-tree contracts used during protocol bootstrap."""

    @runtime_checkable
    class AtomicPhysicalTreeEntry(Protocol):
        """One descriptor-authenticated physical filesystem entry."""

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
        def device(self) -> int: ...

        @property
        def inode(self) -> int: ...

        @property
        def mount_id(self) -> int: ...

    @runtime_checkable
    class AtomicPhysicalTreeManifest(Protocol):
        """One root entry and its ordered physical descendants."""

        @property
        def root(self) -> FlextCliProtocolsBasePart09.AtomicPhysicalTreeEntry: ...

        @property
        def entries(
            self,
        ) -> tuple[FlextCliProtocolsBasePart09.AtomicPhysicalTreeEntry, ...]: ...


__all__: tuple[str, ...] = ("FlextCliProtocolsBasePart09",)
