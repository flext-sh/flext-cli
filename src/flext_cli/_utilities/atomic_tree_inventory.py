"""Descriptor-authenticated inventory for one physical filesystem tree.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import os
import stat
from bisect import bisect_left
from collections.abc import Generator, Iterable, Mapping, MutableMapping, Sequence
from contextlib import contextmanager
from itertools import chain
from pathlib import Path
from types import MappingProxyType
from typing import Literal, Never

from flext_cli import m, t
from flext_cli._utilities import (
    FlextCliUtilitiesAtomicDirectoryChain,
    FlextCliUtilitiesAtomicDirectoryDescriptor,
    FlextCliUtilitiesAtomicFileDescriptor,
    FlextCliUtilitiesAtomicFilePath,
    FlextCliUtilitiesAtomicFileRead,
    FlextCliUtilitiesAtomicFileState,
    FlextCliUtilitiesAtomicParentDescriptor,
    FlextCliUtilitiesAtomicParentFailure,
    FlextCliUtilitiesAtomicTreeDescriptor,
)


class FlextCliUtilitiesAtomicTreeInventory:
    """Canonical namespace owner."""

    _DIRECTORY_FLAGS = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_BINARY", 0)
    )

    @staticmethod
    def directory_membership_value(
        inventory: m.Cli.AtomicDirectoryInventory,
        excluded_names: t.StrTuple,
    ) -> MutableMapping[str, Literal["directory", "file", "symlink", "other"]]:
        """Evaluate the declared direct-child selection on a physical receipt.

        Returns:
            Selected child names and physical kinds.

        """
        return {
            item.name: item.kind
            for item in inventory.entries
            if item.name not in excluded_names
        }

    @staticmethod
    def directory_query_value(
        inventory: m.Cli.AtomicDirectoryInventory,
        name: str,
        predicate: Literal["exists", "isfile", "isdir"],
    ) -> bool:
        """Evaluate one native predicate from its physical directory receipt.

        Returns:
            Whether the captured child satisfies the native predicate.

        Raises:
            OSError: If the queried child is a physical alias.

        """
        index = bisect_left(inventory.entries, name, key=lambda item: item.name)
        entry = inventory.entries[index] if index < len(inventory.entries) else None
        if entry is not None and entry.name != name:
            entry = None
        if entry is not None and entry.kind == "symlink":
            raise OSError(
                errno.ELOOP,
                "atomic directory query encountered a physical alias",
                inventory.root.path / name,
            )
        return entry is not None and (
            predicate == "exists"
            or entry.kind == ("file" if predicate == "isfile" else "directory")
        )

    @classmethod
    def _require_directory_witness_agreement(
        cls,
        previous: m.Cli.AtomicDirectoryInventory,
        originals: Sequence[m.Cli.AtomicDirectoryInventory],
        path: Path,
        selected_queries: tuple[
            tuple[str, Literal["exists", "isfile", "isdir"]],
            ...,
        ],
        selections: tuple[t.StrTuple, ...],
    ) -> None:
        """Require distinct directory witnesses to answer every query alike.

        Raises:
            ValueError: If witness identity, query, or membership epochs disagree.

        """
        for incoming in {id(item.entries): item for item in originals}.values():
            if incoming.entries is previous.entries:
                continue
            cls._require_directory_identity(
                previous.root,
                incoming.root,
                f"source directory query epochs disagree: {path}",
            )
            if any(
                cls.directory_query_value(previous, name, predicate)
                != cls.directory_query_value(incoming, name, predicate)
                for name, predicate in selected_queries
            ):
                msg = f"source directory query epochs disagree: {path}"
                raise ValueError(msg)
            if any(
                cls.directory_membership_value(previous, selection)
                != cls.directory_membership_value(incoming, selection)
                for selection in selections
            ):
                msg = f"source directory membership epochs disagree: {path}"
                raise ValueError(msg)

    @classmethod
    def merge_directory_query_receipts(
        cls,
        inventories: tuple[m.Cli.AtomicDirectoryInventory, ...],
        topology: tuple[m.Cli.AtomicDirectoryChainPlan, ...],
        *,
        queries: Mapping[
            int, set[tuple[str, Literal["exists", "isfile", "isdir"]]]
        ] = MappingProxyType({}),
        membership_queries: Mapping[int, set[t.StrTuple]] = MappingProxyType({}),
    ) -> tuple[
        tuple[m.Cli.AtomicDirectoryInventory, ...],
        tuple[m.Cli.AtomicDirectoryChainPlan, ...],
    ]:
        """Finalize working selectors once over agreeing original native witnesses.

        Optional selector maps are invocation-local working state indexed by
        witness identity, never mutable fields on frozen physical inventories.
        Every selected query crosses alias validation even for one original;
        unchanged finalized receipts retain their original model identities.

        Returns:
            The directory inventories and ancestry plans with united selectors.

        Raises:
            ValueError: If original identity, query, or membership epochs disagree.

        """
        directories: MutableMapping[Path, list[m.Cli.AtomicDirectoryInventory]] = {}
        chains: MutableMapping[Path, list[m.Cli.AtomicDirectoryChainPlan]] = {}
        for incoming in inventories:
            directories.setdefault(incoming.root.path, []).append(incoming)
        for incoming in topology:
            chains.setdefault(incoming.target, []).append(incoming)
        directory_receipts: list[m.Cli.AtomicDirectoryInventory] = []
        for path, originals in directories.items():
            previous = originals[0]
            selected_queries = tuple(
                sorted({
                    query
                    for item in originals
                    for query in chain(item.queries, queries.get(id(item), ()))
                })
            )
            membership_queried = any(item.membership_queried for item in originals)
            selected_membership = tuple(
                sorted({
                    selection
                    for item in originals
                    for selection in chain(
                        item.membership_queries, membership_queries.get(id(item), ())
                    )
                })
            )
            selections = (*(((),) if membership_queried else ()), *selected_membership)
            for name, predicate in selected_queries:
                cls.directory_query_value(previous, name, predicate)
            # Witnesses sharing one physical entry tuple answer every query
            # identically; only distinct observations need comparison.
            cls._require_directory_witness_agreement(
                previous,
                originals,
                path,
                selected_queries,
                selections,
            )
            directory_receipts.append(
                previous
                if selected_queries == previous.queries
                and membership_queried == previous.membership_queried
                and selected_membership == previous.membership_queries
                else m.Cli.AtomicDirectoryInventory(
                    root=previous.root,
                    entries=previous.entries,
                    queries=selected_queries,
                    membership_queried=membership_queried,
                    membership_queries=selected_membership,
                )
            )
        topology_receipts: list[m.Cli.AtomicDirectoryChainPlan] = []
        for target, witnesses in chains.items():
            previous = witnesses[0]
            if any(
                previous.target != incoming.target
                or previous.anchor_path != incoming.anchor_path
                or previous.anchor_device != incoming.anchor_device
                or previous.anchor_inode != incoming.anchor_inode
                or previous.anchor_ancestry != incoming.anchor_ancestry
                or previous.directories != incoming.directories
                for incoming in witnesses
            ):
                msg = f"source directory ancestry epochs disagree: {target}"
                raise ValueError(msg)
            selected_queries = tuple(
                sorted({
                    query
                    for item in witnesses
                    for query in chain(item.queries, queries.get(id(item), ()))
                })
            )
            membership_queried = any(item.membership_queried for item in witnesses)
            selected_membership = tuple(
                sorted({
                    selection
                    for item in witnesses
                    for selection in chain(
                        item.membership_queries, membership_queries.get(id(item), ())
                    )
                })
            )
            topology_receipts.append(
                previous
                if selected_queries == previous.queries
                and membership_queried == previous.membership_queried
                and selected_membership == previous.membership_queries
                else m.Cli.AtomicDirectoryChainPlan(
                    target=previous.target,
                    anchor_path=previous.anchor_path,
                    anchor_device=previous.anchor_device,
                    anchor_inode=previous.anchor_inode,
                    anchor_ancestry=previous.anchor_ancestry,
                    directories=previous.directories,
                    queries=selected_queries,
                    membership_queried=membership_queried,
                    membership_queries=selected_membership,
                )
            )
        return tuple(directory_receipts), tuple(topology_receipts)

    @staticmethod
    def _require_directory_identity(
        expected: m.Cli.AtomicPhysicalTreeEntry,
        observed: m.Cli.AtomicPhysicalTreeEntry,
        diagnostic: str,
    ) -> None:
        """Reject changed physical identity without freezing child membership.

        Raises:
            ValueError: If any original field except membership timestamps and
                link count differs.

        """
        mutable_membership = {"mtime_ns", "ctime_ns", "link_count"}
        if expected.model_dump(exclude=mutable_membership) != observed.model_dump(
            exclude=mutable_membership
        ):
            raise ValueError(diagnostic)

    @classmethod
    def verify_directory_queries(
        cls,
        inventories: tuple[m.Cli.AtomicDirectoryInventory, ...],
        topology: tuple[m.Cli.AtomicDirectoryChainPlan, ...],
        publications: tuple[tuple[m.Cli.AtomicFileState, m.Cli.AtomicFileState], ...]
        | m.Cli.AtomicDirectoryQueryEffects = (),
        directory_publications: tuple[m.Cli.AtomicDirectoryState, ...] = (),
        observations: m.Cli.AtomicDirectoryObservations | None = None,
    ) -> bool:
        """Reprove consumed elections, allowing only supplied physical own effects.

        One verification boundary shares one native observation per physical
        directory and one ancestry observation per target through
        ``observations``, passed by reference. It never outlives that boundary.
        Every original receipt is compared, including shared targets.

        Returns:
            True when every consumed query and physical identity still agrees.

        Raises:
            ValueError: If receipts disagree or an unaccounted change is observed.

        """
        publications = cls._require_membership_policy(
            inventories, topology, publications
        )
        shared = observations or m.Cli.AtomicDirectoryObservations()
        boundary = shared.directories
        published = {before.path: (before, after) for before, after in publications}
        created = {item.path: item for item in directory_publications}
        if len(published) != len(publications) or any(
            before.path != after.path for before, after in publications
        ):
            msg = "directory query publication identities disagree"
            raise ValueError(msg)
        ancestors = cls._published_ancestors(publications)
        cls._verify_query_topology(
            topology, published, created, boundary, shared.topology
        )
        for expected in inventories:
            observed = cls._observe_physical_directory(boundary, expected.root.path)
            cls._require_directory_identity(
                expected.root,
                observed.root,
                f"source directory physical identity changed: {expected.root.path}",
            )
            unchanged = (
                not published
                and not created
                and observed.entries == expected.entries
                and all(entry.kind != "symlink" for entry in expected.entries)
            )
            # An unchanged alias-free membership answers every query exactly as
            # originally observed; no per-query evaluation is needed.
            for name, predicate in () if unchanged else expected.queries:
                value = cls.directory_query_value(expected, name, predicate)
                effect = published.get(expected.root.path / name)
                if effect is not None:
                    before, after = effect
                    before_value = before.content is not None and predicate != "isdir"
                    if value != before_value:
                        msg = f"source query preimage changed: {before.path}"
                        raise ValueError(msg)
                    value = after.content is not None and predicate != "isdir"
                elif predicate != "isfile" and (
                    expected.root.path / name in created
                    or expected.root.path / name in ancestors
                ):
                    # A directory the preimage already held needs no creation
                    # receipt for publications beneath it; only an own creation
                    # or a directory the preimage lacked must bind to one.
                    if expected.root.path / name in created or not (
                        cls.directory_query_value(expected, name, "isdir")
                    ):
                        cls._published_directory_current(
                            expected.root.path / name, created
                        )
                    value = True
                observed_value = cls.directory_query_value(observed, name, predicate)
                if value != observed_value:
                    msg = (
                        f"source directory query changed: "
                        f"{expected.root.path / name}; predicate={predicate}; "
                        f"expected={value}; observed={observed_value}"
                    )
                    raise ValueError(msg)
            for selection in (
                ()
                if unchanged
                else (
                    *(((),) if expected.membership_queried else ()),
                    *expected.membership_queries,
                )
            ):
                cls._verify_query_membership(
                    observed,
                    cls.directory_membership_value(expected, selection),
                    publications,
                    created,
                    selection,
                )
        return True

    @staticmethod
    def _published_ancestors(
        publications: Iterable[tuple[m.Cli.AtomicFileState, m.Cli.AtomicFileState]],
    ) -> Mapping[Path, None]:
        """Return every ancestor path already held by a published file.

        Returns:
            The ancestor path membership.

        """
        return dict.fromkeys(
            path
            for _before, after in publications
            if after.content is not None
            for path in (after.path, *after.path.parents)
        )

    @staticmethod
    def _require_membership_policy(
        inventories: tuple[m.Cli.AtomicDirectoryInventory, ...],
        topology: tuple[m.Cli.AtomicDirectoryChainPlan, ...],
        publications: tuple[tuple[m.Cli.AtomicFileState, m.Cli.AtomicFileState], ...]
        | m.Cli.AtomicDirectoryQueryEffects,
    ) -> tuple[tuple[m.Cli.AtomicFileState, m.Cli.AtomicFileState], ...]:
        """Reject receipt-selected authority before observing native dependencies.

        Returns:
            Native publication effects after independent authority election.

        Raises:
            ValueError: If a receipt selects authority not elected by the caller.

        """
        membership_policy = (
            publications.membership_policy
            if isinstance(publications, m.Cli.AtomicDirectoryQueryEffects)
            else None
        )
        if any(
            selection != membership_policy
            for queries in chain(
                (receipt.membership_queries for receipt in inventories),
                (receipt.membership_queries for receipt in topology),
            )
            for selection in queries
        ):
            msg = "source membership selection differs from admitted policy"
            raise ValueError(msg)
        return (
            publications.files
            if isinstance(publications, m.Cli.AtomicDirectoryQueryEffects)
            else publications
        )

    @classmethod
    def _verify_query_topology(
        cls,
        topology: tuple[m.Cli.AtomicDirectoryChainPlan, ...],
        published: Mapping[Path, tuple[m.Cli.AtomicFileState, m.Cli.AtomicFileState]],
        created: Mapping[Path, m.Cli.AtomicDirectoryState],
        observations: MutableMapping[Path, m.Cli.AtomicDirectoryInventory],
        topology_observations: MutableMapping[Path, m.Cli.AtomicDirectoryChainPlan],
    ) -> None:
        """Reprove absent-parent elections against the original native ancestry.

        The authenticated publication index supplies both file effects and their
        ancestors; no parallel transport of the same effects is needed.

        Raises:
            ValueError: If ancestry or an absent candidate changed unexpectedly.

        """
        publications = published.values()
        ancestors = cls._published_ancestors(publications)
        for witness in topology:
            observed = topology_observations.get(witness.target)
            if observed is None:
                observed = FlextCliUtilitiesAtomicDirectoryChain.plan_directory_chain(
                    witness.target
                )
                topology_observations[witness.target] = observed
            gained = witness.directories[
                : max(0, len(witness.directories) - len(observed.directories))
            ]
            ancestry = dict(
                zip(
                    reversed((observed.anchor_path, *observed.anchor_path.parents)),
                    observed.anchor_ancestry,
                    strict=True,
                )
            )
            if observed.model_dump(
                exclude={"queries", "membership_queried", "membership_queries"}
            ) != witness.model_dump(
                exclude={"queries", "membership_queried", "membership_queries"}
            ) and not (
                gained
                and observed.anchor_path == gained[-1]
                and observed.directories == witness.directories[len(gained) :]
                and observed.anchor_ancestry[: len(witness.anchor_ancestry)]
                == witness.anchor_ancestry
                and all(
                    path in created
                    and created[path].exists
                    and ancestry.get(path)
                    == (created[path].device, created[path].inode)
                    and ancestry.get(path.parent)
                    == (created[path].parent_device, created[path].parent_inode)
                    for path in gained
                )
            ):
                msg = f"source directory ancestry changed: {witness.target}"
                raise ValueError(msg)
            if (
                witness.queries
                or witness.membership_queried
                or witness.membership_queries
            ) and not observed.directories:
                inventory = cls._observe_physical_directory(
                    observations, witness.target
                )
                for name, predicate in witness.queries:
                    path = witness.target / name
                    effect = published.get(path)
                    value = (
                        effect[1].content is not None and predicate != "isdir"
                        if effect is not None
                        else predicate != "isfile" and path in ancestors
                    )
                    if predicate != "isfile" and path in created:
                        cls._published_directory_current(path, created)
                        value = True
                    if value and effect is None:
                        cls._published_directory_current(path, created)
                    if value != cls.directory_query_value(inventory, name, predicate):
                        msg = f"absent source candidate changed: {path}"
                        raise ValueError(msg)
                for selection in (
                    *(((),) if witness.membership_queried else ()),
                    *witness.membership_queries,
                ):
                    cls._verify_query_membership(
                        inventory, {}, publications, created, selection
                    )

    @classmethod
    def _verify_query_membership(
        cls,
        observed: m.Cli.AtomicDirectoryInventory,
        members: MutableMapping[str, Literal["directory", "file", "symlink", "other"]],
        publications: Iterable[tuple[m.Cli.AtomicFileState, m.Cli.AtomicFileState]],
        created: Mapping[Path, m.Cli.AtomicDirectoryState],
        excluded_names: t.StrTuple = (),
    ) -> None:
        """Reprove direct membership with only original native publication effects.

        Raises:
            ValueError: If direct membership or a published directory kind changed.

        """
        root = observed.root.path
        for path in created:
            if path.parent == root:
                cls._published_directory_current(path, created)
                if members.get(path.name) not in {None, "directory"}:
                    msg = f"source directory kind changed: {path}"
                    raise ValueError(msg)
                members[path.name] = "directory"
        for _before, after in publications:
            if after.path.parent == root:
                if after.content is None:
                    members.pop(after.path.name, None)
                else:
                    members[after.path.name] = "file"
            elif after.content is not None and after.path.is_relative_to(root):
                child = root / after.path.relative_to(root).parts[0]
                if child in created or members.get(child.name) != "directory":
                    cls._published_directory_current(child, created)
                members[child.name] = "directory"
        members = {
            name: kind for name, kind in members.items() if name not in excluded_names
        }
        actual = cls.directory_membership_value(observed, excluded_names)
        if members != actual:
            added = sorted(actual.keys() - members.keys())
            removed = sorted(members.keys() - actual.keys())
            changed = [
                (name, members[name], actual[name])
                for name in sorted(members.keys() & actual.keys())
                if members[name] != actual[name]
            ]
            msg = (
                f"source directory membership changed: {root}; "
                f"added={added!r}; removed={removed!r}; kind_changed={changed!r}"
            )
            raise ValueError(msg)

    @staticmethod
    def _published_directory_current(
        path: Path,
        created: Mapping[Path, m.Cli.AtomicDirectoryState],
    ) -> None:
        """Bind an elected own directory to the publisher's original inode.

        Raises:
            ValueError: If the original directory or parent inode no longer agrees.

        """
        receipt = created.get(path)
        observed = FlextCliUtilitiesAtomicDirectoryChain.plan_directory_chain(path)
        if (
            receipt is None
            or not receipt.exists
            or observed.directories
            or (observed.anchor_device, observed.anchor_inode)
            != (receipt.device, receipt.inode)
            or observed.anchor_ancestry[-2]
            != (receipt.parent_device, receipt.parent_inode)
        ):
            msg = f"source directory lacks its original publication: {path}"
            raise ValueError(msg)

    @classmethod
    def _observe_physical_directory(
        cls,
        observations: MutableMapping[Path, m.Cli.AtomicDirectoryInventory],
        root_path: Path,
    ) -> m.Cli.AtomicDirectoryInventory:
        """Return one boundary-scoped native observation of a physical directory.

        The first request inside a verification boundary takes the fresh native
        inventory; later requests for the same path in that boundary reuse that
        one observation. The store is owned by the caller and never outlives the
        boundary, so no receipt is replayed across boundaries.

        Returns:
            The boundary-scoped native observation of the directory.

        """
        observed = observations.get(root_path)
        if observed is None:
            observed = cls.inventory_physical_directory(root_path)
            observations[root_path] = observed
        return observed

    @staticmethod
    def inventory_physical_directory(root_path: Path) -> m.Cli.AtomicDirectoryInventory:
        """Capture immediate elections without descending or hashing child payloads.

        Returns:
            The inventory of the immediate child names with their
            authenticated kinds and version keys.

        """
        with FlextCliUtilitiesAtomicTreeInventory._opened_root(root_path) as (
            root,
            parent,
        ):
            names = FlextCliUtilitiesAtomicTreeInventory._directory_names(
                parent.descriptor
            )
            entries: list[m.Cli.AtomicDirectoryName] = []
            for name in names:
                path = root.path / name
                child = FlextCliUtilitiesAtomicFileDescriptor.entry_stat(parent, path)
                kind: Literal["directory", "file", "symlink", "other"]
                if stat.S_ISDIR(child.st_mode):
                    kind = "directory"
                elif stat.S_ISREG(child.st_mode):
                    kind = "file"
                elif stat.S_ISLNK(child.st_mode):
                    kind = "symlink"
                else:
                    kind = "other"
                entries.append(
                    m.Cli.AtomicDirectoryName(
                        name=name,
                        kind=kind,
                        version_key=FlextCliUtilitiesAtomicFileRead.state_key(child),
                        link_target=os.readlink(name, dir_fd=parent.descriptor)
                        if kind == "symlink"
                        else None,
                    )
                )
                FlextCliUtilitiesAtomicTreeDescriptor.require_entry_state(
                    parent, path, child
                )
            if names != FlextCliUtilitiesAtomicTreeInventory._directory_names(
                parent.descriptor
            ):
                FlextCliUtilitiesAtomicTreeInventory._raise_changed(root.path)
        return m.Cli.AtomicDirectoryInventory(root=root, entries=tuple(entries))

    @staticmethod
    def inventory_physical_tree(root_path: Path) -> m.Cli.AtomicPhysicalTreeManifest:
        """Inventory one exact tree through non-aliased directory descriptors.

        The shared root acquisition rejects a missing physical-tree root with
        ``FileNotFoundError`` before any descendant is read.

        Returns:
            The resulting ``m.Cli.AtomicPhysicalTreeManifest``.

        """
        root_path = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(root_path)
        entries: list[m.Cli.AtomicPhysicalTreeEntry] = []
        with FlextCliUtilitiesAtomicTreeInventory._opened_root(root_path) as (
            root,
            parent,
        ):
            FlextCliUtilitiesAtomicTreeDescriptor.require_same_device(
                root.path, os.fstat(parent.lineage[-1]), parent.state
            )
            FlextCliUtilitiesAtomicTreeDescriptor.require_mount(
                root.path, root.parent_mount_id, root.mount_id
            )
            FlextCliUtilitiesAtomicTreeInventory._inventory_directory(
                parent, root.mount_id, entries, {(root.device, root.inode)}
            )
        return m.Cli.AtomicPhysicalTreeManifest(
            root=root,
            entries=tuple(
                sorted(
                    entries, key=FlextCliUtilitiesAtomicTreeInventory._entry_path_key
                )
            ),
        )

    @staticmethod
    @contextmanager
    def _opened_root(
        root_path: Path,
    ) -> Generator[
        tuple[
            m.Cli.AtomicPhysicalTreeEntry,
            FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        ]
    ]:
        """Retain one shared root acquisition for shallow and recursive inventories.

        Yields:
            The authenticated root entry and its retained parent descriptor
            for the duration of the inventory.

        """
        root_path = FlextCliUtilitiesAtomicFilePath.validate_directory_path(root_path)
        FlextCliUtilitiesAtomicDirectoryDescriptor.require_read_capabilities(root_path)
        with FlextCliUtilitiesAtomicParentDescriptor.physical_directory(
            root_path,
        ) as opened:
            parent_descriptor = (
                opened.lineage[-1] if opened.lineage else opened.descriptor
            )
            parent_state = os.fstat(parent_descriptor)
            parent_mount_id = FlextCliUtilitiesAtomicTreeDescriptor.mount_id(
                parent_descriptor,
                root_path.parent,
            )
            root_mount_id = FlextCliUtilitiesAtomicTreeDescriptor.mount_id(
                opened.descriptor,
                root_path,
            )
            root = FlextCliUtilitiesAtomicTreeInventory._entry(
                root_path,
                parent_state,
                opened.state,
                m.Cli.TreeEntryDetails(
                    kind="directory",
                    parent_mount_id=parent_mount_id,
                    mount_id=root_mount_id,
                ),
            )
            root_parent = FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor(
                root_path,
                opened.descriptor,
                opened.state,
                opened.ancestry,
                opened.lineage,
            )

            def recheck() -> None:
                FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
                    opened.descriptor,
                    root_path,
                    opened.state,
                )
                FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(
                    root_parent
                )

            try:
                yield root, root_parent
            except BaseException as exc:
                FlextCliUtilitiesAtomicParentFailure.preserve_recheck_failure(
                    root_path, exc, recheck
                )
                raise
            recheck()

    @staticmethod
    def _inventory_directory(
        parent: FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor,
        parent_mount_id: int,
        entries: list[m.Cli.AtomicPhysicalTreeEntry],
        directory_identities: set[tuple[int, int]],
    ) -> None:
        FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
            parent.descriptor,
            parent.path,
            parent.state,
        )
        names = FlextCliUtilitiesAtomicTreeInventory._directory_names(parent.descriptor)
        for name in names:
            path = parent.path / name
            observed = FlextCliUtilitiesAtomicFileDescriptor.entry_stat(parent, path)
            if stat.S_ISDIR(observed.st_mode):
                FlextCliUtilitiesAtomicFilePath.validate_directory_state(path, observed)
                FlextCliUtilitiesAtomicTreeDescriptor.require_same_device(
                    path,
                    parent.state,
                    observed,
                )
                identity = FlextCliUtilitiesAtomicFilePath.identity(observed)
                if identity in directory_identities:
                    message = f"atomic physical-tree directory identity repeats: {path}"
                    raise OSError(errno.ELOOP, message, path)
                with FlextCliUtilitiesAtomicFileDescriptor.entry_descriptor(
                    parent,
                    path,
                    FlextCliUtilitiesAtomicTreeInventory._DIRECTORY_FLAGS,
                ) as descriptor:
                    FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
                        descriptor,
                        path,
                        observed,
                    )
                    mount_id = FlextCliUtilitiesAtomicTreeDescriptor.mount_id(
                        descriptor,
                        path,
                    )
                    FlextCliUtilitiesAtomicTreeDescriptor.require_mount(
                        path,
                        parent_mount_id,
                        mount_id,
                    )
                    directory_identities.add(identity)
                    entries.append(
                        FlextCliUtilitiesAtomicTreeInventory._entry(
                            path,
                            parent.state,
                            observed,
                            m.Cli.TreeEntryDetails(
                                kind="directory",
                                parent_mount_id=parent_mount_id,
                                mount_id=mount_id,
                            ),
                        ),
                    )
                    child_parent = (
                        FlextCliUtilitiesAtomicFileDescriptor.ParentDescriptor(
                            path,
                            descriptor,
                            observed,
                            (
                                *parent.ancestry,
                                FlextCliUtilitiesAtomicFilePath.identity(observed),
                            ),
                            (*parent.lineage, parent.descriptor),
                        )
                    )
                    FlextCliUtilitiesAtomicTreeInventory._inventory_directory(
                        child_parent,
                        mount_id,
                        entries,
                        directory_identities,
                    )
                    FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
                        descriptor,
                        path,
                        observed,
                    )
                FlextCliUtilitiesAtomicTreeDescriptor.require_entry_state(
                    parent,
                    path,
                    observed,
                )
            elif stat.S_ISREG(observed.st_mode):
                authenticated = FlextCliUtilitiesAtomicFileState.destination_state(
                    path,
                    parent=parent,
                )
                if authenticated is None:
                    FlextCliUtilitiesAtomicTreeInventory._raise_changed(path)
                FlextCliUtilitiesAtomicTreeDescriptor.require_same_device(
                    path,
                    parent.state,
                    authenticated,
                )
                size, digest = (
                    FlextCliUtilitiesAtomicTreeDescriptor.measure_authenticated_file(
                        parent,
                        path,
                        authenticated,
                        required_mount_id=parent_mount_id,
                    )
                )
                entries.append(
                    FlextCliUtilitiesAtomicTreeInventory._entry(
                        path,
                        parent.state,
                        authenticated,
                        m.Cli.TreeEntryDetails(
                            kind="file",
                            parent_mount_id=parent_mount_id,
                            size=size,
                            digest=digest,
                            mount_id=parent_mount_id,
                        ),
                    ),
                )
            elif stat.S_ISLNK(observed.st_mode):
                target = os.readlink(name, dir_fd=parent.descriptor)
                if not target:
                    FlextCliUtilitiesAtomicTreeInventory._raise_changed(path)
                FlextCliUtilitiesAtomicTreeDescriptor.require_entry_state(
                    parent,
                    path,
                    observed,
                )
                FlextCliUtilitiesAtomicTreeDescriptor.require_same_device(
                    path,
                    parent.state,
                    observed,
                )
                entries.append(
                    FlextCliUtilitiesAtomicTreeInventory._entry(
                        path,
                        parent.state,
                        observed,
                        m.Cli.TreeEntryDetails(
                            kind="symlink",
                            parent_mount_id=parent_mount_id,
                            mount_id=parent_mount_id,
                            link_target=target,
                        ),
                    ),
                )
            else:
                message = (
                    f"atomic physical-tree entry is not regular or a directory: {path}"
                )
                raise OSError(errno.EINVAL, message, path)
        if (
            FlextCliUtilitiesAtomicTreeInventory._directory_names(parent.descriptor)
            != names
        ):
            FlextCliUtilitiesAtomicTreeInventory._raise_changed(parent.path)
        FlextCliUtilitiesAtomicTreeDescriptor.require_directory_state(
            parent.descriptor,
            parent.path,
            parent.state,
        )

    @staticmethod
    def _entry(
        path: Path,
        parent: os.stat_result,
        observed: os.stat_result,
        details: m.Cli.TreeEntryDetails,
    ) -> m.Cli.AtomicPhysicalTreeEntry:
        if details.kind == "file" and observed.st_nlink > 1:
            # Cleanup authority is per pathname; a second physical name sharing
            # the inode means pruning this tree must not silently claim the
            # sibling's content. Read/replace paths stay permissive — this
            # refusal owns the cleanup verb only.
            message = (
                f"cleanup authority refused: {path} has {observed.st_nlink} hard"
                " links (another physical name owns the same inode); "
                f"device={observed.st_dev} inode={observed.st_ino}"
            )
            raise OSError(errno.EMLINK, message, path)
        return m.Cli.AtomicPhysicalTreeEntry(
            path=path,
            kind=details.kind,
            parent_device=parent.st_dev,
            parent_inode=parent.st_ino,
            parent_mount_id=details.parent_mount_id,
            mode=stat.S_IMODE(observed.st_mode),
            device=observed.st_dev,
            inode=observed.st_ino,
            mount_id=details.mount_id,
            link_count=observed.st_nlink,
            uid=observed.st_uid,
            gid=observed.st_gid,
            mtime_ns=observed.st_mtime_ns,
            ctime_ns=observed.st_ctime_ns,
            file_attributes=getattr(observed, "st_file_attributes", None),
            reparse_tag=getattr(observed, "st_reparse_tag", None),
            size=details.size,
            sha256=details.digest,
            link_target=details.link_target,
        )

    @staticmethod
    def _directory_names(descriptor: int) -> tuple[str, ...]:
        """Enumerate names through the authenticated directory descriptor.

        Returns:
            The resulting ``tuple[str, ...],``.

        """
        with os.scandir(descriptor) as entries:
            return tuple(sorted(entry.name for entry in entries))

    @staticmethod
    def _entry_path_key(entry: m.Cli.AtomicPhysicalTreeEntry) -> str:
        """Return the deterministic lexical manifest key.

        Returns:
            The deterministic lexical manifest key.

        """
        return entry.path.as_posix()

    @staticmethod
    def _raise_changed(path: Path) -> Never:
        message = f"atomic physical-tree entry changed during inventory: {path}"
        raise OSError(errno.ESTALE, message, path)


__all__: list[str] = ["FlextCliUtilitiesAtomicTreeInventory"]
