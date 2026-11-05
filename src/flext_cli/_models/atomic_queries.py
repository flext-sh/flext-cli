"""Parameter objects owned by atomic directory-query merge and verification.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from pathlib import Path
from typing import Literal

from flext_core import m

from flext_cli import p, t


class FlextCliModelsAtomicQueries:
    """Directory-query parameter objects exposed through ``m.Cli``."""

    class AtomicDirectoryWorkingSelectors(m.ArbitraryTypesModel):
        """Invocation-local selectors indexed by original witness identity."""

        queries: Mapping[int, set[tuple[str, Literal["exists", "isfile", "isdir"]]]] = (
            m.Field(
                default_factory=dict,
                description="Native predicates selected per witness identity.",
            )
        )
        membership_queries: Mapping[int, set[t.StrTuple]] = m.Field(
            default_factory=dict[int, set[t.StrTuple]],
            description="Membership exclusions selected per witness identity.",
        )

    class AtomicDirectorySelection(m.FrozenModel):
        """United query and membership selectors of agreeing witnesses."""

        queries: tuple[tuple[str, Literal["exists", "isfile", "isdir"]], ...] = m.Field(
            description="Sorted native predicates consumed by the caller."
        )
        membership_queried: bool = m.Field(
            description="Whether the complete direct membership was consumed.",
        )
        membership_queries: tuple[t.StrTuple, ...] = m.Field(
            description="Sorted membership exclusions consumed by the caller.",
        )

    class AtomicDirectoryQueryProof(m.ArbitraryTypesModel):
        """Caller-elected authority and own effects one verification may allow."""

        files: tuple[
            tuple[t.Port[p.Cli.AtomicFileState], t.Port[p.Cli.AtomicFileState]], ...
        ] = m.Field(
            default=(),
            description="Authenticated file effects as before and after states.",
        )
        membership_policy: t.StrTuple | None = m.Field(
            default=None,
            description="Membership policy elected independently of receipts.",
        )
        directories: tuple[t.Port[p.Cli.AtomicDirectoryState], ...] = m.Field(
            default=(),
            description="Own directory creations published in the boundary.",
        )
        directory_observations: t.Port[
            MutableMapping[Path, p.Cli.AtomicDirectoryInventory]
        ] = m.Field(
            exclude=True,
            description="Directory observations shared by reference in the boundary.",
        )
        topology_observations: t.Port[
            MutableMapping[Path, p.Cli.AtomicDirectoryChainPlan]
        ] = m.Field(
            exclude=True,
            description="Ancestry observations shared by reference in the boundary.",
        )

    class AtomicDirectoryQueryBoundary(m.ArbitraryTypesModel):
        """Own publication effects and observations of one verification boundary."""

        published: Mapping[
            Path,
            tuple[t.Port[p.Cli.AtomicFileState], t.Port[p.Cli.AtomicFileState]],
        ] = m.Field(
            description="Authenticated file effects keyed by their destination.",
        )
        created: Mapping[Path, t.Port[p.Cli.AtomicDirectoryState]] = m.Field(
            description="Own directory creations keyed by their path.",
        )
        ancestors: Mapping[Path, None] = m.Field(
            description="Every ancestor already held by a published file.",
        )
        directory_observations: t.Port[
            MutableMapping[Path, p.Cli.AtomicDirectoryInventory]
        ] = m.Field(
            exclude=True,
            description="Directory observations shared by reference in the boundary.",
        )
        topology_observations: t.Port[
            MutableMapping[Path, p.Cli.AtomicDirectoryChainPlan]
        ] = m.Field(
            exclude=True,
            description="Ancestry observations shared by reference in the boundary.",
        )

__all__: list[str] = ["FlextCliModelsAtomicQueries"]
