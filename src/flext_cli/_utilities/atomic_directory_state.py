"""Stable descriptor-authenticated state for physical empty directories."""

from __future__ import annotations

import errno
import os
from pathlib import Path

from . import (
    atomic_file_descriptor as file_descriptor,
    atomic_file_mode as file_mode,
    atomic_file_path as file_path,
    atomic_file_read as file_read,
)

_MAX_EMPTY_DIRECTORY_LINK_COUNT = 2


def destination_state(
    path: Path, *, parent: file_descriptor.ParentDescriptor
) -> os.stat_result | None:
    """Read one final directory entry without following it or crossing devices."""
    try:
        state = file_descriptor.entry_stat(parent, path)
    except FileNotFoundError:
        return None
    file_path.validate_directory_state(path, state)
    if state.st_dev != parent.state.st_dev:
        message = f"atomic directory crosses its physical parent device: {path}"
        raise OSError(errno.EXDEV, message, path)
    return state


def read_empty_state(
    parent: file_descriptor.ParentDescriptor, path: Path, expected: os.stat_result
) -> os.stat_result:
    """Prove one exact directory version remains empty through an FD read."""
    flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_BINARY", 0)
    )
    with file_descriptor.entry_descriptor(parent, path, flags) as descriptor:
        _require_descriptor_state(descriptor, path, expected)
        _require_empty(descriptor, path)
        _require_descriptor_state(descriptor, path, expected)
    return _require_path_state(parent, path, expected)


def initialize_empty_state(
    parent: file_descriptor.ParentDescriptor,
    path: Path,
    expected: os.stat_result,
    permission_mode: int,
) -> os.stat_result:
    """Set and sync exact mode on a newly-created, still-empty directory inode."""
    flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_BINARY", 0)
    )
    with file_descriptor.entry_descriptor(parent, path, flags) as descriptor:
        _require_descriptor_state(descriptor, path, expected)
        _require_empty(descriptor, path)
        os.fchmod(descriptor, permission_mode)
        file_mode.assert_observed_mode(path, os.fstat(descriptor), permission_mode)
        os.fsync(descriptor)
        final = os.fstat(descriptor)
        _require_empty(descriptor, path)
        _require_descriptor_state(descriptor, path, final)
    return _require_path_state(parent, path, final)


def require_identity(
    path: Path, state: os.stat_result, expected: tuple[int, int]
) -> None:
    """Require one directory entry to retain a caller-owned inode."""
    if file_path.identity(state) != expected:
        message = f"atomic directory identity changed: {path}"
        raise OSError(errno.ESTALE, message, path)


def _require_descriptor_state(
    descriptor: int, path: Path, expected: os.stat_result
) -> None:
    observed = os.fstat(descriptor)
    file_path.validate_directory_state(path, observed)
    if file_read.state_key(observed) != file_read.state_key(expected):
        message = f"atomic directory changed during descriptor access: {path}"
        raise OSError(errno.ESTALE, message, path)


def _require_empty(descriptor: int, path: Path) -> None:
    entries = os.listdir(descriptor)
    if entries:
        message = f"atomic directory is not empty: {path}"
        raise OSError(errno.ENOTEMPTY, message, path)
    state = os.fstat(descriptor)
    if state.st_nlink > _MAX_EMPTY_DIRECTORY_LINK_COUNT:
        message = f"empty atomic directory has unexpected links: {path}"
        raise OSError(errno.EMLINK, message, path)


def _require_path_state(
    parent: file_descriptor.ParentDescriptor, path: Path, expected: os.stat_result
) -> os.stat_result:
    current = destination_state(path, parent=parent)
    if current is None or file_read.state_key(current) != file_read.state_key(expected):
        message = f"atomic directory changed during authenticated read: {path}"
        raise OSError(errno.ESTALE, message, path)
    file_descriptor.assert_parent_unchanged(parent)
    return current


__all__: list[str] = [
    "destination_state",
    "initialize_empty_state",
    "read_empty_state",
    "require_identity",
]
