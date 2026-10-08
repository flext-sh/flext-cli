"""Output-pipe ownership for the canonical contained process lifecycle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import threading
from typing import IO, TYPE_CHECKING

from flext_cli import m
from flext_cli._utilities import FlextCliUtilitiesRuntimeProcessThreadsMixin

if TYPE_CHECKING:
    from flext_cli import p, t


class FlextCliUtilitiesRuntimeProcessOutputMixin(
    FlextCliUtilitiesRuntimeProcessThreadsMixin,
):
    """Attach every requested child pipe to exactly one bounded pump."""

    @classmethod
    def _start_process_output(
        cls,
        process: p.Cli.ProcessHandle,
        state: m.Cli.RuntimeProcessState,
        live_fd: int | None,
        *,
        capture_output: bool,
    ) -> t.VariadicTuple[t.Pair[threading.Thread, IO[bytes]]]:
        combine_output = state.durable_log is not None
        pipe_output = combine_output or capture_output
        pump_streams: list[tuple[threading.Thread, IO[bytes]]] = []
        stdout_source = process.stdout
        if pipe_output and stdout_source is None:
            state.failures.append("process stdout is not available")
        elif stdout_source is not None:
            state.stack.callback(stdout_source.close)
            stdout_pump = cls._start_output_pump(
                stdout_source,
                m.Cli.RuntimeOutputTarget(
                    durable_log=state.durable_log,
                    captured_output=state.stdout_output if capture_output else None,
                    live_fd=live_fd,
                ),
                state,
                thread_name=(
                    "flext-cli-process-output"
                    if combine_output
                    else "flext-cli-process-stdout"
                ),
            )
            pump_streams.append((stdout_pump, stdout_source))
        stderr_source = process.stderr
        if capture_output and stderr_source is None:
            state.failures.append("process stderr is not available")
        elif stderr_source is not None:
            state.stack.callback(stderr_source.close)
            stderr_pump = cls._start_output_pump(
                stderr_source,
                m.Cli.RuntimeOutputTarget(captured_output=state.stderr_output),
                state,
                thread_name="flext-cli-process-stderr",
            )
            pump_streams.append((stderr_pump, stderr_source))
        return tuple(pump_streams)


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessOutputMixin"]
