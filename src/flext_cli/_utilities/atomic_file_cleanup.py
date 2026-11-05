"""Public authenticated temporary cleanup after an atomic write failure.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from pathlib import Path

from flext_cli._utilities import (
    FlextCliUtilitiesAtomicFileDescriptor,
    FlextCliUtilitiesAtomicFileDurability,
    FlextCliUtilitiesAtomicFilePath,
    FlextCliUtilitiesAtomicFileState,
    FlextCliUtilitiesAtomicParentFailure,
)


class FlextCliUtilitiesAtomicFileCleanup:
    """Canonical namespace owner."""

    @staticmethod
    def remove_linked_temporary(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        temporary: Path,
        identity: tuple[int, int],
        operation_error: BaseException,
    ) -> None:
        """Remove authenticated post-link staging, never the published destination."""
        cleanup_errors: list[OSError] = []
        try:
            # Publication adds a second link to this authenticated staging inode.
            FlextCliUtilitiesAtomicFilePath.require_identity(
                temporary,
                FlextCliUtilitiesAtomicFileDescriptor.entry_stat(parent, temporary),
                identity,
                subject="file",
            )
            FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(parent)
            FlextCliUtilitiesAtomicFileDescriptor.unlink_entry(parent, temporary)
        except OSError as cleanup_error:
            cleanup_errors.append(cleanup_error)
        try:
            FlextCliUtilitiesAtomicFileDurability.sync_parent(parent)
        except OSError as cleanup_error:
            cleanup_errors.append(cleanup_error)
        if cleanup_errors:
            FlextCliUtilitiesAtomicParentFailure.raise_combined_failure(
                temporary,
                operation_error,
                cleanup_errors,
                ("atomic write", "temporary cleanup"),
            )

    @staticmethod
    def remove_failed_temporary(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        temporary: Path,
        identity: tuple[int, int] | None,
        descriptor: int | None,
        operation_error: BaseException,
    ) -> None:
        """Close and unlink only caller-owned staging while retaining every cause."""
        cleanup_errors: list[OSError] = []
        if identity is None and descriptor is not None:
            try:
                identity = FlextCliUtilitiesAtomicFilePath.path_identity(
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
            FlextCliUtilitiesAtomicParentFailure.raise_combined_failure(
                temporary,
                operation_error,
                cleanup_errors,
                ("atomic write", "temporary cleanup"),
            )


__all__: list[str] = ["FlextCliUtilitiesAtomicFileCleanup"]
