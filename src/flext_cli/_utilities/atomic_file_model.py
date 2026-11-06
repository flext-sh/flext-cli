"""Public typed physical-state authentication for atomic file snapshots.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from flext_cli import p
from flext_cli._utilities import FlextCliUtilitiesAtomicFileDescriptor
from flext_cli.typings import PhysicalState


class FlextCliUtilitiesAtomicFileModel:
    """Canonical namespace owner."""

    @staticmethod
    def require_existing(
        state: p.Cli.AtomicFileState,
        *,
        purpose: str,
    ) -> tuple[bytes, int, tuple[int, int]]:
        """Return required content, mode, and inode identity from an existing state.

        Returns:
            Required content, mode, and inode identity from an existing state.

        Raises:
            FileNotFoundError: If ``state.content is None or state.mode is None or
                state.device is None or (state.inode is None) or (state.link_count is
                None)``.

        """
        message = f"{purpose} atomic file state is absent: {state.path}"
        if state.content is None or state.mode is None:
            raise FileNotFoundError(errno.ENOENT, message, state.path)
        if state.device is None or state.inode is None or state.link_count is None:
            raise FileNotFoundError(errno.ENOENT, message, state.path)
        return state.content, state.mode, (state.device, state.inode)

    @staticmethod
    def require_snapshot_presence(
        path: Path,
        observed: os.stat_result | None,
        *,
        present: bool,
        subject: str,
    ) -> os.stat_result | None:
        """Require one host observation to keep the snapshot's presence.

        Returns:
            The observation to compare, or ``None`` for an absent snapshot.

        Raises:
            OSError: If the entry appeared after an absent snapshot or
                disappeared after a present one.

        """
        if not present:
            if observed is not None:
                message = f"atomic {subject} appeared after absent snapshot: {path}"
                raise OSError(errno.ESTALE, message, path)
            return None
        if observed is None:
            message = f"atomic {subject} disappeared after snapshot: {path}"
            raise OSError(errno.ESTALE, message, path)
        return observed

    @staticmethod
    def require_observed(
        planned: p.Cli.AtomicFileIdentity,
        observed: os.stat_result | None,
        *,
        path: Path | None = None,
    ) -> None:
        """Require host metadata to equal every available planned physical field.

        Raises:
            OSError: If the presence or physical state changed after the snapshot.

        """
        target = planned.path if path is None else path
        current = FlextCliUtilitiesAtomicFileModel.require_snapshot_presence(
            target, observed, present=planned.device is not None, subject="file"
        )
        if (
            current is not None
            and FlextCliUtilitiesAtomicFileModel.planned_physical_state(
                planned, subject="file state"
            )
            != FlextCliUtilitiesAtomicFileModel.physical_state(current)
        ):
            message = f"atomic file physical state changed: {target}"
            raise OSError(errno.ESTALE, message, target)

    @staticmethod
    def require_parent(
        state: p.Cli.AtomicFileIdentity,
        observed: os.stat_result,
        *,
        subject: str = "file",
    ) -> None:
        """Require the authenticated parent to equal the snapshot parent identity.

        Raises:
            FileNotFoundError: If the snapshot parent was absent.
            OSError: If the parent identity changed since the snapshot.

        """
        if state.parent_device is None or state.parent_inode is None:
            message = (
                f"atomic {subject} parent was absent at snapshot: {state.path.parent}"
            )
            raise FileNotFoundError(errno.ENOENT, message, state.path.parent)
        if (state.parent_device, state.parent_inode) != (
            observed.st_dev,
            observed.st_ino,
        ):
            message = f"atomic {subject} parent identity changed: {state.path.parent}"
            raise OSError(errno.ESTALE, message, state.path.parent)

    @staticmethod
    @contextmanager
    def publication_parents(
        paths: tuple[Path, Path],
        states: tuple[p.Cli.AtomicFileIdentity, p.Cli.AtomicFileIdentity],
        *,
        subject: str,
        replace: bool,
    ) -> Generator[
        tuple[
            FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
            FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        ]
    ]:
        """Hold both authenticated publication parents bound to their snapshots.

        ``paths`` and ``states`` name the destination first, then the staged
        entry; each opened parent must still be the parent its snapshot saw.

        Yields:
            The destination parent and the staged parent descriptors.

        """
        destination, staged = paths
        with (
            FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
                destination, replace=replace
            ) as destination_parent,
            FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
                staged, replace=replace
            ) as staged_parent,
        ):
            FlextCliUtilitiesAtomicFileModel.require_parent(
                states[0], destination_parent.state, subject=subject
            )
            FlextCliUtilitiesAtomicFileModel.require_parent(
                states[1], staged_parent.state, subject=subject
            )
            yield destination_parent, staged_parent

    @staticmethod
    def physical_state(state: os.stat_result) -> PhysicalState:
        """Return every caller-visible physical identity field from host state.

        Returns:
            Every caller-visible physical identity field from host state.

        """
        return (
            state.st_dev,
            state.st_ino,
            state.st_nlink,
            getattr(state, "st_file_attributes", None),
            getattr(state, "st_reparse_tag", None),
        )

    @staticmethod
    def planned_physical_state(
        state: p.Cli.AtomicFileIdentity, *, subject: str
    ) -> PhysicalState:
        """Return the physical identity a present snapshot recorded.

        Returns:
            The planned device, inode, link count, and host attributes.

        Raises:
            OSError: If the snapshot lacks a physical identity field.

        """
        if state.device is None or state.inode is None or state.link_count is None:
            message = f"existing atomic {subject} lacks physical identity: {state.path}"
            raise OSError(errno.EINVAL, message, state.path)
        return (
            state.device,
            state.inode,
            state.link_count,
            state.file_attributes,
            state.reparse_tag,
        )


__all__: list[str] = ["FlextCliUtilitiesAtomicFileModel"]
