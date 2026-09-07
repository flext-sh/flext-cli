"""Hostile public contracts for physical-tree inventory and guarded cleanup."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from flext_cli import m
from flext_tests import tm
from tests import u


class TestsAtomicPhysicalTree:
    """Prove manifests authenticate every entry before nonrecursive cleanup."""

    def test_inventory_records_ordered_parent_bound_physical_state(
        self, tmp_path: Path
    ) -> None:
        """Expose exact root, directory, and regular-file identities and digest."""
        root = tmp_path / "tree"
        child = root / "nested"
        child.mkdir(parents=True)
        payload = child / "payload.bin"
        payload.write_bytes(b"payload")

        result = u.Cli.atomic_inventory_physical_tree(root)

        tm.ok(result)
        manifest = result.value
        tm.that(manifest.root.path, eq=root)
        tm.that(manifest.root.kind, eq="directory")
        tm.that(tuple(entry.path for entry in manifest.entries), eq=(child, payload))
        directory, file_entry = manifest.entries
        tm.that(
            (directory.parent_device, directory.parent_inode),
            eq=(manifest.root.device, manifest.root.inode),
        )
        tm.that(
            (file_entry.parent_device, file_entry.parent_inode),
            eq=(directory.device, directory.inode),
        )
        tm.that(file_entry.size, eq=len(b"payload"))
        tm.that(file_entry.sha256, eq=hashlib.sha256(b"payload").hexdigest())
        restored = m.Cli.AtomicPhysicalTreeManifest.model_validate_json(
            manifest.model_dump_json()
        )
        tm.that(restored, eq=manifest)

    def test_cleanup_removes_exact_files_then_directories(self, tmp_path: Path) -> None:
        """Consume the exact manifest and remove the root without recursive delete."""
        root = tmp_path / "tree"
        deepest = root / "one" / "two"
        deepest.mkdir(parents=True)
        (root / "root.txt").write_text("root", encoding="utf-8")
        (deepest / "leaf.txt").write_text("leaf", encoding="utf-8")
        manifest = self._inventory(root)

        result = u.Cli.atomic_cleanup_physical_tree_guarded(manifest)

        tm.ok(result)
        tm.that(root.exists(), eq=False)

    @pytest.mark.parametrize("drift", ["unknown", "missing", "content", "metadata"])
    def test_manifest_drift_fails_before_any_effect(
        self, tmp_path: Path, drift: str
    ) -> None:
        """Preserve the tree for every unknown, missing, or changed entry."""
        root = tmp_path / drift
        root.mkdir()
        protected = root / "protected.txt"
        target = root / "target.txt"
        protected.write_bytes(b"protected")
        target.write_bytes(b"before")
        manifest = self._inventory(root)
        if drift == "unknown":
            (root / "unknown.txt").write_bytes(b"unknown")
        elif drift == "missing":
            target.unlink()
        elif drift == "content":
            target.write_bytes(b"after")
        else:
            observed = target.stat()
            os.utime(
                target, ns=(observed.st_atime_ns, observed.st_mtime_ns + 1_000_000_000)
            )

        result = u.Cli.atomic_cleanup_physical_tree_guarded(manifest)

        tm.fail(result)
        tm.that(protected.read_bytes(), eq=b"protected")
        if target.exists():
            expected = b"after" if drift == "content" else b"before"
            tm.that(target.read_bytes(), eq=expected)

    def test_replaced_root_inode_is_preserved(self, tmp_path: Path) -> None:
        """Never apply an old manifest to a new tree at the same pathname."""
        root = tmp_path / "tree"
        root.mkdir()
        (root / "payload.txt").write_text("payload", encoding="utf-8")
        manifest = self._inventory(root)
        original = tmp_path / "original-tree"
        root.rename(original)
        root.mkdir()
        (root / "payload.txt").write_text("payload", encoding="utf-8")

        result = u.Cli.atomic_cleanup_physical_tree_guarded(manifest)

        tm.fail(result)
        tm.that((root / "payload.txt").read_text(encoding="utf-8"), eq="payload")
        tm.that((original / "payload.txt").read_text(encoding="utf-8"), eq="payload")

    def test_inventory_and_cleanup_treat_symlink_as_authenticated_leaf(
        self, tmp_path: Path
    ) -> None:
        """Record and unlink an alias without traversing or touching its target."""
        target = tmp_path / "target"
        target.mkdir()
        (target / "owned.txt").write_text("owned", encoding="utf-8")
        root = tmp_path / "tree"
        root.mkdir()
        (root / "alias").symlink_to(target, target_is_directory=True)

        result = u.Cli.atomic_inventory_physical_tree(root)

        tm.ok(result)
        tm.that(result.value.entries[0].kind, eq="symlink")
        tm.that(result.value.entries[0].link_target, eq=str(target))
        tm.ok(u.Cli.atomic_cleanup_physical_tree_guarded(result.value))
        tm.that(root.exists(), eq=False)
        tm.that((target / "owned.txt").read_text(encoding="utf-8"), eq="owned")

    def test_inventory_rejects_hardlinked_file(self, tmp_path: Path) -> None:
        """Refuse cleanup authority over a file with another physical name."""
        root = tmp_path / "tree"
        root.mkdir()
        payload = root / "payload.txt"
        payload.write_text("payload", encoding="utf-8")
        alias = tmp_path / "alias.txt"
        alias.hardlink_to(payload)

        result = u.Cli.atomic_inventory_physical_tree(root)

        tm.fail(result)
        tm.that(payload.read_text(encoding="utf-8"), eq="payload")
        tm.that(alias.read_text(encoding="utf-8"), eq="payload")

    def test_inventory_rejects_special_node_causally(self, tmp_path: Path) -> None:
        """Reject a FIFO without opening, reading, or removing it."""
        root = tmp_path / "tree"
        root.mkdir()
        special = root / "fifo"
        os.mkfifo(special)

        result = u.Cli.atomic_inventory_physical_tree(root)

        tm.fail(result)
        tm.that(result.exception, is_=OSError)
        tm.that(result.error, has="not regular or a directory")
        tm.that(special.exists(), eq=True)

    def test_model_rejects_forged_topology(self, tmp_path: Path) -> None:
        """Keep outside paths, bind aliases, and device crossings unrepresentable."""
        root = tmp_path / "tree"
        root.mkdir()
        payload = root / "payload.txt"
        payload.write_text("payload", encoding="utf-8")
        manifest = self._inventory(root)
        entry = manifest.entries[0]
        for update in (
            {"path": tmp_path / "outside"},
            {"mount_id": entry.mount_id + 1},
            {"device": entry.device + 1},
        ):
            forged = entry.model_copy(update=update)
            with pytest.raises(m.ValidationError):
                m.Cli.AtomicPhysicalTreeManifest(root=manifest.root, entries=(forged,))

    def test_forged_parent_binding_fails_before_every_delete(
        self, tmp_path: Path
    ) -> None:
        """Preserve the complete tree when integral preflight rejects its source."""
        root = tmp_path / "tree"
        root.mkdir()
        payload = root / "payload.txt"
        payload.write_text("payload", encoding="utf-8")
        manifest = self._inventory(root)
        forged_root = manifest.root.model_copy(
            update={"parent_inode": manifest.root.parent_inode + 1}
        )
        forged = manifest.model_copy(update={"root": forged_root})

        result = u.Cli.atomic_cleanup_physical_tree_guarded(forged)

        tm.fail(result)
        tm.that(result.exception, is_=OSError)
        tm.that(payload.read_text(encoding="utf-8"), eq="payload")

    @staticmethod
    def _inventory(root: Path) -> m.Cli.AtomicPhysicalTreeManifest:
        result = u.Cli.atomic_inventory_physical_tree(root)
        tm.ok(result)
        return result.value


__all__: list[str] = ["TestsAtomicPhysicalTree"]
