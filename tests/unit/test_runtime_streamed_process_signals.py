"""Public real-signal contracts for streamed process execution."""

from __future__ import annotations

import os
import signal
import sys
import threading
import time
from types import FrameType
from typing import TYPE_CHECKING

import pytest

from flext_tests import tm
from tests import m, u

if TYPE_CHECKING:
    from pathlib import Path


def _deadline(
    *, seconds: float, grace: float, exit_code: int
) -> m.Cli.ProcessDeadline:
    """Build one bounded signal-cleanup deadline."""
    return m.Cli.ProcessDeadline(
        expires_at_monotonic=time.monotonic() + seconds,
        termination_grace_seconds=grace,
        timeout_exit_code=exit_code,
    )


@pytest.mark.skipif(os.name == "nt", reason="POSIX operator-signal contract")
class TestsFlextCliRuntimeStreamedProcessSignals:
    """Prove setup-race capture, normalization, and handler restoration."""

    def test_real_signal_restores_parent_handler_after_full_cleanup(
        self, tmp_path: Path
    ) -> None:
        """Keep forwarding installed until the real child group is gone."""
        ready = tmp_path / "signal-handler-ready"
        observed: list[int] = []
        previous = signal.getsignal(signal.SIGTERM)

        def parent_handler(
            signal_number: int, _frame: FrameType | None
        ) -> None:
            observed.append(signal_number)

        child = (
            "import pathlib,sys,time;"
            "pathlib.Path(sys.argv[1]).touch();time.sleep(30)"
        )

        def send_signal() -> None:
            ready_deadline = time.monotonic() + 1.0
            while not ready.exists() and time.monotonic() < ready_deadline:
                time.sleep(0.01)
            os.kill(os.getpid(), signal.SIGTERM)

        signal.signal(signal.SIGTERM, parent_handler)
        sender = threading.Thread(target=send_signal, daemon=False)
        sender.start()
        try:
            result = u.Cli().run_to_file(
                [sys.executable, "-c", child, str(ready)],
                tmp_path / "signal-handler.log",
                deadline=_deadline(seconds=2.5, grace=1.0, exit_code=98),
            )
            sender.join(timeout=1.0)

            tm.ok(result)
            tm.that(result.value, eq=128 + signal.SIGTERM)
            tm.that(sender.is_alive(), eq=False)
            tm.that(observed, eq=[])
            tm.that(signal.getsignal(signal.SIGTERM), is_=parent_handler)
        finally:
            signal.signal(
                signal.SIGTERM,
                signal.SIG_DFL if previous is None else previous,
            )

    def test_signal_during_pre_spawn_preparation_is_not_lost(
        self, tmp_path: Path
    ) -> None:
        """Queue SIGTERM before spawn and forward it after containment exists."""
        output_file = tmp_path / "pre-spawn-signal.log"
        harness = (
            "import os,signal,sys,threading,time;"
            "from flext_cli import m,u;"
            "threading.Thread(target=lambda:("
            "time.sleep(.01),os.kill(os.getpid(),signal.SIGTERM)),"
            "daemon=True).start();"
            "deadline=m.Cli.ProcessDeadline("
            "expires_at_monotonic=time.monotonic()+2.5,"
            "termination_grace_seconds=1.0,timeout_exit_code=96);"
            "result=u.Cli.run_to_file("
            "[sys.executable,'-c','import time;time.sleep(30)'],"
            f"{str(output_file)!r},input_data=b'x'*(32*1024*1024),"
            "deadline=deadline);"
            "raise SystemExit(result.value if result.success else 99)"
        )

        completed = u.Cli().run_bytes(
            [sys.executable, "-c", harness], timeout=4
        )

        tm.ok(completed)
        tm.that(completed.value.exit_code, eq=128 + signal.SIGTERM)

    @pytest.mark.parametrize(
        "operator_signal",
        [
            pytest.param(signal.SIGINT, id="sigint"),
            pytest.param(signal.SIGTERM, id="sigterm"),
        ],
    )
    def test_manual_interrupt_is_forwarded_and_normalized(
        self, tmp_path: Path, operator_signal: signal.Signals
    ) -> None:
        """Forward an operator signal and return normalized status."""
        ready = tmp_path / "child-ready"
        child = (
            "import pathlib,signal,sys,time;"
            "signal.signal(int(sys.argv[2]),signal.SIG_IGN);"
            "pathlib.Path(sys.argv[1]).touch();time.sleep(30)"
        )
        harness = (
            "import sys,time;"
            "from flext_cli import m,u;"
            "deadline=m.Cli.ProcessDeadline("
            "expires_at_monotonic=time.monotonic()+2.5,"
            "termination_grace_seconds=1.0,timeout_exit_code=95);"
            f"result=u.Cli.run_to_file([sys.executable,'-c',{child!r},"
            f"{str(ready)!r},{str(int(operator_signal))!r}],"
            f"{str(tmp_path / 'manual.log')!r},deadline=deadline);"
            "raise SystemExit(result.value if result.success else 99)"
        )
        started = u.Cli().process_start([sys.executable, "-c", harness])
        tm.ok(started)
        managed = started.value
        ready_deadline = time.monotonic() + 1.0
        while not ready.exists() and time.monotonic() < ready_deadline:
            time.sleep(0.01)

        tm.that(ready.exists(), eq=True)
        os.kill(managed.pid, operator_signal)
        completed = managed.wait(timeout=3.0)

        tm.ok(completed)
        tm.that(completed.value, eq=128 + operator_signal)


__all__: list[str] = ["TestsFlextCliRuntimeStreamedProcessSignals"]
