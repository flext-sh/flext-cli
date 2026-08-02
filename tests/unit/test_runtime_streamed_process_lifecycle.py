"""Public deadline, descendant, and real Windows lifecycle contracts."""

from __future__ import annotations

import ctypes
import os
import sys
import time
from ctypes import wintypes
from typing import TYPE_CHECKING

import pytest

from flext_tests import tm
from tests import m, u

if TYPE_CHECKING:
    from pathlib import Path


def _deadline(
    *, seconds: float, grace: float, exit_code: int
) -> m.Cli.ProcessDeadline:
    """Build one complete lifecycle deadline."""
    return m.Cli.ProcessDeadline(
        expires_at_monotonic=time.monotonic() + seconds,
        termination_grace_seconds=grace,
        timeout_exit_code=exit_code,
    )


class TestsFlextCliRuntimeStreamedProcessLifecycle:
    """Prove soft interrupt, forced cleanup, and zero descendants."""

    def test_deadline_forwards_interrupt_before_forced_cleanup(
        self, tmp_path: Path
    ) -> None:
        """Give the child a soft interrupt before forced cleanup."""
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
        """Escalate an ignored interrupt and stop a real descendant."""
        heartbeat = tmp_path / "heartbeat"
        child = (
            "import pathlib,signal,sys,time;"
            "signal.signal(signal.SIGINT,signal.SIG_IGN);"
            "signal.signal(getattr(signal,'SIGBREAK',signal.SIGINT),signal.SIG_IGN);"
            "path=pathlib.Path(sys.argv[1]);"
            "\nwhile True:\n path.write_text(str(time.monotonic()));time.sleep(.02)"
        )
        parent = (
            "import signal,subprocess,sys,time;"
            "signal.signal(signal.SIGINT,signal.SIG_IGN);"
            "signal.signal(getattr(signal,'SIGBREAK',signal.SIGINT),signal.SIG_IGN);"
            f"subprocess.Popen([sys.executable,'-c',{child!r},sys.argv[1]]);"
            "time.sleep(30)"
        )

        result = u.Cli().run_to_file(
            [sys.executable, "-c", parent, str(heartbeat)],
            tmp_path / "tree.log",
            deadline=_deadline(seconds=1.5, grace=0.7, exit_code=92),
        )

        tm.ok(result)
        tm.that(result.value, eq=92)
        tm.that(heartbeat.exists(), eq=True)
        time.sleep(0.1)
        stopped_value = heartbeat.read_text()
        time.sleep(0.2)
        tm.that(heartbeat.read_text(), eq=stopped_value)

    def test_normal_root_exit_leaves_no_descendant(self, tmp_path: Path) -> None:
        """Contain a surviving descendant after a normal root exit."""
        heartbeat = tmp_path / "normal-heartbeat"
        child = (
            "import pathlib,sys,time;"
            "path=pathlib.Path(sys.argv[1]);"
            "\nwhile True:\n path.write_text(str(time.monotonic()));time.sleep(.02)"
        )
        parent = (
            "import pathlib,subprocess,sys,time;"
            f"subprocess.Popen([sys.executable,'-c',{child!r},sys.argv[1]]);"
            "path=pathlib.Path(sys.argv[1]);"
            "\nwhile not path.exists():\n time.sleep(.01)"
        )

        result = u.Cli().run_to_file(
            [sys.executable, "-c", parent, str(heartbeat)],
            tmp_path / "normal-exit.log",
        )

        tm.ok(result)
        tm.that(result.value, eq=0)
        time.sleep(0.1)
        stopped_value = heartbeat.read_text()
        time.sleep(0.2)
        tm.that(heartbeat.read_text(), eq=stopped_value)

    @pytest.mark.skipif(os.name != "nt", reason="requires real Windows CI")
    def test_windows_repeated_runs_do_not_leak_handles(
        self, tmp_path: Path
    ) -> None:
        """Close process, thread, snapshot, and Job handles on every run."""
        handle_count = self._windows_process_handle_count()

        for index in range(12):
            result = u.Cli().run_to_file(
                [sys.executable, "-c", "print('handle-loop')"],
                tmp_path / f"windows-handle-loop-{index}.log",
            )
            tm.ok(result)
            tm.that(result.value, eq=0)

        tm.that(self._windows_process_handle_count(), eq=handle_count)

    @staticmethod
    def _windows_process_handle_count() -> int:
        """Return this test worker's live Windows handle count."""
        if os.name != "nt":
            raise RuntimeError("Windows handle count is unavailable")
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        get_current_process = kernel32.GetCurrentProcess
        get_current_process.argtypes = ()
        get_current_process.restype = wintypes.HANDLE
        get_process_handle_count = kernel32.GetProcessHandleCount
        get_process_handle_count.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(wintypes.DWORD),
        )
        get_process_handle_count.restype = wintypes.BOOL
        count = wintypes.DWORD()
        if not get_process_handle_count(
            get_current_process(), ctypes.byref(count)
        ):
            raise OSError(
                ctypes.get_last_error(), "GetProcessHandleCount failed"
            )
        return int(count.value)


__all__: list[str] = ["TestsFlextCliRuntimeStreamedProcessLifecycle"]
