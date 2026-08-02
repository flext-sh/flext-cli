"""Typed nonblocking writer for the isolated live-output relay."""

from __future__ import annotations

import os
import queue
import threading
from typing import ClassVar

from flext_cli import p


class FlextCliUtilitiesRuntimeLiveWriterMixin:
    """Offer durable chunks to a relay without blocking durable capture."""

    _relay: p.Cli.ProcessHandle
    _policy: p.Cli.ProcessLivePolicy
    _queue: queue.Queue[bytes | None]
    _force_stop: threading.Event
    _disabled: threading.Event
    _diagnostic_lock: threading.Lock
    _nonfatal: list[str]
    _cleanup: list[str]
    _fatal: list[str]
    _writer: threading.Thread
    _writer_started: bool
    _RELAY_PROGRAM: ClassVar[str]

    def offer(self, chunk: bytes) -> None:
        """Queue one durable chunk without waiting for the live sink."""
        if self._disabled.is_set():
            return
        try:
            self._queue.put_nowait(chunk)
        except queue.Full:
            self._disable("live output truncated: relay queue reached capacity")

    def _write_relay(self) -> None:
        """Write queued bytes only to the dedicated nonblocking relay pipe."""
        relay_stdin = self._relay.stdin
        if relay_stdin is None:
            self._disable("live output truncated: relay stdin disappeared")
            return
        target_fd = relay_stdin.fileno()
        while not self._force_stop.is_set():
            try:
                chunk = self._queue.get(timeout=self._policy.relay_poll_seconds)
            except queue.Empty:
                continue
            if chunk is None:
                return
            remaining = memoryview(chunk)
            while remaining and not self._force_stop.is_set():
                try:
                    written = os.write(target_fd, remaining)
                    if written <= 0:
                        no_progress = "relay pipe write made no progress"
                        raise OSError(no_progress)
                    remaining = remaining[written:]
                except BlockingIOError:
                    self._disable(
                        "live output truncated: relay pipe backpressure"
                    )
                    return
                except (BrokenPipeError, OSError, ValueError) as exc:
                    self._disable(f"live output truncated: relay write failed: {exc}")
                    return

    def _disable(self, diagnostic: str) -> None:
        """Disable live offers while retaining the first truncation reason."""
        with self._diagnostic_lock:
            if not self._disabled.is_set():
                self._nonfatal.append(diagnostic)
                self._disabled.set()
        self._force_stop.set()

    def _record_cleanup(self, diagnostic: str) -> None:
        """Retain every recoverable relay cleanup diagnostic."""
        with self._diagnostic_lock:
            self._cleanup.append(diagnostic)

    def _record_fatal(self, diagnostic: str) -> None:
        """Retain every residual relay ownership failure."""
        with self._diagnostic_lock:
            self._fatal.append(diagnostic)


__all__: list[str] = ["FlextCliUtilitiesRuntimeLiveWriterMixin"]
