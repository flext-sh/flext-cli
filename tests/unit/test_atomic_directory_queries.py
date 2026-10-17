"""Consumed directory queries against the publisher's own physical effects.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

import pytest

from tests import c, m, t, tm, u


class TestsFlextCliAtomicDirectoryQueries:
    """Reprove a queried directory only where its existence depends on a receipt."""

    @staticmethod
    def test_filesystem_root_is_a_directory_not_a_file(tmp_path: Path) -> None:
        """Directory election authenticates anchors without authorizing file IO."""
        root = Path(tmp_path.anchor)
        inventory = tm.ok(u.Cli.atomic_inventory_physical_directory(root))

        tm.that(inventory.root.path, eq=root)
        tm.that(inventory.root.kind, eq="directory")
        tm.that(
            (inventory.root.parent_device, inventory.root.parent_inode),
            eq=(inventory.root.device, inventory.root.inode),
        )
        tm.that(
            u.Cli.atomic_directory_query_value(inventory, tmp_path.parts[1], "exists"),
            eq=True,
        )
        tm.that(
            u.Cli.atomic_read_binary_file_state(root, required=True).failure, eq=True
        )
        tm.that(u.Cli.atomic_inventory_physical_tree(root).failure, eq=True)
        with pytest.raises(ValueError, match="manifest root path"):
            m.Cli.AtomicPhysicalTreeManifest(root=inventory.root)

    @staticmethod
    @pytest.mark.parametrize("kind", ["file", "symlink"])
    def test_filesystem_anchor_cannot_be_a_leaf(
        tmp_path: Path, kind: Literal["file", "symlink"]
    ) -> None:
        """Allowing physical directory anchors never admits invented leaf states."""
        inventory = tm.ok(
            u.Cli.atomic_inventory_physical_directory(Path(tmp_path.anchor))
        )
        with pytest.raises(ValueError, match="path must be absolute and normalized"):
            m.Cli.AtomicPhysicalTreeEntry.model_validate(
                inventory.root.model_dump() | {"kind": kind}
            )

    @staticmethod
    def test_directory_elections_authenticate_mounted_ancestors(tmp_path: Path) -> None:
        """Read-only ancestry election records mount facts, never cleanup authority."""
        directory = next(
            (
                candidate
                for candidate in (tmp_path, *tmp_path.parents)
                if candidate.stat().st_dev != candidate.parent.stat().st_dev
            ),
            tmp_path,
        )
        inventory = tm.ok(u.Cli.atomic_inventory_physical_directory(directory))
        observed = directory.stat()
        tm.that(inventory.root.device, eq=observed.st_dev)
        tm.that(inventory.root.inode, eq=observed.st_ino)
        tm.that(inventory.root.parent_device, eq=directory.parent.stat().st_dev)
        if observed.st_dev != inventory.root.parent_device:
            tm.that(u.Cli.atomic_inventory_physical_tree(directory).failure, eq=True)

    @staticmethod
    @pytest.mark.parametrize("boundary", ["device", "mount"])
    def test_directory_election_cannot_become_cross_boundary_cleanup(
        tmp_path: Path, boundary: Literal["device", "mount"]
    ) -> None:
        """Physical facts can describe a mount without authorizing its destruction."""
        inventory = tm.ok(u.Cli.atomic_inventory_physical_directory(tmp_path))
        transition = (
            {"parent_device": inventory.root.device + 1}
            if boundary == "device"
            else {"parent_mount_id": inventory.root.mount_id + 1}
        )
        root = m.Cli.AtomicPhysicalTreeEntry.model_validate(
            inventory.root.model_dump() | transition
        )
        tm.that(m.Cli.AtomicDirectoryInventory(root=root).root, eq=root)
        with pytest.raises(ValueError, match=f"parent {boundary}"):
            m.Cli.AtomicPhysicalTreeManifest(root=root)

    @staticmethod
    @pytest.mark.parametrize("failure", ["io", "interrupt"])
    def test_inventory_and_lineage_failures_keep_their_causes(
        tmp_path: Path, failure: Literal["io", "interrupt"]
    ) -> None:
        """A real parent move must not replace an operation error or cancellation."""
        script = tmp_path / "consumer.py"
        script.write_text(
            "import errno\n"
            "import os\n"
            "import sys\n"
            "from pathlib import Path\n"
            "from flext_cli import u\n"
            "root = Path(sys.argv[1])\n"
            "parent = root / 'parent'\n"
            "parent.mkdir()\n"
            "directory = parent / 'inventory'\n"
            "directory.mkdir()\n"
            "expected = directory.stat()\n"
            "armed = True\n"
            "def fail_inventory(event, args):\n"
            "    global armed\n"
            "    if event == 'os.scandir' and armed and isinstance(args[0], int):\n"
            "        observed = os.fstat(args[0])\n"
            "        if (observed.st_dev, observed.st_ino) != "
            "(expected.st_dev, expected.st_ino):\n"
            "            return\n"
            "        armed = False\n"
            "        parent.rename(root / 'moved')\n"
            "        if sys.argv[2] == 'interrupt':\n"
            "            raise KeyboardInterrupt('inventory cancelled')\n"
            "        raise OSError(errno.EIO, 'inventory failed')\n"
            "sys.addaudithook(fail_inventory)\n"
            "if sys.argv[2] == 'interrupt':\n"
            "    try:\n"
            "        u.Cli.atomic_inventory_physical_directory(directory)\n"
            "    except BaseExceptionGroup as error:\n"
            "        assert isinstance(error.exceptions[0], KeyboardInterrupt)\n"
            "        assert isinstance(error.exceptions[1], OSError)\n"
            "    else:\n"
            "        raise AssertionError('cancellation was normalized')\n"
            "else:\n"
            "    result = u.Cli.atomic_inventory_physical_directory(directory)\n"
            "    assert result.failure\n"
            "    error = result.exception\n"
            "    assert isinstance(error, OSError)\n"
            "    assert error.errno == errno.ESTALE\n"
            "    assert isinstance(error.__cause__, ExceptionGroup)\n"
            "    assert error.__cause__.exceptions[0].errno == errno.EIO\n"
            "    assert isinstance(error.__cause__.exceptions[1], OSError)\n",
            encoding=c.DEFAULT_ENCODING,
        )
        outcome = tm.ok(
            u.Cli.run_raw((sys.executable, "-I", str(script), str(tmp_path), failure)),
        )
        tm.that(u.Cli.process_succeeded(outcome.outcome), eq=True, msg=outcome.stderr)
        tm.that(outcome.stderr, eq="")

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
