"""Stable descriptor-authenticated state for physical empty directories.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from pathlib import Path
from typing import ClassVar

from flext_cli import t
from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)
from flext_cli._utilities.atomic_file_mode import FlextCliUtilitiesAtomicFileMode
from flext_cli._utilities.atomic_file_path import FlextCliUtilitiesAtomicFilePath
from flext_cli._utilities.atomic_file_read import FlextCliUtilitiesAtomicFileRead


class FlextCliUtilitiesAtomicDirectoryState:
    """Canonical namespace owner."""

    _MAX_EMPTY_DIRECTORY_LINK_COUNT: ClassVar[int] = 2

    @staticmethod
    def destination_state(
        path: Path,
        *,
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
    ) -> os.stat_result | None:
        """Read one final directory entry without following it or crossing devices.

        Returns:
            The resulting ``os.stat_result | None``.

        Raises:
            OSError: If ``state.st_dev != parent.state.st_dev``.

        """
        state: os.stat_result | None
        try:
            state = FlextCliUtilitiesAtomicFileDescriptor.entry_stat(parent, path)
        except FileNotFoundError:
            state = None
        if state is None:
            return None
        FlextCliUtilitiesAtomicFilePath.validate_directory_state(path, state)
        if state.st_dev != parent.state.st_dev:
            message = f"atomic directory crosses its physical parent device: {path}"
            raise OSError(errno.EXDEV, message, path)
        return state

    @staticmethod
    def read_empty_state(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        path: Path,
        expected: os.stat_result,
    ) -> os.stat_result:
        """Prove one exact directory version remains empty through an FD read.

        Returns:
            The resulting ``os.stat_result``.

        """
        flags = (
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_BINARY", 0)
        )
        with FlextCliUtilitiesAtomicFileDescriptor.entry_descriptor(
            parent,
            path,
            flags,
        ) as descriptor:
            FlextCliUtilitiesAtomicDirectoryState._require_descriptor_state(
                descriptor,
                path,
                expected,
            )
            FlextCliUtilitiesAtomicDirectoryState._require_empty(descriptor, path)
            FlextCliUtilitiesAtomicDirectoryState._require_descriptor_state(
                descriptor,
                path,
                expected,
            )
        return FlextCliUtilitiesAtomicDirectoryState._require_path_state(
            parent,
            path,
            expected,
        )

    @staticmethod
    def initialize_empty_state(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        path: Path,
        expected: os.stat_result,
        permission_mode: int,
    ) -> os.stat_result:
        """Set and sync exact mode on a newly-created, still-empty directory inode.

        Returns:
            The resulting ``os.stat_result``.

        """
        flags = (
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_BINARY", 0)
        )
        with FlextCliUtilitiesAtomicFileDescriptor.entry_descriptor(
            parent,
            path,
            flags,
        ) as descriptor:
            FlextCliUtilitiesAtomicDirectoryState._require_descriptor_state(
                descriptor,
                path,
                expected,
            )
            FlextCliUtilitiesAtomicDirectoryState._require_empty(descriptor, path)
            os.fchmod(descriptor, permission_mode)
            FlextCliUtilitiesAtomicFileMode.assert_observed_mode(
                path,
                os.fstat(descriptor),
                permission_mode,
            )
            os.fsync(descriptor)
            final = os.fstat(descriptor)
            FlextCliUtilitiesAtomicDirectoryState._require_empty(descriptor, path)
            FlextCliUtilitiesAtomicDirectoryState._require_descriptor_state(
                descriptor,
                path,
                final,
            )
        return FlextCliUtilitiesAtomicDirectoryState._require_path_state(
            parent,
            path,
            final,
        )

    @staticmethod
    def require_identity(
        path: Path,
        state: os.stat_result,
        expected: t.Pair[int, int],
    ) -> None:
        """Require one directory entry to retain a caller-owned inode.

        Raises:
            OSError: If ``file_path.identity(state) != expected``.

        """
        if FlextCliUtilitiesAtomicFilePath.identity(state) != expected:
            message = f"atomic directory identity changed: {path}"
            raise OSError(errno.ESTALE, message, path)

    @staticmethod
    def _require_descriptor_state(
        descriptor: int,
        path: Path,
        expected: os.stat_result,
    ) -> None:
        observed = os.fstat(descriptor)
        FlextCliUtilitiesAtomicFilePath.validate_directory_state(path, observed)
        if FlextCliUtilitiesAtomicFileRead.state_key(
            observed,
        ) != FlextCliUtilitiesAtomicFileRead.state_key(expected):
            message = f"atomic directory changed during descriptor access: {path}"
            raise OSError(errno.ESTALE, message, path)

    @staticmethod
    def _require_empty(descriptor: int, path: Path) -> None:
        entries = os.listdir(descriptor)
        if entries:
            message = f"atomic directory is not empty: {path}"
            raise OSError(errno.ENOTEMPTY, message, path)
        state = os.fstat(descriptor)
        if (
            state.st_nlink
            > FlextCliUtilitiesAtomicDirectoryState._MAX_EMPTY_DIRECTORY_LINK_COUNT
        ):
            message = f"empty atomic directory has unexpected links: {path}"
            raise OSError(errno.EMLINK, message, path)

    @staticmethod
    def _require_path_state(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        path: Path,
        expected: os.stat_result,
    ) -> os.stat_result:
        current = FlextCliUtilitiesAtomicDirectoryState.destination_state(
            path,
            parent=parent,
        )
        if current is None or FlextCliUtilitiesAtomicFileRead.state_key(
            current,
        ) != FlextCliUtilitiesAtomicFileRead.state_key(expected):
            message = f"atomic directory changed during authenticated read: {path}"
            raise OSError(errno.ESTALE, message, path)
        FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(parent)
        return current


__all__: list[str] = ["FlextCliUtilitiesAtomicDirectoryState"]
