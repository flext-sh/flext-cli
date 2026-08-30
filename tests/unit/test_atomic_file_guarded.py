"""Public raw-byte precondition contract for atomic text publication."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import cli
from flext_tests import tm
from tests import u

if TYPE_CHECKING:
    from pathlib import Path


class TestsAtomicFileGuarded:
    """Observable guarded-write behavior through public Flext CLI surfaces."""

    def test_matching_content_is_replaced(self, tmp_path: Path) -> None:
        """Publish when the explicit raw-byte version matches."""
        path = tmp_path / "atomic.txt"
        path.write_text("before", encoding="utf-8")

        result = u.Cli.atomic_write_text_file_guarded(
            path, "after", expected_bytes=b"before"
        )

        tm.ok(result)
        tm.that(path.read_text(encoding="utf-8"), eq="after")

    def test_empty_content_differs_from_absence(self, tmp_path: Path) -> None:
        """Treat empty bytes as an existing version rather than an absence marker."""
        path = tmp_path / "atomic.txt"
        path.write_bytes(b"")

        result = u.Cli.atomic_write_text_file_guarded(path, "after", expected_bytes=b"")

        tm.ok(result)
        tm.that(path.read_text(encoding="utf-8"), eq="after")

    def test_crlf_precondition_compares_raw_bytes(self, tmp_path: Path) -> None:
        """Keep platform newline translation outside the version contract."""
        path = tmp_path / "atomic.txt"
        path.write_bytes(b"before\r\n")

        result = u.Cli.atomic_write_text_file_guarded(
            path, "after\n", expected_bytes=b"before\r\n"
        )

        tm.ok(result)
        tm.that(path.read_bytes(), eq=b"after\n")

    def test_stale_content_is_preserved(self, tmp_path: Path) -> None:
        """Preserve a destination changed after the caller formed its plan."""
        path = tmp_path / "atomic.txt"
        path.write_text("concurrent", encoding="utf-8")

        result = u.Cli.atomic_write_text_file_guarded(
            path, "replacement", expected_bytes=b"planned"
        )

        tm.fail(result)
        tm.that(path.read_text(encoding="utf-8"), eq="concurrent")

    def test_none_creates_only_an_absent_destination(self, tmp_path: Path) -> None:
        """Use ``None`` as the explicit absence precondition."""
        path = tmp_path / "atomic.txt"

        result = u.Cli.atomic_write_text_file_guarded(
            path, "created", expected_bytes=None
        )

        tm.ok(result)
        tm.that(path.read_text(encoding="utf-8"), eq="created")

    def test_none_rejects_an_existing_destination(self, tmp_path: Path) -> None:
        """Do not overwrite a file that appeared after an absence plan."""
        path = tmp_path / "atomic.txt"
        path.write_text("concurrent", encoding="utf-8")

        result = u.Cli.atomic_write_text_file_guarded(
            path, "replacement", expected_bytes=None
        )

        tm.fail(result)
        tm.that(path.read_text(encoding="utf-8"), eq="concurrent")

    def test_expected_file_must_still_exist(self, tmp_path: Path) -> None:
        """Do not recreate a file removed after planning."""
        path = tmp_path / "atomic.txt"

        result = u.Cli.atomic_write_text_file_guarded(
            path, "replacement", expected_bytes=b"planned"
        )

        tm.fail(result)
        tm.that(path.exists(), eq=False)

    def test_missing_parent_is_not_created(self, tmp_path: Path) -> None:
        """Leave no partial directory tree for a guarded-write failure."""
        parent = tmp_path / "missing"

        result = u.Cli.atomic_write_text_file_guarded(
            parent / "atomic.txt", "replacement", expected_bytes=None
        )

        tm.fail(result)
        tm.that(parent.exists(), eq=False)

    def test_aliased_parent_is_rejected(self, tmp_path: Path) -> None:
        """Do not publish through a parent directory alias."""
        owner = tmp_path / "owner"
        owner.mkdir()
        target = owner / "atomic.txt"
        target.write_text("before", encoding="utf-8")
        linked_parent = tmp_path / "linked"
        linked_parent.symlink_to(owner, target_is_directory=True)

        result = u.Cli.atomic_write_text_file_guarded(
            linked_parent / "atomic.txt", "after", expected_bytes=b"before"
        )

        tm.fail(result)
        tm.that(target.read_text(encoding="utf-8"), eq="before")

    def test_service_facade_enforces_the_same_precondition(
        self, tmp_path: Path
    ) -> None:
        """Expose the guarded contract through the canonical service facade."""
        target = tmp_path / "service-atomic.txt"
        target.write_text("before", encoding="utf-8")

        result = cli.atomic_write_text_file_guarded(
            target, "after", expected_bytes=b"before"
        )

        tm.ok(result)
        tm.that(target.read_text(encoding="utf-8"), eq="after")
