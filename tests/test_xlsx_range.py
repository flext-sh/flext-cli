"""Public typed A1 range parsing contract tests."""

from __future__ import annotations

from flext_cli import cli, m, p
from flext_tests import tm


def test_xlsx_parse_range_returns_typed_concrete_bounds() -> None:
    """Absolute and single-cell A1 inputs return canonical range models."""
    area = cli.xlsx_parse_range(m.Cli.XlsxParseRangeRequest(reference="$B$2:D4"))
    single = cli.xlsx_parse_range(m.Cli.XlsxParseRangeRequest(reference="A1"))

    tm.that(area.success, eq=True)
    tm.that(area.value.first.row, eq=2)
    tm.that(area.value.first.column, eq=2)
    tm.that(area.value.last.row, eq=4)
    tm.that(area.value.last.column, eq=4)
    tm.that(single.success, eq=True)
    tm.that(single.value.first, eq=single.value.last)


def test_xlsx_parse_range_fails_loud_for_non_concrete_or_inverted_input() -> None:
    """Invalid, whole-column, and inverted references never synthesize bounds."""
    for reference in ("not-a-range", "A:B", "B2:A1"):
        result = cli.xlsx_parse_range(m.Cli.XlsxParseRangeRequest(reference=reference))

        tm.that(result.failure, eq=True)
        tm.that("xlsx_range_invalid" in (result.error or ""), eq=True)


def test_xlsx_format_reference_exposes_every_typed_rendering_mode() -> None:
    """Public formatting covers relative, absolute, qualified, and collapsed refs."""
    area = m.Cli.XlsxCellRange(
        first=m.Cli.XlsxCellAddress(row=2, column=2),
        last=m.Cli.XlsxCellAddress(row=4, column=4),
    )
    relative_request = m.Cli.XlsxFormatReferenceRequest(
        area=area, absolute=False, collapse_single_cell=True
    )
    absolute_request = m.Cli.XlsxFormatReferenceRequest(
        area=area, sheet="Sales Q1", absolute=True, collapse_single_cell=False
    )

    relative = cli.xlsx_format_reference(relative_request)
    absolute = cli.xlsx_format_reference(absolute_request)

    tm.that(isinstance(relative_request, p.Cli.XlsxFormatReferenceRequest), eq=True)
    tm.that(relative.value.reference, eq="B2:D4")
    tm.that(absolute.value.reference, eq="'Sales Q1'!$B$2:$D$4")
    tm.that(isinstance(absolute.value, p.Cli.XlsxReference), eq=True)


def test_xlsx_format_reference_collapses_equal_bounds_and_rejects_inversion() -> None:
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
            area=single, sheet="O'Brien", absolute=True, collapse_single_cell=True
        )
    )
    expanded = cli.xlsx_format_reference(
        m.Cli.XlsxFormatReferenceRequest(
            area=single, absolute=False, collapse_single_cell=False
        )
    )
    invalid = cli.xlsx_format_reference(
        m.Cli.XlsxFormatReferenceRequest(
            area=inverted, absolute=False, collapse_single_cell=False
        )
    )

    tm.that(collapsed.value.reference, eq="'O''Brien'!$A$1")
    tm.that(expanded.value.reference, eq="A1:A1")
    tm.that(invalid.failure, eq=True)
    tm.that("xlsx_range_invalid" in (invalid.error or ""), eq=True)


__all__: tuple[str, ...] = (
    "test_xlsx_format_reference_collapses_equal_bounds_and_rejects_inversion",
    "test_xlsx_format_reference_exposes_every_typed_rendering_mode",
    "test_xlsx_parse_range_fails_loud_for_non_concrete_or_inverted_input",
    "test_xlsx_parse_range_returns_typed_concrete_bounds",
)
