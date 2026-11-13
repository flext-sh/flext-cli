"""Heavy engines load only when their public operation runs.

`openpyxl`, `python-docx`, `python-pptx`, and `networkx` are hard dependencies,
but every CLI imports the utility namespace. The XLSX, DOCX, PPTX, and DAG
facades therefore delegate to their `_xlsx`, `_docx`, `_pptx`, and `_dag`
adapter packages, which load on first use: importing the namespace or the
public API loads none of them.

These probes run in a fresh interpreter because `sys.modules` is global: once
any earlier test in the session has imported a document module, an in-process
assertion would silently pass. The child is launched through the project's own
`process_start` primitive rather than `subprocess` directly.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys

from flext_cli import settings
from tests import c, tm, u


def _loaded_heavy_modules(import_statement: str) -> frozenset[str]:
    """Report which document stacks a fresh interpreter loads for one import.

    Returns:
        The resulting ``frozenset[str]``.

    """
    code = (
        "import sys\n"
        f"{import_statement}\n"
        f"heavy = {tuple(c.Tests.DOCUMENT_STACK_MODULES)!r}\n"
        "print(','.join(sorted(n for n in heavy if n in sys.modules)))\n"
    )
    reported = tm.ok(
        u.Cli.capture(
            [sys.executable, "-c", code],
            timeout=int(settings.cli_process_heartbeat_seconds),
        ),
    )
    return frozenset(reported.split(",")) if reported else frozenset()


class TestsFlextCliDocumentFacadesAreLazy:
    """No heavy engine loads with the namespace; each loads on its operation."""

    @staticmethod
    def test_utilities_namespace_loads_no_heavy_engine() -> None:
        loaded = _loaded_heavy_modules(
            "from flext_cli.utilities import FlextCliUtilities as u\n_ = u.Cli",
        )
        tm.that(loaded, eq=frozenset[str]())

    @staticmethod
    def test_cli_entry_import_loads_no_heavy_engine() -> None:
        loaded = _loaded_heavy_modules("from flext_cli import cli\n_ = cli")
        tm.that(loaded, eq=frozenset[str]())

    @staticmethod
    def test_dag_operation_still_resolves_through_the_utility_facade() -> None:
        loaded = _loaded_heavy_modules(
            "from flext_cli import u\nu.Cli.dag_closure({'a': frozenset()}, "
            "frozenset({'a'}))",
        )
        tm.ok("networkx" in loaded)

    @staticmethod
    def test_xlsx_operation_still_resolves_through_the_utility_facade() -> None:
        loaded = _loaded_heavy_modules(
            "from flext_cli import m, p, u\n"
            "u.Cli.xlsx_parse_range(m.Cli.XlsxParseRangeRequest(reference='A1'))",
        )
        tm.ok("openpyxl" in loaded)

    @staticmethod
    def test_docx_operation_still_resolves_through_the_utility_facade() -> None:
        loaded = _loaded_heavy_modules(
            "from flext_cli import u\nu.Cli.docx_read(b'not-a-document')",
        )
        tm.ok("docx" in loaded)

    @staticmethod
    def test_pptx_operation_still_resolves_through_the_utility_facade() -> None:
        loaded = _loaded_heavy_modules(
            "from flext_cli import u\nu.Cli.read_presentation(b'not-a-presentation')",
        )
        tm.ok("pptx" in loaded)


__all__: list[str] = []
