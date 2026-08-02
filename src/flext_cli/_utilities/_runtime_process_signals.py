"""Signal capture and restoration for one streamed process lifecycle."""

from __future__ import annotations

import os
import signal
from types import FrameType
from typing import cast

from flext_cli import t


class FlextCliUtilitiesRuntimeProcessSignalsMixin:
    """Keep operator handlers installed through complete owned cleanup."""

    @classmethod
    def _install_forwarding_handlers(
        cls,
        received_signals: list[int],
    ) -> list[t.Cli.SignalHandlerState]:
        """Capture operator signals before opening the containment window."""
        previous_handlers: list[t.Cli.SignalHandlerState] = []

        def forward(signal_number: int, _frame: FrameType | None) -> None:
            received_signals.append(signal_number)

        forwarded = (signal.SIGINT, signal.SIGTERM)
        if os.name != "nt" and hasattr(signal, "SIGHUP"):
            forwarded = (*forwarded, signal.SIGHUP)
        try:
            for signal_number in forwarded:
                previous_raw = signal.getsignal(signal_number)
                previous = (
                    signal.SIG_DFL
                    if previous_raw is None
                    else cast("t.Cli.SignalHandler", previous_raw)
                )
                signal.signal(signal_number, forward)
                previous_handlers.append((signal_number, previous))
        except (OSError, ValueError) as exc:
            restore_errors = cls._restore_forwarding_handlers(previous_handlers)
            detail = f"; {'; '.join(restore_errors)}" if restore_errors else ""
            message = f"signal-handler setup error: {exc}{detail}"
            raise RuntimeError(message) from exc
        return previous_handlers

    @staticmethod
    def _restore_forwarding_handlers(
        previous_handlers: list[t.Cli.SignalHandlerState],
    ) -> tuple[str, ...]:
        """Restore every parent handler after complete owned cleanup."""
        errors: list[str] = []
        for signal_number, previous in reversed(previous_handlers):
            try:
                signal.signal(signal_number, previous)
            except (OSError, ValueError) as exc:
                errors.append(
                    f"signal-handler {signal_number.name} restore error: {exc}"
                )
        return tuple(errors)


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessSignalsMixin"]
