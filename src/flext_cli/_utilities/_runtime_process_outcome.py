"""Typed exact exits for streamed process execution."""

from __future__ import annotations

import shlex

from flext_cli import c, m, p, r, t


class FlextCliUtilitiesRuntimeProcessOutcomeMixin:
    """Map one completed lifecycle to its public result contract."""

    @staticmethod
    def process_succeeded(outcome: p.Cli.ProcessOutcome) -> bool:
        """Return whether every causal completion field describes success."""
        return (
            outcome.raw_return_code == c.Cli.EXIT_CODE_SUCCESS
            and not outcome.timed_out
            and outcome.forwarded_signal is None
        )

    @staticmethod
    def _process_exit_result(
        cmd: t.StrSequence,
        return_code: int | None,
        received_signals: list[int],
        diagnostics: tuple[str, ...],
        *,
        timed_out: bool,
        legacy_timeout: bool,
        legacy_timeout_seconds: int | None,
        timeout_exit_code: int,
    ) -> p.Result[p.Cli.ProcessOutcome]:
        """Preserve a primary exit while surfacing additive diagnostics."""
        if legacy_timeout and timed_out:
            failure = f"timeout {legacy_timeout_seconds}s: {shlex.join(list(cmd))}"
            if diagnostics:
                failure = f"{failure}; {'; '.join(diagnostics)}"
            return r[p.Cli.ProcessOutcome].fail(failure)
        if received_signals:
            primary_exit = -abs(received_signals[0])
        
        elif return_code is None:
            primary_exit = None
        else:
            primary_exit = return_code
        if diagnostics:
            return r[p.Cli.ProcessOutcome].fail("; ".join(diagnostics))
        if primary_exit is None:
            return r[p.Cli.ProcessOutcome].fail(
                "root process did not expose an exit status"
            )
        return r[p.Cli.ProcessOutcome].ok(
            m.Cli.ProcessOutcome(
                raw_return_code=primary_exit,
                timed_out=timed_out,
                forwarded_signal=(received_signals[0] if received_signals else None),
            )
        )

    @classmethod
    def _captured_process_result(
        cls,
        cmd: t.StrSequence,
        return_code: int | None,
        received_signals: list[int],
        diagnostics: tuple[str, ...],
        stdout_output: bytearray,
        stderr_output: bytearray,
        duration: float,
        *,
        timed_out: bool,
        timeout_seconds: int | None,
        timeout_exit_code: int,
    ) -> p.Result[p.Cli.CommandBytesOutput]:
        """Attach captured bytes only after the owned process boundary is empty."""
        return cls._process_exit_result(
            cmd,
            return_code,
            received_signals,
            diagnostics,
            timed_out=timed_out,
            legacy_timeout=timeout_seconds is not None,
            legacy_timeout_seconds=timeout_seconds,
        ).map(
            lambda outcome: m.Cli.CommandBytesOutput(
                stdout=bytes(stdout_output),
                stderr=bytes(stderr_output),
                outcome=outcome,
                duration=duration,
            )
        )



__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessOutcomeMixin"]
