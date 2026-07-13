"""CLI output helpers shared through ``u.Cli``."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli import c
from flext_cli._utilities._output_parts.flextcliutilitiesoutput_part_01 import (
    FlextCliUtilitiesOutput as FlextCliUtilitiesOutputPart01,
)

if TYPE_CHECKING:
    from flext_cli import p


class FlextCliUtilitiesOutput:
    """Implementation part for FlextCliUtilitiesOutput."""

    @classmethod
    def status(cls, verb: str, proj: str, *, result: bool, elapsed: float) -> None:
        symbol = c.Cli.OUTPUT_STATUS_OK if result else c.Cli.OUTPUT_STATUS_FAIL
        FlextCliUtilitiesOutputPart01.emit_raw(
            f"  {symbol} {verb:<8} {proj:<24} {elapsed:.2f}s\n"
        )

    @classmethod
    def summary(cls, stats: p.Cli.SummaryStats) -> None:
        verb = str(getattr(stats, "verb", c.Cli.OUTPUT_SUMMARY_DEFAULT_VERB))
        total = int(getattr(stats, "total", 0))
        success = int(getattr(stats, "success", 0))
        failed = int(getattr(stats, "failed", 0))
        skipped = int(getattr(stats, "skipped", 0))
        elapsed = float(getattr(stats, "elapsed", 0.0))
        content = FlextCliUtilitiesOutputPart01.output_summary_content(
            total=total, success=success, failed=failed, skipped=skipped
        )
        FlextCliUtilitiesOutputPart01.emit_raw(
            f"\n-- {verb} summary --\n{content}  ({elapsed:.2f}s)\n"
        )

    @classmethod
    def gate_result(
        cls, gate: str, count: int, *, passed: bool, elapsed: float
    ) -> None:
        symbol = c.Cli.OUTPUT_STATUS_OK if passed else c.Cli.OUTPUT_STATUS_FAIL
        FlextCliUtilitiesOutputPart01.emit_raw(
            f"    {symbol} {gate:<10} {count:>5} errors  ({elapsed:.2f}s)\n"
        )

    @classmethod
    def project_failure(cls, info: p.Cli.ProjectFailureInfo) -> None:
        project = str(getattr(info, "project", c.IDENTIFIER_UNKNOWN))
        elapsed = int(getattr(info, "elapsed", 0))
        error_count = int(getattr(info, "error_count", 0))
        log_path = str(getattr(info, "log_path", c.DEFAULT_EMPTY_STRING))
        max_show = int(getattr(info, "max_show", 0))
        errors = tuple(getattr(info, "errors", ()))
        count_label = (
            f"  [{error_count} errors]" if error_count > 0 else c.DEFAULT_EMPTY_STRING
        )
        FlextCliUtilitiesOutputPart01.emit_raw(
            f"  {c.Cli.OUTPUT_STATUS_FAIL} {project} completed in {elapsed}s{count_label}  ({log_path})\n"
        )
        for line in errors[:max_show]:
            FlextCliUtilitiesOutputPart01.emit_raw(f"      {line}\n")
        remaining = error_count - max_show
        if remaining > 0:
            FlextCliUtilitiesOutputPart01.emit_raw(
                f"      ... and {remaining} more (see log)\n"
            )

    @staticmethod
    def resolve_report_dir(workspace_root: Path | str, scope: str, verb: str) -> Path:
        """Resolve standardized report directory path."""
        root_path = (
            Path(workspace_root) if isinstance(workspace_root, str) else workspace_root
        )
        base = root_path / c.Cli.OUTPUT_REPORTS_DIR_NAME
        if scope == c.Cli.OUTPUT_SCOPE_WORKSPACE:
            return (base / c.Cli.OUTPUT_SCOPE_WORKSPACE / verb).resolve()
        return (base / verb).resolve()

    @classmethod
    def resolve_report_path(
        cls, workspace_root: Path | str, scope: str, verb: str, filename: str
    ) -> Path:
        """Resolve standardized report file path."""
        return cls.resolve_report_dir(workspace_root, scope, verb) / filename


__all__: list[str] = ["FlextCliUtilitiesOutput"]
