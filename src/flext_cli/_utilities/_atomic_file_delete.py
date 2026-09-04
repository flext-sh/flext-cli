"""Guarded deletion for transaction rollback under a caller-held lock."""

from __future__ import annotations

import errno
from pathlib import Path

from flext_cli._utilities import _atomic_file_descriptor as file_descriptor
from flext_cli._utilities import _atomic_file_mode as file_mode
from flext_cli._utilities import _atomic_file_state as file_state


def remove_guarded_file(
    path: Path, *, expected_bytes: bytes, expected_mode: int
) -> None:
    """Unlink the exact regular-file version authorized by the caller."""
    if not isinstance(expected_bytes, bytes):
        message = "expected_bytes must be bytes"
        raise OSError(errno.EINVAL, message, path)
    with file_descriptor.parent_descriptor(path, unlink=True) as parent:
        expected = file_state.destination_state(path, parent=parent)
        file_state.validate_precondition(
            path,
            expected,
            expected_bytes,
            enabled=True,
            parent=parent,
        )
        file_mode.validate_mode_precondition(path, expected, expected_mode)
        file_state.assert_destination_unchanged(path, expected, parent=parent)
        file_descriptor.unlink_entry(parent, path)
        if file_state.destination_state(path, parent=parent) is not None:
            message = f"atomic destination still exists after delete: {path}"
            raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["remove_guarded_file"]
