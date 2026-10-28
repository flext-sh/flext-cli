"""CLI output helpers shared through ``u.Cli``.

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
import threading
from pathlib import Path
from typing import ClassVar

from flext_cli import c, p
from flext_cli._utilities import FlextCliUtilitiesOutputPayloads


class FlextCliUtilitiesOutput(FlextCliUtilitiesOutputPayloads):
    """Canonical CLI output rendering helpers exposed through ``u.Cli``."""

    # stdout is one process-wide mutable resource. Pipeline stages that carry no
    # dependency between them run concurrently, so two stages can emit a
    # multi-line block at the same time; unguarded `write` interleaves them and
    # the check report becomes unreadable. Serializing only the write keeps the
    # emitted block atomic without constraining the callers.
    _EMIT_LOCK: ClassVar[threading.Lock] = threading.Lock()

    @staticmethod
    def emit_raw(text: str, *, error: bool = False) -> None:
        """Write raw text atomically to the selected process stream.

        The write is serialized process-wide, so concurrent pipeline stages
        cannot interleave partial lines within one emitted block.

        Args:
            text: Complete text block to write, including any trailing newline.
            error: Route the block to stderr instead of stdout.

        """
        with FlextCliUtilitiesOutput._EMIT_LOCK:
            stream = sys.stderr if error else sys.stdout
            _ = stream.write(text)
            _ = stream.flush()

    @classmethod
    def info(cls, msg: str) -> None:
        """Emit one canonical info line.

        Args:
            msg: Message text rendered after the info level label.

        """
        cls.emit_raw(f"{c.Cli.OUTPUT_LOG_LEVEL_INFO}: {msg}\n")

    @classmethod
    def error(cls, msg: str, detail: str | None = None) -> None:
        """Emit one canonical error line with optional detail.

        Args:
            msg: Message text rendered after the error level label.
            detail: Optional indented line rendered below the message.

        """
        cls.emit_raw(f"{c.Cli.OUTPUT_LOG_LEVEL_ERROR}: {msg}\n", error=True)
        if detail:
            cls.emit_raw(f"  {detail}\n", error=True)

    @classmethod
    def warning(cls, msg: str) -> None:
        """Emit one canonical warning line.

        Args:
            msg: Message text rendered after the warning level label.

        """
        cls.emit_raw(f"{c.Cli.OUTPUT_LOG_LEVEL_WARNING}: {msg}\n")

    @classmethod
    def debug(cls, msg: str) -> None:
        """Emit one canonical debug line.

        Args:
            msg: Message text rendered after the debug level label.

        """
        cls.emit_raw(f"{c.Cli.OUTPUT_LOG_LEVEL_DEBUG}: {msg}\n")

    @classmethod
    def header(cls, title: str) -> None:
        """Emit one canonical header block.

        Args:
            title: Header title rendered between the surrounding rule lines.

        """
        line = "=" * c.Cli.OUTPUT_HEADER_RULE_WIDTH
        cls.emit_raw(f"\n{line}\n  {title}\n{line}\n")

    @classmethod
    def progress(cls, idx: int, total: int, proj: str, verb: str) -> None:
        """Emit one canonical progress line.

        Args:
            idx: Zero-based project position rendered zero-padded.
            total: Total project count that fixes the rendered padding width.
            proj: Project name in the rendered line.
            verb: Running verb rendered after the project name.

        """
        width = len(str(total))
        cls.emit_raw(f"[{idx:0{width}d}/{total:0{width}d}] {proj} {verb} ...\n")

    @classmethod
    def status(cls, verb: str, proj: str, *, result: bool, elapsed: float) -> None:
        """Emit one canonical per-item status line.

        Args:
            verb: Running verb rendered left-aligned.
            proj: Project name rendered left-aligned.
            result: Selects the ok symbol when true, otherwise the fail symbol.
            elapsed: Elapsed seconds rendered with two decimal places.

        """
        symbol = c.Cli.OUTPUT_STATUS_OK if result else c.Cli.OUTPUT_STATUS_FAIL
        cls.emit_raw(f"  {symbol} {verb:<8} {proj:<24} {elapsed:.2f}s\n")

    @classmethod
    def summary(cls, stats: p.Cli.SummaryStats) -> None:
        """Emit one canonical summary block from a typed summary payload.

        Args:
            stats: Typed counts and timings composing the summary block.

        """
        content = cls.output_summary_content(
            total=stats.total,
            success=stats.success,
            failed=stats.failed,
            skipped=stats.skipped,
        )
        cls.emit_raw(
            f"\n-- {stats.verb} summary --\n{content}  ({stats.elapsed:.2f}s)\n",
        )

    @classmethod
    def gate_result(
        cls,
        gate: str,
        count: int,
        *,
        passed: bool,
        elapsed: float,
    ) -> None:
        """Emit one canonical gate-result line.

        Args:
            gate: Gate name rendered left-aligned.
            count: Error count rendered right-aligned.
            passed: Selects the ok symbol when true, otherwise the fail symbol.
            elapsed: Elapsed seconds rendered with two decimal places.

        """
        symbol = c.Cli.OUTPUT_STATUS_OK if passed else c.Cli.OUTPUT_STATUS_FAIL
        cls.emit_raw(f"    {symbol} {gate:<10} {count:>5} errors  ({elapsed:.2f}s)\n")

    @staticmethod
    def resolve_report_dir(repository_root: Path | str, scope: str, verb: str) -> Path:
        """Resolve the standardized report directory for one scope and verb.

        Args:
            repository_root: Repository root owning the reports base directory.
            scope: Report scope selecting the workspace subdirectory layout.
            verb: Verb owning the report directory.

        Returns:
            The resolved report directory.

        """
        root_path = (
            Path(repository_root)
            if isinstance(repository_root, str)
            else repository_root
        )
        base = root_path / c.Cli.OUTPUT_REPORTS_DIR_NAME
        if scope == c.Cli.OUTPUT_SCOPE_WORKSPACE:
            return (base / c.Cli.OUTPUT_SCOPE_WORKSPACE / verb).resolve()
        return (base / verb).resolve()

    @classmethod
    def resolve_report_path(
        cls,
        repository_root: Path | str,
        scope: str,
        verb: str,
        filename: str,
    ) -> Path:
        """Resolve the standardized report file path for one scope and verb.

        Args:
            repository_root: Repository root owning the reports base directory.
            scope: Report scope selecting the workspace subdirectory layout.
            verb: Verb owning the report directory.
            filename: Report file name appended to the resolved directory.

        Returns:
            The resolved report file path.

        """
        return cls.resolve_report_dir(repository_root, scope, verb) / filename


__all__: list[str] = ["FlextCliUtilitiesOutput"]
