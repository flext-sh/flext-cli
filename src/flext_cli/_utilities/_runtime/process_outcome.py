"""Typed exact exits for streamed process execution.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence

from flext_core import r

from flext_cli import c, m, p


class FlextCliUtilitiesRuntimeProcessOutcome:
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
    def process_raise_if_interrupted[T](result: p.Result[T]) -> None:
        """Propagate an operator signal proven by a completed command result.

        Ordinary failures, timeouts and successful results remain untouched.
        Callers retain the original result and its causal exception.

        Raises:
            SystemExit: When native failure metadata proves a forwarded signal.

        """
        if result.failure and result.error_data is not None:
            signum = result.error_data.get(c.Cli.PROCESS_FORWARDED_SIGNAL_KEY)
            if (
                isinstance(signum, int)
                and signum > 0
                and result.error_data.get(c.Cli.PROCESS_TIMED_OUT_KEY) is False
                and result.error_data.get(c.Cli.PROCESS_EXIT_CODE_KEY) == -signum
            ):
                raise SystemExit(-signum) from result.exception

    @staticmethod
    def _process_exit_result(
        return_code: int | None,
        received_signals: Sequence[int],
        diagnostics: tuple[str, ...],
        *,
        timed_out: bool,
    ) -> p.Result[p.Cli.ProcessOutcome]:
        """Preserve a primary exit while surfacing additive diagnostics.

        A lifecycle with diagnostics fails, and the failure still carries the
        observed exit, timeout and forwarded signal in ``error_data``
        (``c.Cli.PROCESS_EXIT_CODE_KEY``, ``PROCESS_TIMED_OUT_KEY``,
        ``PROCESS_FORWARDED_SIGNAL_KEY``), the shape ``run`` reports.

        Returns:
            The resulting ``p.Result[p.Cli.ProcessOutcome]``.

        """
        forwarded_signal = received_signals[0] if received_signals else None
        if forwarded_signal is not None:
            primary_exit = -abs(forwarded_signal)
        else:
            primary_exit = return_code
        if diagnostics:
            return r[p.Cli.ProcessOutcome].fail(
                "; ".join(diagnostics),
                error_data={
                    c.Cli.PROCESS_EXIT_CODE_KEY: primary_exit,
                    c.Cli.PROCESS_TIMED_OUT_KEY: timed_out,
                    c.Cli.PROCESS_FORWARDED_SIGNAL_KEY: forwarded_signal,
                },
            )
        if primary_exit is None:
            return r[p.Cli.ProcessOutcome].fail(
                "root process did not expose an exit status",
            )
        return r[p.Cli.ProcessOutcome].ok(
            m.Cli.ProcessOutcome(
                raw_return_code=primary_exit,
                timed_out=timed_out,
                forwarded_signal=forwarded_signal,
            ),
        )

    @classmethod
    def _captured_process_result(
        cls,
        state: p.Cli.RuntimeProcessState,
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
                m.Cli.CommandBytesOutput.model_validate({
                    "stdout": bytes(state.stdout_output),
                    "stderr": bytes(state.stderr_output),
                    "outcome": outcome,
                    "duration": duration,
                }),
            ),
        )


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessOutcome"]
