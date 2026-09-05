"""Public guarded publication of caller-owned staged files."""

from __future__ import annotations

import errno
import os

from flext_cli import m
from . import atomic_file_descriptor as file_descriptor
from . import atomic_file_durability as file_durability
from . import atomic_file_mode as file_mode
from . import atomic_file_model as file_model
from . import atomic_file_path as file_path
from . import atomic_file_publish_checks as checks
from . import atomic_file_state as file_state


def publish_guarded_staged_file(
    destination_before: m.Cli.AtomicFileState, staged: m.Cli.AtomicFileState
) -> os.stat_result:
    """Move one exact caller-owned staged file over an exact destination state.

    The caller owns both the cooperative lock and staged-file lifecycle.  A
    failure before replacement leaves the staged path in place. A completed
    replace consumes it; any subsequent validation failure requires the caller's
    journal to classify the destination. Every changed physical parent directory
    is synced after a completed replacement.
    """
    destination = file_path.validate_atomic_path(destination_before.path)
    staged_path = file_path.validate_atomic_path(staged.path)
    if destination == staged_path:
        message = "staged file and atomic destination must differ"
        raise OSError(errno.EINVAL, message, destination)
    staged_bytes, staged_mode, staged_identity = file_model.require_existing(
        staged, purpose="staged"
    )
    file_mode.validate_guarded_mode_tuple(
        destination, destination_before.content, destination_before.mode
    )
    checks.validate_identity(staged_path, staged_identity, label="staged_identity")
    with (
        file_descriptor.parent_descriptor(
            destination, replace=True
        ) as destination_parent,
        file_descriptor.parent_descriptor(staged_path, replace=True) as staged_parent,
    ):
        file_model.require_parent(destination_before, destination_parent.state)
        file_model.require_parent(staged, staged_parent.state)
        destination_state = file_state.destination_state(
            destination, parent=destination_parent
        )
        file_model.require_observed(destination_before, destination_state)
        file_state.validate_precondition(
            destination,
            destination_state,
            destination_before.content,
            enabled=True,
            parent=destination_parent,
        )
        file_mode.validate_mode_precondition(
            destination, destination_state, destination_before.mode
        )
        staged_state = file_state.destination_state(staged_path, parent=staged_parent)
        if staged_state is None:
            message = f"atomic staged file is missing: {staged_path}"
            raise FileNotFoundError(errno.ENOENT, message, staged_path)
        file_model.require_observed(staged, staged_state)
        checks.require_distinct_inode(destination, destination_state, staged_identity)
        checks.validate_devices(
            destination,
            destination_parent,
            destination_state,
            staged_path,
            staged_parent,
            staged_state,
        )
        file_state.validate_precondition(
            staged_path, staged_state, staged_bytes, enabled=True, parent=staged_parent
        )
        file_mode.validate_mode_precondition(staged_path, staged_state, staged_mode)
        file_state.assert_destination_unchanged(
            destination, destination_state, parent=destination_parent
        )
        file_state.assert_temporary_owned(
            staged_path, staged_identity, parent=staged_parent
        )
        file_descriptor.replace_entry(
            staged_parent, staged_path, destination_parent, destination
        )
        file_durability.sync_replacement(staged_parent, destination_parent)
        published = checks.validate_publication(
            destination_parent,
            destination,
            staged_parent,
            staged_path,
            staged_bytes,
            staged_mode,
            staged_identity,
        )
        file_model.require_observed(staged, published, path=destination)
        return published


__all__: list[str] = ["publish_guarded_staged_file"]
