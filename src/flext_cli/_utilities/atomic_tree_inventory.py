"""Reproof of consumed directory-query receipts against native observations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from itertools import chain
from pathlib import Path
from typing import Literal

from flext_cli import m, p, t
from flext_cli._utilities.atomic_tree_query_topology import (
    FlextCliUtilitiesAtomicTreeQueryTopology,
)


class FlextCliUtilitiesAtomicTreeInventory(
    FlextCliUtilitiesAtomicTreeQueryTopology,
):
    """Reprove consumed directory elections inside one verification boundary."""

    @classmethod
    def verify_directory_queries(
        cls,
        inventories: tuple[p.Cli.AtomicDirectoryInventory, ...],
        topology: tuple[p.Cli.AtomicDirectoryChainPlan, ...],
        proof: p.Cli.AtomicDirectoryQueryProof,
    ) -> bool:
        """Reprove consumed elections, allowing only supplied physical own effects.

        One verification boundary shares one native observation per physical
        directory and one ancestry observation per target through
        ``proof``, passed by reference. It never outlives that
        boundary. Every original receipt is compared, including shared targets.

        Returns:
            True when every consumed query and physical identity still agrees.

        """
        cls._require_membership_policy(inventories, topology, proof.membership_policy)
        boundary = cls._query_boundary(proof)
        cls._verify_query_topology(topology, boundary)
        for expected in inventories:
            cls._verify_inventory_queries(expected, boundary)
        return True

    @classmethod
    def _query_boundary(
        cls,
        proof: p.Cli.AtomicDirectoryQueryProof,
    ) -> p.Cli.AtomicDirectoryQueryBoundary:
        """Index the own effects and observations of one verification boundary.

        Returns:
            The publication, creation, and ancestor indexes with the shared
            native observations.

        Raises:
            ValueError: If two file effects claim one destination or one
                effect changes its destination.

        """
        published = {before.path: (before, after) for before, after in proof.files}
        if len(published) != len(proof.files) or any(
            before.path != after.path for before, after in proof.files
        ):
            msg = "directory query publication identities disagree"
            raise ValueError(msg)
        return m.Cli.AtomicDirectoryQueryBoundary(
            published=published,
            created={item.path: item for item in proof.directories},
            ancestors=cls._published_ancestors(proof.files),
            directory_observations=proof.directory_observations,
            topology_observations=proof.topology_observations,
        )

    @classmethod
    def _verify_inventory_queries(
        cls,
        expected: p.Cli.AtomicDirectoryInventory,
        boundary: p.Cli.AtomicDirectoryQueryBoundary,
    ) -> None:
        """Reprove one directory receipt's identity, queries, and membership."""
        observed = cls._observe_physical_directory(
            boundary.directory_observations, expected.root.path
        )
        cls._require_directory_identity(
            expected.root,
            observed.root,
            f"source directory physical identity changed: {expected.root.path}",
        )
        # An unchanged alias-free membership answers every query exactly as
        # originally observed; no per-query evaluation is needed.
        if cls._inventory_unchanged(expected, observed, boundary):
            return
        for query in expected.queries:
            cls._verify_inventory_query(expected, observed, query, boundary)
        for selection in (
            *(((),) if expected.membership_queried else ()),
            *expected.membership_queries,
        ):
            cls._verify_query_membership(
                observed,
                cls.directory_membership_value(expected, selection),
                boundary,
                selection,
            )

    @staticmethod
    def _inventory_unchanged(
        expected: p.Cli.AtomicDirectoryInventory,
        observed: p.Cli.AtomicDirectoryInventory,
        boundary: p.Cli.AtomicDirectoryQueryBoundary,
    ) -> bool:
        """Report whether a receipt still holds without per-query evaluation.

        Returns:
            Whether no own effect exists and the alias-free membership is
            physically unchanged.

        """
        if boundary.published or boundary.created:
            return False
        return observed.entries == expected.entries and all(
            entry.kind != "symlink" for entry in expected.entries
        )

    @classmethod
    def _verify_inventory_query(
        cls,
        expected: p.Cli.AtomicDirectoryInventory,
        observed: p.Cli.AtomicDirectoryInventory,
        query: tuple[str, Literal["exists", "isfile", "isdir"]],
        boundary: p.Cli.AtomicDirectoryQueryBoundary,
    ) -> None:
        """Reprove one consumed predicate through the boundary's own effects.

        Raises:
            ValueError: If the predicate answer changed outside the own effects.

        """
        name, predicate = query
        path = expected.root.path / name
        value = cls.directory_query_value(expected, name, predicate)
        effect = boundary.published.get(path)
        if effect is not None:
            value = cls._published_query_value(effect, predicate, preimage=value)
        elif predicate != "isfile" and (
            path in boundary.created or path in boundary.ancestors
        ):
            # A directory the preimage already held needs no creation receipt
            # for publications beneath it; only an own creation or a
            # directory the preimage lacked must bind to one.
            if path in boundary.created or not (
                cls.directory_query_value(expected, name, "isdir")
            ):
                cls._published_directory_current(path, boundary.created)
            value = True
        observed_value = cls.directory_query_value(observed, name, predicate)
        if value != observed_value:
            msg = (
                f"source directory query changed: {path}; "
                f"predicate={predicate}; expected={value}; observed={observed_value}"
            )
            raise ValueError(msg)

    @staticmethod
    def _published_query_value(
        effect: tuple[p.Cli.AtomicFileState, p.Cli.AtomicFileState],
        predicate: Literal["exists", "isfile", "isdir"],
        *,
        preimage: bool,
    ) -> bool:
        """Answer one predicate after an own file effect on its child.

        Returns:
            The predicate answer of the published after-state.

        Raises:
            ValueError: If the receipt answer differs from the effect preimage.

        """
        before, after = effect
        if preimage != (before.content is not None and predicate != "isdir"):
            msg = f"source query preimage changed: {before.path}"
            raise ValueError(msg)
        return after.content is not None and predicate != "isdir"

    @staticmethod
    def _published_ancestors(
        publications: Iterable[tuple[p.Cli.AtomicFileState, p.Cli.AtomicFileState]],
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
        inventories: tuple[p.Cli.AtomicDirectoryInventory, ...],
        topology: tuple[p.Cli.AtomicDirectoryChainPlan, ...],
        membership_policy: t.StrTuple | None,
    ) -> None:
        """Reject receipt-selected authority before observing native dependencies.

        Raises:
            ValueError: If a receipt selects authority not elected by the caller.

        """
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


__all__: list[str] = ["FlextCliUtilitiesAtomicTreeInventory"]
