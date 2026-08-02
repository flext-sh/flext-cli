"""Typed exit normalization for streamed process execution."""

from __future__ import annotations

import shlex
from typing import ClassVar

from flext_cli import p, r, t
from flext_core import u as core_u


class FlextCliUtilitiesRuntimeProcessOutcomeMixin:
    """Map one completed lifecycle to its public result contract."""

    _module_logger: ClassVar[p.Logger] = core_u.fetch_logger(__name__)

    @classmethod
    def _process_exit_result(
        cls,
        cmd: t.StrSequence,
        return_code: int | None,
        received_signals: list[int],
        diagnostics: tuple[str, ...],
        live_diagnostics: tuple[str, ...],
        *,
        timed_out: bool,
        legacy_timeout: bool,
        legacy_timeout_seconds: int | None,
        timeout_exit_code: int,
    ) -> p.Result[int]:
        """Preserve a primary exit while surfacing additive diagnostics."""
        if live_diagnostics:
            cls._module_logger.warning(
                "nonfatal live-output diagnostics",
                diagnostics=live_diagnostics,
            )
        if legacy_timeout and timed_out:
            failure = (
                f"timeout {legacy_timeout_seconds}s: {shlex.join(list(cmd))}"
            )
            if diagnostics:
                failure = f"{failure}; {'; '.join(diagnostics)}"
            return r[int].fail(failure)
        if received_signals:
            primary_exit = 128 + abs(received_signals[0])
        elif timed_out:
            primary_exit = timeout_exit_code
        elif return_code is None:
            primary_exit = None
        else:
            primary_exit = (
                128 + abs(return_code) if return_code < 0 else return_code
            )
        if diagnostics:
            primary_detail = (
                f"primary exit {primary_exit}; " if primary_exit is not None else ""
            )
            return r[int].fail(f"{primary_detail}{'; '.join(diagnostics)}")
        if primary_exit is None:
            return r[int].fail("root process did not expose an exit status")
        return r[int].ok(primary_exit)


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessOutcomeMixin"]
