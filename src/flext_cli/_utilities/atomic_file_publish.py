"""Public guarded publication of caller-owned staged files.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from typing import TYPE_CHECKING

from flext_cli import m
from flext_cli._utilities import (
    FlextCliUtilitiesAtomicFileDescriptor,
    FlextCliUtilitiesAtomicFileDurability,
    FlextCliUtilitiesAtomicFileMode,
    FlextCliUtilitiesAtomicFileModel,
    FlextCliUtilitiesAtomicFilePath,
    FlextCliUtilitiesAtomicFilePublishChecks,
    FlextCliUtilitiesAtomicFileRead,
    FlextCliUtilitiesAtomicFileState,
)

if TYPE_CHECKING:
    from pathlib import Path

    from flext_cli import t


class FlextCliUtilitiesAtomicFilePublish:
    """Canonical namespace owner."""

    @staticmethod
    def publish_guarded_staged_file(
        destination_before: m.Cli.AtomicFileState | m.Cli.AtomicFileReceipt,
        staged: m.Cli.AtomicFileState | m.Cli.AtomicFileReceipt,
    ) -> os.stat_result:
        """Move one exact caller-owned staged file over an exact destination state.

        The caller owns both the cooperative lock and staged-file lifecycle.  A
        failure before replacement leaves the staged path in place. A completed
        replace consumes it; any subsequent validation failure requires the caller's
        journal to classify the destination. Every changed physical parent directory
        is synced after a completed replacement.

        Returns:
            The resulting ``os.stat_result``.

        Raises:
            FileNotFoundError: If ``staged_state is None``.
            OSError: If ``destination == staged_path``.

        """
        destination, staged_path = FlextCliUtilitiesAtomicFilePublish._validated_paths(
            destination_before,
            staged,
        )
        staged_payload, staged_mode, staged_identity, staged_proof = (
            FlextCliUtilitiesAtomicFilePublish._resolve_staged(staged_path, staged)
        )
        destination_payload = (
            FlextCliUtilitiesAtomicFilePublish._resolve_destination_payload(
                destination_before,
            )
        )
        FlextCliUtilitiesAtomicFileMode.validate_guarded_mode_tuple(
            destination,
            destination_payload,
            destination_before.mode,
        )
        FlextCliUtilitiesAtomicFilePublishChecks.validate_identity(
            staged_path,
            staged_identity,
            label="staged_identity",
        )
        with (
            FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
                destination,
                replace=True,
            ) as destination_parent,
            FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
                staged_path,
                replace=True,
            ) as staged_parent,
        ):
            FlextCliUtilitiesAtomicFileModel.require_parent(
                destination_before,
                destination_parent.state,
            )
            FlextCliUtilitiesAtomicFileModel.require_parent(staged, staged_parent.state)
            destination_state = FlextCliUtilitiesAtomicFileState.destination_state(
                destination,
                parent=destination_parent,
            )
            FlextCliUtilitiesAtomicFileModel.require_observed(
                destination_before,
                destination_state,
            )
            FlextCliUtilitiesAtomicFilePublishChecks.validate_payload(
                destination_parent, destination, destination_state, destination_payload
            )
            FlextCliUtilitiesAtomicFileMode.validate_mode_precondition(
                destination,
                destination_state,
                destination_before.mode,
            )
            staged_state = FlextCliUtilitiesAtomicFileState.destination_state(
                staged_path,
                parent=staged_parent,
            )
            if staged_state is None:
                message = f"atomic staged file is missing: {staged_path}"
                raise FileNotFoundError(errno.ENOENT, message, staged_path)
            FlextCliUtilitiesAtomicFileModel.require_observed(staged, staged_state)
            if isinstance(
                staged, m.Cli.AtomicFileReceipt
            ) and staged.version_key != FlextCliUtilitiesAtomicFileRead.state_key(
                staged_state
            ):
                message = f"atomic staged receipt version changed: {staged_path}"
                raise OSError(errno.ESTALE, message, staged_path)
            if (
                isinstance(destination_before, m.Cli.AtomicFileReceipt)
                and destination_state is not None
                and destination_before.version_key
                != FlextCliUtilitiesAtomicFileRead.state_key(destination_state)
            ):
                message = f"atomic destination receipt version changed: {destination}"
                raise OSError(errno.ESTALE, message, destination)
            FlextCliUtilitiesAtomicFilePublishChecks.require_distinct_inode(
                destination,
                destination_state,
                staged_identity,
            )
            FlextCliUtilitiesAtomicFilePublishChecks.validate_devices(
                destination,
                destination_parent,
                destination_state,
                staged_parent,
                m.Cli.ObservedFile(path=staged_path, state=staged_state),
            )
            FlextCliUtilitiesAtomicFilePublishChecks.validate_payload(
                staged_parent, staged_path, staged_state, staged_payload
            )
            FlextCliUtilitiesAtomicFileMode.validate_mode_precondition(
                staged_path,
                staged_state,
                staged_mode,
            )
            FlextCliUtilitiesAtomicFileState.assert_destination_unchanged(
                destination,
                destination_state,
                parent=destination_parent,
            )
            FlextCliUtilitiesAtomicFileState.assert_temporary_owned(
                staged_path,
                staged_identity,
                parent=staged_parent,
            )
            FlextCliUtilitiesAtomicFileDescriptor.replace_entry(
                staged_parent,
                staged_path,
                destination_parent,
                destination,
            )
            FlextCliUtilitiesAtomicFileDurability.sync_replacement(
                staged_parent,
                destination_parent,
            )
            published = FlextCliUtilitiesAtomicFilePublishChecks.validate_publication(
                destination_parent,
                destination,
                staged_parent,
                staged_proof,
            )
            FlextCliUtilitiesAtomicFileModel.require_observed(
                staged,
                published,
                path=destination,
            )
            return published

    @staticmethod
    def _validated_paths(
        destination_before: m.Cli.AtomicFileState | m.Cli.AtomicFileReceipt,
        staged: m.Cli.AtomicFileState | m.Cli.AtomicFileReceipt,
    ) -> t.Pair[Path, Path]:
        """Validate both atomic paths and require a distinct staged destination.

        Returns:
            The validated ``(destination, staged_path)`` pair.

        Raises:
            OSError: If the staged path equals the atomic destination.

        """
        destination = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(
            destination_before.path,
        )
        staged_path = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(staged.path)
        if destination == staged_path:
            message = "staged file and atomic destination must differ"
            raise OSError(errno.EINVAL, message, destination)
        return (destination, staged_path)

    @staticmethod
    def _resolve_staged(
        staged_path: Path,
        staged: m.Cli.AtomicFileState | m.Cli.AtomicFileReceipt,
    ) -> t.Quad[
        bytes | m.Cli.AtomicFileReceipt,
        int,
        t.Pair[int, int],
        m.Cli.StagedFile | m.Cli.AtomicFileReceipt,
    ]:
        """Resolve the staged payload, mode, identity, and publication proof.

        Returns:
            The resulting ``(payload, mode, identity, proof)`` quadruple.

        Raises:
            FileNotFoundError: If the staged receipt metadata is absent.

        """
        if isinstance(staged, m.Cli.AtomicFileReceipt):
            if staged.mode is None or staged.device is None or staged.inode is None:
                raise FileNotFoundError(
                    errno.ENOENT, "staged receipt is absent", staged_path
                )
            return (staged, staged.mode, (staged.device, staged.inode), staged)
        staged_bytes, staged_mode, staged_identity = (
            FlextCliUtilitiesAtomicFileModel.require_existing(
                staged,
                purpose="staged",
            )
        )
        return (
            staged_bytes,
            staged_mode,
            staged_identity,
            m.Cli.StagedFile(
                path=staged_path,
                content=staged_bytes,
                mode=staged_mode,
                identity=staged_identity,
            ),
        )

    @staticmethod
    def _resolve_destination_payload(
        destination_before: m.Cli.AtomicFileState | m.Cli.AtomicFileReceipt,
    ) -> bytes | m.Cli.AtomicFileReceipt | None:
        """Resolve the guarded destination payload from the before-state.

        Returns:
            The destination payload bytes, receipt, or ``None`` when absent.

        """
        if isinstance(destination_before, m.Cli.AtomicFileReceipt):
            return destination_before if destination_before.device is not None else None
        return destination_before.content


__all__: list[str] = ["FlextCliUtilitiesAtomicFilePublish"]
