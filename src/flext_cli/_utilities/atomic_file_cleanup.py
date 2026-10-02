"""Public authenticated temporary cleanup after an atomic write failure.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from pathlib import Path

from flext_cli import t

from . import (
    atomic_file_descriptor as file_descriptor,
    atomic_file_durability as file_durability,
    atomic_file_state as file_state,
)


def remove_failed_temporary(
    parent: file_descriptor.ParentDescriptor,
    temporary: Path,
    identity: t.Pair[int, int] | None,
    descriptor: int | None,
    operation_error: BaseException,
) -> None:
    """Close and unlink only caller-owned staging while retaining every cause."""
    cleanup_errors: list[OSError] = []
    if identity is None and descriptor is not None:
        try:
            identity = file_state.identity(os.fstat(descriptor))
        except OSError as cleanup_error:
            cleanup_errors.append(cleanup_error)
    if descriptor is not None:
        try:
            os.close(descriptor)
        except OSError as cleanup_error:
            cleanup_errors.append(cleanup_error)
    # No captured identity grants no authority over the directory entry.
    # Leave unknown artifacts untouched; the original operation still raises.
    if identity is not None:
        try:
            file_state.assert_temporary_owned(temporary, identity, parent=parent)
            file_descriptor.unlink_entry(parent, temporary)
            file_durability.sync_parent(parent)
        except OSError as cleanup_error:
            cleanup_errors.append(cleanup_error)
    if cleanup_errors:
        _raise_cleanup_failure(temporary, operation_error, cleanup_errors)


def _raise_cleanup_failure(
    temporary: Path,
    operation_error: BaseException,
    cleanup_errors: list[OSError],
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
    raise BaseExceptionGroup(
        group_message,
        [operation_error, *cleanup_errors],
    ) from cleanup_errors[-1]


__all__: list[str] = ["remove_failed_temporary"]
