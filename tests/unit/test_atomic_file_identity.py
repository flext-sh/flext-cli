"""Physical-identity contracts for public atomic file operations."""

from __future__ import annotations

import sys
from pathlib import Path

from flext_cli import m
from flext_tests import tm
from tests import u


class TestsAtomicFileIdentity:
    """Prove callers cannot authorize effects with only matching content."""

    def test_publication_unchanged_requires_equal_bytes_and_mode(
        self, tmp_path: Path
    ) -> None:
        """Treat matching bytes with different permissions as a real change."""
        destination = tmp_path / "live.bin"
        staged = tmp_path / "staged.bin"
        destination.write_bytes(b"content")
        staged.write_bytes(b"content")
        destination.chmod(0o600)
        staged.chmod(0o640)
        before = u.Cli.atomic_read_binary_file_state(destination, required=True)
        replacement = u.Cli.atomic_read_binary_file_state(staged, required=True)
        tm.ok(before)
        tm.ok(replacement)
        publication = m.Cli.AtomicFilePublication(
            before=before.value, replacement=replacement.value
        )

        tm.that(u.Cli.atomic_file_publication_is_unchanged(publication), eq=False)

        staged.chmod(0o600)
        identical = u.Cli.atomic_read_binary_file_state(staged, required=True)
        tm.ok(identical)
        tm.that(
            u.Cli.atomic_file_publication_is_unchanged(
                m.Cli.AtomicFilePublication(
                    before=before.value, replacement=identical.value
                )
            ),
            eq=True,
        )

    def test_exclusive_create_returns_exact_published_state(
        self, tmp_path: Path
    ) -> None:
        """Create one absent binary file with its requested bytes and mode."""
        destination = tmp_path / "created.bin"

        result = u.Cli.atomic_create_binary_file_guarded(
            destination, b"content", permission_mode=0o600
        )

        tm.ok(result)
        tm.that(result.value.content, eq=b"content")
        tm.that(result.value.mode, eq=0o600)
        tm.that(destination.read_bytes(), eq=b"content")

    def test_exclusive_create_rejects_existing_destination(
        self, tmp_path: Path
    ) -> None:
        """Preserve an existing file rather than treating create as overwrite."""
        destination = tmp_path / "existing.bin"
        destination.write_bytes(b"before")

        result = u.Cli.atomic_create_binary_file_guarded(
            destination, b"after", permission_mode=0o600
        )

        tm.fail(result)
        tm.that(destination.read_bytes(), eq=b"before")

    def test_publication_applies_authenticated_staged_replacement(
        self, tmp_path: Path
    ) -> None:
        """Replace one exact live state with one exact staged state."""
        destination = tmp_path / "published.bin"
        staged = tmp_path / "staged.bin"
        destination.write_bytes(b"before")
        before = u.Cli.atomic_read_binary_file_state(destination, required=True)
        replacement = u.Cli.atomic_create_binary_file_guarded(
            staged, b"after", permission_mode=0o640
        )
        tm.ok(before)
        tm.ok(replacement)

        result = u.Cli.atomic_apply_file_publication_guarded(
            m.Cli.AtomicFilePublication(
                before=before.value, replacement=replacement.value
            )
        )

        tm.ok(result)
        tm.that(result.value.content, eq=b"after")
        tm.that(result.value.mode, eq=0o640)
        tm.that(destination.read_bytes(), eq=b"after")
        tm.that(staged.exists(), eq=False)

    def test_publication_applies_authenticated_tombstone(self, tmp_path: Path) -> None:
        """Delete one exact live state when its replacement is absent."""
        destination = tmp_path / "deleted.bin"
        destination.write_bytes(b"content")
        before = u.Cli.atomic_read_binary_file_state(destination, required=True)
        tombstone = u.Cli.atomic_read_binary_file_state(tmp_path / "tombstone")
        tm.ok(before)
        tm.ok(tombstone)

        result = u.Cli.atomic_apply_file_publication_guarded(
            m.Cli.AtomicFilePublication(
                before=before.value, replacement=tombstone.value
            )
        )

        tm.ok(result)
        tm.that(result.value.content, is_=None)
        tm.that(destination.exists(), eq=False)

    def test_relative_write_fails_before_parent_creation(self, tmp_path: Path) -> None:
        """Reject a relative identity without creating its directory tree."""
        destination = Path("relative") / "atomic.txt"
        script = (
            "from pathlib import Path\n"
            "from flext_cli import u\n"
            "destination = Path('relative') / 'atomic.txt'\n"
            "result = u.Cli.atomic_write_text_file(destination, 'content')\n"
            "raise SystemExit(0 if result.failure and "
            "not destination.parent.exists() else 1)\n"
        )

        result = u.Cli.run_raw((sys.executable, "-c", script), cwd=tmp_path)

        tm.ok(result)
        tm.that(result.value.exit_code, eq=0)
        tm.that((tmp_path / destination.parent).exists(), eq=False)

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
        parent_state = tmp_path.lstat()
        tm.that(snapshot.parent_device, eq=parent_state.st_dev)
        tm.that(snapshot.parent_inode, eq=parent_state.st_ino)
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
