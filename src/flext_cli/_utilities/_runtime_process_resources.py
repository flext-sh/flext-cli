"""Pre-spawn and durable-resource ownership for streamed processes."""

from __future__ import annotations

import contextlib
import os
import sys
import tempfile
import time
from typing import BinaryIO

from flext_cli import c, p, r


class FlextCliUtilitiesRuntimeProcessResourcesMixin:
    """Prepare stdin/live descriptors and finalize durable resources."""

    @staticmethod
    def _prepare_streamed_stdin(
        stack: contextlib.ExitStack, input_data: str | bytes | None
    ) -> p.Result[BinaryIO | None]:
        if input_data is None:
            return r[BinaryIO | None].ok(None)
        payload = (
            input_data.encode("utf-8") if isinstance(input_data, str) else input_data
        )
        try:
            prepared = tempfile.TemporaryFile()
            stack.callback(prepared.close)
            written = prepared.write(payload)
            prepared.seek(0)
        except c.EXC_OS_VALUE as exc:
            return r[BinaryIO | None].fail(f"stdin preparation error: {exc}")
        if written != len(payload):
            return r[BinaryIO | None].fail("stdin preparation was partial")
        return r[BinaryIO | None].ok(prepared)

    @staticmethod
    def _prepare_live_descriptor(
        stack: contextlib.ExitStack, *, live: bool
    ) -> p.Result[int | None]:
        if not live:
            return r[int | None].ok(None)
        try:
            live_fd = FlextCliUtilitiesRuntimeProcessResourcesMixin._open_live_fd(
                stack
            )
        except c.EXC_OS_VALUE as exc:
            return r[int | None].fail(f"live output preparation error: {exc}")
        return r[int | None].ok(live_fd)

    @staticmethod
    def _open_live_fd(stack: contextlib.ExitStack) -> int:
        live_fd = os.dup(sys.stdout.fileno())
        stack.callback(os.close, live_fd)
        if os.name != "nt" or not os.isatty(live_fd):
            was_blocking = os.get_blocking(live_fd)
            os.set_blocking(live_fd, False)
            stack.callback(os.set_blocking, live_fd, was_blocking)
        return live_fd

    @staticmethod
    def _flush_durable_log(
        durable_log: BinaryIO, absolute_deadline: float | None
    ) -> tuple[str, ...]:
        errors: list[str] = []
        try:
            durable_log.flush()
            os.fsync(durable_log.fileno())
        except c.EXC_OS_VALUE as exc:
            errors.append(f"durable log flush error: {exc}")
        if absolute_deadline is not None:
            if time.monotonic() > absolute_deadline:
                errors.append("process deadline expired before durable log flush")
        return tuple(errors)

    @staticmethod
    def _close_process_resources(
        stack: contextlib.ExitStack,
    ) -> tuple[str, ...]:
        try:
            stack.close()
        except c.EXC_OS_VALUE as exc:
            return (f"process resource close error: {exc}",)
        return ()


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessResourcesMixin"]
