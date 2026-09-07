"""Descriptor-only namespace effects for physical empty directories."""

from __future__ import annotations

import errno
import os
from pathlib import Path

from . import (
    atomic_directory_noreplace as directory_noreplace,
    atomic_file_descriptor as file_descriptor,
    atomic_parent_descriptor as parent_descriptor,
)

_SECURE_CREATE_MODE = 0o700


def require_read_capabilities(path: Path) -> None:
    """Fail before access when descriptor-bound directory reads are unavailable."""
    if os.listdir not in os.supports_fd:
        message = "descriptor-bound directory listing is unsupported"
        raise OSError(errno.ENOTSUP, message, path)


def require_create_capabilities(path: Path) -> None:
    """Fail before mkdir unless creation, cleanup, and chmod are descriptor-bound."""
    require_read_capabilities(path)
    _require_dir_fd(path, (("mkdir", os.mkdir), ("rmdir", os.rmdir)))
    if not hasattr(os, "fchmod"):
        message = "descriptor-bound directory permission changes are unsupported"
        raise OSError(errno.ENOTSUP, message, path)


def require_delete_capabilities(path: Path) -> None:
    """Fail before inspection unless guarded rmdir is descriptor-bound."""
    require_read_capabilities(path)
    _require_dir_fd(path, (("rmdir", os.rmdir),))


def require_publish_capabilities(source: Path, destination: Path) -> None:
    """Fail before publication unless no-clobber rename and durability exist."""
    require_read_capabilities(source)
    parent_descriptor.require_traversal_capabilities(source)
    parent_descriptor.require_traversal_capabilities(destination)
    directory_noreplace.require_noreplace_capability(destination)
    if not hasattr(os, "fsync"):
        message = "directory durability sync is unsupported"
        raise OSError(errno.ENOTSUP, message, destination)


def create_entry(parent: file_descriptor.ParentDescriptor, path: Path) -> None:
    """Create one secure empty child through an authenticated parent descriptor."""
    file_descriptor.require_entry(parent, path)
    file_descriptor.assert_parent_unchanged(parent)
    os.mkdir(path.name, _SECURE_CREATE_MODE, dir_fd=parent.descriptor)


def remove_entry(parent: file_descriptor.ParentDescriptor, path: Path) -> None:
    """Remove one empty child through an authenticated parent descriptor."""
    file_descriptor.require_entry(parent, path)
    file_descriptor.assert_parent_unchanged(parent)
    os.rmdir(path.name, dir_fd=parent.descriptor)


def rename_entry_noreplace(
    source_parent: file_descriptor.ParentDescriptor,
    source: Path,
    destination_parent: file_descriptor.ParentDescriptor,
    destination: Path,
) -> None:
    """Move one child without clobbering any destination entry."""
    file_descriptor.require_entry(source_parent, source)
    file_descriptor.require_entry(destination_parent, destination)
    file_descriptor.assert_parent_unchanged(source_parent)
    file_descriptor.assert_parent_unchanged(destination_parent)
    directory_noreplace.rename_noreplace(
        source_parent.descriptor,
        source.name,
        destination_parent.descriptor,
        destination.name,
        path=destination,
    )


def _require_dir_fd(path: Path, operations: tuple[tuple[str, object], ...]) -> None:
    missing = [
        name for name, operation in operations if operation not in os.supports_dir_fd
    ]
    if missing:
        message = f"descriptor-bound directory operations are unsupported: {missing}"
        raise OSError(errno.ENOTSUP, message, path)


__all__: list[str] = [
    "create_entry",
    "remove_entry",
    "rename_entry_noreplace",
    "require_create_capabilities",
    "require_delete_capabilities",
    "require_publish_capabilities",
    "require_read_capabilities",
]
