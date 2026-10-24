"""Behavioral tests for the shared ``u.Cli.publish_file_changes`` owner.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from tests import m, tm, u


class TestsFlextCliFileChanges:
    """Observe publication through the public ``u.Cli``/``m.Cli`` surface."""

    @staticmethod
    def _change(path: Path, content: bytes | None) -> m.Cli.FileChange:
        return m.Cli.FileChange(
            path=path,
            before=tm.ok(u.Cli.atomic_read_binary_file_state(path)),
            desired_content=content,
            desired_mode=None if content is None else 0o644,
        )

    @staticmethod
    def test_create_replace_skip_and_delete(tmp_path: Path) -> None:
        """Changed files are published, unchanged ones skipped, deletes applied."""
        lock = tmp_path / ".lock"
        target = tmp_path / "nested" / "file.txt"
        change = TestsFlextCliFileChanges._change
        tm.that(
            tm.ok(u.Cli.publish_file_changes([change(target, b"one")], lock_path=lock)),
            eq=(target,),
        )
        tm.that(target.read_bytes(), eq=b"one")
        tm.ok(u.Cli.publish_file_changes([change(target, b"two")], lock_path=lock))
        tm.that(target.read_bytes(), eq=b"two")
        tm.that(
            tm.ok(u.Cli.publish_file_changes([change(target, b"two")], lock_path=lock)),
            eq=(),
        )
        tm.ok(u.Cli.publish_file_changes([change(target, None)], lock_path=lock))
        tm.that(target.exists(), eq=False)

    @staticmethod
    def test_stale_observation_fails_before_any_effect(tmp_path: Path) -> None:
        """A destination changed after planning blocks the whole batch."""
        lock = tmp_path / ".lock"
        first = tmp_path / "first.txt"
        second = tmp_path / "second.txt"
        second.write_bytes(b"planned")
        change = TestsFlextCliFileChanges._change
        batch = [change(first, b"new"), change(second, b"replacement")]
        second.write_bytes(b"foreign")
        tm.fail(u.Cli.publish_file_changes(batch, lock_path=lock))
        tm.that(first.exists(), eq=False)
        tm.that(second.read_bytes(), eq=b"foreign")
