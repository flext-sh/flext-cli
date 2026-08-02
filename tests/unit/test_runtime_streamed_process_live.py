"""Public durable-first and live-relay process contracts."""

from __future__ import annotations

import os
import signal
import sys
import threading
import time
from typing import TYPE_CHECKING

import pytest

from flext_tests import tm
from tests import m, u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliRuntimeStreamedProcessLive:
    """Prove durable authority and leak-free best-effort live delivery."""

    @pytest.mark.skipif(os.name == "nt", reason="POSIX process-group contract")
    def test_return_proves_owned_process_group_empty(self, tmp_path: Path) -> None:
        """Do not use pipe EOF as a proxy for process-group cleanup."""
        boundary_file = tmp_path / "boundary"
        nested = "import os,time;os.close(1);os.close(2);time.sleep(30)"
        root = (
            "import os,pathlib,subprocess,sys;"
            f"child=subprocess.Popen([sys.executable,'-c',{nested!r}]);"
            "pathlib.Path(sys.argv[1]).write_text("
            "f'{os.getpgrp()} {child.pid}')"
        )
        deadline = m.Cli.ProcessDeadline(
            expires_at_monotonic=time.monotonic() + 2.0,
            termination_grace_seconds=0.8,
            timeout_exit_code=94,
        )

        result = u.Cli().run_to_file(
            [sys.executable, "-c", root, str(boundary_file)],
            tmp_path / "boundary.log",
            deadline=deadline,
        )

        process_group, _child = (
            int(value) for value in boundary_file.read_text().split()
        )
        tm.ok(result)
        tm.that(result.value, eq=0)
        with pytest.raises(ProcessLookupError):
            os.killpg(process_group, 0)

    @pytest.mark.skipif(
        os.name == "nt" or not os.path.isdir("/proc/self/task"),
        reason="POSIX broken-pipe and child-reap contract",
    )
    def test_broken_live_sink_is_diagnosed_and_relay_reaped(
        self, tmp_path: Path
    ) -> None:
        """Retain the first EPIPE diagnostic and reap every owned relay."""
        output_file = tmp_path / "broken-live.log"
        child = (
            "import os,time;"
            "os.write(1,b'durable-before-live\\n');"
            "time.sleep(.1);"
            "os.write(1,b'durable-after-live-failure\\n')"
        )
        harness = (
            "import os,pathlib,signal,sys;"
            "from flext_cli import u;"
            "signal.signal(signal.SIGPIPE,signal.SIG_IGN);"
            "read_fd,write_fd=os.pipe();os.close(read_fd);"
            "saved=os.dup(1);os.dup2(write_fd,1);os.close(write_fd);"
            f"result=u.Cli.run_to_file([sys.executable,'-c',{child!r}],"
            f"{str(output_file)!r},live=True);"
            "os.dup2(saved,1);os.close(saved);"
            "children=pathlib.Path("
            "f'/proc/self/task/{os.getpid()}/children').read_text().strip();"
            "raise SystemExit("
            "97 if children else result.value if result.success else 99)"
        )

        harness_result = u.Cli().run_bytes(
            [sys.executable, "-c", harness], timeout=3
        )

        tm.ok(harness_result)
        tm.that(harness_result.value.exit_code, eq=0)
        tm.that(
            harness_result.value.stderr.decode("utf-8", errors="replace"),
            has="live output truncated",
        )
        tm.that(
            output_file.read_bytes(),
            eq=b"durable-before-live\ndurable-after-live-failure\n",
        )

    @pytest.mark.skipif(
        os.name == "nt" or not os.path.isdir("/proc/self/fd"),
        reason="POSIX procfs descriptor/handler contract",
    )
    def test_repeated_runs_restore_handlers_threads_and_descriptors(
        self, tmp_path: Path
    ) -> None:
        """Restore process-global resources immediately after every run."""
        operator_signals = (signal.SIGINT, signal.SIGTERM)
        handlers = {
            operator_signal: signal.getsignal(operator_signal)
            for operator_signal in operator_signals
        }
        thread_ids = {thread.ident for thread in threading.enumerate()}
        descriptor_count = len(os.listdir("/proc/self/fd"))

        for index in range(12):
            result = u.Cli().run_to_file(
                [sys.executable, "-c", "print('resource-loop')"],
                tmp_path / f"resource-loop-{index}.log",
            )
            tm.ok(result)
            for operator_signal, handler in handlers.items():
                tm.that(signal.getsignal(operator_signal), is_=handler)

        tm.that(
            {thread.ident for thread in threading.enumerate()},
            eq=thread_ids,
        )
        tm.that(len(os.listdir("/proc/self/fd")), eq=descriptor_count)


__all__: list[str] = ["TestsFlextCliRuntimeStreamedProcessLive"]
