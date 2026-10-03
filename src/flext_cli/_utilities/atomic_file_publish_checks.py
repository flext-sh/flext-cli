"""Public physical identity and publication-result checks for staged files.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli._utilities import atomic_file_mode, atomic_file_state

if TYPE_CHECKING:
    from flext_cli import t


IDENTITY_COMPONENT_COUNT: int = 2


def validate_identity(path: Path, value: t.Pair[int, int], *, label: str) -> None:
    """Require one strict non-negative device and inode pair.

    Raises:
        OSError: If ``len(value) != IDENTITY_COMPONENT_COUNT or
        any((isinstance(item, bool) for item in value)) or any((item < 0 for item in
        value))``.

    """
    if (
        len(value) != IDENTITY_COMPONENT_COUNT
        or any(isinstance(item, bool) for item in value)
        or any(item < 0 for item in value)
    ):
        message = f"{label} must be a non-negative device and inode pair"
        raise OSError(errno.EINVAL, message, path)


def require_identity(
    path: Path,
    state: os.stat_result | None,
    expected: t.Pair[int, int] | None,
) -> None:
    """Require an observed physical identity to match its caller snapshot.

    Raises:
        OSError: If ``observed != expected``.

    """
    observed = None if state is None else atomic_file_state.identity(state)
    if observed != expected:
        message = f"atomic file physical identity changed: {path}"
        raise OSError(errno.ESTALE, message, path)


def require_distinct_inode(
    destination: Path,
    destination_state: os.stat_result | None,
    staged_identity: t.Pair[int, int],
) -> None:
    """Reject lexical aliases that identify the same physical file.

    Raises:
        OSError: If ``destination_state is not None and
            file_state.identity(destination_state) == staged_identity``.

    """
    if (
        destination_state is not None
        and atomic_file_state.identity(destination_state) == staged_identity
    ):
        message = "staged file and atomic destination share one inode"
        raise OSError(errno.EINVAL, message, destination)


def validate_devices(
    destination: Path,
    destination_parent: (atomic_file_descriptor.ParentDescriptor),
    destination_state: os.stat_result | None,
    staged: Path,
    staged_parent: atomic_file_descriptor.ParentDescriptor,
    staged_state: os.stat_result,
) -> None:
    """Require both entries and parents to occupy one filesystem.

    Raises:
        OSError: If ``staged_parent.state.st_dev != device or staged_state.st_dev !=
            staged_parent.state.st_dev or (destination_state is not None and
            destination_state.st_dev != device)``.

    """
    device = destination_parent.state.st_dev
    if (
        staged_parent.state.st_dev != device
        or staged_state.st_dev != staged_parent.state.st_dev
        or (destination_state is not None and destination_state.st_dev != device)
    ):
        message = f"atomic staged and destination entries span filesystems: {staged}"
        raise OSError(errno.EXDEV, message, destination)


def validate_publication(
    destination_parent: (atomic_file_descriptor.ParentDescriptor),
    destination: Path,
    staged_parent: atomic_file_descriptor.ParentDescriptor,
    staged: Path,
    staged_bytes: bytes,
    staged_mode: int,
    staged_identity: t.Pair[int, int],
) -> os.stat_result:
    """Prove replacement consumed the staged name and retained its exact state.

    Returns:
        The resulting ``os.stat_result``.

    Raises:
        OSError: If ``file_state.destination_state(staged, parent=staged_parent) is
        not None``; or if ``published is None or file_state.identity(published) !=
        staged_identity``; or if ``file_state.read_authenticated_bytes(destination,
        published, parent=destination_parent) != staged_bytes``.

    """
    if (
        atomic_file_state.destination_state(
            staged,
            parent=staged_parent,
        )
        is not None
    ):
        message = f"atomic staged file still exists after publication: {staged}"
        raise OSError(errno.ESTALE, message, staged)
    published = atomic_file_state.destination_state(
        destination,
        parent=destination_parent,
    )
    if published is None or atomic_file_state.identity(published) != staged_identity:
        message = f"published atomic file has another identity: {destination}"
        raise OSError(errno.ESTALE, message, destination)
    if (
        atomic_file_state.read_authenticated_bytes(
            destination,
            published,
            parent=destination_parent,
        )
        != staged_bytes
    ):
        message = f"published atomic file bytes differ: {destination}"
        raise OSError(errno.ESTALE, message, destination)
    atomic_file_mode.validate_mode_precondition(
        destination,
        published,
        staged_mode,
    )
    return published


__all__: list[str] = [
    "IDENTITY_COMPONENT_COUNT",
    "require_distinct_inode",
    "require_identity",
    "validate_devices",
    "validate_identity",
    "validate_publication",
]
