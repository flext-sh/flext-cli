"""Publish planned file changes for every engine through one shared owner.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path

from filelock import FileLock

from flext_cli import c, m, p, r
from flext_cli._utilities import FlextCliUtilitiesOutput
from flext_cli._utilities._files.binary_reads import FlextCliUtilitiesFilesPart03
from flext_cli._utilities._files.flextcliutilitiesfiles_part_06 import (
    FlextCliUtilitiesFilesPart06,
)
from flext_cli._utilities._files.writes import FlextCliUtilitiesFilesPart02


class FlextCliUtilitiesFileChanges:
    """Apply ``m.Cli.FileChange`` batches under one exclusive lock."""

    @staticmethod
    def file_changes_lock(lock_path: Path) -> FileLock:
        """Return the reentrant exclusive lock shared by every writer of one scope.

        Returns:
            The per-path singleton ``filelock`` context manager.

        """
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        return FileLock(
            lock_path,
            timeout=c.Cli.FILE_CHANGES_LOCK_TIMEOUT_SECONDS,
            is_singleton=True,
        )

    @staticmethod
    def pending_file_changes(
        changes: Sequence[m.Cli.FileChange],
    ) -> tuple[m.Cli.FileChange, ...]:
        """Select the changes whose bytes or mode differ from the observed state.

        Returns:
            The changes publication would apply, in input order.

        """
        return tuple(
            change
            for change in changes
            if change.desired_content != change.before.content
            or (
                change.desired_mode is not None
                and change.desired_mode != change.before.mode
            )
        )

    @staticmethod
    def publish_file_changes(
        changes: Sequence[m.Cli.FileChange],
        *,
        lock_path: Path,
        directory_mode: int = c.Cli.FILE_CHANGES_DIRECTORY_MODE,
        nonsecret_source_paths: Sequence[Path] = (),
    ) -> p.Result[tuple[Path, ...]]:
        """Verify every observed state, then write or delete each changed file.

        No effect happens unless every destination still matches its observed
        state. Unchanged files are skipped; missing parents are created with
        exactly ``directory_mode``. ``nonsecret_source_paths`` explicitly
        attests Python sources for content digest diagnostics; all other
        destinations report only physical metadata and byte counts.

        Returns:
            The paths actually written or deleted, or the first failure.

        """
        result_type = r[tuple[Path, ...]]
        pending = FlextCliUtilitiesFileChanges.pending_file_changes(changes)
        with FlextCliUtilitiesFileChanges.file_changes_lock(lock_path):
            FlextCliUtilitiesOutput.debug(
                f"file_changes: verify pid={os.getpid()} "
                f"pending={len(pending)} lock={lock_path}"
            )
            verified = FlextCliUtilitiesFilesPart06.atomic_verify_binary_file_states(
                tuple(change.before for change in pending),
                nonsecret_source_paths=nonsecret_source_paths,
            )
            if verified.failure:
                return result_type.from_failure(verified)
            for change in pending:
                source_diagnostics = ""
                if change.path in nonsecret_source_paths and change.path.suffix in {
                    ".py",
                    ".pyi",
                }:
                    before_digest = (
                        None
                        if change.before.content is None
                        else FlextCliUtilitiesFilesPart03.sha256_bytes(
                            change.before.content
                        )
                    )
                    desired_digest = (
                        None
                        if change.desired_content is None
                        else FlextCliUtilitiesFilesPart03.sha256_bytes(
                            change.desired_content
                        )
                    )
                    source_diagnostics = (
                        f" before_sha256={before_digest}"
                        f" desired_sha256={desired_digest}"
                    )
                before_length = (
                    None
                    if change.before.content is None
                    else len(change.before.content)
                )
                desired_length = (
                    None
                    if change.desired_content is None
                    else len(change.desired_content)
                )
                FlextCliUtilitiesOutput.debug(
                    f"file_changes: publish pid={os.getpid()} "
                    f"path={change.path} before_inode={change.before.inode} "
                    f"before_bytes={before_length} "
                    f"desired_bytes={desired_length}"
                    f"{source_diagnostics}"
                )
                published = FlextCliUtilitiesFileChanges._publish(
                    change, directory_mode
                )
                if published.failure:
                    return result_type.from_failure(published)
        return result_type.ok(tuple(change.path for change in pending))

    @staticmethod
    def _publish(change: m.Cli.FileChange, directory_mode: int) -> p.Result[bool]:
        if change.desired_content is None:
            return FlextCliUtilitiesFilesPart02.atomic_delete_binary_file_guarded(
                change.before,
            )
        before = change.before
        if before.parent_device is None:
            missing = [
                parent
                for parent in (change.path.parent, *change.path.parent.parents)
                if not parent.exists()
            ]
            try:
                for directory in reversed(missing):
                    directory.mkdir(mode=directory_mode)
                    directory.chmod(directory_mode)
            except OSError as exc:
                return r[bool].fail(
                    c.Cli.ERR_ENSURE_DIR_FAILED.format(error=exc), exception=exc
                )
            observed = FlextCliUtilitiesFilesPart03.atomic_read_binary_file_state(
                change.path,
            )
            if observed.failure:
                return r[bool].from_failure(observed)
            before = observed.value
        return FlextCliUtilitiesFilesPart02.atomic_write_binary_file_guarded(
            before,
            change.desired_content,
            permission_mode=change.desired_mode,
        )


__all__: list[str] = ["FlextCliUtilitiesFileChanges"]
