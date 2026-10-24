"""Behavioral tests for the public dependency-graph contract (``u.Cli.dag_*``).

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import MappingProxyType
from typing import ClassVar

from flext_cli import settings
from tests import m, t, tm, u
from tests.fixtures import dag_report


class TestsFlextCliDag:
    """Assert waves, order, closure, components and their failures."""

    _EDGES: ClassVar[t.Cli.DagEdges] = MappingProxyType({
        "app": ("api", "core"),
        "api": ("core",),
        "core": (),
        "cli": ("core",),
        "docs": ("app", "cli"),
    })

    @staticmethod
    def test_waves_are_dependency_first_and_sorted() -> None:
        """Each wave depends only on earlier waves and is sorted by name."""
        waves = tm.ok(u.Cli.dag_waves(TestsFlextCliDag._EDGES))
        tm.that(waves, eq=(("core",), ("api", "cli"), ("app",), ("docs",)))

    @staticmethod
    def test_order_flattens_waves() -> None:
        """The order is the concatenation of the waves."""
        order = tm.ok(u.Cli.dag_order(TestsFlextCliDag._EDGES))
        tm.that(order, eq=("core", "api", "cli", "app", "docs"))

    @staticmethod
    def test_cycle_reports_its_path() -> None:
        """A cycle fails with the path starting and ending at its smallest node."""
        result = u.Cli.dag_waves({"b": ("c",), "c": ("a",), "a": ("b",), "d": ()})
        tm.fail(result, has="cyclic dependency graph: a -> b -> c -> a")

    @staticmethod
    def test_self_dependency_is_a_cycle() -> None:
        """A node that depends on itself is a one-node cycle."""
        tm.fail(u.Cli.dag_order({"a": ("a",)}), has="cyclic dependency graph: a -> a")

    @staticmethod
    def test_unknown_reference_fails() -> None:
        """Every reference outside the declared nodes is named in the failure."""
        result = u.Cli.dag_waves({"a": ("zeta", "beta"), "c": ()})
        tm.fail(result, has="outside the graph: beta, zeta")

    @staticmethod
    def test_closure_includes_roots_and_transitive_dependencies() -> None:
        """The closure holds the roots and everything they depend on."""
        closure = tm.ok(
            u.Cli.dag_closure(TestsFlextCliDag._EDGES, frozenset({"app"})),
        )
        tm.that(closure, eq=frozenset({"app", "api", "core"}))

    @staticmethod
    def test_closure_rejects_unknown_roots() -> None:
        """A root outside the graph is a typed failure, never silently skipped."""
        result = u.Cli.dag_closure(TestsFlextCliDag._EDGES, frozenset({"ghost"}))
        tm.fail(result, has="roots are outside the graph: ghost")

    @staticmethod
    def test_strongly_connected_components_are_sorted() -> None:
        """Components are frozensets ordered by their sorted members."""
        components = u.Cli.dag_strongly_connected({
            "b": frozenset({"a"}),
            "a": frozenset({"b"}),
            "c": frozenset({"d"}),
        })
        tm.that(
            components,
            eq=(frozenset({"a", "b"}), frozenset({"c"}), frozenset({"d"})),
        )

    @staticmethod
    def test_results_do_not_depend_on_insertion_order() -> None:
        """Reordered nodes and reversed dependency tuples give identical results."""
        edges = TestsFlextCliDag._EDGES
        reordered = {node: tuple(edges[node])[::-1] for node in tuple(edges)[::-1]}
        cyclic = {"b": ("c",), "c": ("a",), "a": ("b",), "x": ("y",), "y": ("x",)}
        cyclic_reordered = {node: cyclic[node] for node in sorted(cyclic, reverse=True)}
        tm.that(u.Cli.dag_waves(reordered).value, eq=u.Cli.dag_waves(edges).value)
        tm.that(
            u.Cli.dag_waves(cyclic_reordered).error,
            eq=u.Cli.dag_waves(cyclic).error,
        )
        tm.that(
            u.Cli.dag_strongly_connected(cyclic_reordered),
            eq=u.Cli.dag_strongly_connected(cyclic),
        )

    @staticmethod
    def test_results_do_not_depend_on_hash_seed() -> None:
        """Fresh interpreters with different hash seeds report identical results."""
        project = Path(__file__).resolve().parents[2]
        outputs = tuple(
            tm.ok(
                u.Cli.run_raw(
                    [sys.executable, "-m", "tests.fixtures.dag_report"],
                    cwd=project,
                    timeout=int(settings.cli_process_heartbeat_seconds),
                    options=m.Cli.ProcessOptions(env={"PYTHONHASHSEED": seed}),
                ),
            )
            for seed in ("0", "1")
        )
        tm.that(
            [(output.exit_code, output.stdout) for output in outputs],
            eq=[(0, f"{dag_report.report()}\n")] * len(outputs),
        )


__all__: list[str] = []
