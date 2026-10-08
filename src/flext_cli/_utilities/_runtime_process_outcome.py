"""Typed exact exits for streamed process execution.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import c, m, p, r, t
from flext_cli._utilities._runtime_models import RuntimeProcessState


class FlextCliUtilitiesRuntimeProcessOutcomeMixin:
    """Map one completed lifecycle to its public result contract."""

    @staticmethod
    def process_succeeded(outcome: p.Cli.ProcessOutcome) -> bool:
        """Return whether every causal completion field describes success.

        Returns:
            Whether every causal completion field describes success.

        """
        return (
            outcome.raw_return_code == c.Cli.EXIT_CODE_SUCCESS
            and not outcome.timed_out
            and outcome.forwarded_signal is None
        )

    @staticmethod
    def _process_exit_result(
        return_code: int | None,
        received_signals: t.SequenceOf[int],
        diagnostics: t.VariadicTuple[str],
        *,
        timed_out: bool,
    ) -> p.Result[m.Cli.ProcessOutcome]:
        """Preserve a primary exit while surfacing additive diagnostics.

        Returns:
            The resulting ``p.Result[m.Cli.ProcessOutcome]``.

        """
        if received_signals:
            primary_exit = -abs(received_signals[0])
        elif return_code is None:
            primary_exit = None
        else:
            primary_exit = return_code
        if diagnostics:
            return r[m.Cli.ProcessOutcome].fail("; ".join(diagnostics))
        if primary_exit is None:
            return r[m.Cli.ProcessOutcome].fail(
                "root process did not expose an exit status",
            )
        return r[m.Cli.ProcessOutcome].ok(
            m.Cli.ProcessOutcome(
                raw_return_code=primary_exit,
                timed_out=timed_out,
                forwarded_signal=(received_signals[0] if received_signals else None),
            ),
        )

    @classmethod
    def _captured_process_result(
        cls,
        state: RuntimeProcessState,
        duration: float,
    ) -> p.Result[p.Cli.CommandBytesOutput]:
        """Attach captured bytes only after the owned process boundary is empty.

        Returns:
            The resulting ``p.Result[p.Cli.CommandBytesOutput]``.

        """
        return cls._process_exit_result(
            state.return_code,
            state.received_signals,
            (*state.failures, *state.cleanup_errors),
            timed_out=state.timed_out,
        ).flat_map(
            lambda outcome: r[p.Cli.CommandBytesOutput].ok(
                m.Cli.CommandBytesOutput(
                    stdout=bytes(state.stdout_output),
                    stderr=bytes(state.stderr_output),
                    outcome=outcome,
                    duration=duration,
                ),
            ),
        )


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessOutcomeMixin"]
