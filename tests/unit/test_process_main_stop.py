"""A stopped CLI process runs its entry's cleanup before it exits.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import signal
from pathlib import Path

import pytest

from tests import c, tm, u


class TestsFlextCliProcessMainStop:
    """``process_main`` turns an operator signal into a normal exit."""

    @staticmethod
    @pytest.mark.parametrize("stop", [signal.SIGTERM, signal.SIGHUP])
    def test_stop_signal_runs_the_entry_cleanup(
        tmp_path: Path,
        stop: signal.Signals,
    ) -> None:
        """The entry's ``finally`` runs and the exit code is 128 + signal."""
        owned = tmp_path / "owned"
        previous = signal.getsignal(stop)

        def entry() -> int:
            owned.mkdir()
            try:
                signal.raise_signal(stop)
            finally:
                owned.rmdir()
            return 0

        try:
            with pytest.raises(SystemExit) as stopped:
                u.Cli.process_main(entry)
        finally:
            signal.signal(stop, previous)
        tm.that(stopped.value.code, eq=c.Cli.SIGNAL_EXIT_OFFSET + stop)
        tm.that(owned.exists(), eq=False)
