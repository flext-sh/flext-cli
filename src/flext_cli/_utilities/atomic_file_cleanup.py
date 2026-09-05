"""Public authenticated temporary cleanup after an atomic write failure."""

from __future__ import annotations

import errno
import os
from pathlib import Path

from . import atomic_file_descriptor as file_descriptor
from . import atomic_file_durability as file_durability
from . import atomic_file_state as file_state


def remove_failed_temporary(
    parent: ParentDescriptor,
    temporary: Path,
    identity: tuple[int, int] | None,
    descriptor: int | None,
    operation_error: BaseException,
) -> None:
    """Close and unlink only caller-owned staging while retaining every cause."""
    cleanup_errors: list[OSError] = []
    if descriptor is not None:
        try:
            os.close(descriptor)
        except OSError as cleanup_error:
            cleanup_errors.append(cleanup_error)
    if identity is None:
        try:
            state = destination_state(temporary, parent=parent)
        except OSError as cleanup_error:
            cleanup_errors.append(cleanup_error)
        else:
            if state is not None:
                message = (
                    f"refusing to remove unauthenticated atomic temporary: {temporary}"
                )
                cleanup_errors.append(OSError(errno.ESTALE, message, temporary))
    else:
        try:
            file_state.assert_temporary_owned(temporary, identity, parent=parent)
            file_descriptor.unlink_entry(parent, temporary)
            file_durability.sync_parent(parent)
        except OSError as cleanup_error:
            cleanup_errors.append(cleanup_error)
    if cleanup_errors:
        _raise_cleanup_failure(temporary, operation_error, cleanup_errors)


def _raise_cleanup_failure(
    temporary: Path, operation_error: BaseException, cleanup_errors: list[OSError]
) -> None:
    cleanup_summary = "; ".join(str(error) for error in cleanup_errors)
    message = (
        f"atomic write failed ({operation_error}); "
        f"temporary cleanup failed ({cleanup_summary})"
    )
    group_message = "atomic write and temporary cleanup failed"
    if isinstance(operation_error, Exception):
        causes = ExceptionGroup(group_message, [operation_error, *cleanup_errors])
        raise OSError(errno.EIO, message, temporary) from causes
    group_message = "atomic write and temporary cleanup failed"
    raise BaseExceptionGroup(
        group_message, [operation_error, *cleanup_errors]
    ) from cleanup_errors[-1]


__all__: list[str] = ["remove_failed_temporary"]
