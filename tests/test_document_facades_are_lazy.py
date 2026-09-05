"""The public facades must not drag the document stacks into every consumer.

`openpyxl`, `python-docx`, and `python-pptx` are hard dependencies, but they
are only needed by the document operations. Importing `flext_cli` or its
utility facade must not pay for them: a cold import costs seconds of pure
module construction that every CLI consumer in the fleet pays on every
invocation, including for `--help`.

These probes run in a fresh interpreter because `sys.modules` is global: once
any earlier test in the session has imported a document module, an in-process
assertion would silently pass. The child is launched through the project's own
`process_start` primitive rather than `subprocess` directly.
"""

from __future__ import annotations

import sys

from flext_cli import u
from flext_tests import tm
from tests import c


def _loaded_heavy_modules(import_statement: str) -> frozenset[str]:
    """Report which document stacks a fresh interpreter loads for one import."""
    code = (
        "import sys\n"
        f"{import_statement}\n"
        f"heavy = {tuple(c.Tests.DOCUMENT_STACK_MODULES)!r}\n"
        "print(','.join(sorted(n for n in heavy if n in sys.modules)))\n"
    )
    reported = tm.ok(
        u.Cli.capture(
            [sys.executable, "-c", code],
            timeout=int(c.Cli.CLI_PROCESS_HEARTBEAT_SECONDS),
        )
    )
    return frozenset(reported.split(",")) if reported else frozenset()


class TestsDocumentFacadesAreLazy:
    """Document owners load on first use, never at facade import."""

    def test_utilities_facade_import_does_not_load_document_stacks(self) -> None:
        loaded = _loaded_heavy_modules(
            "from flext_cli.utilities import FlextCliUtilities as u\n_ = u.Cli"
        )
        tm.that(loaded, eq=frozenset())

    def test_public_api_import_does_not_load_document_stacks(self) -> None:
        loaded = _loaded_heavy_modules("from flext_cli import FlextCli\n_ = FlextCli")
        tm.that(loaded, eq=frozenset())

    def test_xlsx_operation_still_resolves_through_the_utility_facade(self) -> None:
        loaded = _loaded_heavy_modules(
            "from flext_cli import m, u\n"
            "u.Cli.xlsx_parse_range(m.Cli.XlsxParseRangeRequest(reference='A1'))"
        )
        tm.that("openpyxl" in loaded, eq=True)

    def test_docx_operation_still_resolves_through_the_utility_facade(self) -> None:
        loaded = _loaded_heavy_modules(
            "from flext_cli import u\nu.Cli.docx_read(b'not-a-document')"
        )
        tm.that("docx" in loaded, eq=True)

    def test_pptx_operation_still_resolves_through_the_public_api(self) -> None:
        loaded = _loaded_heavy_modules(
            "from flext_cli import cli\ncli.pptx_read(b'not-a-presentation')"
        )
        tm.that("pptx" in loaded, eq=True)


__all__: list[str] = []
