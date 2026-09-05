"""No-clobber publication contract for staged empty directories."""

from __future__ import annotations

from pathlib import Path

from flext_cli import m
from flext_tests import tm
from tests import u


class TestsAtomicDirectoryPublish:
    """Prove staged directory publication preserves identities and names."""

    def test_publish_moves_exact_empty_inode_across_parents(
        self, tmp_path: Path
    ) -> None:
        """Return destination identity while preserving every staged leaf field."""
        source_parent = tmp_path / "source"
        destination_parent = tmp_path / "destination"
        source_parent.mkdir()
        destination_parent.mkdir()
        staged_path = source_parent / "staged"
        staged_path.mkdir()
        staged_path.chmod(0o750)
        destination_path = destination_parent / "published"
        destination = self._snapshot(destination_path)
        staged = self._snapshot(staged_path, required=True)

        result = u.Cli.atomic_publish_staged_empty_directory_guarded(
            destination, staged
        )

        tm.ok(result)
        expected_parent = destination_parent.lstat()
        tm.that(result.value.path, eq=destination_path)
        tm.that(result.value.parent_device, eq=expected_parent.st_dev)
        tm.that(result.value.parent_inode, eq=expected_parent.st_ino)
        for field in (
            "mode",
            "device",
            "inode",
            "link_count",
            "file_attributes",
            "reparse_tag",
        ):
            tm.that(getattr(result.value, field), eq=getattr(staged, field))
        tm.that(destination_path.is_dir(), eq=True)
        tm.that(staged_path.exists(), eq=False)

    def test_publish_rejects_staged_replacement_inode(self, tmp_path: Path) -> None:
        """Never move another empty inode that reuses the staged pathname."""
        staged_path = tmp_path / "staged"
        destination_path = tmp_path / "destination"
        staged_path.mkdir()
        destination = self._snapshot(destination_path)
        staged = self._snapshot(staged_path, required=True)
        original_path = tmp_path / "original"
        staged_path.rename(original_path)
        staged_path.mkdir()
        if staged.mode is None:
            message = "required staged snapshot unexpectedly absent"
            raise AssertionError(message)
        staged_path.chmod(staged.mode)

        result = u.Cli.atomic_publish_staged_empty_directory_guarded(
            destination, staged
        )

        tm.fail(result)
        tm.that(destination_path.exists(), eq=False)
        tm.that(staged_path.is_dir(), eq=True)
        tm.that(original_path.is_dir(), eq=True)

    def test_publish_rejects_late_staged_content(self, tmp_path: Path) -> None:
        """Preserve staging and destination absence when staging stops being empty."""
        staged_path = tmp_path / "staged"
        destination_path = tmp_path / "destination"
        staged_path.mkdir()
        destination = self._snapshot(destination_path)
        staged = self._snapshot(staged_path, required=True)
        child = staged_path / "late"
        child.write_bytes(b"content")

        result = u.Cli.atomic_publish_staged_empty_directory_guarded(
            destination, staged
        )

        tm.fail(result)
        tm.that(destination_path.exists(), eq=False)
        tm.that(staged_path.is_dir(), eq=True)
        tm.that(child.read_bytes(), eq=b"content")

    @staticmethod
    def _snapshot(path: Path, *, required: bool = False) -> m.Cli.AtomicDirectoryState:
        result = u.Cli.atomic_read_empty_directory_state(path, required=required)
        tm.ok(result)
        return result.value


__all__: list[str] = ["TestsAtomicDirectoryPublish"]
