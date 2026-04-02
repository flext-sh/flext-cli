"""Tests for CLI table formatting and display helpers."""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_cli import FlextCliFormatters, FlextCliTables


class TestsCliTables:
    """Regression coverage for public table helpers."""

    def test_format_table_accepts_single_mapping_and_sequence_kwargs(self) -> None:
        """Single mappings and list-based config kwargs must be accepted."""
        result = FlextCliTables.format_table(
            {"status": "ok", "count": 2},
            headers=["Field", "Value"],
            colalign=["left", "right"],
            table_format="grid",
        )
        tm.that(result.is_success, eq=True)
        table = result.value or ""
        tm.that("Field" in table, eq=True)
        tm.that("status" in table, eq=True)
        tm.that("ok" in table, eq=True)

    def test_format_table_supports_headerless_mapping_rows(self) -> None:
        """Headerless rendering must work for row sequences from examples."""
        result = FlextCliTables.format_table(
            [{"identifier": "row-1", "display_name": "Alpha"}],
            show_header=False,
            table_format="plain",
        )
        tm.that(result.is_success, eq=True)
        table = result.value or ""
        tm.that("row-1" in table, eq=True)
        tm.that("Alpha" in table, eq=True)
        tm.that("identifier" in table, eq=False)

    def test_format_table_accepts_public_table_alias(self) -> None:
        """The public 'table' format alias must resolve to the default backend."""
        result = FlextCliTables.format_table(
            [{"name": "Alice", "status": "active"}],
            table_format="table",
        )
        tm.that(result.is_success, eq=True)
        table = result.value or ""
        tm.that("Alice" in table, eq=True)
        tm.that("active" in table, eq=True)

    def test_show_table_prints_title_before_rendered_table(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """show_table must print the title before the rendered table body."""
        printed: list[tuple[str, str | None]] = []

        def fake_print(message: str, style: str | None = None) -> None:
            printed.append((message, style))

        monkeypatch.setattr(
            FlextCliFormatters,
            "print",
            staticmethod(fake_print),
        )
        FlextCliTables.show_table(
            {"service": "cli", "state": "ready"},
            headers=["Field", "Value"],
            title="Current State",
        )
        tm.that(len(printed), eq=2)
        tm.that(printed[0][0], eq="Current State")
        tm.that(printed[0][1], eq="bold")
        tm.that("service" in printed[1][0], eq=True)
