"""Headless recalculation and cache parity contract tests.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import shutil
from concurrent.futures import ThreadPoolExecutor

import pytest

from tests import c, m, p, tm, u

pytestmark = pytest.mark.skipif(
    shutil.which(c.Cli.XLSX_RECALC_COMMAND[0]) is None,
    reason="LibreOffice (soffice) is not installed or available on PATH",
)


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
    result: p.Result[m.Cli.XlsxRenderResult] = u.Cli.xlsx_render(
        m.Cli.XlsxRenderRequest(template=None, plan=plan),
    )
    tm.that(result.success, eq=True, msg=result.error)
    content: bytes = result.value.content
    return content


def _numeric_cell_value(
    source: bytes,
    sheet_name: str,
    coordinate: str,
) -> m.Cli.XlsxIntegerValue | m.Cli.XlsxDecimalValue:
    snapshot = u.Cli.xlsx_snapshot(
        m.Cli.XlsxSnapshotRequest(source=source, data_only=True),
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


class TestsFlextCliXlsxRecalc:
    """Behavioral contract validated by this module."""

    @staticmethod
    @pytest.mark.slow
    def test_xlsx_recalc_refreshes_formula_cache() -> None:
        """Recalculated bytes carry engine-computed cached values."""
        source = _render_workbook()
        recalculated = u.Cli.xlsx_recalc(m.Cli.XlsxRecalcRequest(source=source))
        tm.that(recalculated.success, eq=True, msg=recalculated.error)
        value = _numeric_cell_value(recalculated.value.content, "Report", "A1")
        tm.that(value.value, eq=5)

    @staticmethod
    @pytest.mark.slow
    def test_xlsx_recalc_parity_returns_validated_recalculated_content() -> None:
        """Public parity content carries the caches described by its evidence."""
        source = _render_workbook()
        report = u.Cli.xlsx_recalc_parity(
            m.Cli.XlsxRecalcParityRequest(source=source, expected_formula_count=2),
        )
        tm.that(report.success, eq=True, msg=report.error)
        evidence = report.value
        tm.ok(evidence.recalculated)
        tm.that(evidence.formula_count, eq=2)
        tm.that(evidence.error_cells, eq=())
        tm.that(evidence.uncached_cells, eq=())
        tm.that(evidence.empty_result_cells, eq=("Report!A2",))
        tm.ok(evidence.ok)
        cached_value = _numeric_cell_value(evidence.content, "Report", "A1")
        tm.that(cached_value.value, eq=5)

    @staticmethod
    @pytest.mark.slow
    def test_xlsx_recalc_parity_detects_count_mismatch() -> None:
        """A wrong expected formula count flips the stored verdict."""
        source = _render_workbook()
        report = u.Cli.xlsx_recalc_parity(
            m.Cli.XlsxRecalcParityRequest(source=source, expected_formula_count=9),
        )
        tm.that(report.success, eq=True, msg=report.error)
        tm.that(report.value.formula_count, eq=2)
        tm.fail(report.value.ok)

    @staticmethod
    @pytest.mark.slow
    def test_xlsx_recalc_supports_concurrent_public_calls() -> None:
        """Concurrent callers receive independently recalculated workbooks."""
        source = _render_workbook()
        request = m.Cli.XlsxRecalcRequest(source=source)

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = tuple(
                executor.submit(u.Cli.xlsx_recalc, request) for _ in range(3)
            )
            results = tuple(future.result() for future in futures)
        for result in results:
            tm.that(result.success, eq=True, msg=result.error)
            value = _numeric_cell_value(result.value.content, "Report", "A1")
            tm.that(value.value, eq=5)
