"""Generic guarded publication and file selection helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Literal

from flext_cli import c, m, p, r, t
from flext_cli._utilities._files.binary_reads import FlextCliUtilitiesFilesPart03
from flext_cli._utilities._files.writes import FlextCliUtilitiesFilesPart02
from flext_cli._utilities.runtime import FlextCliUtilitiesRuntime


class FlextCliUtilitiesFilesPart06:
    """Implementation part for FlextCliUtilitiesFilesPart06."""

    @staticmethod
    def atomic_create_binary_file_guarded(
        file_path: t.Cli.TextPath,
        data: bytes,
        *,
        permission_mode: int,
        owner_uid: int | None = None,
        max_bytes: int | None = None,
    ) -> p.Result[m.Cli.AtomicFileState]:
        """Create one absent file and return its authenticated published state.

        ``max_bytes`` rejects oversized ``data`` and ``owner_uid`` rejects a
        parent owned by another uid, both before any effect; the published leaf
        is re-read under the same guards.

        Returns:
            The resulting ``p.Result[m.Cli.AtomicFileState]``.

        """
        if max_bytes is not None and len(data) > max_bytes:
            return r[m.Cli.AtomicFileState].fail(
                f"atomic create content exceeds {max_bytes} bytes: {file_path}",
            )
        before = FlextCliUtilitiesFilesPart03.atomic_read_binary_file_state(
            file_path,
            required=False,
            owner_uid=owner_uid,
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
            owner_uid=owner_uid,
            max_bytes=max_bytes,
        )

    @staticmethod
    def atomic_verify_binary_file_states(
        expected_states: t.SequenceOf[m.Cli.AtomicFileState],
        *,
        nonsecret_source_paths: t.SequenceOf[Path] = (),
    ) -> p.Result[Literal[True]]:
        """Verify one coherent set of physical file states without reread fallback.

        Callers may explicitly attest nonsecret Python source paths for byte
        type, length and SHA256 failure diagnostics. Other files never expose
        payloads or digests, even if included in that allowlist.

        Returns:
            Exactly ``True`` on successful verification, otherwise a failed result.

        """
        by_path: t.MutableMappingKV[t.Cli.TextPath, m.Cli.AtomicFileState] = {}
        for expected in expected_states:
            existing = by_path.get(expected.path)
            if existing is not None and existing != expected:
                return r[Literal[True]].fail(
                    f"atomic source has conflicting snapshots: {expected.path}",
                )
            by_path[expected.path] = expected
        for expected in by_path.values():
            observed = FlextCliUtilitiesFilesPart03.atomic_read_binary_file_state(
                expected.path,
            )
            if observed.failure:
                return r[Literal[True]].from_failure(observed)
            if observed.value != expected:
                source_path = Path(expected.path)
                diagnostics = (
                    FlextCliUtilitiesFilesPart06._content_diagnostic(
                        "expected", expected.content
                    )
                    + FlextCliUtilitiesFilesPart06._content_diagnostic(
                        "observed", observed.value.content
                    )
                    if source_path in nonsecret_source_paths
                    and source_path.suffix in {".py", ".pyi"}
                    else ""
                )
                return r[Literal[True]].fail(
                    f"atomic source changed: {expected.path}; "
                    f"content_changed={observed.value.content != expected.content}; "
                    f"same_model_type={type(observed.value) is type(expected)}; "
                    f"expected={expected.model_dump(exclude={'content'})}; "
                    f"observed={observed.value.model_dump(exclude={'content'})}"
                    f"{diagnostics}"
                )
        return r[Literal[True]].ok(value=True)

    @staticmethod
    def _content_diagnostic(label: str, content: bytes | None) -> str:
        """Describe one attested source payload by type, length and digest only.

        Returns:
            The diagnostic suffix for ``label``.

        """
        digest = (
            FlextCliUtilitiesFilesPart03.sha256_bytes(content)
            if content is not None
            else None
        )
        length = len(content) if content is not None else None
        return (
            f"; {label}_content_type={type(content).__name__}"
            f"; {label}_content_length={length}"
            f"; {label}_content_sha256={digest}"
        )

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
        # Extend, never replace: the caller's git controls (ceiling
        # directories, global config, credential helpers) must survive the
        # probe — replacing the environment silently re-scopes worktree
        # discovery into whatever directory tree hosts the process.
        probe = FlextCliUtilitiesRuntime.run_bytes(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=scope,
            timeout=c.DEFAULT_TIMEOUT_SECONDS,
            options=m.Cli.ProcessOptions(
                env={**os.environ, "LC_ALL": "C"},
            ),
        )
        if probe.failure:
            return result.from_failure(probe)
        outcome = probe.value.outcome
        if outcome.timed_out or outcome.forwarded_signal is not None:
            return result.fail(f"Git worktree probe interrupted: {scope}")
        if outcome.raw_return_code == c.Cli.EXIT_CODE_SUCCESS:
            listed = FlextCliUtilitiesFilesPart06._files_git_candidates(
                scope,
                worktree_status=probe.value.stdout,
            )
            if listed.failure:
                return result.from_failure(listed)
            candidates = listed.value
        elif (
            outcome.raw_return_code == c.Cli.GIT_NOT_A_REPOSITORY_EXIT_CODE
            and b"not a git repository" in probe.value.stderr
        ):
            candidates = list(scope.rglob("*"))
        else:
            return result.fail(
                probe.value.stderr.decode(c.DEFAULT_ENCODING, errors="strict"),
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

    @staticmethod
    def _files_git_candidates(
        scope: Path,
        *,
        worktree_status: bytes,
    ) -> p.Result[t.SequenceOf[Path]]:
        """Read Git-visible candidates after a successful worktree probe.

        Returns:
            Git-visible paths or the original probe/listing failure.

        """
        result = r[t.SequenceOf[Path]]
        if worktree_status.strip() != b"true":
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
                listing.stderr.decode(c.DEFAULT_ENCODING, errors="strict"),
            )
        return result.ok([
            scope / relative.decode(c.DEFAULT_ENCODING, errors="strict")
            for relative in listing.stdout.split(b"\0")
            if relative
        ])


__all__: list[str] = ["FlextCliUtilitiesFilesPart06"]
