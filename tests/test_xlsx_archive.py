"""Safe OOXML archive contract tests."""

from __future__ import annotations

from io import BytesIO

from flext_tests import tm
from openpyxl import Workbook
from openpyxl.styles import Protection
from openpyxl.workbook.defined_name import DefinedName

from flext_cli import cli, m


def test_xlsx_inspect_reports_policy_violations_without_extracting() -> None:
    """Inspection returns typed evidence for caller-owned policy violations."""
    workbook = Workbook()
    worksheet = workbook.worksheets[0]
    worksheet["A1"] = "protected"
    worksheet["A1"].protection = Protection(locked=False, hidden=True)
    worksheet.merge_cells("A1:B1")
    workbook.defined_names.add(DefinedName("OwnedName", attr_text="Sheet!$A$1"))
    stream = BytesIO()
    workbook.save(stream)

    result = cli.xlsx_inspect(
        m.Cli.XlsxArchiveInspectionRequest(
            source=stream.getvalue(),
            policy=m.Cli.XlsxArchivePolicy(
                forbidden_worksheet_tags=frozenset(("mergeCells",)),
                required_worksheet_count=1,
                reject_defined_names=True,
                reject_style_protection=True,
            ),
        )
    )

    tm.that(result.success, eq=True)
    tm.that(result.value.clean, eq=False)
    kinds = frozenset(violation.kind for violation in result.value.violations)
    tm.that("worksheet_tag" in kinds, eq=True)
    tm.that("defined_name" in kinds, eq=True)
    tm.that("style_protection" in kinds, eq=True)


def test_xlsx_inspect_rejects_invalid_archive_bytes() -> None:
    """Malformed bytes fail instead of yielding a synthetic inventory."""
    result = cli.xlsx_inspect(
        m.Cli.XlsxArchiveInspectionRequest(
            source=b"not-an-xlsx", policy=m.Cli.XlsxArchivePolicy()
        )
    )

    tm.that(result.failure, eq=True)
    tm.that("xlsx_archive_invalid" in (result.error or ""), eq=True)
