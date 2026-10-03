"""Descriptor-only namespace effects for physical empty directories.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli._utilities import (
    atomic_directory_noreplace,
    atomic_file_descriptor,
    atomic_parent_descriptor,
)

if TYPE_CHECKING:
    from flext_cli import t


_SECURE_CREATE_MODE: int = 0o700


def require_read_capabilities(path: Path) -> None:
    """Fail before access when descriptor-bound directory reads are unavailable.

    Raises:
        OSError: If ``os.listdir not in os.supports_fd``.

    """
    if os.listdir not in os.supports_fd:
        message = "descriptor-bound directory listing is unsupported"
        raise OSError(errno.ENOTSUP, message, path)


def require_create_capabilities(path: Path) -> None:
    """Fail before mkdir unless creation, cleanup, and chmod are descriptor-bound.

    Raises:
        OSError: If ``not hasattr(os, 'fchmod')``.

    """
    require_read_capabilities(path)
    _require_dir_fd(
        path,
        (("mkdir", os.mkdir), ("rmdir", os.rmdir)),
    )
    if not hasattr(os, "fchmod"):
        message = "descriptor-bound directory permission changes are unsupported"
        raise OSError(errno.ENOTSUP, message, path)


def require_delete_capabilities(path: Path) -> None:
    """Fail before inspection unless guarded rmdir is descriptor-bound."""
    require_read_capabilities(path)
    _require_dir_fd(
        path,
        (("rmdir", os.rmdir),),
    )


def require_publish_capabilities(source: Path, destination: Path) -> None:
    """Fail before publication unless no-clobber rename and durability exist.

    Raises:
        OSError: If ``not hasattr(os, 'fsync')``.

    """
    require_read_capabilities(source)
    atomic_parent_descriptor.require_traversal_capabilities(source)
    atomic_parent_descriptor.require_traversal_capabilities(
        destination,
    )
    atomic_directory_noreplace.require_noreplace_capability(
        destination,
    )
    if not hasattr(os, "fsync"):
        message = "directory durability sync is unsupported"
        raise OSError(errno.ENOTSUP, message, destination)


def create_entry(
    parent: atomic_file_descriptor.ParentDescriptor,
    path: Path,
) -> None:
    """Create one secure empty child through an authenticated parent descriptor."""
    atomic_file_descriptor.require_entry(parent, path)
    atomic_file_descriptor.assert_parent_unchanged(parent)
    os.mkdir(
        path.name,
        _SECURE_CREATE_MODE,
        dir_fd=parent.descriptor,
    )


def remove_entry(
    parent: atomic_file_descriptor.ParentDescriptor,
    path: Path,
) -> None:
    """Remove one empty child through an authenticated parent descriptor."""
    atomic_file_descriptor.require_entry(parent, path)
    atomic_file_descriptor.assert_parent_unchanged(parent)
    os.rmdir(path.name, dir_fd=parent.descriptor)


def rename_entry_noreplace(
    source_parent: atomic_file_descriptor.ParentDescriptor,
    source: Path,
    destination_parent: (atomic_file_descriptor.ParentDescriptor),
    destination: Path,
) -> None:
    """Move one child without clobbering any destination entry."""
    atomic_file_descriptor.require_entry(source_parent, source)
    atomic_file_descriptor.require_entry(
        destination_parent,
        destination,
    )
    atomic_file_descriptor.assert_parent_unchanged(source_parent)
    atomic_file_descriptor.assert_parent_unchanged(
        destination_parent,
    )
    atomic_directory_noreplace.rename_noreplace(
        source_parent.descriptor,
        source.name,
        destination_parent.descriptor,
        destination.name,
        path=destination,
    )


def _require_dir_fd(
    path: Path,
    operations: t.VariadicTuple[t.Pair[str, t.Cli.DirFdOperation]],
) -> None:
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
