"""Public guarded deletion for transaction rollback under a caller-held lock.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno

from flext_cli import m
from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)
from flext_cli._utilities.atomic_file_durability import (
    FlextCliUtilitiesAtomicFileDurability,
)
from flext_cli._utilities.atomic_file_mode import FlextCliUtilitiesAtomicFileMode
from flext_cli._utilities.atomic_file_model import FlextCliUtilitiesAtomicFileModel
from flext_cli._utilities.atomic_file_path import FlextCliUtilitiesAtomicFilePath
from flext_cli._utilities.atomic_file_state import FlextCliUtilitiesAtomicFileState


class FlextCliUtilitiesAtomicFileDelete:
    """Canonical namespace owner."""

    @staticmethod
    def remove_guarded_file(state: m.Cli.AtomicFileState) -> None:
        """Unlink the complete physical file version authorized by the caller.

        Raises:
            OSError: If ``file_state.destination_state(path, parent=parent) is not None``.

        """
        path = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(state.path)
        content, mode, _identity = FlextCliUtilitiesAtomicFileModel.require_existing(
            state, purpose="deleted"
        )
        with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
            path, unlink=True
        ) as parent:
            FlextCliUtilitiesAtomicFileModel.require_parent(state, parent.state)
            expected = FlextCliUtilitiesAtomicFileState.destination_state(
                path, parent=parent
            )
            FlextCliUtilitiesAtomicFileModel.require_observed(state, expected)
            FlextCliUtilitiesAtomicFileState.validate_precondition(
                path,
                expected,
                content,
                enabled=True,
                parent=parent,
            )
            FlextCliUtilitiesAtomicFileMode.validate_mode_precondition(
                path, expected, mode
            )
            FlextCliUtilitiesAtomicFileState.assert_destination_unchanged(
                path, expected, parent=parent
            )
            FlextCliUtilitiesAtomicFileDescriptor.unlink_entry(parent, path)
            FlextCliUtilitiesAtomicFileDurability.sync_parent(parent)
            if (
                FlextCliUtilitiesAtomicFileState.destination_state(path, parent=parent)
                is not None
            ):
                message = f"atomic destination still exists after delete: {path}"
                raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicFileDelete"]
