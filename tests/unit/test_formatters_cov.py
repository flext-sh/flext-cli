"""Behavioral tests for the CLI formatters public contract.

Exercises the observable behavior promised by ``FlextCli`` formatter methods
(``print``/``render_rule``/``render_panel``/``render_table``),
which delegate through ``FlextCliFormatters`` and ``FlextCliUtilitiesFormatters``:

- ``print``/``render_rule``/``render_panel``/``render_table`` render their
  content to the console (observable on stdout).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from flext_cli import cli
from flext_tests import tm
from tests import c

if TYPE_CHECKING:
    from tests import t


class TestsFlextCliFormattersCov:
    """Behavioral tests for the public CLI formatter contract."""

    # ── print: message rendered to stdout ────────────────────────────

    @pytest.mark.parametrize(("msg", "style"), c.Tests.FORMATTERS_PRINT_CASES)
    def test_print_renders_message_to_stdout(
        self, capsys: pytest.CaptureFixture[str], msg: str, style: str | None
    ) -> None:
        """Verify that print renders message to stdout."""
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
        """Verify that render rule renders label to stdout."""
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
        """Verify that render panel renders content to stdout."""
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
        """Verify that render table renders columns and cells."""
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
