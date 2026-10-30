"""Public guarded deletion for transaction rollback under a caller-held lock.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
from collections.abc import MutableSequence
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli._utilities import (
    FlextCliUtilitiesAtomicFileDescriptor,
    FlextCliUtilitiesAtomicFileDurability,
    FlextCliUtilitiesAtomicFileMode,
    FlextCliUtilitiesAtomicFileModel,
    FlextCliUtilitiesAtomicFilePath,
    FlextCliUtilitiesAtomicFileState,
)

if TYPE_CHECKING:
    from flext_cli import m


class FlextCliUtilitiesAtomicFileDelete:
    """Canonical namespace owner."""

    @staticmethod
    def remove_guarded_file(
        state: m.Cli.AtomicFileState,
        *,
        published_paths: MutableSequence[Path] | None = None,
    ) -> None:
        """Unlink the complete physical file version authorized by the caller.

        The receipt records the native unlink before durability and final proof;
        those later failures retain the original exception and the physical effect.

        Raises:
            OSError: If ``file_state.destination_state(path, parent=parent) is not
            None``.

        """
        path = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(state.path)
        content, mode, _identity = FlextCliUtilitiesAtomicFileModel.require_existing(
            state,
            purpose="deleted",
        )
        with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
            path,
            unlink=True,
        ) as parent:
            FlextCliUtilitiesAtomicFileModel.require_parent(state, parent.state)
            expected = FlextCliUtilitiesAtomicFileState.destination_state(
                path,
                parent=parent,
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
                path,
                expected,
                mode,
            )
            FlextCliUtilitiesAtomicFileState.assert_destination_unchanged(
                path,
                expected,
                parent=parent,
            )
            FlextCliUtilitiesAtomicFileDescriptor.unlink_entry(parent, path)
            if published_paths is not None:
                published_paths.append(path)
            FlextCliUtilitiesAtomicFileDurability.sync_parent(parent)
            if (
                FlextCliUtilitiesAtomicFileState.destination_state(path, parent=parent)
                is not None
            ):
                message = f"atomic destination still exists after delete: {path}"
                raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicFileDelete"]
