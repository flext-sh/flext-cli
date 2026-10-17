"""Consumed directory queries against the publisher's own physical effects.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import pytest

from tests import m, t, tm, u


class TestsFlextCliAtomicDirectoryQueries:
    """Reprove a queried directory only where its existence depends on a receipt."""

    @staticmethod
    def _queried(root: Path, name: str) -> m.Cli.AtomicDirectoryInventory:
        """Capture ``root`` with one consumed ``isdir`` query and its membership.

        Returns:
            The physical inventory carrying the consumed selectors.

        """
        return tm.ok(u.Cli.atomic_inventory_physical_directory(root)).model_copy(
            update={"queries": ((name, "isdir"),), "membership_queried": True},
        )

    @staticmethod
    def _publish(
        path: Path,
    ) -> t.Pair[m.Cli.AtomicFileState, m.Cli.AtomicFileState]:
        """Publish one new file and return its before/after physical states.

        Returns:
            The absent preimage and the published state of ``path``.

        """
        before = tm.ok(u.Cli.atomic_read_binary_file_state(path))
        tm.ok(u.Cli.atomic_write_text_file(path, "VALUE = 1\n"))
        return before, tm.ok(u.Cli.atomic_read_binary_file_state(path, required=True))

    def test_publication_under_preexisting_directory_needs_no_receipt(
        self,
        tmp_path: Path,
    ) -> None:
        """A directory the preimage held keeps its existence without a receipt."""
        source = tmp_path / "src"
        source.mkdir()
        inventory = self._queried(tmp_path, "src")
        publication = self._publish(source / "module.py")

        verified = u.Cli.atomic_verify_directory_queries(
            (inventory,),
            (),
            publications=(publication,),
        )

        tm.that(tm.ok(verified), eq=True)

    def test_directory_appearing_without_receipt_fails_loud(
        self,
        tmp_path: Path,
    ) -> None:
        """A directory absent from the preimage must be the publisher's own."""
        inventory = self._queried(tmp_path, "fresh")
        fresh = tmp_path / "fresh"
        fresh.mkdir()
        publication = self._publish(fresh / "module.py")

        with pytest.raises(ValueError, match="lacks its original publication"):
            u.Cli.atomic_verify_directory_queries(
                (inventory,),
                (),
                publications=(publication,),
            )

    def test_own_directory_creation_binds_to_its_receipt(
        self,
        tmp_path: Path,
    ) -> None:
        """A directory the publisher created verifies through its own receipt."""
        inventory = self._queried(tmp_path, "fresh")
        created = tm.ok(
            u.Cli.atomic_create_empty_directory_guarded(
                u.atomic_directory_snapshot(tmp_path / "fresh"),
                permission_mode=0o700,
            ),
        )
        publication = self._publish(tmp_path / "fresh" / "module.py")

        verified = u.Cli.atomic_verify_directory_queries(
            (inventory,),
            (),
            publications=(publication,),
            directory_publications=(created,),
        )

        tm.that(tm.ok(verified), eq=True)

    def test_created_directory_replacement_rejects_the_original_receipt(
        self,
        tmp_path: Path,
    ) -> None:
        """A replacement inode cannot inherit the original publisher's birth."""
        inventory = self._queried(tmp_path, "fresh")
        fresh = tmp_path / "fresh"
        created = tm.ok(
            u.Cli.atomic_create_empty_directory_guarded(
                u.atomic_directory_snapshot(fresh),
                permission_mode=0o700,
            ),
        )
        fresh.rename(tmp_path / "retired")
        fresh.mkdir()
        publication = self._publish(fresh / "module.py")

        with pytest.raises(ValueError, match="lacks its original publication"):
            u.Cli.atomic_verify_directory_queries(
                (inventory,),
                (),
                publications=(publication,),
                directory_publications=(created,),
            )

    def test_preexisting_directory_replaced_by_file_rejects_the_query(
        self,
        tmp_path: Path,
    ) -> None:
        """A preexisting name cannot keep its directory predicate after replacement."""
        source = tmp_path / "src"
        source.mkdir()
        inventory = self._queried(tmp_path, "src")
        source.rename(tmp_path / "retired")
        source.write_text("replacement\n", encoding="utf-8")

        with pytest.raises(ValueError, match="source directory query changed"):
            u.Cli.atomic_verify_directory_queries((inventory,), ())

    def test_unpublished_child_rejects_consumed_membership(
        self,
        tmp_path: Path,
    ) -> None:
        """An unchanged directory predicate does not excuse new queried membership."""
        (tmp_path / "src").mkdir()
        inventory = self._queried(tmp_path, "src")
        (tmp_path / "unpublished.py").write_text("VALUE = 1\n", encoding="utf-8")

        with pytest.raises(ValueError, match="source directory membership changed"):
            u.Cli.atomic_verify_directory_queries((inventory,), ())

    @pytest.mark.parametrize("predicate", ["exists", "isdir"])
    def test_neighboring_name_is_not_a_publication_ancestor(
        self,
        tmp_path: Path,
        predicate: Literal["exists", "isdir"],
    ) -> None:
        """Lexical ancestors never admit a sibling with a shared name prefix."""
        neighbor = tmp_path / "source-extra"
        neighbor.mkdir()
        inventory = self._queried(tmp_path, "source").model_copy(
            update={
                "queries": (("source", predicate),),
                "membership_queried": False,
            },
        )
        publication = self._publish(neighbor / "module.py")
        tm.that(
            tm.ok(
                u.Cli.atomic_verify_directory_queries(
                    (inventory,), (), publications=(publication,)
                ),
            ),
            eq=True,
        )

    @pytest.mark.parametrize("child_name", ["package", "package-extra"])
    def test_absent_parent_query_preserves_exact_publication_ancestry(
        self,
        tmp_path: Path,
        child_name: str,
    ) -> None:
        """A gained parent retains exact queries and original directory receipts."""
        root = tmp_path / "fresh"
        topology = tm.ok(u.Cli.atomic_plan_directory_chain(root)).model_copy(
            update={"queries": (("package", "isdir"),)},
        )
        created_root = tm.ok(
            u.Cli.atomic_create_empty_directory_guarded(
                u.atomic_directory_snapshot(root), permission_mode=0o700
            ),
        )
        child = root / child_name
        created_child = tm.ok(
            u.Cli.atomic_create_empty_directory_guarded(
                u.atomic_directory_snapshot(child), permission_mode=0o700
            ),
        )
        publication = self._publish(child / "module.py")
        tm.that(
            tm.ok(
                u.Cli.atomic_verify_directory_queries(
                    (),
                    (topology,),
                    publications=(publication,),
                    directory_publications=(created_root, created_child),
                ),
            ),
            eq=True,
        )

    @pytest.mark.parametrize("replacement", ["root", "parent"])
    def test_replaced_physical_identity_rejects_unchanged_membership(
        self,
        tmp_path: Path,
        replacement: str,
    ) -> None:
        """Equal names and kinds do not authorize a replaced root or ancestor."""
        parent = tmp_path / "parent"
        parent.mkdir()
        source = parent / "source"
        source.mkdir()
        (source / "child").mkdir()
        inventory = self._queried(source, "child")
        if replacement == "root":
            source.rename(parent / "retired")
            source.mkdir()
            (source / "child").mkdir()
        else:
            retired = parent.rename(tmp_path / "retired")
            parent.mkdir()
            (retired / source.name).rename(source)

        with pytest.raises(
            ValueError, match="source directory physical identity changed"
        ):
            u.Cli.atomic_verify_directory_queries((inventory,), ())
