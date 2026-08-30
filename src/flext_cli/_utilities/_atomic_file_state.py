"""Filesystem-state authentication for the atomic publication owner."""

from __future__ import annotations

import errno
import os
import stat
from pathlib import Path


def validate_parent(parent: Path) -> None:
    """Require the destination's immediate parent to be a real directory."""
    try:
        state = parent.lstat()
    except FileNotFoundError as exc:
        msg = f"atomic destination parent is missing: {parent}"
        raise FileNotFoundError(errno.ENOENT, msg, parent) from exc
    if not stat.S_ISDIR(state.st_mode) or _is_reparse_point(state):
        msg = f"atomic destination parent is not a real directory: {parent}"
        raise NotADirectoryError(errno.ENOTDIR, msg, parent)


def destination_state(path: Path) -> os.stat_result | None:
    """Return an authorized destination snapshot without following links."""
    try:
        state = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(state.st_mode) or _is_reparse_point(state):
        msg = f"atomic destination is not a regular file: {path}"
        raise OSError(errno.EINVAL, msg, path)
    if state.st_nlink != 1:
        msg = f"atomic destination has {state.st_nlink} hard links: {path}"
        raise OSError(errno.EMLINK, msg, path)
    return state


def permission_state(path: Path) -> os.stat_result | None:
    """Return mode provenance only when one legacy destination owns its inode."""
    try:
        state = path.lstat()
    except FileNotFoundError:
        return None
    if (
        stat.S_ISREG(state.st_mode)
        and state.st_nlink == 1
        and not _is_reparse_point(state)
    ):
        return state
    return None


def validate_precondition(
    path: Path,
    state: os.stat_result | None,
    expected_bytes: bytes | None,
    *,
    enabled: bool,
) -> None:
    """Authenticate an explicit raw-byte version before staging."""
    if not enabled:
        return
    if expected_bytes is None:
        if state is not None:
            msg = f"atomic destination exists but absence was required: {path}"
            raise FileExistsError(errno.EEXIST, msg, path)
        return
    if state is None:
        msg = f"atomic destination is missing: {path}"
        raise FileNotFoundError(errno.ENOENT, msg, path)
    if _read_authenticated_bytes(path, state) != expected_bytes:
        msg = f"atomic destination content changed before write: {path}"
        raise OSError(errno.ESTALE, msg, path)


def assert_temporary_owned(temporary: Path, expected_identity: tuple[int, int]) -> None:
    """Require the staged pathname to retain its uniquely owned inode."""
    try:
        state = temporary.lstat()
    except FileNotFoundError as exc:
        msg = f"atomic temporary disappeared before publication: {temporary}"
        raise FileNotFoundError(errno.ENOENT, msg, temporary) from exc
    if (
        not stat.S_ISREG(state.st_mode)
        or state.st_nlink != 1
        or identity(state) != expected_identity
    ):
        msg = f"atomic temporary identity changed before publication: {temporary}"
        raise OSError(errno.ESTALE, msg, temporary)


def assert_destination_unchanged(path: Path, expected: os.stat_result | None) -> None:
    """Fail before publication when destination identity or state changed."""
    current = destination_state(path)
    if expected is None:
        if current is not None:
            msg = f"atomic destination appeared during write: {path}"
            raise FileExistsError(errno.EEXIST, msg, path)
        return
    if current is None or _state_key(current) != _state_key(expected):
        msg = f"atomic destination changed during write: {path}"
        raise OSError(errno.ESTALE, msg, path)


def identity(state: os.stat_result) -> tuple[int, int]:
    """Return the filesystem identity shared by descriptor and pathname stats."""
    return (state.st_dev, state.st_ino)


def _read_authenticated_bytes(path: Path, expected: os.stat_result) -> bytes:
    """Read one file descriptor and retain read/close failures without suppression."""
    flags = (
        os.O_RDONLY
        | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_NONBLOCK", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(path, flags)
    try:
        content = _read_stable_descriptor(descriptor, path, expected)
    except BaseException as operation_error:
        _close_after_failure(descriptor, path, operation_error)
        raise
    os.close(descriptor)
    return content


def _read_stable_descriptor(
    descriptor: int, path: Path, expected: os.stat_result
) -> bytes:
    """Read all bytes while the authenticated descriptor state remains stable."""
    if _state_key(os.fstat(descriptor)) != _state_key(expected):
        _raise_changed(path)
    chunks: list[bytes] = []
    while chunk := os.read(descriptor, 1024 * 1024):
        chunks.append(chunk)
    if _state_key(os.fstat(descriptor)) != _state_key(expected):
        _raise_changed(path)
    return b"".join(chunks)


def _close_after_failure(
    descriptor: int, path: Path, operation_error: BaseException
) -> None:
    """Close a failed read and expose both errors when closing also fails."""
    try:
        os.close(descriptor)
    except OSError as close_error:
        message = (
            f"atomic read failed ({operation_error}); close failed ({close_error})"
        )
        if isinstance(operation_error, Exception):
            causes = ExceptionGroup(
                "atomic read and descriptor close failed",
                [operation_error, close_error],
            )
            raise OSError(errno.EIO, message, path) from causes
        group_message = "atomic read and descriptor close failed"
        raise BaseExceptionGroup(
            group_message, [operation_error, close_error]
        ) from close_error


def _raise_changed(path: Path) -> None:
    """Raise the stable stale-version error for one destination."""
    msg = f"atomic destination changed during authenticated read: {path}"
    raise OSError(errno.ESTALE, msg, path)


def _state_key(state: os.stat_result) -> tuple[int, ...]:
    """Return fields that identify the authorized destination version."""
    return (
        state.st_dev,
        state.st_ino,
        state.st_mode,
        state.st_nlink,
        state.st_uid,
        state.st_gid,
        state.st_size,
        state.st_mtime_ns,
        state.st_ctime_ns,
    )


def _is_reparse_point(state: os.stat_result) -> bool:
    """Identify Windows reparse-point aliases without platform branching."""
    attributes = getattr(state, "st_file_attributes", 0)
    marker = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(attributes & marker)


__all__: list[str] = [
    "assert_destination_unchanged",
    "assert_temporary_owned",
    "destination_state",
    "identity",
    "permission_state",
    "validate_parent",
    "validate_precondition",
]
