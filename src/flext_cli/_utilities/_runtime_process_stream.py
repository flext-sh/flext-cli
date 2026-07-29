"""Byte-exact process stream mirroring for ``u.Cli``."""

from __future__ import annotations

import os
import threading
from typing import BinaryIO, ClassVar


class FlextCliUtilitiesRuntimeProcessStreamMixin:
    """Mirror combined child output to a live descriptor and durable log."""

    _STREAM_CHUNK_BYTES: ClassVar[int] = 64 * 1024
    _STREAM_POLL_SECONDS: ClassVar[float] = 0.01

    @classmethod
    def _pump_process_output(
        cls,
        source: BinaryIO,
        durable_log: BinaryIO,
        live_fd: int | None,
        failures: list[str],
        stop: threading.Event,
    ) -> None:
        """Persist each chunk before bounded best-effort live mirroring."""
        live_available = live_fd is not None
        while not stop.is_set():
            try:
                chunk = source.read(cls._STREAM_CHUNK_BYTES)
            except BlockingIOError:
                stop.wait(cls._STREAM_POLL_SECONDS)
                continue
            except (OSError, ValueError) as exc:
                failures.append(f"output read error: {exc}")
                return
            if chunk is None:
                stop.wait(cls._STREAM_POLL_SECONDS)
                continue
            if not chunk:
                return
            remaining = memoryview(chunk)
            try:
                while remaining:
                    written = durable_log.write(remaining)
                    if written is None or written <= 0:
                        raise OSError("durable log write made no progress")
                    remaining = remaining[written:]
                durable_log.flush()
            except (OSError, ValueError) as exc:
                failures.append(f"durable log write error: {exc}")
                return
            if not live_available or live_fd is None:
                continue
            remaining = memoryview(chunk)
            while remaining and not stop.is_set():
                try:
                    written = os.write(live_fd, remaining)
                    if written <= 0:
                        raise OSError("live write made no progress")
                    remaining = remaining[written:]
                except BlockingIOError:
                    stop.wait(cls._STREAM_POLL_SECONDS)
                except (BrokenPipeError, OSError, ValueError) as exc:
                    failures.append(f"live output write error: {exc}")
                    live_available = False
                    break
            if remaining and stop.is_set():
                failures.append("live output drain stopped before completion")


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessStreamMixin"]
