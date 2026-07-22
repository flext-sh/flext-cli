"""Headless recalculation and cache parity contract tests."""

from __future__ import annotations

from flext_cli import cli, m
from flext_tests import tm


def _render_workbook() -> bytes:
    plan = m.Cli.XlsxWorkbookPlan(
        sheets=(
            m.Cli.XlsxSheetPlan(
                name="Input",
                cells=(
                    m.Cli.XlsxCellPlan(
                        at=m.Cli.XlsxCellAddress(row=1, column=1),
                        value=m.Cli.XlsxIntegerValue(value=2),
                        style="Normal",
                    ),
                    m.Cli.XlsxCellPlan(
                        at=m.Cli.XlsxCellAddress(row=2, column=1),
                        value=m.Cli.XlsxIntegerValue(value=3),
                        style="Normal",
                    ),
                ),
                tables=(),
                layout=m.Cli.XlsxSheetLayoutPlan(),
                rules=m.Cli.XlsxSheetRulesPlan(),
            ),
            m.Cli.XlsxSheetPlan(
                name="Report",
                cells=(
                    m.Cli.XlsxCellPlan(
                        at=m.Cli.XlsxCellAddress(row=1, column=1),
                        value=m.Cli.XlsxFormulaValue(value="=SUM(Input!A1:A2)"),
                        style="Normal",
                    ),
                    m.Cli.XlsxCellPlan(
                        at=m.Cli.XlsxCellAddress(row=2, column=1),
                        value=m.Cli.XlsxFormulaValue(value='=IF(Input!A1>100,"x","")'),
                        style="Normal",
                    ),
                ),
                tables=(),
                layout=m.Cli.XlsxSheetLayoutPlan(),
                rules=m.Cli.XlsxSheetRulesPlan(),
            ),
        ),
        defined_names=(),
    )
    result = cli.xlsx_render(m.Cli.XlsxRenderRequest(template=None, plan=plan))
    tm.that(result.success, eq=True, msg=result.error)
    return result.value.content


def _numeric_cell_value(
    source: bytes, sheet_name: str, coordinate: str
) -> m.Cli.XlsxIntegerValue | m.Cli.XlsxDecimalValue:
    snapshot = cli.xlsx_snapshot(
        m.Cli.XlsxSnapshotRequest(source=source, data_only=True)
    )
    tm.that(snapshot.success, eq=True, msg=snapshot.error)
    for sheet in snapshot.value.sheets:
        if sheet.name != sheet_name:
            continue
        for cell in sheet.cells:
            if cell.coordinate == coordinate:
                value = cell.value
                if isinstance(value, m.Cli.XlsxIntegerValue | m.Cli.XlsxDecimalValue):
                    return value
                msg = f"Cell {sheet_name}!{coordinate} is not numeric: {value.kind}"
                raise AssertionError(msg)
    msg = f"Cell {sheet_name}!{coordinate} not found in snapshot"
    raise AssertionError(msg)


def test_xlsx_recalc_refreshes_formula_cache() -> None:
    """Recalculated bytes carry engine-computed cached values."""
    source = _render_workbook()
    recalculated = cli.xlsx_recalc(m.Cli.XlsxRecalcRequest(source=source))
    tm.that(recalculated.success, eq=True, msg=recalculated.error)
    value = _numeric_cell_value(recalculated.value.content, "Report", "A1")
    tm.that(value.value, eq=5)


def test_xlsx_recalc_parity_returns_validated_recalculated_content() -> None:
    """Public parity content carries the caches described by its evidence."""
    source = _render_workbook()
    report = cli.xlsx_recalc_parity(
        m.Cli.XlsxRecalcParityRequest(source=source, expected_formula_count=2)
    )
    tm.that(report.success, eq=True, msg=report.error)
    evidence = report.value
    tm.that(evidence.recalculated, eq=True)
    tm.that(evidence.formula_count, eq=2)
    tm.that(evidence.error_cells, eq=())
    tm.that(evidence.uncached_cells, eq=())
    tm.that(evidence.empty_result_cells, eq=("Report!A2",))
    tm.that(evidence.ok, eq=True)
    cached_value = _numeric_cell_value(evidence.content, "Report", "A1")
    tm.that(cached_value.value, eq=5)


def test_xlsx_recalc_parity_detects_count_mismatch() -> None:
    """A wrong expected formula count flips the stored verdict."""
    source = _render_workbook()
    report = cli.xlsx_recalc_parity(
        m.Cli.XlsxRecalcParityRequest(source=source, expected_formula_count=9)
    )
    tm.that(report.success, eq=True, msg=report.error)
    tm.that(report.value.formula_count, eq=2)
    tm.that(report.value.ok, eq=False)
