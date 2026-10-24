"""Real child completion ends monitoring before the execution deadline.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import gc
import os
import signal
import sys
import threading
import traceback
from pathlib import Path
from types import FrameType

import pytest

from tests import tm, u


class TestsFlextCliRuntimeProcessCompletion:
    """A completed child must not wait for its execution deadline."""

    @staticmethod
    def test_completion_before_wake_clear_ends_monitoring(tmp_path: Path) -> None:
        """A child that completes is reported complete, never timed out.

        A monitor that lost the completion notification would sleep until its
        deadline and report ``timed_out``; the public outcome, not the host
        clock or private scheduling state, proves that it did not.
        """
        result = u.Cli().run_to_file(
            [sys.executable, "-I", "-S", "-c", "print('complete')"],
            tmp_path / "completion.log",
            timeout=4,
        )

        outcome = tm.ok(result)
        tm.that(outcome.raw_return_code, eq=0)
        tm.fail(outcome.timed_out)
        tm.that((tmp_path / "completion.log").read_text(), eq="complete\n")

    @staticmethod
    @pytest.mark.skipif(os.name == "nt", reason="Requires native POSIX user signals")
    @pytest.mark.parametrize("durable", [False, True])
    def test_cancellation_reaps_owned_children_and_preserves_cleanup_notes(
        tmp_path: Path, *, durable: bool
    ) -> None:
        """A real cancellation escapes unchanged after closing its owned boundary."""
        process_info = tmp_path / "cancelled-processes"
        child = "import os,signal;print(os.getpid(),flush=True);signal.pause()"
        parent = (
            "import os,pathlib,signal,subprocess,sys\n"
            "def stop(*_): raise SystemExit(0)\n"
            "signal.signal(signal.SIGTERM,stop)\n"
            "with subprocess.Popen([sys.executable,'-I','-S','-c',sys.argv[2]],"
            "stdout=subprocess.PIPE) as child:\n"
            " pid=child.stdout.readline().decode().strip()\n"
            " pathlib.Path(sys.argv[1]).write_text("
            "f'{os.getpid()} {os.getpgrp()} {pid}')\n"
            " os.kill(os.getppid(),signal.SIGUSR1)\n"
            " try: signal.pause()\n"
            " finally: child.wait()\n"
        )
        command = (sys.executable, "-I", "-S", "-c", parent, str(process_info), child)
        interrupted = pytest.fail.Exception("original process cancellation")
        interrupted.add_note("original caller note")
        cause = RuntimeError("original caller boundary")

        def interrupt(_signal: int, _frame: FrameType | None) -> None:
            raise interrupted from cause

        handlers = tuple(
            signal.getsignal(number)
            for number in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)
        )
        threads = tuple(threading.enumerate())
        previous = signal.signal(signal.SIGUSR1, interrupt)
        try:
            with pytest.raises(
                pytest.fail.Exception, match="original process"
            ) as raised:
                u.Cli.run_to_file(command, os.devnull) if durable else u.Cli.run_bytes(
                    command
                )
        finally:
            signal.signal(signal.SIGUSR1, previous)

        tm.that(raised.value is interrupted, eq=True)
        tm.that(raised.value.__cause__ is cause, eq=True)
        tm.that(
            traceback.extract_tb(raised.value.__traceback__)[-1].name, eq="interrupt"
        )
        tm.that(raised.value.__notes__[0], eq="original caller note")
        if durable:
            tm.that(
                any(
                    "durable log flush error" in note for note in raised.value.__notes__
                ),
                eq=True,
            )
        else:
            tm.that(raised.value.__notes__, eq=["original caller note"])
        root_pid, group, child_pid = map(int, process_info.read_text().split())
        tm.that(root_pid, eq=group)
        tm.that(group, ne=os.getpgrp())
        for pid in (root_pid, child_pid):
            with pytest.raises(ProcessLookupError):
                os.kill(pid, 0)
        with pytest.raises(ProcessLookupError):
            os.killpg(group, 0)
        tm.that(tuple(threading.enumerate()), eq=threads)
        tm.that(
            tuple(
                signal.getsignal(number)
                for number in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)
            ),
            eq=handlers,
        )
        gc.collect()
