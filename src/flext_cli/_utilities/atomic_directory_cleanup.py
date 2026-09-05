"""Authenticated cleanup for a failed guarded empty-directory creation."""

from __future__ import annotations

import errno
import os
from pathlib import Path

from . import atomic_directory_descriptor as directory_descriptor
from . import atomic_directory_state as directory_state
from . import atomic_file_descriptor as file_descriptor
from . import atomic_file_durability as file_durability
from . import atomic_file_read as file_read


def remove_created_directory(
    parent: file_descriptor.ParentDescriptor,
    path: Path,
    identity: tuple[int, int] | None,
    operation_error: BaseException,
) -> None:
    """Remove only the still-empty inode created by the failed operation."""
    cleanup_errors: list[OSError] = []
    try:
        _remove_created_directory(parent, path, identity)
    except OSError as cleanup_error:
        cleanup_errors.append(cleanup_error)
    if cleanup_errors:
        _raise_cleanup_failure(path, operation_error, cleanup_errors)


def _remove_created_directory(
    parent: file_descriptor.ParentDescriptor,
    path: Path,
    identity: tuple[int, int] | None,
) -> None:
    state = directory_state.destination_state(path, parent=parent)
    if state is None:
        file_durability.sync_parent(parent)
        return
    owned_identity = _require_cleanup_identity(path, state, identity)
    authenticated = directory_state.read_empty_state(parent, path, state)
    directory_state.require_identity(path, authenticated, owned_identity)
    current = directory_state.destination_state(path, parent=parent)
    _require_unchanged_cleanup_state(path, current, authenticated)
    directory_descriptor.remove_entry(parent, path)
    file_durability.sync_parent(parent)


def _require_cleanup_identity(
    path: Path, state: os.stat_result, identity: tuple[int, int] | None
) -> tuple[int, int]:
    if identity is None:
        message = f"refusing unauthenticated directory cleanup: {path}"
        raise OSError(errno.ESTALE, message, path)
    directory_state.require_identity(path, state, identity)
    return identity


def _require_unchanged_cleanup_state(
    path: Path, current: os.stat_result | None, authenticated: os.stat_result
) -> None:
    if current is None:
        message = f"atomic directory changed before cleanup: {path}"
        raise OSError(errno.ESTALE, message, path)
    if file_read.state_key(current) != file_read.state_key(authenticated):
        message = f"atomic directory changed before cleanup: {path}"
        raise OSError(errno.ESTALE, message, path)


def _raise_cleanup_failure(
    path: Path, operation_error: BaseException, cleanup_errors: list[OSError]
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
        group_message, [operation_error, *cleanup_errors]
    ) from cleanup_errors[-1]


__all__: list[str] = ["remove_created_directory"]
