"""OOXML future-function storage encoding contract tests."""

from __future__ import annotations

import zipfile
from io import BytesIO

from flext_cli import cli, m
from flext_tests import tm


def _render_formula(formula: str) -> str:
    plan = m.Cli.XlsxWorkbookPlan(
        sheets=(
            m.Cli.XlsxSheetPlan(
                name="Data",
                cells=(
                    m.Cli.XlsxCellPlan(
                        at=m.Cli.XlsxCellAddress(row=1, column=1),
                        value=m.Cli.XlsxFormulaValue(value=formula),
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
    archive = zipfile.ZipFile(BytesIO(result.value.content))
    return archive.read("xl/worksheets/sheet1.xml").decode("utf-8")


def test_xlsx_future_function_stored_with_xlfn_prefix() -> None:
    """OOXML storage prefixes post-2007 functions so readers resolve them."""
    sheet_xml = _render_formula("=XLOOKUP(A1,B1:B5,C1:C5)+SUM(D1:D5)")
    tm.that("_xlfn.XLOOKUP(A1,B1:B5,C1:C5)" in sheet_xml, eq=True)
    tm.that("SUM(D1:D5)" in sheet_xml, eq=True)
    tm.that("_xlfn.SUM" not in sheet_xml, eq=True)


def test_xlsx_future_function_skips_string_literals() -> None:
    """Text inside formula string literals is never rewritten."""
    sheet_xml = _render_formula('=IF(A1="","XLOOKUP(",XLOOKUP(A1,B1:B5,C1:C5))')
    tm.that('"XLOOKUP("' in sheet_xml, eq=True)
    tm.that("_xlfn.XLOOKUP(A1,B1:B5,C1:C5)" in sheet_xml, eq=True)


def test_xlsx_prefixed_function_not_double_prefixed() -> None:
    """Storage-safe input passes through without a second prefix."""
    sheet_xml = _render_formula("=_xlfn.XLOOKUP(A1,B1:B5,C1:C5)")
    tm.that("_xlfn._xlfn" not in sheet_xml, eq=True)
    tm.that("_xlfn.XLOOKUP(A1,B1:B5,C1:C5)" in sheet_xml, eq=True)
