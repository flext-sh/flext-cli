"""Lightweight public utility boundary for dependency graphs.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence

from flext_cli import p, t
from flext_cli._utilities import _dag


class FlextCliUtilitiesDag:
    """Route waves/order to the standard library and the rest to NetworkX.

    Waves and order run on every configuration validation, so they never load
    the NetworkX engine; closure and components load it on first use.
    """

    @staticmethod
    def dag_waves(edges: t.Cli.DagEdges) -> p.Result[Sequence[Sequence[str]]]:
        """Group nodes into dependency waves on the standard library.

        Returns:
            The ``dag_waves`` result.

        """
        return _dag.FlextCliUtilitiesDagWaves.dag_waves(edges)

    @staticmethod
    def dag_order(edges: t.Cli.DagEdges) -> p.Result[Sequence[str]]:
        """Order nodes dependencies-first on the standard library.

        Returns:
            The ``dag_order`` result.

        """
        return _dag.FlextCliUtilitiesDagWaves.dag_order(edges)

    @staticmethod
    def dag_closure(
        edges: t.Cli.DagEdges,
        roots: frozenset[str],
    ) -> p.Result[frozenset[str]]:
        """Return the roots with every transitive dependency.

        Returns:
            The engine's ``dag_closure`` result.

        """
        return _dag.FlextCliUtilitiesDagGraph.dag_closure(edges, roots)

    @staticmethod
    def dag_strongly_connected(
        edges: t.Cli.DagEdges,
    ) -> Sequence[frozenset[str]]:
        """Return every strongly connected component through the graph engine.

        Returns:
            The engine's ``dag_strongly_connected`` result.

        """
        return _dag.FlextCliUtilitiesDagGraph.dag_strongly_connected(edges)


__all__: list[str] = ["FlextCliUtilitiesDag"]
