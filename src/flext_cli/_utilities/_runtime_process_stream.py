"""Byte-exact process stream mirroring for ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import threading
from typing import IO, BinaryIO, ClassVar

from flext_cli import r, t
from flext_cli._utilities._runtime_models import (
    FlextCliRuntimeBinaryStream,
    FlextCliRuntimeOutputTarget,
    FlextCliRuntimeProcessState,
)


class FlextCliUtilitiesRuntimeProcessStreamMixin:
    """Route child bytes to captured, durable, and live output owners."""

    _STREAM_CHUNK_BYTES: ClassVar[int] = 64 * 1024
    _STREAM_POLL_SECONDS: ClassVar[float] = 0.01

    @staticmethod
    def _pump_process_input(
        sink: BinaryIO,
        payload: bytes,
        failures: t.MutableSequenceOf[str],
        wake: threading.Event,
    ) -> None:
        """Write every input byte to the child pipe, then publish EOF."""
        remaining = memoryview(payload)
        try:
            while remaining:
                written = sink.write(remaining)
                if written <= 0:
                    failures.append("stdin write made no progress")
                    return
                remaining = remaining[written:]
        except BrokenPipeError:
            # Why: the child stopped reading stdin early (exited or was
            # killed) -- an expected end for the writer, not an execution
            # failure; wake immediately instead of waiting for `finally`.
            wake.set()
        except (OSError, ValueError) as exc:
            failures.append(
                r[str].fail(f"stdin write error: {exc}", exception=exc).error
                or str(exc),
            )
        finally:
            try:
                sink.close()
            except (OSError, ValueError) as exc:
                failures.append(
                    r[str].fail(f"stdin close error: {exc}", exception=exc).error
                    or str(exc),
                )
            wake.set()

    @classmethod
    def _pump_process_output(
        cls,
        source: IO[bytes],
        target: FlextCliRuntimeOutputTarget,
        state: FlextCliRuntimeProcessState,
    ) -> None:
        """Own one child pipe until EOF and preserve each byte exactly once."""
        live_available = target.live_fd is not None
        try:
            while not state.pump_stop.is_set():
                chunk = cls._read_process_chunk(source, state.failures)
                if chunk is None:
                    return
                if target.durable_log is not None:
                    durable_error = cls._write_durable_chunk(target.durable_log, chunk)
                    if durable_error is not None:
                        state.failures.append(durable_error)
                        return
                if target.captured_output is not None:
                    target.captured_output.extend(chunk)
                if live_available and target.live_fd is not None:
                    live_available = cls._write_live_chunk(
                        target.live_fd,
                        chunk,
                        state.pump_stop,
                        state.failures,
                    )
        finally:
            state.wake.set()

    @classmethod
    def _read_process_chunk(
        cls,
        source: IO[bytes],
        failures: t.MutableSequenceOf[str],
    ) -> bytes | None:
        try:
            chunk = source.read(cls._STREAM_CHUNK_BYTES)
        except (OSError, ValueError) as exc:
            failures.append(
                r[str].fail(f"output read error: {exc}", exception=exc).error
                or str(exc),
            )
            return None
        return chunk or None

    @staticmethod
    def _write_durable_chunk(
        durable_log: FlextCliRuntimeBinaryStream,
        chunk: bytes,
    ) -> str | None:
        remaining = memoryview(chunk)
        try:
            while remaining:
                written = durable_log.write(remaining)
                if written is None or written <= 0:
                    return "durable log write made no progress"
                remaining = remaining[written:]
            durable_log.flush()
        except (OSError, ValueError) as exc:
            return r[str].fail(
                f"durable log write error: {exc}",
                exception=exc,
            ).error or str(exc)
        return None

    @classmethod
    def _write_live_chunk(
        cls,
        live_fd: int,
        chunk: bytes,
        stop: threading.Event,
        diagnostics: t.MutableSequenceOf[str],
    ) -> bool:
        remaining = memoryview(chunk)
        while remaining and not stop.is_set():
            try:
                written = os.write(live_fd, remaining)
            except BlockingIOError:
                stop.wait(cls._STREAM_POLL_SECONDS)
                continue
            except (BrokenPipeError, OSError, ValueError) as exc:
                diagnostics.append(
                    r[str].fail(f"live output unavailable: {exc}", exception=exc).error
                    or str(exc),
                )
                return False
            if written <= 0:
                diagnostics.append("live output write made no progress")
                return False
            remaining = remaining[written:]
        if remaining:
            diagnostics.append("live output mirror stopped after durable persistence")
            return False
        return True


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessStreamMixin"]
