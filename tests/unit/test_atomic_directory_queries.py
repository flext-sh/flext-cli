"""Consumed directory queries against the publisher's own physical effects.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

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
