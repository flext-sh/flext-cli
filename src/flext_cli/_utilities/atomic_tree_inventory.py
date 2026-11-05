"""Reproof of consumed directory-query receipts against native observations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, MutableMapping
from itertools import chain
from pathlib import Path
from typing import Literal, Never

from flext_cli import m, p, t
from flext_cli._utilities import FlextCliUtilitiesAtomicDirectoryChain
from flext_cli._utilities.atomic_tree_physical import (
    FlextCliUtilitiesAtomicTreePhysical,
)
from flext_cli._utilities.atomic_tree_query_receipts import (
    FlextCliUtilitiesAtomicTreeQueryReceipts,
)


class FlextCliUtilitiesAtomicTreeInventory(
    FlextCliUtilitiesAtomicTreeQueryReceipts,
    FlextCliUtilitiesAtomicTreePhysical,
):
    """Reprove consumed directory elections inside one verification boundary."""

    @classmethod
    def verify_directory_queries(
        cls,
        inventories: tuple[p.Cli.AtomicDirectoryInventory, ...],
        topology: tuple[p.Cli.AtomicDirectoryChainPlan, ...],
        proof: m.Cli.AtomicDirectoryQueryProof,
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
        proof: m.Cli.AtomicDirectoryQueryProof,
    ) -> m.Cli.AtomicDirectoryQueryBoundary:
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
        boundary: m.Cli.AtomicDirectoryQueryBoundary,
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
        boundary: m.Cli.AtomicDirectoryQueryBoundary,
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
        boundary: m.Cli.AtomicDirectoryQueryBoundary,
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

    @classmethod
    def _verify_query_topology(
        cls,
        topology: tuple[p.Cli.AtomicDirectoryChainPlan, ...],
        boundary: m.Cli.AtomicDirectoryQueryBoundary,
    ) -> None:
        """Reprove absent-parent elections against the original native ancestry.

        The authenticated publication index supplies both file effects and their
        ancestors; no parallel transport of the same effects is needed.

        """
        observations = boundary.topology_observations
        for witness in topology:
            observed = observations.get(witness.target)
            if observed is None:
                observed = FlextCliUtilitiesAtomicDirectoryChain.plan_directory_chain(
                    witness.target
                )
                observations[witness.target] = observed
            cls._require_ancestry_current(witness, observed, boundary.created)
            if cls._consumes_selectors(witness) and not observed.directories:
                cls._verify_absent_candidate(witness, boundary)

    @classmethod
    def _require_ancestry_current(
        cls,
        witness: p.Cli.AtomicDirectoryChainPlan,
        observed: p.Cli.AtomicDirectoryChainPlan,
        created: Mapping[Path, p.Cli.AtomicDirectoryState],
    ) -> None:
        """Require unchanged ancestry, or ancestry gained only by own creations.

        Raises:
            ValueError: If the ancestry changed outside the own creations.

        """
        if observed.model_dump(exclude=cls._SELECTOR_FIELDS) == witness.model_dump(
            exclude=cls._SELECTOR_FIELDS
        ):
            return
        if not cls._ancestry_gained_by_creation(witness, observed, created):
            msg = f"source directory ancestry changed: {witness.target}"
            raise ValueError(msg)

    @classmethod
    def _ancestry_gained_by_creation(
        cls,
        witness: p.Cli.AtomicDirectoryChainPlan,
        observed: p.Cli.AtomicDirectoryChainPlan,
        created: Mapping[Path, p.Cli.AtomicDirectoryState],
    ) -> bool:
        """Report whether every newly present ancestor is one own creation.

        Returns:
            Whether the observed ancestry extends the witness exactly through
            directories this boundary created.

        """
        gained = witness.directories[
            : max(0, len(witness.directories) - len(observed.directories))
        ]
        if not gained or observed.anchor_path != gained[-1]:
            return False
        if observed.directories != witness.directories[len(gained) :] or (
            observed.anchor_ancestry[: len(witness.anchor_ancestry)]
            != witness.anchor_ancestry
        ):
            return False
        ancestry = dict(
            zip(
                reversed((observed.anchor_path, *observed.anchor_path.parents)),
                observed.anchor_ancestry,
                strict=True,
            )
        )
        return all(cls._created_at(path, ancestry, created) for path in gained)

    @staticmethod
    def _created_at(
        path: Path,
        ancestry: Mapping[Path, tuple[int, int]],
        created: Mapping[Path, p.Cli.AtomicDirectoryState],
    ) -> bool:
        """Report whether one ancestor is the own creation now observed there.

        Returns:
            Whether the creation receipt binds the observed identity and parent.

        """
        receipt = created.get(path)
        if receipt is None or not receipt.exists:
            return False
        return ancestry.get(path) == (receipt.device, receipt.inode) and (
            ancestry.get(path.parent) == (receipt.parent_device, receipt.parent_inode)
        )

    @staticmethod
    def _consumes_selectors(witness: p.Cli.AtomicDirectoryChainPlan) -> bool:
        """Report whether a caller consumed any query of an ancestry witness.

        Returns:
            Whether any query or membership selector was consumed.

        """
        return bool(
            witness.queries or witness.membership_queried or witness.membership_queries
        )

    @classmethod
    def _verify_absent_candidate(
        cls,
        witness: p.Cli.AtomicDirectoryChainPlan,
        boundary: m.Cli.AtomicDirectoryQueryBoundary,
    ) -> None:
        """Reprove the queries consumed on a target that existed at election.

        Raises:
            ValueError: If a consumed candidate answer changed.

        """
        inventory = cls._observe_physical_directory(
            boundary.directory_observations, witness.target
        )
        for name, predicate in witness.queries:
            path = witness.target / name
            effect = boundary.published.get(path)
            value = (
                effect[1].content is not None and predicate != "isdir"
                if effect is not None
                else predicate != "isfile" and path in boundary.ancestors
            )
            if predicate != "isfile" and path in boundary.created:
                cls._published_directory_current(path, boundary.created)
                value = True
            if value and effect is None:
                cls._published_directory_current(path, boundary.created)
            if value != cls.directory_query_value(inventory, name, predicate):
                msg = f"absent source candidate changed: {path}"
                raise ValueError(msg)
        for selection in (
            *(((),) if witness.membership_queried else ()),
            *witness.membership_queries,
        ):
            cls._verify_query_membership(inventory, {}, boundary, selection)

    @classmethod
    def _verify_query_membership(
        cls,
        observed: p.Cli.AtomicDirectoryInventory,
        members: MutableMapping[str, Literal["directory", "file", "symlink", "other"]],
        boundary: m.Cli.AtomicDirectoryQueryBoundary,
        excluded_names: t.StrTuple = (),
    ) -> None:
        """Reprove direct membership with only original native publication effects.

        Raises:
            ValueError: If direct membership changed.

        """
        root = observed.root.path
        cls._apply_created_members(root, members, boundary.created)
        cls._apply_published_members(root, members, boundary)
        expected = {
            name: kind for name, kind in members.items() if name not in excluded_names
        }
        actual = cls.directory_membership_value(observed, excluded_names)
        if expected != actual:
            added = sorted(actual.keys() - expected.keys())
            removed = sorted(expected.keys() - actual.keys())
            changed = [
                (name, expected[name], actual[name])
                for name in sorted(expected.keys() & actual.keys())
                if expected[name] != actual[name]
            ]
            msg = (
                f"source directory membership changed: {root}; "
                f"added={added!r}; removed={removed!r}; kind_changed={changed!r}"
            )
            raise ValueError(msg)

    @classmethod
    def _apply_created_members(
        cls,
        root: Path,
        members: MutableMapping[str, Literal["directory", "file", "symlink", "other"]],
        created: Mapping[Path, p.Cli.AtomicDirectoryState],
    ) -> None:
        """Add every own direct child directory creation to the membership.

        Raises:
            ValueError: If an own creation replaced a child of another kind.

        """
        for path in created:
            if path.parent != root:
                continue
            cls._published_directory_current(path, created)
            if members.get(path.name) not in {None, "directory"}:
                msg = f"source directory kind changed: {path}"
                raise ValueError(msg)
            members[path.name] = "directory"

    @classmethod
    def _apply_published_members(
        cls,
        root: Path,
        members: MutableMapping[str, Literal["directory", "file", "symlink", "other"]],
        boundary: m.Cli.AtomicDirectoryQueryBoundary,
    ) -> None:
        """Apply every own file effect at or beneath the root to the membership."""
        for _before, after in boundary.published.values():
            if after.path.parent == root:
                if after.content is None:
                    members.pop(after.path.name, None)
                else:
                    members[after.path.name] = "file"
            elif after.content is not None and after.path.is_relative_to(root):
                child = root / after.path.relative_to(root).parts[0]
                if child in boundary.created or members.get(child.name) != "directory":
                    cls._published_directory_current(child, boundary.created)
                members[child.name] = "directory"

    @classmethod
    def _published_directory_current(
        cls,
        path: Path,
        created: Mapping[Path, p.Cli.AtomicDirectoryState],
    ) -> None:
        """Bind an elected own directory to the publisher's original inode."""
        receipt = created.get(path)
        observed = FlextCliUtilitiesAtomicDirectoryChain.plan_directory_chain(path)
        if receipt is None or not receipt.exists or observed.directories:
            cls._raise_unpublished_directory(path)
        if (observed.anchor_device, observed.anchor_inode) != (
            receipt.device,
            receipt.inode,
        ) or observed.anchor_ancestry[-2] != (
            receipt.parent_device,
            receipt.parent_inode,
        ):
            cls._raise_unpublished_directory(path)

    @staticmethod
    def _raise_unpublished_directory(path: Path) -> Never:
        """Reject an elected directory lacking its original own publication.

        Raises:
            ValueError: Always.

        """
        msg = f"source directory lacks its original publication: {path}"
        raise ValueError(msg)


__all__: list[str] = ["FlextCliUtilitiesAtomicTreeInventory"]
