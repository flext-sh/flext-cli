"""Public typed physical-state authentication for atomic file snapshots."""

from __future__ import annotations

import errno
import os
from pathlib import Path

from flext_cli import m

type PhysicalState = tuple[int, int, int, int | None, int | None]


def require_existing(
    state: m.Cli.AtomicFileState, *, purpose: str
) -> tuple[bytes, int, tuple[int, int]]:
    """Return required content, mode, and inode identity from an existing state."""
    if (
        state.content is None
        or state.mode is None
        or state.device is None
        or state.inode is None
        or state.link_count is None
    ):
        message = f"{purpose} atomic file state is absent: {state.path}"
        raise FileNotFoundError(errno.ENOENT, message, state.path)
    return state.content, state.mode, (state.device, state.inode)


def require_observed(
    planned: m.Cli.AtomicFileState,
    observed: os.stat_result | None,
    *,
    path: Path | None = None,
) -> None:
    """Require host metadata to equal every available planned physical field."""
    target = planned.path if path is None else path
    if planned.content is None:
        if observed is not None:
            message = f"atomic file appeared after absent snapshot: {target}"
            raise OSError(errno.ESTALE, message, target)
        return
    if observed is None:
        message = f"atomic file disappeared after snapshot: {target}"
        raise OSError(errno.ESTALE, message, target)
    expected = _planned_physical_state(planned)
    if expected != physical_state(observed):
        message = f"atomic file physical state changed: {target}"
        raise OSError(errno.ESTALE, message, target)


def require_parent(state: m.Cli.AtomicFileState, observed: os.stat_result) -> None:
    """Require the authenticated parent to equal the snapshot parent identity."""
    if (state.parent_device, state.parent_inode) != (
        observed.st_dev,
        observed.st_ino,
    ):
        message = f"atomic file parent identity changed: {state.path.parent}"
        raise OSError(errno.ESTALE, message, state.path.parent)


def physical_state(state: os.stat_result) -> PhysicalState:
    """Return every caller-visible physical identity field from host state."""
    return (
        state.st_dev,
        state.st_ino,
        state.st_nlink,
        getattr(state, "st_file_attributes", None),
        getattr(state, "st_reparse_tag", None),
    )


def _planned_physical_state(state: m.Cli.AtomicFileState) -> PhysicalState:
    if state.device is None or state.inode is None or state.link_count is None:
        message = f"existing atomic file state lacks physical identity: {state.path}"
        raise OSError(errno.EINVAL, message, state.path)
    return (
        state.device,
        state.inode,
        state.link_count,
        state.file_attributes,
        state.reparse_tag,
    )


__all__: list[str] = [
    "PhysicalState",
    "physical_state",
    "require_existing",
    "require_observed",
    "require_parent",
]
