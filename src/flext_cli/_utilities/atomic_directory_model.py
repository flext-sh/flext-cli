"""Typed physical-state contracts for guarded empty-directory operations."""

from __future__ import annotations

import errno
import os
import stat
from pathlib import Path

from flext_cli import m

type DirectoryPhysicalState = tuple[int, int, int, int, int | None, int | None]


def from_observed(
    path: Path, parent: os.stat_result | None, observed: os.stat_result | None
) -> m.Cli.AtomicDirectoryState:
    """Build the caller-owned state from one authenticated observation."""
    return m.Cli.AtomicDirectoryState(
        path=path,
        exists=observed is not None,
        parent_device=None if parent is None else parent.st_dev,
        parent_inode=None if parent is None else parent.st_ino,
        mode=None if observed is None else stat.S_IMODE(observed.st_mode),
        device=None if observed is None else observed.st_dev,
        inode=None if observed is None else observed.st_ino,
        link_count=None if observed is None else observed.st_nlink,
        file_attributes=(
            None if observed is None else getattr(observed, "st_file_attributes", None)
        ),
        reparse_tag=(
            None if observed is None else getattr(observed, "st_reparse_tag", None)
        ),
    )


def require_absent(state: m.Cli.AtomicDirectoryState, *, purpose: str) -> None:
    """Require the caller state to authorize creation from exact absence."""
    if state.exists:
        message = f"{purpose} atomic directory state already exists: {state.path}"
        raise FileExistsError(errno.EEXIST, message, state.path)


def require_existing(state: m.Cli.AtomicDirectoryState, *, purpose: str) -> None:
    """Require the caller state to authorize an existing empty directory."""
    if not state.exists:
        message = f"{purpose} atomic directory state is absent: {state.path}"
        raise FileNotFoundError(errno.ENOENT, message, state.path)


def require_observed(
    planned: m.Cli.AtomicDirectoryState, observed: os.stat_result | None
) -> None:
    """Require presence, mode, and every physical field to match the snapshot."""
    if not planned.exists:
        if observed is not None:
            message = f"atomic directory appeared after absent snapshot: {planned.path}"
            raise OSError(errno.ESTALE, message, planned.path)
        return
    if observed is None:
        message = f"atomic directory disappeared after snapshot: {planned.path}"
        raise OSError(errno.ESTALE, message, planned.path)
    if _planned_state(planned) != physical_state(observed):
        message = f"atomic directory physical state changed: {planned.path}"
        raise OSError(errno.ESTALE, message, planned.path)


def require_parent(
    planned: m.Cli.AtomicDirectoryState, observed: os.stat_result
) -> None:
    """Require the authenticated parent to equal the snapshot parent identity."""
    if planned.parent_device is None or planned.parent_inode is None:
        message = (
            f"atomic directory parent was absent at snapshot: {planned.path.parent}"
        )
        raise FileNotFoundError(errno.ENOENT, message, planned.path.parent)
    if (planned.parent_device, planned.parent_inode) != (
        observed.st_dev,
        observed.st_ino,
    ):
        message = f"atomic directory parent identity changed: {planned.path.parent}"
        raise OSError(errno.ESTALE, message, planned.path.parent)


def physical_state(state: os.stat_result) -> DirectoryPhysicalState:
    """Return every caller-visible directory identity field."""
    return (
        stat.S_IMODE(state.st_mode),
        state.st_dev,
        state.st_ino,
        state.st_nlink,
        getattr(state, "st_file_attributes", None),
        getattr(state, "st_reparse_tag", None),
    )


def _planned_state(state: m.Cli.AtomicDirectoryState) -> DirectoryPhysicalState:
    mode, device, inode, link_count = (
        state.mode,
        state.device,
        state.inode,
        state.link_count,
    )
    if mode is None or device is None or inode is None or link_count is None:
        message = f"existing atomic directory lacks physical identity: {state.path}"
        raise OSError(errno.EINVAL, message, state.path)
    return (mode, device, inode, link_count, state.file_attributes, state.reparse_tag)


__all__: list[str] = [
    "DirectoryPhysicalState",
    "from_observed",
    "physical_state",
    "require_absent",
    "require_existing",
    "require_observed",
    "require_parent",
]
