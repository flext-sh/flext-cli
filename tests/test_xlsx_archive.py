"""Safe OOXML archive contract tests.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Protection
from openpyxl.workbook.defined_name import DefinedName

from tests import m, tm, u


class TestsFlextCliXlsxArchive:
    """Behavioral contract validated by this module."""

    @staticmethod
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

        result = u.Cli.xlsx_inspect(
            m.Cli.XlsxArchiveInspectionRequest(
                source=stream.getvalue(),
                policy=m.Cli.XlsxArchivePolicy(
                    forbidden_worksheet_tags=frozenset(("mergeCells",)),
                    required_worksheet_count=1,
                    reject_defined_names=True,
                    reject_style_protection=True,
                ),
            ),
        )

        tm.ok(result.success)
        tm.fail(result.value.clean)
        kinds = frozenset(violation.kind for violation in result.value.violations)
        tm.ok("worksheet_tag" in kinds)
        tm.ok("defined_name" in kinds)
        tm.ok("style_protection" in kinds)

    @staticmethod
    def test_xlsx_inspect_rejects_invalid_archive_bytes() -> None:
        """Malformed bytes fail instead of yielding a synthetic inventory."""
        result = u.Cli.xlsx_inspect(
            m.Cli.XlsxArchiveInspectionRequest(
                source=b"not-an-xlsx",
                policy=m.Cli.XlsxArchivePolicy(),
            ),
        )

        tm.ok(result.failure)
        tm.ok("xlsx_archive_invalid" in (result.error or ""))


__all__: list[str] = ["TestsFlextCliXlsxArchive"]
