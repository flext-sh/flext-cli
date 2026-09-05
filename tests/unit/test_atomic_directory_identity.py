"""Physical identity contract for guarded empty-directory operations."""

from __future__ import annotations

import stat
from pathlib import Path

import pytest

from flext_cli import cli, m
from flext_tests import tm
from tests import u


class TestsAtomicDirectoryIdentity:
    """Prove directory effects consume exact parent and leaf identities."""

    def test_snapshot_distinguishes_absence_from_empty_directory(
        self, tmp_path: Path
    ) -> None:
        """Return parent identity for absence and complete identity for presence."""
        target = tmp_path / "state"
        absent = self._snapshot(target)
        parent_state = tmp_path.lstat()
        tm.that(absent.exists, eq=False)
        tm.that(absent.parent_device, eq=parent_state.st_dev)
        tm.that(absent.parent_inode, eq=parent_state.st_ino)

        target.mkdir()
        present = self._snapshot(target, required=True)
        host_state = target.lstat()
        tm.that(present.exists, eq=True)
        tm.that(present.mode, eq=stat.S_IMODE(host_state.st_mode))
        tm.that(present.device, eq=host_state.st_dev)
        tm.that(present.inode, eq=host_state.st_ino)
        tm.that(present.link_count, eq=host_state.st_nlink)

    def test_required_snapshot_rejects_absence(self, tmp_path: Path) -> None:
        """Fail rather than manufacturing an existing directory identity."""
        result = u.Cli.atomic_read_empty_directory_state(
            tmp_path / "missing", required=True
        )

        tm.fail(result)

    def test_create_materializes_exact_mode_and_returns_inode(
        self, tmp_path: Path
    ) -> None:
        """Create from exact absence and report the materialized physical state."""
        target = tmp_path / "created"
        before = self._snapshot(target)

        result = u.Cli.atomic_create_empty_directory_guarded(
            before, permission_mode=0o750
        )

        tm.ok(result)
        host_state = target.lstat()
        tm.that(stat.S_IMODE(host_state.st_mode), eq=0o750)
        tm.that(result.value.inode, eq=host_state.st_ino)
        tm.that(tuple(target.iterdir()), eq=())

    def test_create_rejects_replaced_parent(self, tmp_path: Path) -> None:
        """Never apply an absent snapshot to a new directory at the same path."""
        parent = tmp_path / "parent"
        parent.mkdir()
        target = parent / "created"
        before = self._snapshot(target)
        original_parent = tmp_path / "original-parent"
        parent.rename(original_parent)
        parent.mkdir()

        result = u.Cli.atomic_create_empty_directory_guarded(
            before, permission_mode=0o700
        )

        tm.fail(result)
        tm.that(target.exists(), eq=False)
        tm.that((original_parent / target.name).exists(), eq=False)

    def test_delete_rejects_replacement_inode_with_same_mode(
        self, tmp_path: Path
    ) -> None:
        """Do not remove a new empty inode that merely matches visible mode."""
        target = tmp_path / "empty"
        target.mkdir(mode=0o750)
        before = self._snapshot(target, required=True)
        old = tmp_path / "old"
        target.rename(old)
        target.mkdir()
        if before.mode is None:
            message = "required directory snapshot unexpectedly absent"
            raise AssertionError(message)
        target.chmod(before.mode)

        result = u.Cli.atomic_delete_empty_directory_guarded(before)

        tm.fail(result)
        tm.that(target.is_dir(), eq=True)
        tm.that(old.is_dir(), eq=True)

    @pytest.mark.parametrize("entry_kind", ["file", "directory"])
    def test_late_content_prevents_delete(
        self, tmp_path: Path, entry_kind: str
    ) -> None:
        """Preserve regular or directory content added after the empty snapshot."""
        target = tmp_path / f"empty-{entry_kind}"
        target.mkdir()
        before = self._snapshot(target, required=True)
        child = target / "late"
        if entry_kind == "file":
            child.write_bytes(b"content")
        else:
            child.mkdir()

        result = u.Cli.atomic_delete_empty_directory_guarded(before)

        tm.fail(result)
        tm.that(target.is_dir(), eq=True)
        tm.that(child.exists(), eq=True)

    def test_leaf_symlink_is_never_a_directory_state(self, tmp_path: Path) -> None:
        """Reject a final-entry alias without touching its physical target."""
        physical = tmp_path / "physical"
        physical.mkdir()
        alias = tmp_path / "alias"
        alias.symlink_to(physical, target_is_directory=True)

        result = u.Cli.atomic_read_empty_directory_state(alias, required=True)

        tm.fail(result)
        tm.that(physical.is_dir(), eq=True)
        tm.that(alias.is_symlink(), eq=True)

    def test_ancestor_symlink_is_never_traversed(self, tmp_path: Path) -> None:
        """Reject aliases in every ancestor, not only the final parent entry."""
        physical = tmp_path / "physical"
        physical.mkdir()
        (physical / "empty").mkdir()
        alias = tmp_path / "alias"
        alias.symlink_to(physical, target_is_directory=True)

        result = u.Cli.atomic_read_empty_directory_state(alias / "empty", required=True)

        tm.fail(result)
        tm.that((physical / "empty").is_dir(), eq=True)

    def test_state_model_rejects_reparse_identity(self, tmp_path: Path) -> None:
        """Keep a nonzero host reparse tag outside the public CAS contract."""
        parent_state = tmp_path.lstat()
        with pytest.raises(m.ValidationError):
            m.Cli.AtomicDirectoryState(
                path=tmp_path / "reparse",
                exists=True,
                parent_device=parent_state.st_dev,
                parent_inode=parent_state.st_ino,
                mode=0o700,
                device=parent_state.st_dev,
                inode=parent_state.st_ino,
                link_count=1,
                reparse_tag=1,
            )

    def test_service_facade_uses_the_same_guarded_contract(
        self, tmp_path: Path
    ) -> None:
        """Expose snapshot, create, and delete through the service facade."""
        target = tmp_path / "service-empty"
        before_result = cli.atomic_read_empty_directory_state(target)
        tm.ok(before_result)
        created = cli.atomic_create_empty_directory_guarded(
            before_result.value, permission_mode=0o700
        )
        tm.ok(created)

        deleted = cli.atomic_delete_empty_directory_guarded(created.value)

        tm.ok(deleted)
        tm.that(target.exists(), eq=False)

    @staticmethod
    def _snapshot(path: Path, *, required: bool = False) -> m.Cli.AtomicDirectoryState:
        result = u.Cli.atomic_read_empty_directory_state(path, required=required)
        tm.ok(result)
        return result.value


__all__: list[str] = ["TestsAtomicDirectoryIdentity"]
