"""Coverage tests for _utilities/formatters.py and services/formatters.py.

Targets: formatters_create_tree, formatters_print, formatters_render_rule,
         formatters_render_panel, formatters_render_table (and services wrapper).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_cli import u
from flext_cli._utilities.formatters import FlextCliUtilitiesFormatters
from flext_cli.services.formatters import FlextCliFormatters
from tests import c


class TestsFlextCliFormattersCov:
    """Data-driven coverage tests for FlextCliUtilitiesFormatters."""

    # ── formatters_create_tree ───────────────────────────────────────

    @pytest.mark.parametrize("label", c.Tests.FORMATTER_TREE_LABELS)
    def test_create_tree_parametrized(self, label: str) -> None:
        result = u.Cli.formatters_create_tree(label)
        assert result.success

    def test_create_tree_returns_rich_tree(self) -> None:
        result = u.Cli.formatters_create_tree("Root")
        assert result.success
        # The value is a Rich Tree object
        tree = result.value
        assert hasattr(tree, "label") or hasattr(tree, "add")

    # ── formatters_print ─────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("msg", "style"),
        c.Tests.FORMATTERS_PRINT_CASES,
    )
    def test_formatters_print_parametrized(
        self, capsys: pytest.CaptureFixture[str], msg: str, style: str | None
    ) -> None:
        if style is not None:
            u.Cli.formatters_print(msg, style)
        else:
            u.Cli.formatters_print(msg)

    # ── formatters_render_rule ───────────────────────────────────────

    @pytest.mark.parametrize("label", c.Tests.FORMATTER_RULE_LABELS)
    def test_render_rule_parametrized(self, label: str) -> None:
        # Should not raise
        u.Cli.formatters_render_rule(label)

    # ── formatters_render_panel ──────────────────────────────────────

    @pytest.mark.parametrize(
        ("content", "title"),
        c.Tests.FORMATTER_PANEL_CASES,
    )
    def test_render_panel_parametrized(self, content: str, title: str) -> None:
        u.Cli.formatters_render_panel(content, title=title)

    # ── formatters_render_table ───────────────────────────────────────

    @pytest.mark.parametrize(
        ("columns", "rows", "title"),
        c.Tests.FORMATTER_TABLE_CASES,
    )
    def test_render_table_parametrized(
        self,
        columns: tuple[str, ...],
        rows: tuple[tuple[str, ...], ...],
        title: str,
    ) -> None:
        request = FlextCliUtilitiesFormatters.TableRenderRequest(
            columns=list(columns),
            rows=[list(row) for row in rows],
            title=title,
        )
        u.Cli.formatters_render_table(request)


class TestsFlextCliServicesFormattersCov:
    """Coverage tests for services/formatters.py (thin facade)."""

    def test_create_tree_via_service(self) -> None:
        svc = FlextCliFormatters()
        result = svc.create_tree("ServiceRoot")
        assert result.success

    def test_print_via_service(self) -> None:
        svc = FlextCliFormatters()
        svc.print("service print test")

    def test_render_rule_via_service(self) -> None:
        svc = FlextCliFormatters()
        svc.render_rule("Rule label")

    def test_render_panel_via_service(self) -> None:
        svc = FlextCliFormatters()
        svc.render_panel("panel content", title="My Title")

    def test_render_table_via_service(self) -> None:
        svc = FlextCliFormatters()
        svc.render_table(
            columns=["Name", "Value"],
            rows=[["foo", "bar"]],
            title="Test",
        )


__all__: list[str] = [
    "TestsFlextCliFormattersCov",
    "TestsFlextCliServicesFormattersCov",
]
