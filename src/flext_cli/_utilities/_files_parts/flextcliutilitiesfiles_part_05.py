"""Strict physical empty-directory helpers shared through ``u.Cli``."""

from __future__ import annotations

from pathlib import Path

from flext_cli import c, m, p, r, t
from flext_cli._utilities.atomic_directory_chain import (
    create_guarded_directory_chain,
    plan_directory_chain,
)
from flext_cli._utilities.atomic_directory_create import (
    create_guarded_empty_directory,
)
from flext_cli._utilities.atomic_directory_delete import (
    remove_guarded_empty_directory,
)
from flext_cli._utilities.atomic_directory_publish import (
    publish_guarded_staged_empty_directory,
)
from flext_cli._utilities.atomic_directory_snapshot import (
    read_authenticated_empty_directory,
)
from flext_cli._utilities.atomic_tree_cleanup import (
    cleanup_physical_tree_guarded,
)
from flext_cli._utilities.atomic_tree_inventory import inventory_physical_tree


class FlextCliUtilitiesFiles:
    """Implementation part for strict physical empty-directory effects."""

    @staticmethod
    def atomic_plan_directory_chain(
        directory_path: t.Cli.TextPath,
    ) -> p.Result[m.Cli.AtomicDirectoryChainPlan]:
        """Plan missing ancestors from one exact existing physical anchor.

        Planning has no filesystem effect and records no future inode. The caller
        must retain one exclusive cooperative lock through later materialization.
        """
        try:
            plan = plan_directory_chain(Path(directory_path))
        except OSError as exc:
            return r[m.Cli.AtomicDirectoryChainPlan].fail(
                c.Cli.ERR_ATOMIC_DIRECTORY_PLAN_FAILED.format(error=exc)
            )
        return r[m.Cli.AtomicDirectoryChainPlan].ok(plan)

    @staticmethod
    def atomic_create_directory_chain_guarded(
        plan: m.Cli.AtomicDirectoryChainPlan, *, permission_mode: int
    ) -> p.Result[t.SequenceOf[m.Cli.AtomicDirectoryState]]:
        """Materialize a planned chain under the caller's exclusive lock.

        Each level uses the nonrecursive guarded primitive and successful levels
        roll back in reverse after failure. This is not CAS against actors that
        ignore the lock. Snapshot any destination file only after this succeeds.
        """
        try:
            created = create_guarded_directory_chain(
                plan, permission_mode=permission_mode
            )
        except OSError as exc:
            return r[t.SequenceOf[m.Cli.AtomicDirectoryState]].fail(
                c.Cli.ERR_ATOMIC_DIRECTORY_CHAIN_CREATE_FAILED.format(error=exc)
            )
        return r[t.SequenceOf[m.Cli.AtomicDirectoryState]].ok(created)

    @staticmethod
    def atomic_read_empty_directory_state(
        directory_path: t.Cli.TextPath, *, required: bool = False
    ) -> p.Result[m.Cli.AtomicDirectoryState]:
        """Read exact absence or one stable physical empty-directory identity."""
        try:
            state = read_authenticated_empty_directory(
                Path(directory_path), required=required
            )
        except OSError as exc:
            return r[m.Cli.AtomicDirectoryState].fail(
                c.Cli.ERR_ATOMIC_DIRECTORY_READ_FAILED.format(error=exc)
            )
        return r[m.Cli.AtomicDirectoryState].ok(state)

    @staticmethod
    def atomic_create_empty_directory_guarded(
        before: m.Cli.AtomicDirectoryState, *, permission_mode: int
    ) -> p.Result[m.Cli.AtomicDirectoryState]:
        """Create one exact empty directory under the caller's exclusive lock.

        The immediate parent identity is part of ``before`` and must still match.
        This nonrecursive operation is not CAS against actors ignoring the lock.
        """
        try:
            state = create_guarded_empty_directory(
                before, permission_mode=permission_mode
            )
        except OSError as exc:
            return r[m.Cli.AtomicDirectoryState].fail(
                c.Cli.ERR_ATOMIC_DIRECTORY_CREATE_FAILED.format(error=exc)
            )
        return r[m.Cli.AtomicDirectoryState].ok(state)

    @staticmethod
    def atomic_delete_empty_directory_guarded(
        state: m.Cli.AtomicDirectoryState,
    ) -> p.Result[bool]:
        """Delete one exact empty directory under the caller's exclusive lock.

        The final descriptor-bound recheck precedes ``rmdir`` and the parent is
        synced afterward. POSIX has no expected-inode rmdir, so actors ignoring
        the cooperative lock remain outside this CAS contract.
        """
        try:
            remove_guarded_empty_directory(state)
        except OSError as exc:
            return r[bool].fail(
                c.Cli.ERR_ATOMIC_DIRECTORY_DELETE_FAILED.format(error=exc)
            )
        return r[bool].ok(True)

    @staticmethod
    def atomic_publish_staged_empty_directory_guarded(
        destination_before: m.Cli.AtomicDirectoryState,
        staged: m.Cli.AtomicDirectoryState,
    ) -> p.Result[m.Cli.AtomicDirectoryState]:
        """Publish one staged empty directory without clobbering a destination.

        The destination must be an authenticated absent state. Linux uses
        ``renameat2(RENAME_NOREPLACE)``; unsupported hosts fail before effects.
        """
        try:
            published = publish_guarded_staged_empty_directory(
                destination_before, staged
            )
        except OSError as exc:
            return r[m.Cli.AtomicDirectoryState].fail(
                c.Cli.ERR_ATOMIC_DIRECTORY_PUBLISH_FAILED.format(error=exc)
            )
        return r[m.Cli.AtomicDirectoryState].ok(published)

    @staticmethod
    def atomic_inventory_physical_tree(
        root_path: t.Cli.TextPath,
    ) -> p.Result[m.Cli.AtomicPhysicalTreeManifest]:
        """Return an exact descriptor-authenticated tree manifest.

        The root, every parent binding, regular-file digest, and physical directory
        identity are recorded. Linux mount IDs reject bind aliases before their
        contents are read; unsupported hosts fail closed. Hardlinks, special nodes,
        and device or mount transitions also fail. The caller retains one exclusive
        cooperative lock through inventory and cleanup.
        """
        try:
            manifest = inventory_physical_tree(Path(root_path))
        except OSError as exc:
            return r[m.Cli.AtomicPhysicalTreeManifest].fail(
                c.Cli.ERR_ATOMIC_PHYSICAL_TREE_INVENTORY_FAILED.format(error=exc),
                exception=exc,
            )
        return r[m.Cli.AtomicPhysicalTreeManifest].ok(manifest)

    @staticmethod
    def atomic_cleanup_physical_tree_guarded(
        manifest: m.Cli.AtomicPhysicalTreeManifest,
    ) -> p.Result[bool]:
        """Delete only an unchanged manifested tree under one exclusive lock.

        Every affected parent is authenticated and sync-probed before a complete
        inventory comparison and the first namespace mutation. Files and then empty
        directories are removed without recursion. A later storage failure can
        leave an authenticated deletion prefix, so the caller must retain recovery
        state. Writers that ignore the caller's lock are outside this contract.
        """
        try:
            cleanup_physical_tree_guarded(manifest)
        except OSError as exc:
            return r[bool].fail(
                c.Cli.ERR_ATOMIC_PHYSICAL_TREE_CLEANUP_FAILED.format(error=exc),
                exception=exc,
            )
        return r[bool].ok(True)


__all__: list[str] = ["FlextCliUtilitiesFiles"]
