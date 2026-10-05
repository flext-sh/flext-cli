"""Low-level descriptor measurements for physical-tree ownership.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import hashlib
import os
import sys
from pathlib import Path
from typing import Never

from flext_cli import t
from flext_cli._utilities import atomic_tree_darwin as tree_darwin
from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)
from flext_cli._utilities.atomic_file_path import FlextCliUtilitiesAtomicFilePath
from flext_cli._utilities.atomic_file_read import FlextCliUtilitiesAtomicFileRead
from flext_cli._utilities.atomic_file_state import FlextCliUtilitiesAtomicFileState


class FlextCliUtilitiesAtomicTreeDescriptor:
    """Canonical namespace owner."""

    _FILE_FLAGS = (
        os.O_RDONLY
        | getattr(os, "O_NONBLOCK", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_BINARY", 0)
    )

    @staticmethod
    def measure_authenticated_file(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        path: Path,
        expected: os.stat_result,
        *,
        required_mount_id: int,
    ) -> t.Pair[int, str]:
        """Hash one stable regular file without materializing it in memory.

        Returns:
            The resulting ``t.Pair[int, str]``.

        """
        digest = hashlib.sha256()
        size = 0
        with FlextCliUtilitiesAtomicFileDescriptor.entry_descriptor(
            parent,
            path,
            FlextCliUtilitiesAtomicTreeDescriptor._FILE_FLAGS,
        ) as descriptor:
            FlextCliUtilitiesAtomicTreeDescriptor._require_file_state(
                descriptor,
                path,
                expected,
            )
            FlextCliUtilitiesAtomicTreeDescriptor.require_mount(
                path,
                required_mount_id,
                FlextCliUtilitiesAtomicTreeDescriptor.mount_id(descriptor, path),
            )
            while chunk := os.read(descriptor, 1024 * 1024):
                size += len(chunk)
                digest.update(chunk)
            FlextCliUtilitiesAtomicTreeDescriptor._require_file_state(
                descriptor,
                path,
                expected,
            )
        FlextCliUtilitiesAtomicFileState.assert_destination_unchanged(
            path,
            expected,
            parent=parent,
        )
        return size, digest.hexdigest()

    @staticmethod
    def mount_id(descriptor: int, path: Path) -> int:
        """Return the host's descriptor-bound mount identity or fail closed.

        Returns:
            The host's descriptor-bound mount identity or fail closed.

        Raises:
            OSError: If ``platform_name != 'linux'``; or if ``len(values) != 1 or not
                values[0].isdecimal()``; or if ``value < 1``; or if a ``(OSError,
                UnicodeError)`` is caught.

        """
        platform_name = FlextCliUtilitiesAtomicTreeDescriptor._runtime_platform()
        if platform_name == "darwin":
            return tree_darwin.FlextCliAtomicTreeDarwin.mount_id(descriptor, path)
        if platform_name != "linux":
            message = "descriptor-bound mount identity is unsupported"
            raise OSError(errno.ENOTSUP, message, path)
        values: list[str]
        try:
            with (Path("/proc/self/fdinfo") / str(descriptor)).open(
                encoding="ascii",
            ) as stream:
                values = [
                    line.removeprefix("mnt_id:").strip()
                    for line in stream
                    if line.startswith("mnt_id:")
                ]
        except (OSError, UnicodeError) as exc:
            message = "descriptor-bound mount identity is unavailable"
            raise OSError(errno.ENOTSUP, message, path) from exc
        if len(values) != 1 or not values[0].isdecimal():
            message = "descriptor-bound mount identity is invalid"
            raise OSError(errno.EIO, message, path)
        value = int(values[0])
        if value < 1:
            message = "descriptor-bound mount identity must be positive"
            raise OSError(errno.EIO, message, path)
        return value

    @staticmethod
    def require_mount(path: Path, expected: int, observed: int) -> None:
        """Reject a mount transition before reading through the descriptor.

        Raises:
            OSError: If ``observed != expected``.

        """
        if observed != expected:
            message = f"atomic physical-tree entry crosses its parent mount: {path}"
            raise OSError(errno.EXDEV, message, path)

    @staticmethod
    def require_same_device(
        path: Path,
        parent: os.stat_result,
        observed: os.stat_result,
    ) -> None:
        """Reject a device transition before traversing or reading an entry.

        Raises:
            OSError: If ``observed.st_dev != parent.st_dev``.

        """
        if observed.st_dev != parent.st_dev:
            message = f"atomic physical-tree entry crosses its parent device: {path}"
            raise OSError(errno.EXDEV, message, path)

    @staticmethod
    def require_directory_state(
        descriptor: int,
        path: Path,
        expected: os.stat_result,
    ) -> None:
        """Require one directory FD to retain the complete observed state."""
        observed = os.fstat(descriptor)
        FlextCliUtilitiesAtomicFilePath.validate_directory_state(path, observed)
        if FlextCliUtilitiesAtomicFileRead.state_key(
            observed,
        ) != FlextCliUtilitiesAtomicFileRead.state_key(expected):
            FlextCliUtilitiesAtomicTreeDescriptor._raise_changed(path)

    @staticmethod
    def require_entry_state(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        path: Path,
        expected: os.stat_result,
    ) -> None:
        """Require one parent-relative name to retain the complete observed state."""
        observed = FlextCliUtilitiesAtomicFileDescriptor.entry_stat(parent, path)
        if FlextCliUtilitiesAtomicFileRead.state_key(
            observed,
        ) != FlextCliUtilitiesAtomicFileRead.state_key(expected):
            FlextCliUtilitiesAtomicTreeDescriptor._raise_changed(path)

    @staticmethod
    def _require_file_state(
        descriptor: int,
        path: Path,
        expected: os.stat_result,
    ) -> None:
        if FlextCliUtilitiesAtomicFileRead.state_key(
            os.fstat(descriptor),
        ) != FlextCliUtilitiesAtomicFileRead.state_key(expected):
            FlextCliUtilitiesAtomicTreeDescriptor._raise_changed(path)

    @staticmethod
    def _runtime_platform() -> str:
        """Read the platform at invocation time for typed portable dispatch.

        Returns:
            The resulting ``str``.

        """
        return sys.platform

    @staticmethod
    def _raise_changed(path: Path) -> Never:
        message = f"atomic physical-tree entry changed during authentication: {path}"
        raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicTreeDescriptor"]
