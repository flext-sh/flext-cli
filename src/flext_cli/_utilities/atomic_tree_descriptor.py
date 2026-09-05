"""Low-level descriptor measurements for physical-tree ownership."""

from __future__ import annotations

import errno
import hashlib
import os
import sys
from pathlib import Path
from typing import Never

from . import atomic_file_descriptor as file_descriptor
from . import atomic_file_path as file_path
from . import atomic_file_read as file_read
from . import atomic_file_state as file_state

_FILE_FLAGS = (
    os.O_RDONLY
    | getattr(os, "O_NONBLOCK", 0)
    | getattr(os, "O_CLOEXEC", 0)
    | getattr(os, "O_BINARY", 0)
)


def measure_authenticated_file(
    parent: file_descriptor.ParentDescriptor,
    path: Path,
    expected: os.stat_result,
    *,
    required_mount_id: int,
) -> tuple[int, str]:
    """Hash one stable regular file without materializing it in memory."""
    digest = hashlib.sha256()
    size = 0
    with file_descriptor.entry_descriptor(parent, path, _FILE_FLAGS) as descriptor:
        _require_file_state(descriptor, path, expected)
        require_mount(path, required_mount_id, mount_id(descriptor, path))
        while chunk := os.read(descriptor, 1024 * 1024):
            size += len(chunk)
            digest.update(chunk)
        _require_file_state(descriptor, path, expected)
    file_state.assert_destination_unchanged(path, expected, parent=parent)
    return size, digest.hexdigest()


def mount_id(descriptor: int, path: Path) -> int:
    """Return Linux's descriptor-bound mount ID or fail closed."""
    if _runtime_platform() != "linux":
        message = "descriptor-bound mount identity is unsupported"
        raise OSError(errno.ENOTSUP, message, path)
    values: list[str]
    try:
        with (Path("/proc/self/fdinfo") / str(descriptor)).open(
            encoding="ascii"
        ) as stream:
            values = [
                line.removeprefix("mnt_id:").strip()
                for line in stream
                if line.startswith("mnt_id:")
            ]
    except (OSError, UnicodeError) as exc:
        message = "descriptor-bound mount identity is unavailable"
        raise OSError(errno.ENOTSUP, message, path) from exc
    if len(values) != 1 or not values[0].isdecimal():
        message = "descriptor-bound mount identity is invalid"
        raise OSError(errno.EIO, message, path)
    value = int(values[0])
    if value < 1:
        message = "descriptor-bound mount identity must be positive"
        raise OSError(errno.EIO, message, path)
    return value


def require_mount(path: Path, expected: int, observed: int) -> None:
    """Reject a mount transition before reading through the descriptor."""
    if observed != expected:
        message = f"atomic physical-tree entry crosses its parent mount: {path}"
        raise OSError(errno.EXDEV, message, path)


def require_same_device(
    path: Path, parent: os.stat_result, observed: os.stat_result
) -> None:
    """Reject a device transition before traversing or reading an entry."""
    if observed.st_dev != parent.st_dev:
        message = f"atomic physical-tree entry crosses its parent device: {path}"
        raise OSError(errno.EXDEV, message, path)


def require_directory_state(
    descriptor: int, path: Path, expected: os.stat_result
) -> None:
    """Require one directory FD to retain the complete observed state."""
    observed = os.fstat(descriptor)
    file_path.validate_directory_state(path, observed)
    if file_read.state_key(observed) != file_read.state_key(expected):
        _raise_changed(path)


def require_entry_state(
    parent: file_descriptor.ParentDescriptor, path: Path, expected: os.stat_result
) -> None:
    """Require one parent-relative name to retain the complete observed state."""
    observed = file_descriptor.entry_stat(parent, path)
    if file_read.state_key(observed) != file_read.state_key(expected):
        _raise_changed(path)


def _require_file_state(descriptor: int, path: Path, expected: os.stat_result) -> None:
    if file_read.state_key(os.fstat(descriptor)) != file_read.state_key(expected):
        _raise_changed(path)


def _runtime_platform() -> str:
    """Read the platform at invocation time for typed portable dispatch."""
    return sys.platform


def _raise_changed(path: Path) -> Never:
    message = f"atomic physical-tree entry changed during authentication: {path}"
    raise OSError(errno.ESTALE, message, path)


__all__: list[str] = [
    "measure_authenticated_file",
    "mount_id",
    "require_directory_state",
    "require_entry_state",
    "require_mount",
    "require_same_device",
]
