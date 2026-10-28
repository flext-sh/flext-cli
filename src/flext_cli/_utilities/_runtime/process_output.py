"""Output-pipe ownership for the canonical contained process lifecycle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import threading
from typing import IO, TYPE_CHECKING

from flext_cli import m
from flext_cli._utilities._runtime import FlextCliUtilitiesRuntimeProcessThreads

if TYPE_CHECKING:
    from flext_cli import p, t


class FlextCliUtilitiesRuntimeProcessOutput(
    FlextCliUtilitiesRuntimeProcessThreads,
):
    """Attach every requested child pipe to exactly one bounded pump."""

    @classmethod
    def _start_process_output(
        cls,
        process: p.Cli.ProcessHandle,
        state: m.Cli.RuntimeProcessState,
        live_fds: t.Pair[int | None, int | None],
        *,
        capture_output: bool,
    ) -> tuple[t.Pair[threading.Thread, IO[bytes]], ...]:
        combine_output = state.durable_log is not None and state.durable_stderr is None
        pump_streams: list[tuple[threading.Thread, IO[bytes]]] = []
        for source, sink, captured, live_fd, channel in (
            (
                process.stdout,
                state.durable_log,
                state.stdout_output,
                live_fds[0],
                "stdout",
            ),
            (
                process.stderr,
                state.durable_stderr,
                state.stderr_output,
                live_fds[1],
                "stderr",
            ),
        ):
            required = sink is not None or (
                capture_output and not (combine_output and channel == "stderr")
            )
            if required and source is None:
                state.failures.append(f"process {channel} is not available")
            elif source is not None:
                state.stack.callback(source.close)
                pump = cls._start_output_pump(
                    source,
                    m.Cli.RuntimeOutputTarget(
                        durable_log=sink,
                        captured_output=captured if capture_output else None,
                        live_fd=live_fd,
                    ),
                    state,
                    thread_name=(
                        "flext-cli-process-output"
                        if combine_output and channel == "stdout"
                        else f"flext-cli-process-{channel}"
                    ),
                )
                pump_streams.append((pump, source))
        return tuple(pump_streams)


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessOutput"]
