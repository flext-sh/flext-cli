"""Public directory durability for completed atomic namespace mutations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os

from flext_cli._utilities import atomic_file_descriptor, atomic_file_path


def sync_parent(
    parent: atomic_file_descriptor.ParentDescriptor,
) -> None:
    """Sync one authenticated directory after its namespace was mutated."""
    atomic_file_descriptor.assert_parent_unchanged(parent)
    os.fsync(parent.descriptor)
    atomic_file_descriptor.assert_parent_unchanged(parent)


def sync_replacement(
    source: atomic_file_descriptor.ParentDescriptor,
    destination: atomic_file_descriptor.ParentDescriptor,
) -> None:
    """Sync every physical directory changed by one completed replacement."""
    sync_parent(source)
    if atomic_file_path.identity(
        source.state,
    ) != atomic_file_path.identity(destination.state):
        sync_parent(destination)


__all__: list[str] = [
    "sync_parent",
    "sync_replacement",
]
