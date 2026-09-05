"""Component-authenticated physical directory descriptor traversal."""

from __future__ import annotations

import errno
import os
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from . import atomic_file_path as file_path

type DirectoryChainInspection = tuple[
    Path,
    os.stat_result,
    tuple[tuple[int, int], ...],
    tuple[Path, ...],
]


@dataclass(frozen=True, slots=True)
class PhysicalDirectory:
    """One descriptor and the exact ancestry used to reach it."""

    descriptor: int
    state: os.stat_result
    ancestry: tuple[tuple[int, int], ...]


@contextmanager
def physical_directory(path: Path) -> Generator[PhysicalDirectory]:
    """Open an absolute directory one non-aliased component at a time."""
    require_traversal_capabilities(path)
    file_path.validate_parent_path(path)
    descriptors: list[int] = []
    try:
        descriptor, state, ancestry, _consumed = _open_components(
            path, descriptors, stop_at_missing=False
        )
    except BaseException as operation_error:
        _close_after_failure(descriptors, path, operation_error)
        raise
    descriptors.pop()
    try:
        _close_descriptors(descriptors, path)
    except BaseException as operation_error:
        _close_after_failure([descriptor], path, operation_error)
        raise
    opened = PhysicalDirectory(descriptor, state, ancestry)
    try:
        yield opened
    except BaseException as operation_error:
        _close_after_failure([descriptor], path, operation_error)
        raise
    os.close(descriptor)


def inspect_directory_chain(path: Path) -> DirectoryChainInspection:
    """Find the exact existing anchor and every contiguous missing directory."""
    target = file_path.validate_directory_path(path)
    require_traversal_capabilities(target)
    descriptors: list[int] = []
    try:
        _descriptor, state, ancestry, consumed = _open_components(
            target, descriptors, stop_at_missing=True
        )
        parts = target.relative_to(Path(target.anchor)).parts
        anchor = Path(target.anchor).joinpath(*parts[:consumed])
        missing = _missing_paths(anchor, parts[consumed:])
        _close_descriptors(descriptors, target)
    except BaseException as operation_error:
        _close_after_failure(descriptors, target, operation_error)
        raise
    with physical_directory(anchor) as current:
        if current.ancestry != ancestry or file_path.identity(current.state) != (
            state.st_dev,
            state.st_ino,
        ):
            message = f"atomic directory-chain anchor changed: {anchor}"
            raise OSError(errno.ESTALE, message, anchor)
    return anchor, state, ancestry, missing


def require_traversal_capabilities(path: Path) -> None:
    """Require the descriptor and no-follow operations used for path traversal."""
    missing = [
        name
        for name, operation in (("open", os.open), ("stat", os.stat))
        if operation not in os.supports_dir_fd
    ]
    if os.stat not in os.supports_follow_symlinks:
        missing.append("stat(follow_symlinks=False)")
    if not getattr(os, "O_DIRECTORY", 0):
        missing.append("O_DIRECTORY")
    if not getattr(os, "O_NOFOLLOW", 0):
        missing.append("O_NOFOLLOW")
    if missing:
        unsupported = sorted(set(missing))
        message = f"descriptor-bound path traversal is unsupported: {unsupported}"
        raise OSError(errno.ENOTSUP, message, path)


def _open_components(
    path: Path, descriptors: list[int], *, stop_at_missing: bool
) -> tuple[int, os.stat_result, tuple[tuple[int, int], ...], int]:
    flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_BINARY", 0)
    )
    root = Path(path.anchor)
    descriptor = os.open(root, flags)
    descriptors.append(descriptor)
    state = os.fstat(descriptor)
    file_path.validate_directory_state(root, state)
    ancestry: list[tuple[int, int]] = [file_path.identity(state)]
    parts = path.relative_to(root).parts
    for index, component in enumerate(parts):
        try:
            relative_state = os.stat(
                component, dir_fd=descriptor, follow_symlinks=False
            )
        except FileNotFoundError:
            if stop_at_missing:
                return descriptor, state, tuple(ancestry), index
            raise
        file_path.validate_directory_state(path, relative_state)
        next_descriptor = os.open(component, flags, dir_fd=descriptor)
        descriptors.append(next_descriptor)
        descriptor_state = os.fstat(next_descriptor)
        file_path.validate_directory_state(path, descriptor_state)
        if file_path.identity(relative_state) != file_path.identity(descriptor_state):
            message = f"atomic parent component identity changed: {path}"
            raise OSError(errno.ESTALE, message, path)
        descriptor = next_descriptor
        state = descriptor_state
        ancestry.append(file_path.identity(state))
    return descriptor, state, tuple(ancestry), len(parts)


def _missing_paths(anchor: Path, parts: tuple[str, ...]) -> tuple[Path, ...]:
    missing: list[Path] = []
    current = anchor
    for component in parts:
        current /= component
        missing.append(current)
    return tuple(missing)


def _close_descriptors(descriptors: list[int], path: Path) -> None:
    close_errors: list[OSError] = []
    while descriptors:
        try:
            os.close(descriptors.pop())
        except OSError as close_error:
            close_errors.append(close_error)
    if close_errors:
        message = "; ".join(str(error) for error in close_errors)
        raise OSError(errno.EIO, f"atomic descriptor close failed: {message}", path)


def _close_after_failure(
    descriptors: list[int], path: Path, operation_error: BaseException
) -> None:
    try:
        _close_descriptors(descriptors, path)
    except OSError as close_error:
        message = f"atomic operation failed ({operation_error}); {close_error}"
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
    "DirectoryChainInspection",
    "PhysicalDirectory",
    "inspect_directory_chain",
    "physical_directory",
    "require_traversal_capabilities",
]
