"""Generic guarded publication and file selection helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

from flext_cli import c, m, p, r, t

from ..runtime import FlextCliUtilitiesRuntime
from .flextcliutilitiesfiles_part_02 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart02,
)
from .flextcliutilitiesfiles_part_03 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart03,
)


class FlextCliUtilitiesFiles:
    """Implementation part for FlextCliUtilitiesFiles."""

    @staticmethod
    def atomic_file_publication_is_unchanged(
        publication: m.Cli.AtomicFilePublication,
    ) -> bool:
        """Return whether staged bytes and permissions equal the live state.

        Returns:
            Whether staged bytes and permissions equal the live state.

        """
        return (
            publication.before.content == publication.replacement.content
            and publication.before.mode == publication.replacement.mode
        )

    @staticmethod
    def atomic_create_binary_file_guarded(
        file_path: t.Cli.TextPath,
        data: bytes,
        *,
        permission_mode: int,
    ) -> p.Result[m.Cli.AtomicFileState]:
        """Create one absent file and return its authenticated published state.

        Returns:
            The resulting ``p.Result[m.Cli.AtomicFileState]``.

        """
        before = FlextCliUtilitiesFilesPart03.atomic_read_binary_file_state(
            file_path,
            required=False,
        )
        if before.failure:
            return r[m.Cli.AtomicFileState].from_failure(before)
        if before.value.content is not None:
            return r[m.Cli.AtomicFileState].fail(
                f"atomic create destination already exists: {before.value.path}",
            )
        written = FlextCliUtilitiesFilesPart02.atomic_write_binary_file_guarded(
            before.value,
            data,
            permission_mode=permission_mode,
        )
        if written.failure:
            return r[m.Cli.AtomicFileState].from_failure(written)
        return FlextCliUtilitiesFilesPart03.atomic_read_binary_file_state(
            before.value.path,
            required=True,
        )

    @staticmethod
    def atomic_apply_file_publication_guarded(
        publication: m.Cli.AtomicFilePublication,
    ) -> p.Result[m.Cli.AtomicFileState]:
        """Apply one exact staged replacement or tombstone under caller lock.

        Returns:
            The resulting ``p.Result[m.Cli.AtomicFileState]``.

        """
        before = publication.before
        replacement = publication.replacement
        if replacement.content is None:
            if before.content is None:
                return r[m.Cli.AtomicFileState].ok(before)
            removed = FlextCliUtilitiesFilesPart02.atomic_delete_binary_file_guarded(
                before,
            )
            if removed.failure:
                return r[m.Cli.AtomicFileState].from_failure(removed)
            return FlextCliUtilitiesFilesPart03.atomic_read_binary_file_state(
                before.path,
                required=False,
            )
        return FlextCliUtilitiesFilesPart03.atomic_publish_staged_binary_file_guarded(
            before,
            replacement,
        )

    @staticmethod
    def atomic_verify_binary_file_states(
        expected_states: t.SequenceOf[m.Cli.AtomicFileState],
    ) -> p.Result[bool]:
        """Verify one coherent set of physical file states without reread fallback.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        by_path: dict[t.Cli.TextPath, m.Cli.AtomicFileState] = {}
        for expected in expected_states:
            existing = by_path.get(expected.path)
            if existing is not None and existing != expected:
                return r[bool].fail(
                    f"atomic source has conflicting snapshots: {expected.path}",
                )
            by_path[expected.path] = expected
        for expected in by_path.values():
            current = FlextCliUtilitiesFilesPart03.atomic_read_binary_file_state(
                expected.path,
                required=expected.content is not None,
            )
            if current.failure:
                return r[bool].from_failure(current)
            if current.value != expected:
                return r[bool].fail(f"atomic source changed: {expected.path}")
        return r[bool].ok(True)

    @staticmethod
    def files_matching(
        root: Path,
        *,
        includes: t.StrSequence,
        excludes: t.StrSequence = (),
    ) -> p.Result[t.SequenceOf[Path]]:
        """Select Git-visible files under ``root``: tracked, untracked, never ignored.

        Outside a Git worktree every file on disk is a candidate. Patterns match the
        POSIX path relative to ``root``; an empty ``includes`` selects every file.

        Returns:
            The resulting ``p.Result[t.SequenceOf[Path]]``.

        """
        result = r[t.SequenceOf[Path]]
        if not root.is_dir():
            return result.fail(f"file selection root is not a directory: {root}")
        scope = root.resolve()
        probe = FlextCliUtilitiesRuntime.run_bytes(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=scope,
            timeout=c.DEFAULT_TIMEOUT_SECONDS,
            env={"LC_ALL": "C"},
        )
        if probe.failure:
            return result.from_failure(probe)
        outcome = probe.value.outcome
        if outcome.timed_out or outcome.forwarded_signal is not None:
            return result.fail(f"Git worktree probe interrupted: {scope}")
        if outcome.raw_return_code == c.Cli.EXIT_CODE_SUCCESS:
            if probe.value.stdout.strip() != b"true":
                return result.fail(f"file selection root is not in a worktree: {scope}")
            listed = FlextCliUtilitiesRuntime.run_bytes(
                ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                cwd=scope,
                timeout=c.DEFAULT_TIMEOUT_SECONDS,
            )
            if listed.failure:
                return result.from_failure(listed)
            listing = listed.value
            if (
                listing.outcome.raw_return_code != c.Cli.EXIT_CODE_SUCCESS
                or listing.outcome.timed_out
                or listing.outcome.forwarded_signal is not None
            ):
                return result.fail(
                    listing.stderr.decode(c.Cli.ENCODING_DEFAULT, errors="strict"),
                )
            candidates = [
                scope / relative.decode(c.Cli.ENCODING_DEFAULT, errors="strict")
                for relative in listing.stdout.split(b"\0")
                if relative
            ]
        elif (
            outcome.raw_return_code == c.Cli.GIT_NOT_A_REPOSITORY_EXIT_CODE
            and b"not a git repository" in probe.value.stderr
        ):
            candidates = list(scope.rglob("*"))
        else:
            return result.fail(
                probe.value.stderr.decode(c.Cli.ENCODING_DEFAULT, errors="strict"),
            )

        def selected(path: Path) -> bool:
            relative = path.relative_to(scope).as_posix()
            return (
                path.is_file()
                and (
                    not includes
                    or any(fnmatch.fnmatchcase(relative, rule) for rule in includes)
                )
                and not any(fnmatch.fnmatchcase(relative, rule) for rule in excludes)
            )

        return result.ok(sorted(path for path in candidates if selected(path)))


__all__: list[str] = ["FlextCliUtilitiesFiles"]
