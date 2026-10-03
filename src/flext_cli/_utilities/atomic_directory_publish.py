"""Guarded no-clobber publication of caller-owned staged directories.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
from pathlib import Path
from typing import Never

from flext_cli import m
from flext_cli._utilities.atomic_directory_descriptor import (
    FlextCliUtilitiesAtomicDirectoryDescriptor,
)
from flext_cli._utilities.atomic_directory_model import (
    FlextCliUtilitiesAtomicDirectoryModel,
)
from flext_cli._utilities.atomic_directory_state import (
    FlextCliUtilitiesAtomicDirectoryState,
)
from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)
from flext_cli._utilities.atomic_file_durability import (
    FlextCliUtilitiesAtomicFileDurability,
)
from flext_cli._utilities.atomic_file_path import FlextCliUtilitiesAtomicFilePath


class FlextCliUtilitiesAtomicDirectoryPublish:
    """Canonical namespace owner."""

    @staticmethod
    def publish_guarded_staged_empty_directory(
        destination_before: m.Cli.AtomicDirectoryState,
        staged: m.Cli.AtomicDirectoryState,
    ) -> m.Cli.AtomicDirectoryState:
        """Move one exact empty directory into an exact absent destination.

        Linux uses ``renameat2(RENAME_NOREPLACE)`` so a concurrent destination can
        never be overwritten. Windows is accepted only when descriptor-relative
        ``os.rename`` is available with its documented no-replace behavior. Other
        platforms fail before effects. Source identity still requires every writer
        to honor the caller's exclusive cooperative lock.

        Returns:
            The resulting ``m.Cli.AtomicDirectoryState``.

        Raises:
            OSError: If ``destination == staged_path``.

        """
        destination = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(
            destination_before.path
        )
        staged_path = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(staged.path)
        if destination == staged_path:
            message = "staged directory and destination must differ"
            raise OSError(errno.EINVAL, message, destination)
        FlextCliUtilitiesAtomicDirectoryModel.require_absent(
            destination_before, purpose="published"
        )
        FlextCliUtilitiesAtomicDirectoryModel.require_existing(staged, purpose="staged")
        FlextCliUtilitiesAtomicDirectoryDescriptor.require_publish_capabilities(
            staged_path, destination
        )
        with (
            FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
                destination
            ) as destination_parent,
            FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(
                staged_path
            ) as staged_parent,
        ):
            FlextCliUtilitiesAtomicDirectoryModel.require_parent(
                destination_before, destination_parent.state
            )
            FlextCliUtilitiesAtomicDirectoryModel.require_parent(
                staged, staged_parent.state
            )
            FlextCliUtilitiesAtomicDirectoryPublish._require_destination_absent(
                destination_before, destination_parent, destination
            )
            authenticated = (
                FlextCliUtilitiesAtomicDirectoryPublish._authenticated_staged(
                    staged, staged_parent, staged_path
                )
            )
            FlextCliUtilitiesAtomicDirectoryPublish._require_same_filesystem(
                destination,
                destination_parent,
                staged_parent,
                authenticated,
            )
            FlextCliUtilitiesAtomicFileDurability.sync_replacement(
                staged_parent, destination_parent
            )
            FlextCliUtilitiesAtomicDirectoryPublish._require_destination_absent(
                destination_before, destination_parent, destination
            )
            authenticated = (
                FlextCliUtilitiesAtomicDirectoryPublish._authenticated_staged(
                    staged, staged_parent, staged_path
                )
            )
            FlextCliUtilitiesAtomicDirectoryDescriptor.rename_entry_noreplace(
                staged_parent,
                staged_path,
                destination_parent,
                destination,
            )
            try:
                FlextCliUtilitiesAtomicFileDurability.sync_replacement(
                    staged_parent, destination_parent
                )
                return FlextCliUtilitiesAtomicDirectoryPublish._published_state(
                    destination_parent,
                    destination,
                    staged_parent,
                    staged_path,
                    staged,
                )
            except OSError as post_error:
                FlextCliUtilitiesAtomicDirectoryPublish._raise_post_publication_failure(
                    destination, post_error
                )

    @staticmethod
    def _require_destination_absent(
        planned: m.Cli.AtomicDirectoryState,
        parent: FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor,
        path: Path,
    ) -> None:
        observed = FlextCliUtilitiesAtomicDirectoryState.destination_state(
            path, parent=parent
        )
        FlextCliUtilitiesAtomicDirectoryModel.require_observed(planned, observed)
        FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(parent)

    @staticmethod
    def _authenticated_staged(
        planned: m.Cli.AtomicDirectoryState,
        parent: FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor,
        path: Path,
    ) -> os.stat_result:
        observed = FlextCliUtilitiesAtomicDirectoryState.destination_state(
            path, parent=parent
        )
        FlextCliUtilitiesAtomicDirectoryModel.require_observed(planned, observed)
        if observed is None:
            message = f"atomic staged directory disappeared: {path}"
            raise OSError(errno.ESTALE, message, path)
        authenticated = FlextCliUtilitiesAtomicDirectoryState.read_empty_state(
            parent, path, observed
        )
        FlextCliUtilitiesAtomicDirectoryModel.require_observed(planned, authenticated)
        return authenticated

    @staticmethod
    def _require_same_filesystem(
        destination: Path,
        destination_parent: FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor,
        staged_parent: FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor,
        staged: os.stat_result,
    ) -> None:
        device = destination_parent.state.st_dev
        if staged_parent.state.st_dev != device or staged.st_dev != device:
            message = "staged directory and destination span filesystems"
            raise OSError(errno.EXDEV, message, destination)

    @staticmethod
    def _published_state(
        destination_parent: FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor,
        destination: Path,
        staged_parent: FlextCliUtilitiesAtomicFileDescriptor.FlextCliParentDescriptor,
        staged_path: Path,
        staged: m.Cli.AtomicDirectoryState,
    ) -> m.Cli.AtomicDirectoryState:
        if (
            FlextCliUtilitiesAtomicDirectoryState.destination_state(
                staged_path, parent=staged_parent
            )
            is not None
        ):
            message = f"staged directory name exists after publication: {staged_path}"
            raise OSError(errno.ESTALE, message, staged_path)
        observed = FlextCliUtilitiesAtomicDirectoryState.destination_state(
            destination, parent=destination_parent
        )
        if observed is None:
            message = f"published directory is missing: {destination}"
            raise OSError(errno.ESTALE, message, destination)
        authenticated = FlextCliUtilitiesAtomicDirectoryState.read_empty_state(
            destination_parent,
            destination,
            observed,
        )
        FlextCliUtilitiesAtomicDirectoryModel.require_observed(staged, authenticated)
        return FlextCliUtilitiesAtomicDirectoryModel.from_observed(
            destination,
            destination_parent.state,
            authenticated,
        )

    @staticmethod
    def _raise_post_publication_failure(destination: Path, error: OSError) -> Never:
        message = (
            "atomic directory rename completed but durability or live-state proof failed: "
            f"{error}"
        )
        raise OSError(errno.EIO, message, destination) from error


__all__: list[str] = ["FlextCliUtilitiesAtomicDirectoryPublish"]
