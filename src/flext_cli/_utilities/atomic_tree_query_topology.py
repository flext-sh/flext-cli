"""Reproof of consumed absent-parent elections against native ancestry.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from flext_cli import p
from flext_cli._utilities import FlextCliUtilitiesAtomicDirectoryChain
from flext_cli._utilities.atomic_tree_query_membership import (
    FlextCliUtilitiesAtomicTreeQueryMembership,
)


class FlextCliUtilitiesAtomicTreeQueryTopology(
    FlextCliUtilitiesAtomicTreeQueryMembership,
):
    """Reprove ancestry elections, allowing only ancestors this boundary created."""

    @classmethod
    def _verify_query_topology(
        cls,
        topology: tuple[p.Cli.AtomicDirectoryChainPlan, ...],
        boundary: p.Cli.AtomicDirectoryQueryBoundary,
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
        boundary: p.Cli.AtomicDirectoryQueryBoundary,
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


__all__: list[str] = ["FlextCliUtilitiesAtomicTreeQueryTopology"]
