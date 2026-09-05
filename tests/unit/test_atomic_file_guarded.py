"""Public complete-state precondition contract for atomic text publication."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import cli, m
from flext_tests import tm
from tests import u

if TYPE_CHECKING:
    from pathlib import Path


class TestsAtomicFileGuarded:
    """Observable guarded-write behavior through public Flext CLI surfaces."""

    def test_state_diff_detects_content_and_mode_changes(self, tmp_path: Path) -> None:
        """Compare desired leaf state through the public utility facade."""
        path = tmp_path / "atomic.txt"
        path.write_text("observed", encoding="utf-8")
        before = self._snapshot(path, required=True)

        tm.that(
            u.Cli.atomic_file_state_differs(
                before, desired_content=before.content, desired_mode=before.mode
            ),
            eq=False,
        )
        tm.that(
            u.Cli.atomic_file_state_differs(
                before, desired_content=b"desired", desired_mode=before.mode
            ),
            eq=True,
        )

    def test_matching_content_is_replaced(self, tmp_path: Path) -> None:
        """Publish when the complete physical version matches."""
        path = tmp_path / "atomic.txt"
        path.write_text("before", encoding="utf-8")
        before = self._snapshot(path, required=True)

        result = u.Cli.atomic_write_text_file_guarded(before, "after")

        tm.ok(result)
        tm.that(path.read_text(encoding="utf-8"), eq="after")

    def test_empty_content_differs_from_absence(self, tmp_path: Path) -> None:
        """Treat empty bytes as an existing version rather than an absence marker."""
        path = tmp_path / "atomic.txt"
        path.write_bytes(b"")
        before = self._snapshot(path, required=True)

        result = u.Cli.atomic_write_text_file_guarded(before, "after")

        tm.ok(result)
        tm.that(path.read_text(encoding="utf-8"), eq="after")

    def test_crlf_precondition_compares_raw_bytes(self, tmp_path: Path) -> None:
        """Keep platform newline translation outside the version contract."""
        path = tmp_path / "atomic.txt"
        path.write_bytes(b"before\r\n")
        before = self._snapshot(path, required=True)

        result = u.Cli.atomic_write_text_file_guarded(before, "after\n")

        tm.ok(result)
        tm.that(path.read_bytes(), eq=b"after\n")

    def test_stale_content_is_preserved(self, tmp_path: Path) -> None:
        """Preserve a destination changed after the caller formed its plan."""
        path = tmp_path / "atomic.txt"
        path.write_text("planned", encoding="utf-8")
        before = self._snapshot(path, required=True)
        path.write_text("concurrent", encoding="utf-8")

        result = u.Cli.atomic_write_text_file_guarded(before, "replacement")

        tm.fail(result)
        tm.that(path.read_text(encoding="utf-8"), eq="concurrent")

    def test_none_creates_only_an_absent_destination(self, tmp_path: Path) -> None:
        """Create only when the complete planned state records absence."""
        path = tmp_path / "atomic.txt"
        before = self._snapshot(path)

        result = u.Cli.atomic_write_text_file_guarded(before, "created")

        tm.ok(result)
        tm.that(path.read_text(encoding="utf-8"), eq="created")

    def test_none_rejects_an_existing_destination(self, tmp_path: Path) -> None:
        """Do not overwrite a file that appeared after an absence plan."""
        path = tmp_path / "atomic.txt"
        before = self._snapshot(path)
        path.write_text("concurrent", encoding="utf-8")

        result = u.Cli.atomic_write_text_file_guarded(before, "replacement")

        tm.fail(result)
        tm.that(path.read_text(encoding="utf-8"), eq="concurrent")

    def test_expected_file_must_still_exist(self, tmp_path: Path) -> None:
        """Do not recreate a file removed after planning."""
        path = tmp_path / "atomic.txt"
        path.write_text("planned", encoding="utf-8")
        before = self._snapshot(path, required=True)
        path.unlink()

        result = u.Cli.atomic_write_text_file_guarded(before, "replacement")

        tm.fail(result)
        tm.that(path.exists(), eq=False)

    def test_missing_parent_is_not_created(self, tmp_path: Path) -> None:
        """Leave no partial directory tree for a guarded-write failure."""
        parent = tmp_path / "missing"
        parent.mkdir()
        path = parent / "atomic.txt"
        before = self._snapshot(path)
        parent.rmdir()

        result = u.Cli.atomic_write_text_file_guarded(before, "replacement")

        tm.fail(result)
        tm.that(parent.exists(), eq=False)

    def test_absent_snapshot_rejects_replaced_parent(self, tmp_path: Path) -> None:
        """Never create a file under a new parent that reused the planned path."""
        parent = tmp_path / "parent"
        parent.mkdir()
        path = parent / "atomic.txt"
        before = self._snapshot(path)
        original = tmp_path / "original-parent"
        parent.rename(original)
        parent.mkdir()

        result = u.Cli.atomic_write_text_file_guarded(before, "replacement")

        tm.fail(result)
        tm.that(path.exists(), eq=False)
        tm.that((original / path.name).exists(), eq=False)

    def test_aliased_parent_is_rejected(self, tmp_path: Path) -> None:
        """Do not publish through a parent directory alias."""
        linked_parent = tmp_path / "linked"
        linked_parent.mkdir()
        target = linked_parent / "atomic.txt"
        target.write_text("before", encoding="utf-8")
        before = self._snapshot(target, required=True)
        owner = tmp_path / "owner"
        linked_parent.rename(owner)
        linked_parent.symlink_to(owner, target_is_directory=True)

        result = u.Cli.atomic_write_text_file_guarded(before, "after")

        tm.fail(result)
        tm.that((owner / "atomic.txt").read_text(encoding="utf-8"), eq="before")

    def test_service_facade_enforces_the_same_precondition(
        self, tmp_path: Path
    ) -> None:
        """Expose the guarded contract through the canonical service facade."""
        target = tmp_path / "service-atomic.txt"
        target.write_text("before", encoding="utf-8")
        before = self._snapshot(target, required=True)

        result = cli.atomic_write_text_file_guarded(before, "after")

        tm.ok(result)
        tm.that(target.read_text(encoding="utf-8"), eq="after")

    @staticmethod
    def _snapshot(path: Path, *, required: bool = False) -> m.Cli.AtomicFileState:
        result = u.Cli.atomic_read_binary_file_state(path, required=required)
        tm.ok(result)
        return result.value
