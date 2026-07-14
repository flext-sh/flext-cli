"""Behavioral tests for the CLI formatters public contract.

Exercises the observable behavior promised by ``FlextCli`` formatter methods
(``create_tree``/``print``/``render_rule``/``render_panel``/``render_table``),
which delegate through ``FlextCliFormatters`` and ``FlextCliUtilitiesFormatters``:

- ``create_tree`` returns ``r[RichTree]`` whose value carries the given label.
- ``print``/``render_rule``/``render_panel``/``render_table`` render their
  content to the console (observable on stdout).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from rich.tree import Tree as RichTree

from flext_cli import cli
from tests import c
from flext_tests import tm

if TYPE_CHECKING:
    from tests import t


class TestsFlextCliFormattersCov:
    """Behavioral tests for the public CLI formatter contract."""

    # ── create_tree: fallible contract (r[RichTree]) ─────────────────

    @pytest.mark.parametrize("label", c.Tests.FORMATTER_TREE_LABELS)
    def test_create_tree_succeeds_and_preserves_label(self, label: str) -> None:
        result = cli.create_tree(label)

        tm.ok(result)
        tree = result.unwrap()
        tm.that(tree, is_=RichTree)
        tm.that(tree.label, eq=label)

    def test_create_tree_value_matches_unwrap(self) -> None:
        result = cli.create_tree("Root")

        tm.ok(result)
        assert result.value is result.unwrap()

    def test_create_tree_result_maps_to_label(self) -> None:
        # r[T] monadic contract: map projects the success value.
        mapped = cli.create_tree("Branch").map(lambda tree: tree.label)

        tm.ok(mapped)
        tm.that(mapped.unwrap(), eq="Branch")

    def test_create_tree_children_can_be_attached(self) -> None:
        # Public Rich Tree contract: the returned root accepts children.
        root = cli.create_tree("Root").unwrap()
        child = root.add("Leaf")

        tm.that(child.label, eq="Leaf")
        assert root.children[0] is child

    # ── print: message rendered to stdout ────────────────────────────

    @pytest.mark.parametrize(("msg", "style"), c.Tests.FORMATTERS_PRINT_CASES)
    def test_print_renders_message_to_stdout(
        self, capsys: pytest.CaptureFixture[str], msg: str, style: str | None
    ) -> None:
        if style is not None:
            cli.print(msg, style)
        else:
            cli.print(msg)

        out = capsys.readouterr().out
        tm.that(out, has=msg)

    # ── render_rule: label rendered to stdout ────────────────────────

    @pytest.mark.parametrize("label", c.Tests.FORMATTER_RULE_LABELS)
    def test_render_rule_renders_label_to_stdout(
        self, capsys: pytest.CaptureFixture[str], label: str
    ) -> None:
        cli.render_rule(label)

        out = capsys.readouterr().out
        # A rule always emits a horizontal line; its text appears when present.
        tm.that(out.strip(), ne="")
        tm.that(out, has=label)

    # ── render_panel: content rendered to stdout ─────────────────────

    @pytest.mark.parametrize(("content", "title"), c.Tests.FORMATTER_PANEL_CASES)
    def test_render_panel_renders_content_to_stdout(
        self, capsys: pytest.CaptureFixture[str], content: str, title: str
    ) -> None:
        cli.render_panel(content, title=title)

        out = capsys.readouterr().out
        tm.that(out, has=content)

    # ── render_table: columns and cells rendered to stdout ───────────

    @pytest.mark.parametrize(
        ("columns", "rows", "title"), c.Tests.FORMATTER_TABLE_CASES
    )
    def test_render_table_renders_columns_and_cells(
        self,
        capsys: pytest.CaptureFixture[str],
        columns: t.StrSequence,
        rows: tuple[t.StrSequence, ...],
        title: str,
    ) -> None:
        cli.render_table(
            columns=list(columns), rows=[list(row) for row in rows], title=title
        )

        out = capsys.readouterr().out
        for column in columns:
            tm.that(out, has=column)
        for row in rows:
            for cell in row:
                tm.that(out, has=cell)


__all__: list[str] = ["TestsFlextCliFormattersCov"]
