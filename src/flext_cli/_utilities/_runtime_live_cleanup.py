"""Bounded cleanup and death proof for the owned live-output relay."""

from __future__ import annotations

import time

from flext_cli._utilities._runtime_live_writer import (
    FlextCliUtilitiesRuntimeLiveWriterMixin,
)


class FlextCliUtilitiesRuntimeLiveCleanupMixin(
    FlextCliUtilitiesRuntimeLiveWriterMixin
):
    """Close, stop, reap, and prove the isolated relay lifecycle."""

    def _close_relay_input(self) -> None:
        """Close the owned relay input while retaining cleanup failures."""
        relay_stdin = self._relay.stdin
        if relay_stdin is not None:
            try:
                relay_stdin.close()
            except (OSError, ValueError) as exc:
                self._record_cleanup(f"live output relay close error: {exc}")

    def _join_writer(self, cleanup_deadline: float) -> None:
        """Join the relay writer only when setup actually started it."""
        if self._writer_started:
            self._writer.join(
                max(0.0, cleanup_deadline - time.monotonic())
            )

    def _terminate_relay(
        self,
        deadline: float,
        *,
        phase: str,
        force: bool,
    ) -> None:
        """Reap naturally when healthy, otherwise kill and prove death."""
        relay_alive = self._relay_alive(phase)
        if relay_alive and not force:
            natural_deadline = min(
                deadline,
                time.monotonic()
                + (
                    self._policy.relay_poll_seconds
                    * self._policy.queue_capacity_chunks
                ),
            )
            relay_alive = not self._wait_until_reaped(
                natural_deadline,
                phase=phase,
            )
            if relay_alive:
                self._disable(
                    "live output truncated: terminal sink did not drain"
                )
                force = True
        if relay_alive and force:
            try:
                self._relay.kill()
            except (OSError, ValueError) as exc:
                self._record_cleanup(
                    f"live output relay kill error during {phase}: {exc}"
                )
        if relay_alive:
            relay_alive = not self._wait_until_reaped(
                deadline,
                phase=phase,
            )
            if relay_alive:
                self._record_fatal(
                    f"live output relay remained alive after {phase}"
                )
        if self._relay_alive(f"death proof after {phase}"):
            self._record_fatal(
                f"live output relay death proof failed after {phase}"
            )

    def _wait_until_reaped(self, deadline: float, *, phase: str) -> bool:
        """Poll within the shared budget until the relay is reaped."""
        while time.monotonic() < deadline:
            if not self._relay_alive(phase):
                return True
            time.sleep(
                min(
                    self._policy.relay_poll_seconds,
                    max(0.0, deadline - time.monotonic()),
                )
            )
        return not self._relay_alive(phase)

    def _relay_alive(self, phase: str) -> bool:
        """Probe relay ownership while retaining poll failures."""
        try:
            return self._relay.poll() is None
        except (OSError, ValueError) as exc:
            self._record_cleanup(
                f"live output relay poll error during {phase}: {exc}"
            )
            return True


__all__: list[str] = ["FlextCliUtilitiesRuntimeLiveCleanupMixin"]
