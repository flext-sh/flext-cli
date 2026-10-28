"""Document imports follow their public facade composition contracts.

`openpyxl`, `python-docx`, and `python-pptx` are hard dependencies, but they
DOCX behavior owners compose directly through MRO and load with the utility
namespace. The remaining document adapters load when their operations run.

These probes run in a fresh interpreter because `sys.modules` is global: once
any earlier test in the session has imported a document module, an in-process
assertion would silently pass. The child is launched through the project's own
`process_start` primitive rather than `subprocess` directly.

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
    """Direct MRO owners load with the namespace; other adapters stay lazy."""

    @staticmethod
    def test_utilities_namespace_loads_its_docx_mro_owners() -> None:
        loaded = _loaded_heavy_modules(
            "from flext_cli.utilities import FlextCliUtilities as u\n_ = u.Cli",
        )
        tm.that(loaded, eq=frozenset({"docx"}))

    @staticmethod
    def test_public_api_import_does_not_load_document_stacks() -> None:
        loaded = _loaded_heavy_modules("from flext_cli import FlextCli\n_ = FlextCli")
        tm.that(loaded.difference({"docx"}), eq=frozenset[str]())

    @staticmethod
    def test_xlsx_operation_still_resolves_through_the_utility_facade() -> None:
        loaded = _loaded_heavy_modules(
            "from flext_cli import m, u\n"
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
    def test_pptx_operation_still_resolves_through_the_public_api() -> None:
        loaded = _loaded_heavy_modules(
            "from flext_cli import cli\ncli.pptx_read(b'not-a-presentation')",
        )
        tm.ok("pptx" in loaded)


__all__: list[str] = []
