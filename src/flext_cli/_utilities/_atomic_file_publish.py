"""Guarded publication of caller-owned staged files."""

from __future__ import annotations

import errno
import os
from pathlib import Path

from flext_cli._utilities import _atomic_file_descriptor as file_descriptor
from flext_cli._utilities import _atomic_file_mode as file_mode
from flext_cli._utilities import _atomic_file_path as file_path
from flext_cli._utilities import _atomic_file_publish_checks as checks
from flext_cli._utilities import _atomic_file_state as file_state


def publish_guarded_staged_file(
    destination: Path,
    staged: Path,
    *,
    expected_bytes: bytes | None,
    expected_mode: int | None,
    expected_identity: tuple[int, int] | None,
    staged_bytes: bytes,
    staged_mode: int,
    staged_identity: tuple[int, int],
) -> os.stat_result:
    """Move one exact caller-owned staged file over an exact destination state.

    The caller owns both the cooperative lock and staged-file lifecycle.  A
    failure before replacement leaves the staged path in place. A completed
    replace consumes it; any subsequent validation failure requires the caller's
    journal to classify the destination. Parent-directory power-loss durability
    is outside this primitive's contract.
    """
    destination = file_path.validate_atomic_path(destination)
    staged = file_path.validate_atomic_path(staged)
    if destination == staged:
        message = "staged file and atomic destination must differ"
        raise OSError(errno.EINVAL, message, destination)
    file_mode.validate_guarded_mode_tuple(
        destination, expected_bytes, expected_mode
    )
    required_staged_mode = file_mode.validate_mode(
        staged_mode, label="staged_mode"
    )
    if required_staged_mode is None:
        message = "staged_mode is required"
        raise OSError(errno.EINVAL, message, staged)
    checks.validate_expected_identity(destination, expected_bytes, expected_identity)
    checks.validate_identity(staged, staged_identity, label="staged_identity")
    with file_descriptor.parent_descriptor(
        destination, replace=True
    ) as destination_parent:
        with file_descriptor.parent_descriptor(staged, replace=True) as staged_parent:
            destination_state = file_state.destination_state(
                destination, parent=destination_parent
            )
            checks.require_identity(
                destination, destination_state, expected_identity
            )
            file_state.validate_precondition(
                destination,
                destination_state,
                expected_bytes,
                enabled=True,
                parent=destination_parent,
            )
            file_mode.validate_mode_precondition(
                destination, destination_state, expected_mode
            )
            staged_state = file_state.destination_state(staged, parent=staged_parent)
            if staged_state is None:
                message = f"atomic staged file is missing: {staged}"
                raise FileNotFoundError(errno.ENOENT, message, staged)
            checks.require_identity(staged, staged_state, staged_identity)
            checks.require_distinct_inode(
                destination, destination_state, staged_identity
            )
            checks.validate_devices(
                destination,
                destination_parent,
                destination_state,
                staged,
                staged_parent,
                staged_state,
            )
            file_state.validate_precondition(
                staged,
                staged_state,
                staged_bytes,
                enabled=True,
                parent=staged_parent,
            )
            file_mode.validate_mode_precondition(
                staged, staged_state, required_staged_mode
            )
            file_state.assert_destination_unchanged(
                destination, destination_state, parent=destination_parent
            )
            file_state.assert_temporary_owned(
                staged, staged_identity, parent=staged_parent
            )
            file_descriptor.replace_entry(
                staged_parent, staged, destination_parent, destination
            )
            return checks.validate_publication(
                destination_parent,
                destination,
                staged_parent,
                staged,
                staged_bytes,
                required_staged_mode,
                staged_identity,
            )


__all__: list[str] = ["publish_guarded_staged_file"]
