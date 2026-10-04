"""Public guarded deletion for transaction rollback under a caller-held lock.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
from typing import TYPE_CHECKING

from flext_cli._utilities import (
    atomic_file_descriptor,
    atomic_file_durability,
    atomic_file_mode,
    atomic_file_path,
    atomic_file_state,
)
from flext_cli._utilities.atomic_file_model import FlextCliUtilitiesAtomicFileModel

if TYPE_CHECKING:
    from flext_cli import m


def remove_guarded_file(state: m.Cli.AtomicFileState) -> None:
    """Unlink the complete physical file version authorized by the caller.

    Raises:
        OSError: If ``file_state.destination_state(path, parent=parent) is not
        None``.

    """
    path = atomic_file_path.validate_atomic_path(state.path)
    content, mode, _identity = FlextCliUtilitiesAtomicFileModel.require_existing(
        state,
        purpose="deleted",
    )
    with atomic_file_descriptor.parent_descriptor(
        path,
        unlink=True,
    ) as parent:
        FlextCliUtilitiesAtomicFileModel.require_parent(state, parent.state)
        expected = atomic_file_state.destination_state(
            path,
            parent=parent,
        )
        FlextCliUtilitiesAtomicFileModel.require_observed(state, expected)
        atomic_file_state.validate_precondition(
            path,
            expected,
            content,
            enabled=True,
            parent=parent,
        )
        atomic_file_mode.validate_mode_precondition(
            path,
            expected,
            mode,
        )
        atomic_file_state.assert_destination_unchanged(
            path,
            expected,
            parent=parent,
        )
        atomic_file_descriptor.unlink_entry(parent, path)
        atomic_file_durability.sync_parent(parent)
        if atomic_file_state.destination_state(path, parent=parent) is not None:
            message = f"atomic destination still exists after delete: {path}"
            raise OSError(errno.ESTALE, message, path)


__all__: list[str] = [
    "remove_guarded_file",
]
