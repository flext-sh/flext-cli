"""Public lexical and physical path validation for atomic file owners."""

from __future__ import annotations

import errno
import os
import stat
from pathlib import Path


def validate_atomic_path(path: Path) -> Path:
    """Require one absolute, normalized file pathname without traversal."""
    validate_directory_path(path)
    if not path.name:
        message = f"atomic file path cannot identify a filesystem root: {path}"
        raise OSError(errno.EINVAL, message, path)
    return path


def validate_directory_path(path: Path) -> Path:
    """Require one absolute, normalized directory path without traversal."""
    normalized = Path(os.path.normpath(path))
    if not path.is_absolute() or ".." in path.parts or normalized != path:
        message = f"atomic directory path is not absolute and normalized: {path}"
        raise OSError(errno.EINVAL, message, path)
    return path


def resolve_parent_path(parent: Path) -> tuple[os.stat_result | None, Path]:
    """Return one physical parent state, or the first missing path component.

    Every present component is still required to be a non-aliased physical
    directory: an aliased component is a defect, never absence.
    """
    validate_directory_path(parent)
    state: os.stat_result | None = None
    for component in (*reversed(parent.parents), parent):
        try:
            state = component.lstat()
        except FileNotFoundError:
            return None, component
        validate_directory_state(component, state)
    if state is None:
        return None, parent
    return state, parent


def validate_parent_path(parent: Path) -> os.stat_result:
    """Return a physical parent only when every path component is non-aliased."""
    state, component = resolve_parent_path(parent)
    if state is None:
        message = f"atomic destination parent is missing: {component}"
        raise FileNotFoundError(errno.ENOENT, message, component)
    return state


def validate_directory_state(path: Path, state: os.stat_result) -> None:
    """Require one non-reparse physical directory state."""
    if not stat.S_ISDIR(state.st_mode) or is_reparse_point(state):
        message = f"atomic destination parent is not a real directory: {path}"
        raise NotADirectoryError(errno.ENOTDIR, message, path)


def identity(state: os.stat_result) -> tuple[int, int]:
    """Return the physical device and inode identity of one filesystem object."""
    return (state.st_dev, state.st_ino)


def is_reparse_point(state: os.stat_result) -> bool:
    """Identify Windows reparse-point aliases without platform branching."""
    attributes = getattr(state, "st_file_attributes", 0)
    marker = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    reparse_tag = getattr(state, "st_reparse_tag", None)
    return bool(attributes & marker) or reparse_tag not in {None, 0}


__all__: list[str] = [
    "identity",
    "is_reparse_point",
    "resolve_parent_path",
    "validate_atomic_path",
    "validate_directory_path",
    "validate_directory_state",
    "validate_parent_path",
]
