"""Dependency waves and order on the standard library — ``u.Cli.dag_waves``.

Waves are the hot query: configuration validation proves acyclicity through
them on every import. ``graphlib`` answers it without loading the NetworkX
engine, which is reached only to explain a cycle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from graphlib import CycleError, TopologicalSorter

from flext_core import r

from flext_cli import p, t
from flext_cli._utilities import _dag


class FlextCliUtilitiesDagWaves:
    """Closed-graph checks, dependency-first waves and their flattened order."""

    @staticmethod
    def dag_unknown(edges: t.Cli.DagEdges) -> Sequence[str]:
        """Return every referenced dependency that is not a declared node.

        Returns:
            The unknown references, sorted.

        """
        return sorted({
            dependency
            for dependencies in edges.values()
            for dependency in dependencies
            if dependency not in edges
        })

    @staticmethod
    def dag_waves(edges: t.Cli.DagEdges) -> p.Result[Sequence[Sequence[str]]]:
        """Split a closed dependency graph into dependency-first waves.

        Wave ``n`` holds only nodes whose dependencies all live in earlier
        waves; each wave is sorted.

        Returns:
            The waves, or the failure naming the unknown references or the
            cycle path.

        """
        unknown = FlextCliUtilitiesDagWaves.dag_unknown(edges)
        if unknown:
            return r[Sequence[Sequence[str]]].fail(
                "dependency graph references names outside the graph: "
                + ", ".join(unknown),
            )
        sorter = TopologicalSorter({
            node: tuple(sorted(edges[node])) for node in sorted(edges)
        })
        try:
            sorter.prepare()
        except CycleError:
            return r[Sequence[Sequence[str]]].fail(
                _dag.FlextCliUtilitiesDagGraph.dag_cycle(edges),
            )
        waves: list[tuple[str, ...]] = []
        while sorter.is_active():
            wave = tuple(sorted(sorter.get_ready()))
            waves.append(wave)
            sorter.done(*wave)
        return r[Sequence[Sequence[str]]].ok(tuple(waves))

    @staticmethod
    def dag_order(edges: t.Cli.DagEdges) -> p.Result[Sequence[str]]:
        """Return the closed graph's nodes dependencies-first, wave by wave.

        Returns:
            The flattened waves, or the first graph failure.

        """
        return FlextCliUtilitiesDagWaves.dag_waves(edges).map(
            lambda waves: tuple(node for wave in waves for node in wave),
        )


__all__: tuple[str, ...] = ("FlextCliUtilitiesDagWaves",)
