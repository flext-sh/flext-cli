"""Deterministic scheduling of real child completion at the monitor boundary.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import linecache
import sys
import threading
from pathlib import Path
from types import FrameType
from typing import TYPE_CHECKING

from flext_tests import tm

from tests import u

if TYPE_CHECKING:
    from _typeshed import TraceFunction


class TestsRuntimeProcessCompletion:
    """A completed child must not wait for its execution deadline."""

    @staticmethod
    def test_completion_before_wake_clear_ends_monitoring(tmp_path: Path) -> None:
        """Schedule a real waiter at the exact lost-notification boundary.

        The trace holds the monitor at its first ``state.wake.clear()`` until the
        root waiter has set both ``process_done`` and ``wake``, so completion
        is always observed before the wake is cleared. A monitor that lost
        that notification would sleep until its deadline and report
        ``timed_out``; the outcome, not the host clock, proves it did not.
        Tracing only controls thread scheduling; process creation, events,
        waiting, output and cleanup all use the unmodified public runtime.
        """
        scheduled: list[bool] = []

        def trace(frame: FrameType, event: str, _argument: object) -> TraceFunction:
            if (
                event == "line"
                and frame.f_code.co_name == "_monitor_process"
                and linecache.getline(frame.f_code.co_filename, frame.f_lineno).strip()
                == "state.wake.clear()"
                and not scheduled
            ):
                state = frame.f_locals["state"]
                done = state.process_done
                wake = state.wake
                assert isinstance(done, threading.Event)
                assert isinstance(wake, threading.Event)
                done.wait()
                wake.wait()
                scheduled.append(True)
            return trace

        previous = sys.gettrace()
        try:
            sys.settrace(trace)
            result = u.Cli().run_to_file(
                [sys.executable, "-I", "-S", "-c", "print('complete')"],
                tmp_path / "completion.log",
                timeout=4,
            )
        finally:
            sys.settrace(previous)
        outcome = tm.ok(result)
        assert scheduled == [True]
        assert outcome.raw_return_code == 0
        assert not outcome.timed_out
        assert (tmp_path / "completion.log").read_text() == "complete\n"
