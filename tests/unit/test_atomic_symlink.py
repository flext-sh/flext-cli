"""Real filesystem contracts for the public guarded symbolic-link facade."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from tests import u

if TYPE_CHECKING:
    from pathlib import Path


class TestsAtomicSymlink:
    """Guard link text and physical ownership independently of target existence."""

    def test_create_replace_and_delete_dangling_link(self, tmp_path: Path) -> None:
        path = tmp_path / "link"
        absent = tm.ok(u.Cli.atomic_read_symlink_state(path))
        tm.that(absent.target, eq=None)
        tm.ok(u.Cli.atomic_write_symlink_guarded(absent, "missing target"))
        before = tm.ok(u.Cli.atomic_read_symlink_state(path, required=True))
        tm.that(before.target, eq="missing target")
        tm.ok(u.Cli.atomic_write_symlink_guarded(before, "other missing target"))
        after = tm.ok(u.Cli.atomic_read_symlink_state(path, required=True))
        tm.that(after.target, eq="other missing target")
        tm.ok(u.Cli.atomic_delete_symlink_guarded(after))
        tm.that(path.is_symlink(), eq=False)
        tm.that(tuple(tmp_path.iterdir()), eq=())

    def test_same_target_is_noop(self, tmp_path: Path) -> None:
        path = tmp_path / "link"
        path.symlink_to("unresolved")
        before = tm.ok(u.Cli.atomic_read_symlink_state(path, required=True))
        tm.ok(u.Cli.atomic_write_symlink_guarded(before, "unresolved"))
        after = tm.ok(u.Cli.atomic_read_symlink_state(path, required=True))
        tm.that(after, eq=before)

    def test_delete_never_follows_target(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        target.write_bytes(b"preserved")
        path = tmp_path / "link"
        path.symlink_to(target)
        before = tm.ok(u.Cli.atomic_read_symlink_state(path, required=True))
        tm.ok(u.Cli.atomic_delete_symlink_guarded(before))
        tm.that(target.read_bytes(), eq=b"preserved")

    def test_changed_identity_with_same_text_is_preserved(self, tmp_path: Path) -> None:
        path = tmp_path / "link"
        path.symlink_to("missing")
        before = tm.ok(u.Cli.atomic_read_symlink_state(path, required=True))
        path.rename(tmp_path / "original")
        path.symlink_to("missing")
        tm.fail(u.Cli.atomic_write_symlink_guarded(before, "replacement"))
        tm.fail(u.Cli.atomic_delete_symlink_guarded(before))
        tm.that(str(path.readlink()), eq="missing")

    def test_absence_does_not_authorize_existing_file(self, tmp_path: Path) -> None:
        path = tmp_path / "link"
        before = tm.ok(u.Cli.atomic_read_symlink_state(path))
        path.write_bytes(b"concurrent")
        tm.fail(u.Cli.atomic_write_symlink_guarded(before, "replacement"))
        tm.that(path.read_bytes(), eq=b"concurrent")

    def test_parent_replacement_is_rejected(self, tmp_path: Path) -> None:
        parent = tmp_path / "parent"
        parent.mkdir()
        path = parent / "link"
        before = tm.ok(u.Cli.atomic_read_symlink_state(path))
        parent.rename(tmp_path / "original-parent")
        parent.mkdir()
        tm.fail(u.Cli.atomic_write_symlink_guarded(before, "replacement"))
        tm.that(tuple(parent.iterdir()), eq=())

    def test_symlink_parent_and_nonlink_leaf_are_rejected(self, tmp_path: Path) -> None:
        physical = tmp_path / "physical"
        physical.mkdir()
        alias = tmp_path / "alias"
        alias.symlink_to(physical, target_is_directory=True)
        tm.fail(u.Cli.atomic_read_symlink_state(alias / "link"))
        regular = physical / "regular"
        regular.write_bytes(b"data")
        tm.fail(u.Cli.atomic_read_symlink_state(regular))

    def test_required_absence_and_invalid_target_fail(self, tmp_path: Path) -> None:
        path = tmp_path / "link"
        tm.fail(u.Cli.atomic_read_symlink_state(path, required=True))
        before = tm.ok(u.Cli.atomic_read_symlink_state(path))
        tm.fail(u.Cli.atomic_write_symlink_guarded(before, ""))
        tm.fail(u.Cli.atomic_write_symlink_guarded(before, "invalid\0target"))
        tm.fail(u.Cli.atomic_delete_symlink_guarded(before))
        tm.that(tuple(tmp_path.iterdir()), eq=())

    @pytest.mark.parametrize("target", ["line one\nline two\n", " \tname\t ", "\n"])
    def test_newline_target_round_trips_without_normalization(
        self, tmp_path: Path, target: str
    ) -> None:
        path = tmp_path / "link"
        before = tm.ok(u.Cli.atomic_read_symlink_state(path))
        tm.ok(u.Cli.atomic_write_symlink_guarded(before, target))
        after = tm.ok(u.Cli.atomic_read_symlink_state(path, required=True))
        tm.that(after.target, eq=target)
        tm.that(str(path.readlink()), eq=target)
        tm.ok(u.Cli.atomic_delete_symlink_guarded(after))
        tm.that(tuple(tmp_path.iterdir()), eq=())

    def test_surrogate_target_fails_before_publication(self, tmp_path: Path) -> None:
        path = tmp_path / "link"
        before = tm.ok(u.Cli.atomic_read_symlink_state(path))
        tm.fail(u.Cli.atomic_write_symlink_guarded(before, "invalid\udcff"))
        tm.that(tuple(tmp_path.iterdir()), eq=())

    def test_non_utf8_existing_link_is_preserved(self, tmp_path: Path) -> None:
        path = tmp_path / "link"
        target = b"non-utf8-\xff"
        path.symlink_to(os.fsdecode(target))
        with pytest.raises(UnicodeEncodeError):
            u.Cli.atomic_read_symlink_state(path, required=True)
        tm.that(os.fsencode(path.readlink()), eq=target)
