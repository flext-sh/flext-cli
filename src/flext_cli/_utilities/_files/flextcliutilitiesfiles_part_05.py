"""Strict physical empty-directory helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, MutableSequence, Sequence
from pathlib import Path
from types import MappingProxyType
from typing import Literal

from flext_core import r

from flext_cli import c, m, p, t
from flext_cli._utilities import (
    FlextCliUtilitiesAtomicDirectoryChain,
    FlextCliUtilitiesAtomicDirectoryCreate,
    FlextCliUtilitiesAtomicDirectoryDelete,
    FlextCliUtilitiesAtomicDirectorySnapshot,
    FlextCliUtilitiesAtomicTreeCleanup,
    FlextCliUtilitiesAtomicTreeInventory,
)


class FlextCliUtilitiesFilesPart05:
    """Implementation part for strict physical empty-directory effects."""

    @staticmethod
    def atomic_plan_directory_chain(
        directory_path: t.Cli.TextPath,
    ) -> p.Result[p.Cli.AtomicDirectoryChainPlan]:
        """Plan missing ancestors from one exact existing physical anchor.

        Planning has no filesystem effect and records no future inode. The caller
        must retain one exclusive cooperative lock through later materialization.

        Returns:
            The resulting ``p.Result[p.Cli.AtomicDirectoryChainPlan]``.

        """
        try:
            plan = FlextCliUtilitiesAtomicDirectoryChain.plan_directory_chain(
                Path(directory_path),
            )
        except OSError as exc:
            return r[p.Cli.AtomicDirectoryChainPlan].fail(
                c.Cli.ERR_ATOMIC_DIRECTORY_PLAN_FAILED.format(error=exc),
                exception=exc,
            )
        return r.ok(plan)

    @staticmethod
    def atomic_create_directory_chain_guarded(
        plan: p.Cli.AtomicDirectoryChainPlan,
        *,
        permission_mode: int,
        created: MutableSequence[p.Cli.AtomicDirectoryState] | None = None,
    ) -> p.Result[Sequence[p.Cli.AtomicDirectoryState]]:
        """Materialize a planned chain under the caller's exclusive lock.

        Each level uses the nonrecursive guarded primitive. Preserve the original
        file observation and directory plan before these effects; a later read
        can validate them but never replace their publication authority. This is
        not CAS against actors that ignore the caller's exclusive lock.

        Returns:
            The resulting ``p.Result[Sequence[p.Cli.AtomicDirectoryState]]``.

        """
        progress: MutableSequence[p.Cli.AtomicDirectoryState] = (
            [] if created is None else created
        )
        initial_count = len(progress)
        try:
            completed = (
                FlextCliUtilitiesAtomicDirectoryChain.create_guarded_directory_chain(
                    plan,
                    permission_mode=permission_mode,
                    created=progress,
                )
            )
        except OSError as exc:
            return r[Sequence[p.Cli.AtomicDirectoryState]].fail(
                c.Cli.ERR_ATOMIC_DIRECTORY_CHAIN_CREATE_FAILED.format(error=exc),
                exception=exc,
                error_data={
                    "created_directories": [
                        state.model_dump(mode="json")
                        for state in progress[initial_count:]
                    ],
                },
            )
        return r[Sequence[p.Cli.AtomicDirectoryState]].ok(completed)

    @staticmethod
    def atomic_read_empty_directory_state(
        directory_path: t.Cli.TextPath,
        *,
        required: bool = False,
    ) -> p.Result[p.Cli.AtomicDirectoryState]:
        """Read exact absence or one stable physical empty-directory identity.

        Returns:
            The resulting ``p.Result[p.Cli.AtomicDirectoryState]``.

        """
        try:
            snapshot = FlextCliUtilitiesAtomicDirectorySnapshot
            state = snapshot.read_authenticated_empty_directory(
                Path(directory_path),
                required=required,
            )
        except OSError as exc:
            return r[p.Cli.AtomicDirectoryState].fail(
                c.Cli.ERR_ATOMIC_DIRECTORY_READ_FAILED.format(error=exc),
            )
        return r[p.Cli.AtomicDirectoryState].ok(state)

    @staticmethod
    def atomic_create_empty_directory_guarded(
        before: p.Cli.AtomicDirectoryState,
        *,
        permission_mode: int,
    ) -> p.Result[p.Cli.AtomicDirectoryState]:
        """Create one exact empty directory under the caller's exclusive lock.

        The immediate parent identity is part of ``before`` and must still match.
        This nonrecursive operation is not CAS against actors ignoring the lock.

        Returns:
            The resulting ``p.Result[p.Cli.AtomicDirectoryState]``.

        """
        try:
            state = (
                FlextCliUtilitiesAtomicDirectoryCreate.create_guarded_empty_directory(
                    before,
                    permission_mode=permission_mode,
                )
            )
        except OSError as exc:
            return r[p.Cli.AtomicDirectoryState].fail(
                c.Cli.ERR_ATOMIC_DIRECTORY_CREATE_FAILED.format(error=exc),
            )
        return r[p.Cli.AtomicDirectoryState].ok(state)

    @staticmethod
    def atomic_delete_empty_directory_guarded(
        state: p.Cli.AtomicDirectoryState,
    ) -> p.Result[bool]:
        """Delete one exact empty directory under the caller's exclusive lock.

        The final descriptor-bound recheck precedes ``rmdir`` and the parent is
        synced afterward. POSIX has no expected-inode rmdir, so actors ignoring
        the cooperative lock remain outside this CAS contract.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        try:
            FlextCliUtilitiesAtomicDirectoryDelete.remove_guarded_empty_directory(state)
        except OSError as exc:
            return r[bool].fail(
                c.Cli.ERR_ATOMIC_DIRECTORY_DELETE_FAILED.format(error=exc),
            )
        return r[bool].ok(value=True)

    @staticmethod
    def atomic_merge_directory_query_receipts(
        inventories: tuple[p.Cli.AtomicDirectoryInventory, ...],
        topology: tuple[p.Cli.AtomicDirectoryChainPlan, ...],
        *,
        queries: Mapping[
            int, set[tuple[str, Literal["exists", "isfile", "isdir"]]]
        ] = MappingProxyType({}),
        membership_queries: Mapping[int, set[t.StrTuple]] = MappingProxyType({}),
    ) -> tuple[
        tuple[p.Cli.AtomicDirectoryInventory, ...],
        tuple[p.Cli.AtomicDirectoryChainPlan, ...],
    ]:
        """Forward original epochs and working selectors to their sole merge owner.

        Returns:
            The directory inventories and ancestry plans with united selectors.

        """
        return FlextCliUtilitiesAtomicTreeInventory.merge_directory_query_receipts(
            inventories,
            topology,
            m.Cli.AtomicDirectoryWorkingSelectors(
                queries=queries, membership_queries=membership_queries
            ),
        )

    @staticmethod
    def atomic_directory_membership_value(
        inventory: p.Cli.AtomicDirectoryInventory,
        excluded_names: t.StrTuple,
    ) -> Mapping[str, Literal["directory", "file", "symlink", "other"]]:
        """Evaluate a declared membership selection on its physical receipt.

        Returns:
            Selected child names and physical kinds.

        """
        return FlextCliUtilitiesAtomicTreeInventory.directory_membership_value(
            inventory, excluded_names
        )

    @staticmethod
    def atomic_directory_query_value(
        inventory: p.Cli.AtomicDirectoryInventory,
        name: str,
        predicate: Literal["exists", "isfile", "isdir"],
    ) -> bool:
        """Read one native filesystem predicate from its captured receipt.

        Returns:
            Whether the captured child satisfies the native predicate.

        """
        return FlextCliUtilitiesAtomicTreeInventory.directory_query_value(
            inventory, name, predicate
        )

    @staticmethod
    def atomic_verify_directory_queries(
        inventories: tuple[p.Cli.AtomicDirectoryInventory, ...],
        topology: tuple[p.Cli.AtomicDirectoryChainPlan, ...],
        *,
        publications: tuple[tuple[p.Cli.AtomicFileState, p.Cli.AtomicFileState], ...]
        | m.Cli.AtomicDirectoryQueryEffects = (),
        directory_publications: tuple[p.Cli.AtomicDirectoryState, ...] = (),
        observations: p.Cli.AtomicDirectoryObservations | None = None,
    ) -> p.Result[bool]:
        """Verify native source queries without authorizing publication effects.

        One verification boundary shares its directory and ancestry observations
        through one ``observations`` instance passed by reference. Successful
        observations are shared only within that boundary; a failed capture
        remains a native exception, never an empty substitute.

        Returns:
            A successful result when all consumed native queries still agree.

        """
        effects = (
            publications
            if isinstance(publications, m.Cli.AtomicDirectoryQueryEffects)
            else None
        )
        return r[bool].ok(
            FlextCliUtilitiesAtomicTreeInventory.verify_directory_queries(
                inventories,
                topology,
                m.Cli.AtomicDirectoryQueryProof(
                    files=publications if effects is None else effects.files,
                    membership_policy=(
                        None if effects is None else effects.membership_policy
                    ),
                    directories=directory_publications,
                    observations=observations,
                ),
            )
        )

    @staticmethod
    def atomic_inventory_physical_directory(
        root_path: t.Cli.TextPath,
    ) -> p.Result[p.Cli.AtomicDirectoryInventory]:
        """Capture immediate namespace elections without reading descendant bytes.

        Returns:
            The resulting ``p.Result[p.Cli.AtomicDirectoryInventory]``.

        """
        try:
            inventory = (
                FlextCliUtilitiesAtomicTreeInventory.inventory_physical_directory(
                    Path(root_path)
                )
            )
        except OSError as exc:
            return r[p.Cli.AtomicDirectoryInventory].fail(
                c.Cli.ERR_ATOMIC_PHYSICAL_TREE_INVENTORY_FAILED.format(error=exc),
                exception=exc,
            )
        return r[p.Cli.AtomicDirectoryInventory].ok(inventory)

    @staticmethod
    def atomic_inventory_physical_tree(
        root_path: t.Cli.TextPath,
    ) -> p.Result[p.Cli.AtomicPhysicalTreeManifest]:
        """Return an exact descriptor-authenticated tree manifest.

        The root, every parent binding, regular-file digest, and physical directory
        identity are recorded. Linux mount IDs reject bind aliases before their
        contents are read; unsupported hosts fail closed. Hardlinks, special nodes,
        and device or mount transitions also fail. The caller retains one exclusive
        cooperative lock through inventory and cleanup.

        Returns:
            An exact descriptor-authenticated tree manifest.

        """
        try:
            manifest = FlextCliUtilitiesAtomicTreeInventory.inventory_physical_tree(
                Path(root_path),
            )
        except OSError as exc:
            return r[p.Cli.AtomicPhysicalTreeManifest].fail(
                c.Cli.ERR_ATOMIC_PHYSICAL_TREE_INVENTORY_FAILED.format(error=exc),
                exception=exc,
            )
        return r[p.Cli.AtomicPhysicalTreeManifest].ok(manifest)

    @staticmethod
    def atomic_cleanup_physical_tree_guarded(
        manifest: p.Cli.AtomicPhysicalTreeManifest,
    ) -> p.Result[bool]:
        """Delete only an unchanged manifested tree under one exclusive lock.

        Every affected parent is authenticated and sync-probed before a complete
        inventory comparison and the first namespace mutation. Files and then empty
        directories are removed without recursion. A later storage failure can
        leave an authenticated deletion prefix, so the caller must retain recovery
        state. Writers that ignore the caller's lock are outside this contract.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        try:
            FlextCliUtilitiesAtomicTreeCleanup.cleanup_physical_tree_guarded(manifest)
        except OSError as exc:
            return r[bool].fail(
                c.Cli.ERR_ATOMIC_PHYSICAL_TREE_CLEANUP_FAILED.format(error=exc),
                exception=exc,
            )
        return r[bool].ok(value=True)


__all__: list[str] = ["FlextCliUtilitiesFilesPart05"]
