"""Authenticated cleanup for a failed guarded empty-directory creation.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli._utilities.atomic_directory_descriptor import (
    FlextCliUtilitiesAtomicDirectoryDescriptor,
)
from flext_cli._utilities.atomic_directory_state import (
    FlextCliUtilitiesAtomicDirectoryState,
)
from flext_cli._utilities.atomic_file_durability import (
    FlextCliUtilitiesAtomicFileDurability,
)
from flext_cli._utilities.atomic_file_read import FlextCliUtilitiesAtomicFileRead

if TYPE_CHECKING:
    from flext_cli import t
    from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)


class FlextCliUtilitiesAtomicDirectoryCleanup:
    """Canonical namespace owner."""

    @staticmethod
    def remove_created_directory(
        parent: FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor,
        path: Path,
        identity: t.Pair[int, int] | None,
        operation_error: BaseException,
    ) -> None:
        """Remove only the still-empty inode created by the failed operation."""
        cleanup_errors: list[OSError] = []
        try:
            FlextCliUtilitiesAtomicDirectoryCleanup._remove_created_directory(
                parent, path, identity,
            )
        except OSError as cleanup_error:
            cleanup_errors.append(cleanup_error)
        if cleanup_errors:
            FlextCliUtilitiesAtomicDirectoryCleanup._raise_cleanup_failure(
                path, operation_error, cleanup_errors,
            )

    @staticmethod
    def _remove_created_directory(
        parent: FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor,
        path: Path,
        identity: t.Pair[int, int] | None,
    ) -> None:
        state = FlextCliUtilitiesAtomicDirectoryState.destination_state(
            path, parent=parent,
        )
        if state is None:
            FlextCliUtilitiesAtomicFileDurability.sync_parent(parent)
            return
        owned_identity = (
            FlextCliUtilitiesAtomicDirectoryCleanup._require_cleanup_identity(
                path, state, identity,
            )
        )
        authenticated = FlextCliUtilitiesAtomicDirectoryState.read_empty_state(
            parent, path, state,
        )
        FlextCliUtilitiesAtomicDirectoryState.require_identity(
            path, authenticated, owned_identity,
        )
        current = FlextCliUtilitiesAtomicDirectoryState.destination_state(
            path, parent=parent,
        )
        FlextCliUtilitiesAtomicDirectoryCleanup._require_unchanged_cleanup_state(
            path, current, authenticated,
        )
        FlextCliUtilitiesAtomicDirectoryDescriptor.remove_entry(parent, path)
        FlextCliUtilitiesAtomicFileDurability.sync_parent(parent)

    @staticmethod
    def _require_cleanup_identity(
        path: Path,
        state: os.stat_result,
        identity: t.Pair[int, int] | None,
    ) -> t.Pair[int, int]:
        if identity is None:
            message = f"refusing unauthenticated directory cleanup: {path}"
            raise OSError(errno.ESTALE, message, path)
        FlextCliUtilitiesAtomicDirectoryState.require_identity(path, state, identity)
        return identity

    @staticmethod
    def _require_unchanged_cleanup_state(
        path: Path,
        current: os.stat_result | None,
        authenticated: os.stat_result,
    ) -> None:
        if current is None:
            message = f"atomic directory changed before cleanup: {path}"
            raise OSError(errno.ESTALE, message, path)
        if FlextCliUtilitiesAtomicFileRead.state_key(
            current,
        ) != FlextCliUtilitiesAtomicFileRead.state_key(authenticated):
            message = f"atomic directory changed before cleanup: {path}"
            raise OSError(errno.ESTALE, message, path)

    @staticmethod
    def _raise_cleanup_failure(
        path: Path,
        operation_error: BaseException,
        cleanup_errors: list[OSError],
    ) -> None:
        cleanup_summary = "; ".join(str(error) for error in cleanup_errors)
        message = (
            f"atomic directory creation failed ({operation_error}); "
            f"cleanup failed ({cleanup_summary})"
        )
        if isinstance(operation_error, Exception):
            causes = ExceptionGroup(
                "atomic directory creation and cleanup failed",
                [operation_error, *cleanup_errors],
            )
            raise OSError(errno.EIO, message, path) from causes
        group_message = "atomic directory creation and cleanup failed"
        raise BaseExceptionGroup(
            group_message,
            [operation_error, *cleanup_errors],
        ) from cleanup_errors[-1]


__all__: list[str] = ["FlextCliUtilitiesAtomicDirectoryCleanup"]
