"""Public physical identity and publication-result checks for staged files.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import hashlib
import os
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli import c, m
from flext_cli._utilities._atomic_models import FlextCliUtilitiesAtomicModels
from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)
from flext_cli._utilities.atomic_file_mode import FlextCliUtilitiesAtomicFileMode
from flext_cli._utilities.atomic_file_read import FlextCliUtilitiesAtomicFileRead
from flext_cli._utilities.atomic_file_state import FlextCliUtilitiesAtomicFileState

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliUtilitiesAtomicFilePublishChecks:
    """Canonical namespace owner."""

    @staticmethod
    def validate_identity(path: Path, value: t.Pair[int, int], *, label: str) -> None:
        """Require one strict non-negative device and inode pair.

        Raises:
            OSError: If ``len(value) != c.Cli.IDENTITY_COMPONENT_COUNT or
            any((isinstance(item, bool) for item in value)) or any((item < 0 for item in
            value))``.

        """
        if (
            len(value) != c.Cli.IDENTITY_COMPONENT_COUNT
            or any(isinstance(item, bool) for item in value)
            or any(item < 0 for item in value)
        ):
            message = f"{label} must be a non-negative device and inode pair"
            raise OSError(errno.EINVAL, message, path)

    @staticmethod
    def require_identity(
        path: Path,
        state: os.stat_result | None,
        expected: t.Pair[int, int] | None,
    ) -> None:
        """Require an observed physical identity to match its caller snapshot.

        Raises:
            OSError: If ``observed != expected``.

        """
        observed = (
            None if state is None else FlextCliUtilitiesAtomicFileState.identity(state)
        )
        if observed != expected:
            message = f"atomic file physical identity changed: {path}"
            raise OSError(errno.ESTALE, message, path)

    @staticmethod
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
            and FlextCliUtilitiesAtomicFileState.identity(destination_state)
            == staged_identity
        ):
            message = "staged file and atomic destination share one inode"
            raise OSError(errno.EINVAL, message, destination)

    @staticmethod
    def validate_devices(
        destination: Path,
        destination_parent: (FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor),
        destination_state: os.stat_result | None,
        staged_parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        staged: FlextCliUtilitiesAtomicModels.ObservedFile,
    ) -> None:
        """Require both entries and parents to occupy one filesystem.

        Raises:
            OSError: If ``staged_parent.state.st_dev != device or staged.state.st_dev !=
                staged_parent.state.st_dev or (destination_state is not None and
                destination_state.st_dev != device)``.

        """
        device = destination_parent.state.st_dev
        if (
            staged_parent.state.st_dev != device
            or staged.state.st_dev != staged_parent.state.st_dev
            or (destination_state is not None and destination_state.st_dev != device)
        ):
            message = (
                f"atomic staged and destination entries span filesystems: {staged.path}"
            )
            raise OSError(errno.EXDEV, message, destination)

    @staticmethod
    def validate_publication(
        destination_parent: (FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor),
        destination: Path,
        staged_parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        staged: FlextCliUtilitiesAtomicModels.StagedFile | m.Cli.AtomicFileReceipt,
    ) -> os.stat_result:
        """Prove replacement consumed the staged name and retained its exact state.

        Returns:
            The resulting ``os.stat_result``.

        Raises:
            OSError: If the staged name remains, or the published identity, bytes or
                mode differ from the captured staging context.

        """
        if (
            FlextCliUtilitiesAtomicFileState.destination_state(
                staged.path,
                parent=staged_parent,
            )
            is not None
        ):
            message = (
                f"atomic staged file still exists after publication: {staged.path}"
            )
            raise OSError(errno.ESTALE, message, staged.path)
        published = FlextCliUtilitiesAtomicFileState.destination_state(
            destination,
            parent=destination_parent,
        )
        staged_identity = (
            (staged.device, staged.inode)
            if isinstance(staged, m.Cli.AtomicFileReceipt)
            else staged.identity
        )
        if (
            published is None
            or FlextCliUtilitiesAtomicFileState.identity(published) != staged_identity
        ):
            message = f"published atomic file has another identity: {destination}"
            raise OSError(errno.ESTALE, message, destination)
        FlextCliUtilitiesAtomicFilePublishChecks.validate_payload(
            destination_parent,
            destination,
            published,
            staged if isinstance(staged, m.Cli.AtomicFileReceipt) else staged.content,
        )
        FlextCliUtilitiesAtomicFileMode.validate_mode_precondition(
            destination,
            published,
            staged.mode,
        )
        return published

    @staticmethod
    def validate_payload(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        path: Path,
        state: os.stat_result | None,
        expected: bytes | m.Cli.AtomicFileReceipt | None,
    ) -> None:
        """Authenticate either exact owned bytes or a streamed content receipt.

        Raises:
            OSError: If the receipt size or content bytes differ from the state.

        """
        if not isinstance(expected, m.Cli.AtomicFileReceipt):
            FlextCliUtilitiesAtomicFileState.validate_precondition(
                path, state, expected, enabled=True, parent=parent
            )
            return
        if state is None or state.st_size != expected.size:
            message = f"atomic receipt size differs: {path}"
            raise OSError(errno.ESTALE, message, path)
        with FlextCliUtilitiesAtomicFileDescriptor.entry_descriptor(
            parent, path, c.Cli.READ_FLAGS
        ) as descriptor:
            digest = hashlib.sha256()
            for chunk in FlextCliUtilitiesAtomicFileRead.descriptor_chunks(
                descriptor, path, state
            ):
                digest.update(chunk)
            if digest.hexdigest() != expected.sha256:
                message = f"atomic receipt bytes differ: {path}"
                raise OSError(errno.ESTALE, message, path)
        FlextCliUtilitiesAtomicFileState.assert_destination_unchanged(
            path, state, parent=parent
        )


__all__: list[str] = ["FlextCliUtilitiesAtomicFilePublishChecks"]
