"""Generic headless recalculation and cache parity for XLSX bytes."""

from __future__ import annotations

import tempfile
from pathlib import Path

from flext_cli import c, m, p, r

from flext_cli._utilities.processes import FlextCliUtilitiesProcesses
from .xlsx_recalc_evidence import FlextCliUtilitiesXlsxRecalcEvidence
from .xlsx_snapshot import FlextCliUtilitiesXlsxSnapshot


class FlextCliUtilitiesXlsxRecalc(
    FlextCliUtilitiesXlsxSnapshot, FlextCliUtilitiesXlsxRecalcEvidence
):
    """Recalculate formula caches and prove parity through typed evidence."""

    # mro-wkii.17.26 (xlsx-a): isolate filesystem and process failure boundaries.
    @staticmethod
    def _recalc_error(detail: str) -> str:
        return f"{c.Cli.XlsxError.RECALC_FAILED}: {detail}"

    @classmethod
    def _recalc_in_workspace(
        cls, request: m.Cli.XlsxRecalcRequest, workdir: Path
    ) -> p.Result[p.Cli.XlsxRecalcResult]:
        input_dir = workdir / "input"
        output_dir = workdir / "output"
        source_path = input_dir / c.Cli.XLSX_RECALC_SOURCE_NAME
        try:
            input_dir.mkdir()
            output_dir.mkdir()
            source_path.write_bytes(request.source)
        except (OSError, ValueError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[p.Cli.XlsxRecalcResult].fail(cls._recalc_error(detail))
        try:
            started = FlextCliUtilitiesProcesses.process_start(
                (*c.Cli.XLSX_RECALC_COMMAND, str(output_dir), str(source_path)),
                cwd=workdir,
            )
        except (OSError, ValueError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[p.Cli.XlsxRecalcResult].fail(cls._recalc_error(detail))
        if started.failure:
            return r[p.Cli.XlsxRecalcResult].fail(cls._recalc_error(f"{started.error}"))
        process = started.value
        try:
            completed = process.wait(timeout=c.Cli.XLSX_RECALC_TIMEOUT_SECONDS)
        except (OSError, ValueError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[p.Cli.XlsxRecalcResult].fail(cls._recalc_error(detail))
        if completed.failure:
            try:
                killed = process.kill()
            except (OSError, ValueError) as exc:
                detail = str(exc).strip() or exc.__class__.__name__
                return r[p.Cli.XlsxRecalcResult].fail(cls._recalc_error(detail))
            detail = completed.error or "process wait failed"
            if killed.failure:
                detail = f"{detail}; kill failed: {killed.error}"
            return r[p.Cli.XlsxRecalcResult].fail(cls._recalc_error(detail))
        if completed.value != 0:
            detail = process.stderr.strip() or process.stdout.strip()
            return r[p.Cli.XlsxRecalcResult].fail(
                cls._recalc_error(f"exit={completed.value}: {detail}")
            )
        try:
            content = (output_dir / c.Cli.XLSX_RECALC_SOURCE_NAME).read_bytes()
        except (OSError, ValueError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[p.Cli.XlsxRecalcResult].fail(cls._recalc_error(detail))
        return r[p.Cli.XlsxRecalcResult].ok(m.Cli.XlsxRecalcResult(content=content))

    # NOTE (multi-agent, mro-j2yt.1): the headless engine process terminates
    # at this private adapter; process spawning is consumed from the generic
    # processes facade without polluting the XLSX composition order.
    @classmethod
    def xlsx_recalc(
        cls, request: m.Cli.XlsxRecalcRequest
    ) -> p.Result[p.Cli.XlsxRecalcResult]:
        """Recalculate every formula cache through the headless office engine."""
        try:
            with tempfile.TemporaryDirectory(
                prefix=c.Cli.XLSX_RECALC_TEMP_PREFIX
            ) as workspace:
                result = cls._recalc_in_workspace(request, Path(workspace))
        except (OSError, ValueError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[p.Cli.XlsxRecalcResult].fail(cls._recalc_error(detail))
        return result

    @classmethod
    def xlsx_recalc_parity(
        cls, request: m.Cli.XlsxRecalcParityRequest
    ) -> p.Result[p.Cli.XlsxRecalcParityReport]:
        """Recalculate and compare cached values against source formulas."""
        formula_snapshot = cls.xlsx_snapshot(
            m.Cli.XlsxSnapshotRequest(source=request.source, data_only=False)
        )
        if formula_snapshot.failure:
            return r[p.Cli.XlsxRecalcParityReport].fail(
                f"{c.Cli.XlsxError.PARITY_FAILED}: {formula_snapshot.error}"
            )
        recalculated = cls.xlsx_recalc(m.Cli.XlsxRecalcRequest(source=request.source))
        if recalculated.failure:
            return r[p.Cli.XlsxRecalcParityReport].fail(
                f"{c.Cli.XlsxError.PARITY_FAILED}: {recalculated.error}"
            )
        value_snapshot = cls.xlsx_snapshot(
            m.Cli.XlsxSnapshotRequest(source=recalculated.value.content, data_only=True)
        )
        if value_snapshot.failure:
            return r[p.Cli.XlsxRecalcParityReport].fail(
                f"{c.Cli.XlsxError.PARITY_FAILED}: {value_snapshot.error}"
            )
        cache_evidence = cls._formula_cache_evidence(recalculated.value.content)
        if cache_evidence.failure:
            return r[p.Cli.XlsxRecalcParityReport].fail(
                f"{c.Cli.XlsxError.PARITY_FAILED}: {cache_evidence.error}"
            )
        uncached_cells, empty_result_cells = cache_evidence.value
        error_cells: tuple[str, ...] = ()
        for sheet in value_snapshot.value.sheets:
            for cell in sheet.cells:
                if cell.formula is None:
                    continue
                value = cell.value
                if isinstance(value, m.Cli.XlsxTextValue) and value.value.startswith(
                    c.Cli.XLSX_ERROR_CELL_PREFIX
                ):
                    error_cells = (*error_cells, f"{sheet.name}!{cell.coordinate}")
        formula_count = formula_snapshot.value.formula_count
        count_matches = (
            request.expected_formula_count is None
            or formula_count == request.expected_formula_count
        )
        report = m.Cli.XlsxRecalcParityReport(
            content=recalculated.value.content,
            recalculated=True,
            formula_count=formula_count,
            error_cells=error_cells,
            uncached_cells=uncached_cells,
            empty_result_cells=empty_result_cells,
            ok=not error_cells and not uncached_cells and count_matches,
        )
        return r[p.Cli.XlsxRecalcParityReport].ok(report)


__all__: tuple[str, ...] = ("FlextCliUtilitiesXlsxRecalc",)
