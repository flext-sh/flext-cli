"""Signal, deadline, and descendant containment contracts."""

from __future__ import annotations

import os
import signal
import sys
import threading
import time
from collections import UserList
from collections.abc import Iterator
from typing import TYPE_CHECKING, override

import pytest

from flext_tests import tm
from tests import m, u

if TYPE_CHECKING:
    from pathlib import Path


def _deadline(
    *, seconds: float, grace: float, exit_code: int = 124
) -> m.Cli.ProcessDeadline:
    return m.Cli.ProcessDeadline(
        expires_at_monotonic=time.monotonic() + seconds,
        termination_grace_seconds=grace,
        timeout_exit_code=exit_code,
    )


class _InterruptingCommand(UserList[str]):
    @override
    def __iter__(self) -> Iterator[str]:
        os.kill(os.getpid(), signal.SIGTERM)
        return super().__iter__()


class TestsFlextCliRuntimeProcessContainment:
    """Prove pre-spawn signals, deadline escalation, and empty boundaries."""

    @pytest.mark.skipif(os.name == "nt", reason="POSIX process-group contract")
    def test_return_proves_owned_process_group_empty(self, tmp_path: Path) -> None:
        boundary_file = tmp_path / "boundary"
        nested = "import os,time;os.close(1);os.close(2);time.sleep(30)"
        root = (
            "import os,pathlib,subprocess,sys;"
            f"child=subprocess.Popen([sys.executable,'-c',{nested!r}]);"
            "pathlib.Path(sys.argv[1]).write_text(f'{os.getpgrp()} {child.pid}')"
        )

        result = u.Cli().run_to_file(
            [sys.executable, "-c", root, str(boundary_file)],
            tmp_path / "boundary.log",
            deadline=_deadline(seconds=2.0, grace=0.8, exit_code=94),
        )

        process_group, _child = (
            int(value) for value in boundary_file.read_text().split()
        )
        tm.ok(result)
        tm.that(result.value, eq=0)
        with pytest.raises(ProcessLookupError):
            os.killpg(process_group, 0)

    @pytest.mark.skipif(os.name == "nt", reason="POSIX operator-signal contract")
    @pytest.mark.parametrize("signal_number", [signal.SIGINT, signal.SIGTERM])
    def test_manual_signal_is_forwarded_and_normalized(
        self, tmp_path: Path, signal_number: signal.Signals
    ) -> None:
        ready = tmp_path / f"child-ready-{signal_number}"
        output_file = tmp_path / f"manual-{signal_number}.log"
        child = (
            "import pathlib,signal,sys,time;"
            "signal.signal(signal.SIGINT,signal.SIG_IGN);"
            "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
            "pathlib.Path(sys.argv[1]).touch();time.sleep(30)"
        )
        signaler_errors: list[str] = []

        def signal_when_ready() -> None:
            ready_deadline = time.monotonic() + 1.0
            while not ready.exists() and time.monotonic() < ready_deadline:
                time.sleep(0.005)
            if ready.exists():
                os.kill(os.getpid(), signal_number)
            else:
                signaler_errors.append("child did not become ready")

        signaler = threading.Thread(target=signal_when_ready, daemon=False)
        signaler.start()
        signal_started = time.monotonic()
        result = u.Cli().run_to_file(
            [sys.executable, "-c", child, str(ready)],
            output_file,
            deadline=_deadline(seconds=3.0, grace=1.0, exit_code=95),
        )
        signaler.join(timeout=1.0)

        tm.ok(result)
        tm.that(result.value, eq=128 + signal_number)
        tm.that(signaler_errors, eq=[])
        tm.that(signaler.is_alive(), eq=False)
        tm.that(time.monotonic() - signal_started, lt=3.0)

    @pytest.mark.skipif(os.name == "nt", reason="POSIX operator-signal contract")
    def test_pre_spawn_signal_is_captured_before_command_materialization(
        self, tmp_path: Path
    ) -> None:
        marker = tmp_path / "must-not-spawn"
        result = u.Cli().run_to_file(
            _InterruptingCommand([
                sys.executable,
                "-c",
                "import pathlib,sys;pathlib.Path(sys.argv[1]).touch()",
                str(marker),
            ]),
            tmp_path / "pre-spawn.log",
        )

        tm.ok(result)
        tm.that(result.value, eq=128 + signal.SIGTERM)
        tm.that(marker.exists(), eq=False)

    def test_deadline_forwards_interrupt_before_forced_cleanup(
        self, tmp_path: Path
    ) -> None:
        output_file = tmp_path / "interrupt.log"
        script = (
            "import os,signal,time;"
            "handler=lambda *_: (os.write(1,b'interrupted\\n'),raise_exit())[0];"
            "raise_exit=lambda: (_ for _ in ()).throw(SystemExit(0));"
            "signal.signal(signal.SIGINT,handler);"
            "signal.signal(getattr(signal,'SIGBREAK',signal.SIGINT),handler);"
            "time.sleep(30)"
        )
        started = time.monotonic()

        result = u.Cli().run_to_file(
            [sys.executable, "-c", script],
            output_file,
            deadline=_deadline(seconds=1.2, grace=0.6, exit_code=91),
        )

        tm.ok(result)
        tm.that(result.value, eq=91)
        tm.that(output_file.read_bytes(), has=b"interrupted")
        tm.that(time.monotonic() - started, lt=1.2)

    def test_deadline_kills_recursive_process_tree(self, tmp_path: Path) -> None:
        output_file = tmp_path / "tree.log"
        heartbeat = tmp_path / "heartbeat"
        child = (
            "import pathlib,signal,sys,time;"
            "signal.signal(signal.SIGINT,signal.SIG_IGN);"
            "path=pathlib.Path(sys.argv[1]);"
            "\nwhile True:\n path.write_text(str(time.monotonic()));time.sleep(.02)"
        )
        parent = (
            "import signal,subprocess,sys,time;"
            "signal.signal(signal.SIGINT,signal.SIG_IGN);"
            f"subprocess.Popen([sys.executable,'-c',{child!r},sys.argv[1]]);"
            "time.sleep(30)"
        )
        started = time.monotonic()

        result = u.Cli().run_to_file(
            [sys.executable, "-c", parent, str(heartbeat)],
            output_file,
            deadline=_deadline(seconds=1.5, grace=0.7, exit_code=92),
        )

        tm.ok(result)
        tm.that(result.value, eq=92)
        tm.that(heartbeat.exists(), eq=True)
        stopped_value = heartbeat.stat().st_mtime_ns
        tm.that(heartbeat.stat().st_mtime_ns, eq=stopped_value)
        tm.that(time.monotonic() - started, lt=2.0)


__all__: list[str] = ["TestsFlextCliRuntimeProcessContainment"]
