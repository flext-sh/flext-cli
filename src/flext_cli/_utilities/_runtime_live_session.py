"""Bounded live-output relay isolated from the authoritative durable reader."""

from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
from typing import ClassVar, cast

from flext_cli import m, p, r
from flext_cli._utilities._runtime_live_cleanup import (
    FlextCliUtilitiesRuntimeLiveCleanupMixin,
)


class FlextCliUtilitiesRuntimeLiveSession(
    FlextCliUtilitiesRuntimeLiveCleanupMixin
):
    """Relay best-effort live bytes without blocking durable child capture."""

    _RELAY_PROGRAM: ClassVar[str] = (
        "import os,sys;"
        "source=sys.stdin.buffer;"
        "target=sys.stdout.fileno();"
        "\nwhile chunk:=source.read(65536):"
        "\n view=memoryview(chunk)"
        "\n while view:"
        "\n  written=os.write(target,view)"
        "\n  view=view[written:]"
    )

    def __init__(
        self,
        relay: p.Cli.ProcessHandle,
        policy: p.Cli.ProcessLivePolicy,
    ) -> None:
        self._relay = relay
        self._policy = policy
        self._queue: queue.Queue[bytes | None] = queue.Queue(
            policy.queue_capacity_chunks
        )
        self._force_stop = threading.Event()
        self._disabled = threading.Event()
        self._diagnostic_lock = threading.Lock()
        self._nonfatal: list[str] = []
        self._cleanup: list[str] = []
        self._fatal: list[str] = []
        self._writer = threading.Thread(
            target=self._write_relay,
            name="flext-cli-live-relay",
            daemon=False,
        )
        self._writer_started = False

    @classmethod
    def start(
        cls,
        policy: p.Cli.ProcessLivePolicy,
        cleanup_deadline: float,
    ) -> p.Result[p.Cli.ProcessLiveSession]:
        """Start an interruptible relay process inheriting the live terminal."""
        try:
            relay = cast(
                "p.Cli.ProcessHandle",
                subprocess.Popen(
                    [sys.executable, "-c", cls._RELAY_PROGRAM],
                    stdin=subprocess.PIPE,
                    stdout=None,
                    stderr=subprocess.DEVNULL,
                    text=False,
                    bufsize=0,
                    start_new_session=os.name != "nt",
                    creationflags=(
                        int(getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
                        if os.name == "nt"
                        else 0
                    ),
                ),
            )
        except (OSError, ValueError) as exc:
            return r[p.Cli.ProcessLiveSession].fail(
                f"live output truncated: relay spawn failed: {exc}"
            )
        session = cls(relay, policy)
        relay_stdin = relay.stdin
        if relay_stdin is None:
            session._disable(
                "live output truncated: relay stdin unavailable"
            )
            session._terminate_relay(
                cleanup_deadline,
                phase="setup",
                force=True,
            )
            return r[p.Cli.ProcessLiveSession].ok(session)
        try:
            os.set_blocking(relay_stdin.fileno(), False)
            session._writer.start()
            session._writer_started = True
        except (OSError, RuntimeError, ValueError) as exc:
            session._disable(
                f"live output truncated: relay setup failed: {exc}"
            )
            session._close_relay_input()
            session._terminate_relay(
                cleanup_deadline,
                phase="setup",
                force=True,
            )
        return r[p.Cli.ProcessLiveSession].ok(session)

    def finish(self, cleanup_deadline: float) -> m.Cli.ProcessLiveDiagnostics:
        """Stop writer and relay within the shared cleanup deadline."""
        if self._writer_started and not self._disabled.is_set():
            try:
                self._queue.put_nowait(None)
            except queue.Full:
                self._disable(
                    "live output truncated: relay queue did not drain"
                )
        self._join_writer(cleanup_deadline)
        if self._writer_started and self._writer.is_alive():
            self._disable(
                "live output truncated: relay writer exceeded cleanup deadline"
            )
        self._force_stop.set()
        self._close_relay_input()
        self._join_writer(cleanup_deadline)
        if self._writer_started and self._writer.is_alive():
            self._record_fatal("live output relay writer remained alive")
        self._terminate_relay(
            cleanup_deadline,
            phase="final cleanup",
            force=self._disabled.is_set(),
        )
        return m.Cli.ProcessLiveDiagnostics(
            nonfatal=tuple(self._nonfatal),
            cleanup=tuple(self._cleanup),
            fatal=tuple(self._fatal),
        )

__all__: list[str] = ["FlextCliUtilitiesRuntimeLiveSession"]
