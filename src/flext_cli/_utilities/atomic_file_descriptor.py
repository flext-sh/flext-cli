"""Public descriptor-bound parent ownership for atomic file operations."""

from __future__ import annotations

import errno
import os
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from . import atomic_file_path as file_path
from . import atomic_parent_descriptor as parent_path
from . import atomic_parent_failure as parent_failure


@dataclass(frozen=True, slots=True)
class ParentDescriptor:
    """One open physical parent directory bound to its lexical pathname."""

    path: Path
    descriptor: int
    state: os.stat_result
    ancestry: tuple[tuple[int, int], ...]


@contextmanager
def parent_descriptor(
    path: Path, *, replace: bool = False, unlink: bool = False
) -> Generator[ParentDescriptor]:
    """Yield one authenticated parent descriptor with required OS capabilities."""
    validated = file_path.validate_atomic_path(path)
    _require_capabilities(validated, replace=replace, unlink=unlink)
    with parent_path.physical_directory(validated.parent) as opened:
        handle = ParentDescriptor(
            validated.parent, opened.descriptor, opened.state, opened.ancestry
        )
        assert_parent_unchanged(handle)
        try:
            yield handle
        except BaseException as operation_error:
            parent_failure.preserve_recheck_failure(
                handle.path,
                operation_error,
                lambda: assert_parent_unchanged(handle),
            )
            raise
        assert_parent_unchanged(handle)


def assert_parent_unchanged(parent: ParentDescriptor) -> None:
    """Require descriptor and pathname to retain the opened directory identity."""
    descriptor_state = os.fstat(parent.descriptor)
    file_path.validate_directory_state(parent.path, descriptor_state)
    expected = file_path.identity(parent.state)
    if file_path.identity(descriptor_state) != expected:
        message = f"atomic file parent identity changed: {parent.path}"
        raise OSError(errno.ESTALE, message, parent.path)
    with parent_path.physical_directory(parent.path) as current:
        if (
            file_path.identity(current.state) != expected
            or current.ancestry != parent.ancestry
        ):
            message = f"atomic file parent ancestry changed: {parent.path}"
            raise OSError(errno.ESTALE, message, parent.path)


def entry_stat(parent: ParentDescriptor, path: Path) -> os.stat_result:
    """Read one final entry relative to its authenticated parent descriptor."""
    require_entry(parent, path)
    return os.stat(path.name, dir_fd=parent.descriptor, follow_symlinks=False)


def open_entry(
    parent: ParentDescriptor, path: Path, flags: int, *, mode: int | None = None
) -> int:
    """Open one final entry relative to its authenticated parent descriptor."""
    require_entry(parent, path)
    nofollow_flag = getattr(os, "O_NOFOLLOW", 0)
    guarded_flags = flags | nofollow_flag
    if mode is None:
        return os.open(path.name, guarded_flags, dir_fd=parent.descriptor)
    return os.open(path.name, guarded_flags, mode, dir_fd=parent.descriptor)


@contextmanager
def entry_descriptor(
    parent: ParentDescriptor, path: Path, flags: int
) -> Generator[int]:
    """Yield one final-entry descriptor and retain close failures causally."""
    descriptor = open_entry(parent, path, flags)
    try:
        yield descriptor
    except BaseException as operation_error:
        _close_after_failure(descriptor, path, operation_error)
        raise
    os.close(descriptor)


def unlink_entry(parent: ParentDescriptor, path: Path) -> None:
    """Unlink one entry from the still-authorized physical parent."""
    require_entry(parent, path)
    assert_parent_unchanged(parent)
    os.unlink(path.name, dir_fd=parent.descriptor)


def replace_entry(
    source_parent: ParentDescriptor,
    source: Path,
    destination_parent: ParentDescriptor,
    destination: Path,
) -> None:
    """Replace one entry using only authenticated directory descriptors."""
    require_entry(source_parent, source)
    require_entry(destination_parent, destination)
    assert_parent_unchanged(source_parent)
    assert_parent_unchanged(destination_parent)
    os.replace(
        source.name,
        destination.name,
        src_dir_fd=source_parent.descriptor,
        dst_dir_fd=destination_parent.descriptor,
    )


def _require_capabilities(path: Path, *, replace: bool, unlink: bool) -> None:
    parent_path.require_traversal_capabilities(path)
    operations: list[tuple[str, object]] = []
    if replace:
        # CPython exposes ``src_dir_fd``/``dst_dir_fd`` on ``os.replace`` via
        # the same renameat primitive as ``os.rename``, but records only
        # ``os.rename`` in ``supports_dir_fd`` on supported POSIX runtimes.
        operations.append(("replace", os.rename))
    if unlink:
        operations.append(("unlink", os.unlink))
    missing = [
        name for name, operation in operations if operation not in os.supports_dir_fd
    ]
    if missing:
        unsupported = sorted(set(missing))
        message = f"descriptor-bound atomic files are unsupported: {unsupported}"
        raise OSError(errno.ENOTSUP, message)


def require_entry(parent: ParentDescriptor, path: Path) -> None:
    """Require one validated path to name a child of the opened parent."""
    validated = file_path.validate_atomic_path(path)
    if validated.parent != parent.path:
        message = f"atomic file does not belong to authenticated parent: {path}"
        raise OSError(errno.EINVAL, message, path)


def _close_after_failure(
    descriptor: int, path: Path, operation_error: BaseException
) -> None:
    try:
        os.close(descriptor)
    except OSError as close_error:
        message = (
            f"atomic operation failed ({operation_error}); close failed ({close_error})"
        )
        if isinstance(operation_error, Exception):
            causes = ExceptionGroup(
                "atomic operation and descriptor close failed",
                [operation_error, close_error],
            )
            raise OSError(errno.EIO, message, path) from causes
        group_message = "atomic operation and descriptor close failed"
        raise BaseExceptionGroup(
            group_message, [operation_error, close_error]
        ) from close_error


__all__: list[str] = [
    "ParentDescriptor",
    "assert_parent_unchanged",
    "entry_descriptor",
    "entry_stat",
    "open_entry",
    "parent_descriptor",
    "replace_entry",
    "require_entry",
    "unlink_entry",
]
