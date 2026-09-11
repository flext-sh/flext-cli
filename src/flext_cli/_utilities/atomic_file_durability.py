"""Public directory durability for completed atomic namespace mutations."""

from __future__ import annotations

import os

from . import atomic_file_descriptor as file_descriptor, atomic_file_path as file_path


def sync_parent(parent: file_descriptor.ParentDescriptor) -> None:
    """Sync one authenticated directory after its namespace was mutated."""
    file_descriptor.assert_parent_unchanged(parent)
    os.fsync(parent.descriptor)
    file_descriptor.assert_parent_unchanged(parent)


def sync_replacement(
    source: file_descriptor.ParentDescriptor,
    destination: file_descriptor.ParentDescriptor,
) -> None:
    """Sync every physical directory changed by one completed replacement."""
    sync_parent(source)
    if file_path.identity(source.state) != file_path.identity(destination.state):
        sync_parent(destination)


__all__: list[str] = ["sync_parent", "sync_replacement"]
