"""The public facades load no document stack until a document operation runs.

`openpyxl`, `python-docx`, and `python-pptx` are hard dependencies, but only
the document operations need them. The project declares them deferred, so the
generated initializers hand the facades stand-ins whose members load the
document owners on first use (ADR-018, deferred heavy capabilities).

These probes run in a fresh interpreter because `sys.modules` is global: once
any earlier test in the session has imported a document module, an in-process
assertion would silently pass. The child is launched through the project's own
`capture` primitive rather than `subprocess` directly.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys

from flext_cli import settings
from tests import c, tm, u


class TestsFlextCliDocumentFacadesAreLazy:
    """Document owners load on first use, never at facade import."""

    @staticmethod
    def _loaded_heavy_modules(import_statement: str) -> frozenset[str]:
        """Report which document stacks a fresh interpreter loads for one import.

        Returns:
            The document stack modules loaded after the import statement.

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

    @classmethod
    def test_utilities_namespace_loads_no_document_stack(cls) -> None:
        loaded = cls._loaded_heavy_modules(
            "from flext_cli.utilities import FlextCliUtilities as u\n_ = u.Cli",
        )
        tm.that(loaded, eq=frozenset[str]())

    @classmethod
    def test_public_api_import_does_not_load_document_stacks(cls) -> None:
        loaded = cls._loaded_heavy_modules(
            "from flext_cli import FlextCli\n_ = FlextCli"
        )
        tm.that(loaded, eq=frozenset[str]())

    @classmethod
    def test_xlsx_operation_still_resolves_through_the_utility_facade(cls) -> None:
        loaded = cls._loaded_heavy_modules(
            "from flext_cli import m, p, u\n"
            "u.Cli.xlsx_parse_range(m.Cli.XlsxParseRangeRequest(reference='A1'))",
        )
        tm.ok("openpyxl" in loaded)

    @classmethod
    def test_docx_operation_still_resolves_through_the_utility_facade(cls) -> None:
        loaded = cls._loaded_heavy_modules(
            "from flext_cli import u\nu.Cli.docx_read(b'not-a-document')",
        )
        tm.ok("docx" in loaded)

    @classmethod
    def test_pptx_operation_still_resolves_through_the_public_api(cls) -> None:
        loaded = cls._loaded_heavy_modules(
            "from flext_cli import cli\ncli.pptx_read(b'not-a-presentation')",
        )
        tm.ok("pptx" in loaded)


__all__: list[str] = []
