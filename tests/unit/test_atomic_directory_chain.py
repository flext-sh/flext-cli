"""Guarded planning and materialization of missing directory ancestors."""

from __future__ import annotations

import stat
from pathlib import Path

from flext_tests import tm
from tests import u


class TestsAtomicDirectoryChain:
    """Prove missing ancestors are explicit, physical, and rollback-capable."""

    def test_plan_anchors_at_deepest_existing_directory(
        self, tmp_path: Path
    ) -> None:
        """Allow a nonempty anchor while recording every lower path as absent."""
        anchor = tmp_path / "docs"
        anchor.mkdir()
        (anchor / "README.md").write_text("owner", encoding="utf-8")
        target = anchor / "api-reference" / "generated"

        result = u.Cli.atomic_plan_directory_chain(target)

        tm.ok(result)
        plan = result.value
        anchor_state = anchor.lstat()
        tm.that(plan.anchor_path, eq=anchor)
        tm.that(plan.anchor_device, eq=anchor_state.st_dev)
        tm.that(plan.anchor_inode, eq=anchor_state.st_ino)
        tm.that(
            plan.directories,
            eq=(anchor / "api-reference", target),
        )

    def test_materialize_then_resnapshot_file_parent(self, tmp_path: Path) -> None:
        """Bind file absence only after its planned parent physically exists."""
        target = tmp_path / "docs" / "api-reference" / "generated"
        plan_result = u.Cli.atomic_plan_directory_chain(target)
        tm.ok(plan_result)

        created = u.Cli.atomic_create_directory_chain_guarded(
            plan_result.value, permission_mode=0o750
        )

        tm.ok(created)
        tm.that(tuple(state.path for state in created.value), eq=plan_result.value.directories)
        for directory in plan_result.value.directories:
            tm.that(stat.S_IMODE(directory.lstat().st_mode), eq=0o750)
        file_path = target / "overview.md"
        before = u.Cli.atomic_read_binary_file_state(file_path)
        tm.ok(before)
        parent_state = target.lstat()
        tm.that(before.value.parent_device, eq=parent_state.st_dev)
        tm.that(before.value.parent_inode, eq=parent_state.st_ino)
        published = u.Cli.atomic_write_text_file_guarded(before.value, "overview")
        tm.ok(published)
        tm.that(file_path.read_text(encoding="utf-8"), eq="overview")

    def test_materialization_rejects_replaced_anchor(self, tmp_path: Path) -> None:
        """Apply no path when the physical anchor changed after planning."""
        anchor = tmp_path / "docs"
        anchor.mkdir()
        target = anchor / "generated"
        plan_result = u.Cli.atomic_plan_directory_chain(target)
        tm.ok(plan_result)
        original = tmp_path / "original-docs"
        anchor.rename(original)
        anchor.mkdir()

        result = u.Cli.atomic_create_directory_chain_guarded(
            plan_result.value, permission_mode=0o700
        )

        tm.fail(result)
        tm.that(target.exists(), eq=False)
        tm.that((original / target.name).exists(), eq=False)

    def test_existing_target_is_verified_without_effect(self, tmp_path: Path) -> None:
        """Represent an already-existing physical target as an empty effect list."""
        target = tmp_path / "existing"
        target.mkdir()
        (target / "owned.txt").write_text("content", encoding="utf-8")
        plan_result = u.Cli.atomic_plan_directory_chain(target)
        tm.ok(plan_result)
        tm.that(plan_result.value.directories, eq=())

        result = u.Cli.atomic_create_directory_chain_guarded(
            plan_result.value, permission_mode=0o700
        )

        tm.ok(result)
        tm.that(tuple(result.value), eq=())
        tm.that((target / "owned.txt").read_text(encoding="utf-8"), eq="content")

    def test_planner_rejects_ancestor_alias(self, tmp_path: Path) -> None:
        """Never use a symlink as an existing chain component or anchor."""
        physical = tmp_path / "physical"
        physical.mkdir()
        alias = tmp_path / "alias"
        alias.symlink_to(physical, target_is_directory=True)

        result = u.Cli.atomic_plan_directory_chain(alias / "generated")

        tm.fail(result)
        tm.that(tuple(physical.iterdir()), eq=())


__all__: list[str] = ["TestsAtomicDirectoryChain"]
