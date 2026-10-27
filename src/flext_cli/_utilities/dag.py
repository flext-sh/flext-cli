"""Dependency graph queries backed by NetworkX — ``u.Cli.dag_*``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import networkx as nx

from flext_cli import p, r, t


class FlextCliUtilitiesDag:
    """Dependency graphs: waves, order, closure and strongly connected components.

    ``edges`` maps every node to the nodes it depends on. Waves, order and
    closure require a closed graph: a dependency that is not itself a key is
    a typed failure.
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
        unknown = sorted({
            dependency
            for dependencies in edges.values()
            for dependency in dependencies
            if dependency not in edges
        })
        if unknown:
            return r[t.Cli.DagGraph].fail(
                "dependency graph references names outside the graph: "
                + ", ".join(unknown),
            )
        return r[t.Cli.DagGraph].ok(FlextCliUtilitiesDag._dag_graph(edges))

    @staticmethod
    def dag_waves(edges: t.Cli.DagEdges) -> p.Result[t.SequenceOf[t.StrSequence]]:
        """Split a closed dependency graph into dependency-first waves.

        Wave ``n`` holds only nodes whose dependencies all live in earlier
        waves; each wave is sorted.

        Returns:
            The waves, or the failure naming the unknown references or the
            cycle path.

        """
        built = FlextCliUtilitiesDag._dag_closed_graph(edges)
        if built.failure:
            return r[t.SequenceOf[t.StrSequence]].from_failure(built)
        graph = built.value
        for component in FlextCliUtilitiesDag._dag_components(graph):
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
                return r[t.SequenceOf[t.StrSequence]].fail(
                    "cyclic dependency graph: " + " -> ".join((start, *reversed(path))),
                )
        return r[t.SequenceOf[t.StrSequence]].ok(
            tuple(
                tuple(sorted(wave))
                for wave in nx.topological_generations(graph.reverse(copy=False))
            ),
        )

    @staticmethod
    def dag_order(edges: t.Cli.DagEdges) -> p.Result[t.StrSequence]:
        """Return the closed graph's nodes dependencies-first, wave by wave.

        Returns:
            The flattened waves, or the first graph failure.

        """
        return FlextCliUtilitiesDag.dag_waves(edges).map(
            lambda waves: tuple(node for wave in waves for node in wave),
        )

    @staticmethod
    def dag_closure(
        edges: t.Cli.DagEdges,
        roots: frozenset[str],
    ) -> p.Result[frozenset[str]]:
        """Return the roots together with every transitive dependency.

        Returns:
            The closure, or the failure naming unknown roots or references.

        """
        built = FlextCliUtilitiesDag._dag_closed_graph(edges)
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
    def _dag_components(graph: t.Cli.DagGraph) -> t.SequenceOf[frozenset[str]]:
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
    ) -> t.SequenceOf[frozenset[str]]:
        """Return every strongly connected component, deterministically sorted.

        This query inspects arbitrary graphs: a reference outside the keys
        becomes a node of its own.

        Returns:
            The components ordered by their sorted members.

        """
        return FlextCliUtilitiesDag._dag_components(
            FlextCliUtilitiesDag._dag_graph(edges),
        )


__all__: tuple[str, ...] = ("FlextCliUtilitiesDag",)
