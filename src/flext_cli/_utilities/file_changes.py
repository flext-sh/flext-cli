"""Publish planned file changes for every engine through one shared owner.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from filelock import FileLock

from flext_cli import c, m, p, r, t
from flext_cli._utilities._files.flextcliutilitiesfiles_part_02 import (
    FlextCliUtilitiesFilesPart02,
)
from flext_cli._utilities._files.flextcliutilitiesfiles_part_03 import (
    FlextCliUtilitiesFilesPart03,
)
from flext_cli._utilities._files.flextcliutilitiesfiles_part_06 import (
    FlextCliUtilitiesFilesPart06,
)


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
    def publish_file_changes(
        changes: t.SequenceOf[m.Cli.FileChange],
        *,
        lock_path: Path,
    ) -> p.Result[t.VariadicTuple[Path]]:
        """Verify every observed state, then write or delete each changed file.

        No effect happens unless every destination still matches its observed
        state. Unchanged files are skipped; missing parents are created.

        Returns:
            The paths actually written or deleted, or the first failure.

        """
        result_type = r[tuple[Path, ...]]
        pending = tuple(
            change
            for change in changes
            if change.desired_content != change.before.content
            or (
                change.desired_mode is not None
                and change.desired_mode != change.before.mode
            )
        )
        with FlextCliUtilitiesFileChanges.file_changes_lock(lock_path):
            verified = FlextCliUtilitiesFilesPart06.atomic_verify_binary_file_states(
                tuple(change.before for change in pending),
            )
            if verified.failure:
                return result_type.from_failure(verified)
            for change in pending:
                published = FlextCliUtilitiesFileChanges._publish(change)
                if published.failure:
                    return result_type.from_failure(published)
        return result_type.ok(tuple(change.path for change in pending))

    @staticmethod
    def _publish(change: m.Cli.FileChange) -> p.Result[bool]:
        if change.desired_content is None:
            return FlextCliUtilitiesFilesPart02.atomic_delete_binary_file_guarded(
                change.before,
            )
        before = change.before
        if before.parent_device is None:
            created = FlextCliUtilitiesFilesPart02.ensure_dir(change.path.parent)
            if created.failure:
                return r[bool].from_failure(created)
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
