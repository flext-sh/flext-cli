"""Filesystem-state authentication for the atomic publication owner."""

from __future__ import annotations

import errno
import os
import stat
from pathlib import Path

from . import _atomic_file_descriptor as file_descriptor
from . import _atomic_file_path as file_path
from . import _atomic_file_read as file_read


def destination_state(
    path: Path, *, parent: file_descriptor.ParentDescriptor | None = None
) -> os.stat_result | None:
    """Return an authorized destination snapshot without following links."""
    if parent is None:
        with file_descriptor.parent_descriptor(path) as opened:
            state = destination_state(path, parent=opened)
            file_descriptor.assert_parent_unchanged(opened)
            return state
    try:
        state = file_descriptor.entry_stat(parent, path)
    except FileNotFoundError:
        return None
    _validate_regular_state(path, state)
    return state


def validate_precondition(
    path: Path,
    state: os.stat_result | None,
    expected_bytes: bytes | None,
    *,
    enabled: bool,
    parent: file_descriptor.ParentDescriptor | None = None,
) -> None:
    """Authenticate an explicit raw-byte version before staging."""
    if not enabled:
        return
    if expected_bytes is None:
        if state is not None:
            message = f"atomic destination exists but absence was required: {path}"
            raise FileExistsError(errno.EEXIST, message, path)
        return
    if state is None:
        message = f"atomic destination is missing: {path}"
        raise FileNotFoundError(errno.ENOENT, message, path)
    if read_authenticated_bytes(path, state, parent=parent) != expected_bytes:
        message = f"atomic destination content changed before write: {path}"
        raise OSError(errno.ESTALE, message, path)


def assert_temporary_owned(
    temporary: Path,
    expected_identity: tuple[int, int],
    *,
    parent: file_descriptor.ParentDescriptor | None = None,
) -> None:
    """Require the staged pathname to retain its uniquely owned inode."""
    if parent is None:
        with file_descriptor.parent_descriptor(temporary) as opened:
            assert_temporary_owned(temporary, expected_identity, parent=opened)
            return
    try:
        state = file_descriptor.entry_stat(parent, temporary)
    except FileNotFoundError as exc:
        message = f"atomic temporary disappeared before publication: {temporary}"
        raise FileNotFoundError(errno.ENOENT, message, temporary) from exc
    if identity(state) != expected_identity:
        message = f"atomic temporary identity changed before publication: {temporary}"
        raise OSError(errno.ESTALE, message, temporary)
    _validate_regular_state(temporary, state)
    file_descriptor.assert_parent_unchanged(parent)


def assert_destination_unchanged(
    path: Path,
    expected: os.stat_result | None,
    *,
    parent: file_descriptor.ParentDescriptor | None = None,
) -> None:
    """Fail before publication when destination identity or state changed."""
    if parent is None:
        with file_descriptor.parent_descriptor(path) as opened:
            assert_destination_unchanged(path, expected, parent=opened)
            return
    current = destination_state(path, parent=parent)
    if expected is None:
        if current is not None:
            message = f"atomic destination appeared during write: {path}"
            raise FileExistsError(errno.EEXIST, message, path)
    elif current is None or file_read.state_key(current) != file_read.state_key(
        expected
    ):
        message = f"atomic destination changed during write: {path}"
        raise OSError(errno.ESTALE, message, path)
    file_descriptor.assert_parent_unchanged(parent)


def identity(state: os.stat_result) -> tuple[int, int]:
    """Return the filesystem identity shared by descriptor and pathname stats."""
    return file_path.identity(state)


def read_authenticated_bytes(
    path: Path,
    expected: os.stat_result,
    *,
    parent: file_descriptor.ParentDescriptor | None = None,
) -> bytes:
    """Read exact bytes and prove the descriptor remains bound to its pathname."""
    if parent is None:
        with file_descriptor.parent_descriptor(path) as opened:
            return read_authenticated_bytes(path, expected, parent=opened)
    content = file_read.read_descriptor_bytes(parent, path, expected)
    assert_destination_unchanged(path, expected, parent=parent)
    return content


def _validate_regular_state(path: Path, state: os.stat_result) -> None:
    if not stat.S_ISREG(state.st_mode) or file_path.is_reparse_point(state):
        message = f"atomic destination is not a regular file: {path}"
        raise OSError(errno.EINVAL, message, path)
    if state.st_nlink != 1:
        message = f"atomic destination has {state.st_nlink} hard links: {path}"
        raise OSError(errno.EMLINK, message, path)


__all__: list[str] = [
    "assert_destination_unchanged",
    "assert_temporary_owned",
    "destination_state",
    "identity",
    "read_authenticated_bytes",
    "validate_precondition",
]
