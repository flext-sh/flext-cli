"""Thread ownership for streamed process wait and output work.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import threading
from typing import IO, TYPE_CHECKING, BinaryIO

from flext_cli._utilities import (
    FlextCliUtilitiesRuntimeProcessStreamMixin,
    FlextCliUtilitiesRuntimeProcessWaitMixin,
)
from flext_cli._utilities._runtime_models import (
    FlextCliRuntimeOutputTarget,
    FlextCliRuntimeProcessState,
)

if TYPE_CHECKING:
    from flext_cli import p, t


class FlextCliUtilitiesRuntimeProcessThreadsMixin(
    FlextCliUtilitiesRuntimeProcessStreamMixin,
    FlextCliUtilitiesRuntimeProcessWaitMixin,
):
    """Start bounded lifecycle threads at their canonical owner."""

    @classmethod
    def _start_input_pump(
        cls,
        sink: BinaryIO,
        payload: bytes,
        failures: t.MutableSequenceOf[str],
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
        return_codes: t.MutableSequenceOf[int],
        failures: t.MutableSequenceOf[str],
        process_done: threading.Event,
        wake: threading.Event,
    ) -> threading.Thread:
        waiter = threading.Thread(
            target=cls._wait_for_root_process,
            args=(process, return_codes, failures, process_done, wake),
            name="flext-cli-process-waiter",
            daemon=False,
        )
        waiter.start()
        return waiter

    @classmethod
    def _start_output_pump(
        cls,
        source: IO[bytes],
        target: FlextCliRuntimeOutputTarget,
        state: FlextCliRuntimeProcessState,
        *,
        thread_name: str,
    ) -> threading.Thread:
        pump = threading.Thread(
            target=cls._pump_process_output,
            args=(source, target, state),
            name=thread_name,
            daemon=False,
        )
        pump.start()
        return pump


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessThreadsMixin"]
