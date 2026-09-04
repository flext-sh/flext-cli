"""Physical-identity contracts for public atomic file operations."""

from __future__ import annotations

from pathlib import Path

import pytest

from flext_tests import tm
from tests import u


class TestsAtomicFileIdentity:
    """Prove callers cannot authorize effects with only matching content."""

    def test_relative_write_fails_before_parent_creation(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Reject a relative identity without creating its directory tree."""
        monkeypatch.chdir(tmp_path)
        destination = Path("relative") / "atomic.txt"

        result = u.Cli.atomic_write_text_file(destination, "content")

        tm.fail(result)
        tm.that(destination.parent.exists(), eq=False)

    def test_delete_consumes_complete_snapshot(self, tmp_path: Path) -> None:
        """Delete the same physical version returned by the snapshot owner."""
        destination = tmp_path / "atomic.bin"
        destination.write_bytes(b"content")
        snapshot_result = u.Cli.atomic_read_binary_file_state(
            destination, required=True
        )
        tm.ok(snapshot_result)
        snapshot = snapshot_result.value
        host_state = destination.lstat()
        tm.that(snapshot.link_count, eq=1)
        tm.that(
            snapshot.file_attributes, eq=getattr(host_state, "st_file_attributes", None)
        )
        tm.that(snapshot.reparse_tag, eq=getattr(host_state, "st_reparse_tag", None))

        result = u.Cli.atomic_delete_binary_file_guarded(snapshot)

        tm.ok(result)
        tm.that(destination.exists(), eq=False)

    def test_delete_rejects_replacement_with_same_bytes_and_mode(
        self, tmp_path: Path
    ) -> None:
        """Treat a new inode as stale even when bytes and mode are unchanged."""
        destination = tmp_path / "atomic.bin"
        destination.write_bytes(b"content")
        snapshot_result = u.Cli.atomic_read_binary_file_state(
            destination, required=True
        )
        tm.ok(snapshot_result)
        snapshot = snapshot_result.value
        if snapshot.content is None or snapshot.mode is None:
            message = "required atomic snapshot was absent"
            raise AssertionError(message)
        replacement = tmp_path / "replacement.bin"
        replacement.write_bytes(snapshot.content)
        replacement.chmod(snapshot.mode)
        Path(replacement).replace(destination)

        result = u.Cli.atomic_delete_binary_file_guarded(snapshot)

        tm.fail(result)
        tm.that(destination.read_bytes(), eq=b"content")

    def test_delete_rejects_link_count_changed_after_snapshot(
        self, tmp_path: Path
    ) -> None:
        """Reject a hard link added after the caller observed unique ownership."""
        destination = tmp_path / "atomic.bin"
        destination.write_bytes(b"content")
        snapshot_result = u.Cli.atomic_read_binary_file_state(
            destination, required=True
        )
        tm.ok(snapshot_result)
        alias = tmp_path / "alias.bin"
        alias.hardlink_to(destination)

        result = u.Cli.atomic_delete_binary_file_guarded(snapshot_result.value)

        tm.fail(result)
        tm.that(destination.read_bytes(), eq=b"content")
        tm.that(alias.read_bytes(), eq=b"content")

    def test_guarded_write_rejects_link_count_changed_after_snapshot(
        self, tmp_path: Path
    ) -> None:
        """Require unique ownership from plan through binary publication."""
        destination = tmp_path / "atomic.bin"
        destination.write_bytes(b"before")
        snapshot_result = u.Cli.atomic_read_binary_file_state(
            destination, required=True
        )
        tm.ok(snapshot_result)
        snapshot = snapshot_result.value
        if snapshot.mode is None:
            message = "required atomic snapshot was absent"
            raise AssertionError(message)
        alias = tmp_path / "alias.bin"
        alias.hardlink_to(destination)

        result = u.Cli.atomic_write_binary_file_guarded(
            snapshot, b"after", permission_mode=snapshot.mode
        )

        tm.fail(result)
        tm.that(destination.read_bytes(), eq=b"before")
        tm.that(alias.read_bytes(), eq=b"before")

    def test_staged_publish_preserves_complete_physical_state(
        self, tmp_path: Path
    ) -> None:
        """Move the authenticated staged inode and every available host field."""
        destination = tmp_path / "published.bin"
        staged = tmp_path / "staged.bin"
        staged.write_bytes(b"content")
        destination_result = u.Cli.atomic_read_binary_file_state(destination)
        staged_result = u.Cli.atomic_read_binary_file_state(staged, required=True)
        tm.ok(destination_result)
        tm.ok(staged_result)

        result = u.Cli.atomic_publish_staged_binary_file_guarded(
            destination_result.value, staged_result.value
        )

        tm.ok(result)
        tm.that(result.value.inode, eq=staged_result.value.inode)
        tm.that(result.value.link_count, eq=1)
        tm.that(result.value.file_attributes, eq=staged_result.value.file_attributes)
        tm.that(result.value.reparse_tag, eq=staged_result.value.reparse_tag)
        tm.that(destination.read_bytes(), eq=b"content")
        tm.that(staged.exists(), eq=False)

    def test_staged_publish_rejects_new_hard_link(self, tmp_path: Path) -> None:
        """Reject staging whose unique-link invariant changed after snapshot."""
        destination = tmp_path / "published.bin"
        staged = tmp_path / "staged.bin"
        staged.write_bytes(b"content")
        destination_result = u.Cli.atomic_read_binary_file_state(destination)
        staged_result = u.Cli.atomic_read_binary_file_state(staged, required=True)
        tm.ok(destination_result)
        tm.ok(staged_result)
        alias = tmp_path / "alias.bin"
        alias.hardlink_to(staged)

        result = u.Cli.atomic_publish_staged_binary_file_guarded(
            destination_result.value, staged_result.value
        )

        tm.fail(result)
        tm.that(destination.exists(), eq=False)
        tm.that(staged.read_bytes(), eq=b"content")
        tm.that(alias.read_bytes(), eq=b"content")


__all__: list[str] = ["TestsAtomicFileIdentity"]
