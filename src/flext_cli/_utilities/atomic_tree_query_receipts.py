"""Directory-query receipts: native predicates and witness-epoch merging.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
from bisect import bisect_left
from collections.abc import MutableMapping, Sequence
from itertools import chain
from pathlib import Path
from typing import ClassVar, Literal

from flext_cli import m, p, t


class FlextCliUtilitiesAtomicTreeQueryReceipts:
    """Evaluate and merge descriptor-authenticated directory-query receipts."""

    _SELECTOR_FIELDS: ClassVar[set[str]] = {
        "queries",
        "membership_queried",
        "membership_queries",
    }

    @staticmethod
    def directory_membership_value(
        inventory: p.Cli.AtomicDirectoryInventory,
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
        inventory: p.Cli.AtomicDirectoryInventory,
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
    def merge_directory_query_receipts(
        cls,
        inventories: tuple[p.Cli.AtomicDirectoryInventory, ...],
        topology: tuple[p.Cli.AtomicDirectoryChainPlan, ...],
        selectors: m.Cli.AtomicDirectoryWorkingSelectors,
    ) -> tuple[
        tuple[p.Cli.AtomicDirectoryInventory, ...],
        tuple[p.Cli.AtomicDirectoryChainPlan, ...],
    ]:
        """Finalize working selectors once over agreeing original native witnesses.

        Working selectors are invocation-local state indexed by witness
        identity, never mutable fields on frozen physical inventories. Every
        selected query crosses alias validation even for one original;
        unchanged finalized receipts retain their original model identities.

        Returns:
            The directory inventories and ancestry plans with united selectors.

        """
        directories: MutableMapping[Path, list[p.Cli.AtomicDirectoryInventory]] = {}
        chains: MutableMapping[Path, list[p.Cli.AtomicDirectoryChainPlan]] = {}
        for incoming in inventories:
            directories.setdefault(incoming.root.path, []).append(incoming)
        for witness in topology:
            chains.setdefault(witness.target, []).append(witness)
        return (
            tuple(
                cls._merge_directory_witnesses(originals, selectors)
                for originals in directories.values()
            ),
            tuple(
                cls._merge_topology_witnesses(witnesses, selectors)
                for witnesses in chains.values()
            ),
        )

    @classmethod
    def _merge_directory_witnesses(
        cls,
        originals: Sequence[p.Cli.AtomicDirectoryInventory],
        selectors: m.Cli.AtomicDirectoryWorkingSelectors,
    ) -> p.Cli.AtomicDirectoryInventory:
        """Merge the witnesses of one physical directory into one receipt.

        Returns:
            The original receipt when its selectors are already united,
            otherwise one receipt carrying the united selectors.

        """
        previous = originals[0]
        selection = cls._united_selection(originals, selectors)
        for name, predicate in selection.queries:
            cls.directory_query_value(previous, name, predicate)
        # Witnesses sharing one physical entry tuple answer every query
        # identically; only distinct observations need comparison.
        cls._require_directory_witness_agreement(previous, originals, selection)
        if cls._selection_unchanged(previous, selection):
            return previous
        return m.Cli.AtomicDirectoryInventory(
            root=previous.root,
            entries=previous.entries,
            queries=selection.queries,
            membership_queried=selection.membership_queried,
            membership_queries=selection.membership_queries,
        )

    @classmethod
    def _merge_topology_witnesses(
        cls,
        witnesses: Sequence[p.Cli.AtomicDirectoryChainPlan],
        selectors: m.Cli.AtomicDirectoryWorkingSelectors,
    ) -> p.Cli.AtomicDirectoryChainPlan:
        """Merge the ancestry witnesses of one target into one plan.

        Returns:
            The original plan when its selectors are already united,
            otherwise one plan carrying the united selectors.

        Raises:
            ValueError: If the witnesses observed different ancestry epochs.

        """
        previous = witnesses[0]
        observed = previous.model_dump(exclude=cls._SELECTOR_FIELDS)
        if any(
            incoming.model_dump(exclude=cls._SELECTOR_FIELDS) != observed
            for incoming in witnesses
        ):
            msg = f"source directory ancestry epochs disagree: {previous.target}"
            raise ValueError(msg)
        selection = cls._united_selection(witnesses, selectors)
        if cls._selection_unchanged(previous, selection):
            return previous
        return m.Cli.AtomicDirectoryChainPlan(
            target=previous.target,
            anchor_path=previous.anchor_path,
            anchor_device=previous.anchor_device,
            anchor_inode=previous.anchor_inode,
            anchor_ancestry=previous.anchor_ancestry,
            directories=previous.directories,
            queries=selection.queries,
            membership_queried=selection.membership_queried,
            membership_queries=selection.membership_queries,
        )

    @staticmethod
    def _united_selection(
        witnesses: Sequence[
            p.Cli.AtomicDirectoryInventory | p.Cli.AtomicDirectoryChainPlan
        ],
        selectors: m.Cli.AtomicDirectoryWorkingSelectors,
    ) -> m.Cli.AtomicDirectorySelection:
        """Unite receipt and working selectors across every original witness.

        Returns:
            The sorted united query and membership selection.

        """
        return m.Cli.AtomicDirectorySelection(
            queries=tuple(
                sorted({
                    query
                    for item in witnesses
                    for query in chain(
                        item.queries, selectors.queries.get(id(item), ())
                    )
                })
            ),
            membership_queried=any(item.membership_queried for item in witnesses),
            membership_queries=tuple(
                sorted({
                    selection
                    for item in witnesses
                    for selection in chain(
                        item.membership_queries,
                        selectors.membership_queries.get(id(item), ()),
                    )
                })
            ),
        )

    @staticmethod
    def _selection_unchanged(
        receipt: p.Cli.AtomicDirectoryInventory | p.Cli.AtomicDirectoryChainPlan,
        selection: m.Cli.AtomicDirectorySelection,
    ) -> bool:
        """Report whether one receipt already carries the united selection.

        Returns:
            Whether the receipt can be retained by identity.

        """
        return (
            selection.queries,
            selection.membership_queried,
            selection.membership_queries,
        ) == (
            receipt.queries,
            receipt.membership_queried,
            receipt.membership_queries,
        )

    @classmethod
    def _require_directory_witness_agreement(
        cls,
        previous: p.Cli.AtomicDirectoryInventory,
        originals: Sequence[p.Cli.AtomicDirectoryInventory],
        selection: m.Cli.AtomicDirectorySelection,
    ) -> None:
        """Require distinct directory witnesses to answer every query alike.

        Raises:
            ValueError: If witness identity, query, or membership epochs disagree.

        """
        path = previous.root.path
        selections = (
            *(((),) if selection.membership_queried else ()),
            *selection.membership_queries,
        )
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
                for name, predicate in selection.queries
            ):
                msg = f"source directory query epochs disagree: {path}"
                raise ValueError(msg)
            if any(
                cls.directory_membership_value(previous, excluded)
                != cls.directory_membership_value(incoming, excluded)
                for excluded in selections
            ):
                msg = f"source directory membership epochs disagree: {path}"
                raise ValueError(msg)

    @staticmethod
    def _require_directory_identity(
        expected: p.Cli.AtomicPhysicalTreeEntry,
        observed: p.Cli.AtomicPhysicalTreeEntry,
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


__all__: list[str] = ["FlextCliUtilitiesAtomicTreeQueryReceipts"]
