"""Publish planned file changes for every engine through one shared owner.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from filelock import FileLock

from flext_cli import c, m, p, r, t
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
        changes: t.SequenceOf[m.Cli.FileChange],
    ) -> t.VariadicTuple[m.Cli.FileChange]:
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
        changes: t.SequenceOf[m.Cli.FileChange],
        *,
        lock_path: Path,
        directory_mode: int = c.Cli.FILE_CHANGES_DIRECTORY_MODE,
    ) -> p.Result[t.VariadicTuple[Path]]:
        """Verify every observed state, then write or delete each changed file.

        No effect happens unless every destination still matches its observed
        state. Unchanged files are skipped; missing parents are created with
        exactly ``directory_mode``.

        Returns:
            The paths actually written or deleted, or the first failure.

        """
        result_type = r[tuple[Path, ...]]
        pending = FlextCliUtilitiesFileChanges.pending_file_changes(changes)
        with FlextCliUtilitiesFileChanges.file_changes_lock(lock_path):
            verified = FlextCliUtilitiesFilesPart06.atomic_verify_binary_file_states(
                tuple(change.before for change in pending),
            )
            if verified.failure:
                return result_type.from_failure(verified)
            for change in pending:
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
