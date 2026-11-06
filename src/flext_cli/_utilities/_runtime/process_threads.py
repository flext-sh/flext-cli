"""Thread ownership for streamed process wait and output work.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import threading
from collections.abc import MutableSequence
from typing import TYPE_CHECKING, BinaryIO

from flext_cli._utilities._runtime import (
    FlextCliUtilitiesRuntimeProcessStream,
    FlextCliUtilitiesRuntimeProcessWait,
)

if TYPE_CHECKING:
    from flext_cli import p


class FlextCliUtilitiesRuntimeProcessThreads(
    FlextCliUtilitiesRuntimeProcessStream,
    FlextCliUtilitiesRuntimeProcessWait,
):
    """Start bounded lifecycle threads at their canonical owner."""

    @classmethod
    def _start_input_pump(
        cls,
        sink: BinaryIO,
        payload: bytes,
        failures: MutableSequence[str],
        wake: threading.Event,
    ) -> threading.Thread:
        """Start the sole non-daemon writer for one anonymous stdin pipe.

        Returns:
            The resulting ``threading.Thread``.

        """
        pump = threading.Thread(
            target=cls._pump_process_input,
            args=(sink, payload, failures, wake),
            name="flext-cli-process-input",
            daemon=False,
        )
        pump.start()
        return pump

    @classmethod
    def _start_root_waiter(
        cls,
        process: p.Cli.ProcessHandle,
        state: p.Cli.RuntimeProcessState,
    ) -> threading.Thread:
        waiter = threading.Thread(
            target=cls._wait_for_root_process,
            args=(process, state),
            name="flext-cli-process-waiter",
            daemon=False,
        )
        waiter.start()
        return waiter


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessThreads"]
