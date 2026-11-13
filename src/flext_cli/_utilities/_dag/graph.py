"""NetworkX-backed dependency graph queries — closure and components.

The engine loads only for these queries and to explain a cycle the
standard-library waves (``waves.py``) detected.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence

import networkx as nx
from flext_core import r

from flext_cli import p, t
from flext_cli._utilities import _dag


class FlextCliUtilitiesDagGraph:
    """Dependency graphs: closure, strongly connected components, cycle paths.

    ``edges`` maps every node to the nodes it depends on. Closure requires a
    closed graph: a dependency that is not itself a key is a typed failure.
    """

    @staticmethod
    def _dag_graph(edges: t.Cli.DagEdges) -> t.Cli.DagGraph:
        """Build the node-to-dependency graph in deterministic insertion order.

        Returns:
            One edge per declared node-to-dependency link.

        """
        graph: t.Cli.DagGraph = nx.DiGraph()
        graph.add_nodes_from(sorted(edges))
        graph.add_edges_from(
            (node, dependency)
            for node in sorted(edges)
            for dependency in sorted(edges[node])
        )
        return graph

    @staticmethod
    def _dag_closed_graph(edges: t.Cli.DagEdges) -> p.Result[t.Cli.DagGraph]:
        """Build the graph after proving every reference is a declared node.

        Returns:
            The graph, or the failure naming every reference outside it.

        """
        unknown = _dag.FlextCliUtilitiesDagWaves.dag_unknown(edges)
        if unknown:
            return r[t.Cli.DagGraph].fail(
                "dependency graph references names outside the graph: "
                + ", ".join(unknown),
            )
        return r[t.Cli.DagGraph].ok(FlextCliUtilitiesDagGraph._dag_graph(edges))

    @staticmethod
    def dag_cycle(edges: t.Cli.DagEdges) -> str:
        """Explain the first cycle of a closed graph as a deterministic path.

        The cyclic component with the smallest sorted members is chosen; the
        path starts and ends at its smallest node and follows dependency edges.

        Returns:
            The ``cyclic dependency graph: a -> ... -> a`` message.

        Raises:
            ValueError: If the graph is open or holds no cycle.

        """
        graph = FlextCliUtilitiesDagGraph._dag_closed_graph(edges).unwrap()
        for component in FlextCliUtilitiesDagGraph._dag_components(graph):
            start = min(component)
            if len(component) > 1 or graph.has_edge(start, start):
                successor = min(
                    node for node in graph.successors(start) if node in component
                )
                parents = {
                    reached: parent
                    for parent, reached in nx.bfs_edges(graph, successor)
                }
                path = [start]
                while path[-1] != successor:
                    path.append(parents[path[-1]])
                return "cyclic dependency graph: " + " -> ".join(
                    (start, *reversed(path)),
                )
        msg = "dependency graph holds no cycle to explain"
        raise ValueError(msg)

    @staticmethod
    def dag_closure(
        edges: t.Cli.DagEdges,
        roots: frozenset[str],
    ) -> p.Result[frozenset[str]]:
        """Return the roots together with every transitive dependency.

        Returns:
            The closure, or the failure naming unknown roots or references.

        """
        built = FlextCliUtilitiesDagGraph._dag_closed_graph(edges)
        if built.failure:
            return r[frozenset[str]].from_failure(built)
        unknown = sorted(roots.difference(edges))
        if unknown:
            return r[frozenset[str]].fail(
                "dependency closure roots are outside the graph: " + ", ".join(unknown),
            )
        graph = built.value
        return r[frozenset[str]].ok(
            frozenset(
                node for root in roots for node in nx.dfs_preorder_nodes(graph, root)
            ),
        )

    @staticmethod
    def _dag_components(graph: t.Cli.DagGraph) -> Sequence[frozenset[str]]:
        """Return the graph's strongly connected components in sorted order.

        Returns:
            The components ordered by their sorted members.

        """
        return tuple(
            sorted(
                (
                    frozenset(component)
                    for component in nx.strongly_connected_components(graph)
                ),
                key=sorted,
            ),
        )

    @staticmethod
    def dag_strongly_connected(
        edges: t.Cli.DagEdges,
    ) -> Sequence[frozenset[str]]:
        """Return every strongly connected component, deterministically sorted.

        This query inspects arbitrary graphs: a reference outside the keys
        becomes a node of its own.

        Returns:
            The components ordered by their sorted members.

        """
        return FlextCliUtilitiesDagGraph._dag_components(
            FlextCliUtilitiesDagGraph._dag_graph(edges),
        )


__all__: tuple[str, ...] = ("FlextCliUtilitiesDagGraph",)
