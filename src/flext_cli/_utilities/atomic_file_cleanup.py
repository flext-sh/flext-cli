"""Public authenticated temporary cleanup after an atomic write failure.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli._utilities import FlextCliUtilitiesAtomicFileDescriptor

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliUtilitiesAtomicFileCleanup:
    """Canonical namespace owner."""

    @staticmethod
    def remove_failed_temporary(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        temporary: Path,
        identity: t.Pair[int, int] | None,
        descriptor: int | None,
        operation_error: BaseException,
    ) -> None:
        """Close and unlink only caller-owned staging while retaining every cause."""
        from flext_cli._utilities import FlextCliUtilitiesAtomicFileDurability, FlextCliUtilitiesAtomicFileState
        cleanup_errors: list[OSError] = []
        if identity is None and descriptor is not None:
            try:
                identity = FlextCliUtilitiesAtomicFileState.identity(
                    os.fstat(descriptor),
                )
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
                FlextCliUtilitiesAtomicFileState.assert_temporary_owned(
                    temporary,
                    identity,
                    parent=parent,
                )
                FlextCliUtilitiesAtomicFileDescriptor.unlink_entry(parent, temporary)
                FlextCliUtilitiesAtomicFileDurability.sync_parent(parent)
            except OSError as cleanup_error:
                cleanup_errors.append(cleanup_error)
        if cleanup_errors:
            FlextCliUtilitiesAtomicFileCleanup._raise_cleanup_failure(
                temporary,
                operation_error,
                cleanup_errors,
            )

    @staticmethod
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


__all__: list[str] = ["FlextCliUtilitiesAtomicFileCleanup"]
