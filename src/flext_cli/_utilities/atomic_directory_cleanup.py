"""Authenticated cleanup for a failed guarded empty-directory creation.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli._utilities import atomic_directory_descriptor
from flext_cli._utilities import atomic_directory_state
from flext_cli._utilities import atomic_file_durability
from flext_cli._utilities import atomic_file_read

if TYPE_CHECKING:
    from flext_cli import t



def remove_created_directory(
    parent: atomic_file_descriptor.ParentDescriptor,
    path: Path,
    identity: t.Pair[int, int] | None,
    operation_error: BaseException,
) -> None:
    """Remove only the still-empty inode created by the failed operation."""
    cleanup_errors: list[OSError] = []
    try:
        _remove_created_directory(
            parent, path, identity,
        )
    except OSError as cleanup_error:
        cleanup_errors.append(cleanup_error)
    if cleanup_errors:
        _raise_cleanup_failure(
            path, operation_error, cleanup_errors,
        )

def _remove_created_directory(
    parent: atomic_file_descriptor.ParentDescriptor,
    path: Path,
    identity: t.Pair[int, int] | None,
) -> None:
    state = atomic_directory_state.destination_state(
        path, parent=parent,
    )
    if state is None:
        atomic_file_durability.sync_parent(parent)
        return
    owned_identity = (
        _require_cleanup_identity(
            path, state, identity,
        )
    )
    authenticated = atomic_directory_state.read_empty_state(
        parent, path, state,
    )
    atomic_directory_state.require_identity(
        path, authenticated, owned_identity,
    )
    current = atomic_directory_state.destination_state(
        path, parent=parent,
    )
    _require_unchanged_cleanup_state(
        path, current, authenticated,
    )
    atomic_directory_descriptor.remove_entry(parent, path)
    atomic_file_durability.sync_parent(parent)

def _require_cleanup_identity(
    path: Path,
    state: os.stat_result,
    identity: t.Pair[int, int] | None,
) -> t.Pair[int, int]:
    if identity is None:
        message = f"refusing unauthenticated directory cleanup: {path}"
        raise OSError(errno.ESTALE, message, path)
    atomic_directory_state.require_identity(path, state, identity)
    return identity

def _require_unchanged_cleanup_state(
    path: Path,
    current: os.stat_result | None,
    authenticated: os.stat_result,
) -> None:
    if current is None:
        message = f"atomic directory changed before cleanup: {path}"
        raise OSError(errno.ESTALE, message, path)
    if atomic_file_read.state_key(
        current,
    ) != atomic_file_read.state_key(authenticated):
        message = f"atomic directory changed before cleanup: {path}"
        raise OSError(errno.ESTALE, message, path)

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


__all__: list[str] = [
    "remove_created_directory",
]
