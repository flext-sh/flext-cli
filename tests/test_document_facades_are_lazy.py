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

from flext_cli.utilities import FlextCliUtilities as u

_HEAVY_MODULES = ("openpyxl", "docx", "pptx")
_PROBE_TIMEOUT_SECONDS = 300.0


def _loaded_heavy_modules(import_statement: str) -> frozenset[str]:
    """Report which document stacks a fresh interpreter loads for one import."""
    code = (
        "import sys\n"
        f"{import_statement}\n"
        f"heavy = {_HEAVY_MODULES!r}\n"
        "print(','.join(sorted(n for n in heavy if n in sys.modules)))\n"
    )
    started = u.Cli.process_start([sys.executable, "-c", code])
    assert started.success, started.error
    process = started.value
    waited = process.wait(timeout=_PROBE_TIMEOUT_SECONDS)
    assert waited.success, waited.error
    assert waited.value == 0, f"probe failed: {process.stderr}"
    reported = process.stdout.strip()
    return frozenset(reported.split(",")) if reported else frozenset()


class TestsDocumentFacadesAreLazy:
    """Document owners load on first use, never at facade import."""

    def test_utilities_facade_import_does_not_load_document_stacks(self) -> None:
        loaded = _loaded_heavy_modules(
            "from flext_cli.utilities import FlextCliUtilities as u\n_ = u.Cli"
        )
        assert loaded == frozenset(), (
            f"importing the utility facade loaded document stacks: {sorted(loaded)}"
        )

    def test_public_api_import_does_not_load_document_stacks(self) -> None:
        loaded = _loaded_heavy_modules("from flext_cli import FlextCli\n_ = FlextCli")
        assert loaded == frozenset(), (
            f"importing FlextCli loaded document stacks: {sorted(loaded)}"
        )

    def test_xlsx_operation_still_resolves_through_the_utility_facade(self) -> None:
        loaded = _loaded_heavy_modules(
            "from flext_cli.utilities import FlextCliUtilities as u\n"
            "assert callable(u.Cli.xlsx_render), 'u.Cli.xlsx_render is not callable'"
        )
        assert "openpyxl" in loaded, (
            f"reaching u.Cli.xlsx_render must load its owner; loaded={sorted(loaded)}"
        )

    def test_docx_operation_still_resolves_through_the_utility_facade(self) -> None:
        loaded = _loaded_heavy_modules(
            "from flext_cli.utilities import FlextCliUtilities as u\n"
            "assert callable(u.Cli.docx_render), 'u.Cli.docx_render is not callable'"
        )
        assert "docx" in loaded, (
            f"reaching u.Cli.docx_render must load its owner; loaded={sorted(loaded)}"
        )

    def test_pptx_operation_still_resolves_through_the_public_api(self) -> None:
        loaded = _loaded_heavy_modules(
            "from flext_cli import FlextCli\n"
            "assert callable(FlextCli.pptx_render), 'pptx_render is not callable'"
        )
        assert "pptx" in loaded, (
            f"reaching FlextCli.pptx_render must load its service; "
            f"loaded={sorted(loaded)}"
        )


class TestsDocumentImportsFailLoudly:
    """A broken install raises the real error instead of degrading silently."""

    def test_no_module_not_found_fallback_survives_in_the_cli_namespace(self) -> None:
        # Why: a `try: import X / except ModuleNotFoundError: class XStub: ...`
        # in the namespace would delete the document operations from the facade
        # on a broken install, so callers would hit AttributeError far from the
        # cause instead of the real missing-dependency error.
        from pathlib import Path

        source = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "flext_cli"
            / "_utilities"
            / "_cli_namespace.py"
        ).read_text(encoding="utf-8")
        assert "ModuleNotFoundError" not in source, (
            "_cli_namespace.py still swallows ModuleNotFoundError"
        )


__all__: list[str] = []
