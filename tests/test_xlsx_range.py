"""Public typed A1 range parsing contract tests.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import cli
from tests import m, tm

if TYPE_CHECKING:
    from tests import t


class TestsFlextCliXlsxRange:
    """Behavioral contract validated by this module."""

    @staticmethod
    def test_xlsx_parse_range_returns_typed_concrete_bounds() -> None:
        """Absolute and single-cell A1 inputs return canonical range models."""
        area = cli.xlsx_parse_range(m.Cli.XlsxParseRangeRequest(reference="$B$2:D4"))
        single = cli.xlsx_parse_range(m.Cli.XlsxParseRangeRequest(reference="A1"))

        tm.ok(area.success)
        tm.that(area.value.first.row, eq=2)
        tm.that(area.value.first.column, eq=2)
        tm.that(area.value.last.row, eq=4)
        tm.that(area.value.last.column, eq=4)
        tm.ok(single.success)
        tm.that(single.value.first, eq=single.value.last)

    @staticmethod
    def test_xlsx_parse_range_fails_loud_for_non_concrete_or_inverted_input() -> None:
        """Invalid, whole-column, and inverted references never synthesize bounds."""
        for reference in ("not-a-range", "A:B", "B2:A1"):
            result = cli.xlsx_parse_range(
                m.Cli.XlsxParseRangeRequest(reference=reference)
            )

            tm.ok(result.failure)
            tm.ok("xlsx_range_invalid" in (result.error or ""))

    @staticmethod
    def test_xlsx_format_reference_exposes_every_typed_rendering_mode() -> None:
        """Public formatting covers relative, absolute, qualified, collapsed refs."""
        area = m.Cli.XlsxCellRange(
            first=m.Cli.XlsxCellAddress(row=2, column=2),
            last=m.Cli.XlsxCellAddress(row=4, column=4),
        )
        relative_request = m.Cli.XlsxFormatReferenceRequest(
            area=area,
            absolute=False,
            collapse_single_cell=True,
        )
        absolute_request = m.Cli.XlsxFormatReferenceRequest(
            area=area,
            sheet="Sales Q1",
            absolute=True,
            collapse_single_cell=False,
        )

        relative = cli.xlsx_format_reference(relative_request)
        absolute = cli.xlsx_format_reference(absolute_request)

        tm.ok(relative.success)
        tm.that(relative.value.reference, eq="B2:D4")
        tm.that(absolute.value.reference, eq="'Sales Q1'!$B$2:$D$4")
        tm.ok(absolute.success)

    @staticmethod
    def test_xlsx_format_reference_collapses_equal_bounds_and_rejects_inversion() -> (
        None
    ):
        """Single-cell collapse is exact while invalid ordering fails loudly."""
        single = m.Cli.XlsxCellRange(
            first=m.Cli.XlsxCellAddress(row=1, column=1),
            last=m.Cli.XlsxCellAddress(row=1, column=1),
        )
        inverted = m.Cli.XlsxCellRange(
            first=m.Cli.XlsxCellAddress(row=3, column=2),
            last=m.Cli.XlsxCellAddress(row=1, column=1),
        )

        collapsed = cli.xlsx_format_reference(
            m.Cli.XlsxFormatReferenceRequest(
                area=single,
                sheet="O'Brien",
                absolute=True,
                collapse_single_cell=True,
            ),
        )
        expanded = cli.xlsx_format_reference(
            m.Cli.XlsxFormatReferenceRequest(
                area=single,
                absolute=False,
                collapse_single_cell=False,
            ),
        )
        invalid = cli.xlsx_format_reference(
            m.Cli.XlsxFormatReferenceRequest(
                area=inverted,
                absolute=False,
                collapse_single_cell=False,
            ),
        )

        tm.that(collapsed.value.reference, eq="'O''Brien'!$A$1")
        tm.that(expanded.value.reference, eq="A1:A1")
        tm.ok(invalid.failure)
        tm.ok("xlsx_range_invalid" in (invalid.error or ""))


__all__: t.VariadicTuple[str] = ()
