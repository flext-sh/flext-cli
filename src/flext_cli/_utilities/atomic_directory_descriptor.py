"""Descriptor-only namespace effects for physical empty directories.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from pathlib import Path
from typing import ClassVar

from flext_cli import t
from flext_cli._utilities.atomic_directory_noreplace import (
    FlextCliUtilitiesAtomicDirectoryNoreplace,
)
from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)
from flext_cli._utilities.atomic_parent_descriptor import (
    FlextCliUtilitiesAtomicParentDescriptor,
)


class FlextCliUtilitiesAtomicDirectoryDescriptor:
    """Canonical namespace owner."""

    _SECURE_CREATE_MODE: ClassVar[int] = 0o700

    @staticmethod
    def require_read_capabilities(path: Path) -> None:
        """Fail before access when descriptor-bound directory reads are unavailable.

        Raises:
            OSError: If ``os.listdir not in os.supports_fd``.

        """
        if os.listdir not in os.supports_fd:
            message = "descriptor-bound directory listing is unsupported"
            raise OSError(errno.ENOTSUP, message, path)

    @staticmethod
    def require_create_capabilities(path: Path) -> None:
        """Fail before mkdir unless creation, cleanup, and chmod are descriptor-bound.

        Raises:
            OSError: If ``not hasattr(os, 'fchmod')``.

        """
        FlextCliUtilitiesAtomicDirectoryDescriptor.require_read_capabilities(path)
        FlextCliUtilitiesAtomicDirectoryDescriptor._require_dir_fd(
            path, (("mkdir", os.mkdir), ("rmdir", os.rmdir))
        )
        if not hasattr(os, "fchmod"):
            message = "descriptor-bound directory permission changes are unsupported"
            raise OSError(errno.ENOTSUP, message, path)

    @staticmethod
    def require_delete_capabilities(path: Path) -> None:
        """Fail before inspection unless guarded rmdir is descriptor-bound."""
        FlextCliUtilitiesAtomicDirectoryDescriptor.require_read_capabilities(path)
        FlextCliUtilitiesAtomicDirectoryDescriptor._require_dir_fd(
            path, (("rmdir", os.rmdir),)
        )

    @staticmethod
    def require_publish_capabilities(source: Path, destination: Path) -> None:
        """Fail before publication unless no-clobber rename and durability exist.

        Raises:
            OSError: If ``not hasattr(os, 'fsync')``.

        """
        FlextCliUtilitiesAtomicDirectoryDescriptor.require_read_capabilities(source)
        FlextCliUtilitiesAtomicParentDescriptor.require_traversal_capabilities(source)
        FlextCliUtilitiesAtomicParentDescriptor.require_traversal_capabilities(
            destination
        )
        FlextCliUtilitiesAtomicDirectoryNoreplace.require_noreplace_capability(
            destination
        )
        if not hasattr(os, "fsync"):
            message = "directory durability sync is unsupported"
            raise OSError(errno.ENOTSUP, message, destination)

    @staticmethod
    def create_entry(
        parent: FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor,
        path: Path,
    ) -> None:
        """Create one secure empty child through an authenticated parent descriptor."""
        FlextCliUtilitiesAtomicFileDescriptor.require_entry(parent, path)
        FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(parent)
        os.mkdir(
            path.name,
            FlextCliUtilitiesAtomicDirectoryDescriptor._SECURE_CREATE_MODE,
            dir_fd=parent.descriptor,
        )

    @staticmethod
    def remove_entry(
        parent: FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor,
        path: Path,
    ) -> None:
        """Remove one empty child through an authenticated parent descriptor."""
        FlextCliUtilitiesAtomicFileDescriptor.require_entry(parent, path)
        FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(parent)
        os.rmdir(path.name, dir_fd=parent.descriptor)

    @staticmethod
    def rename_entry_noreplace(
        source_parent: FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor,
        source: Path,
        destination_parent: FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor,
        destination: Path,
    ) -> None:
        """Move one child without clobbering any destination entry."""
        FlextCliUtilitiesAtomicFileDescriptor.require_entry(source_parent, source)
        FlextCliUtilitiesAtomicFileDescriptor.require_entry(
            destination_parent, destination
        )
        FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(source_parent)
        FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(
            destination_parent
        )
        FlextCliUtilitiesAtomicDirectoryNoreplace.rename_noreplace(
            source_parent.descriptor,
            source.name,
            destination_parent.descriptor,
            destination.name,
            path=destination,
        )

    @staticmethod
    def _require_dir_fd(
        path: Path,
        operations: t.VariadicTuple[t.Pair[str, t.Cli.DirFdOperation]],
    ) -> None:
        missing = [
            name
            for name, operation in operations
            if operation not in os.supports_dir_fd
        ]
        if missing:
            message = (
                f"descriptor-bound directory operations are unsupported: {missing}"
            )
            raise OSError(errno.ENOTSUP, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicDirectoryDescriptor"]
