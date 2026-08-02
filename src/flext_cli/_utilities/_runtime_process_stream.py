"""Byte-exact process stream mirroring for ``u.Cli``."""

from __future__ import annotations

import threading
from typing import BinaryIO

from flext_cli import p


class FlextCliUtilitiesRuntimeProcessStreamMixin:
    """Mirror combined child output to a live descriptor and durable log."""

    @classmethod
    def _pump_process_output(
        cls,
        source: BinaryIO,
        durable_log: BinaryIO,
        live_sink: p.Cli.ProcessLiveSink | None,
        failures: list[str],
        stop: threading.Event,
        stream_chunk_bytes: int,
        poll_seconds: float,
    ) -> None:
        """Persist every chunk, then offer it to the nonblocking live sink."""
        while not stop.is_set():
            try:
                chunk = source.read(stream_chunk_bytes)
            except BlockingIOError:
                stop.wait(poll_seconds)
                continue
            except (OSError, ValueError) as exc:
                failures.append(f"output read error: {exc}")
                return
            if chunk is None:
                stop.wait(poll_seconds)
                continue
            if not chunk:
                return
            durable_error = cls._persist_process_chunk(durable_log, chunk)
            if durable_error is not None:
                failures.append(durable_error)
                return
            if live_sink is not None:
                live_sink.offer(bytes(chunk))

    @staticmethod
    def _persist_process_chunk(
        durable_log: BinaryIO,
        chunk: bytes,
    ) -> str | None:
        """Write one complete child-output chunk to the durable sink."""
        remaining = memoryview(chunk)
        try:
            while remaining:
                written = durable_log.write(remaining)
                if written is None or written <= 0:
                    no_progress = "durable log write made no progress"
                    raise OSError(no_progress)
                remaining = remaining[written:]
            durable_log.flush()
        except (OSError, ValueError) as exc:
            return f"durable log write error: {exc}"
        return None


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessStreamMixin"]
