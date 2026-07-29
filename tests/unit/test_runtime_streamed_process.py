"""Portable public-contract tests for streamed process execution."""

from __future__ import annotations

import os
import signal
import sys
import threading
import time
from typing import TYPE_CHECKING

import pytest

from flext_tests import tm
from tests import m, p, u

if TYPE_CHECKING:
    from pathlib import Path


def _deadline(*, seconds: float, grace: float, exit_code: int = 124) -> m.Cli.ProcessDeadline:
    """Build an absolute deadline with a bounded cleanup reserve."""
    return m.Cli.ProcessDeadline(
        expires_at_monotonic=time.monotonic() + seconds,
        termination_grace_seconds=grace,
        timeout_exit_code=exit_code,
    )


class TestsFlextCliRuntimeStreamedProcess:
    """Prove streaming, deadlines, exact exits, and descendant cleanup."""

    def test_combined_output_is_byte_exact_and_live(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ) -> None:
        """Copy one combined byte stream to the terminal and durable log."""
        output_file = tmp_path / "combined.log"
        script = (
            "import os;"
            "os.write(1,b'stdout-one\\n');"
            "os.write(2,b'stderr-two\\n')"
        )
        stdout_was_blocking = os.get_blocking(sys.stdout.fileno())

        result = u.Cli().run_to_file(
            [sys.executable, "-c", script], output_file, live=True
        )

        expected = b"stdout-one\nstderr-two\n"
        tm.ok(result)
        tm.that(result.value, eq=0)
        tm.that(output_file.read_bytes(), eq=expected)
        tm.that(capfd.readouterr().out.encode(), eq=expected)
        tm.that(os.get_blocking(sys.stdout.fileno()), eq=stdout_was_blocking)
        tm.that(
            any(
                thread.name == "flext-cli-process-output"
                for thread in threading.enumerate()
            ),
            eq=False,
        )

    def test_completed_nonzero_exit_is_returned_exactly(self, tmp_path: Path) -> None:
        """Keep a completed nonzero status in the success channel."""
        result = u.Cli().run_to_file(
            [sys.executable, "-c", "raise SystemExit(37)"],
            tmp_path / "exit.log",
        )

        tm.ok(result)
        tm.that(result.value, eq=37)

    def test_deadline_model_satisfies_public_protocol(self) -> None:
        """Expose one typed model through the structural public protocol."""
        deadline = _deadline(seconds=2.0, grace=0.5, exit_code=93)

        tm.that(deadline, is_=p.Cli.ProcessDeadline)

    def test_legacy_timeout_contract_remains_a_failure(self, tmp_path: Path) -> None:
        """Keep the existing relative-timeout failure contract on one path."""
        result = u.Cli().run_to_file(
            [sys.executable, "-c", "import time;time.sleep(30)"],
            tmp_path / "legacy-timeout.log",
            timeout=1,
        )

        tm.fail(result)
        tm.that(tm.not_none(result.error).lower(), has="timeout")

    def test_conflicting_deadlines_fail_before_spawn(self, tmp_path: Path) -> None:
        """Reject two timeout owners without starting the command."""
        marker = tmp_path / "must-not-exist"
        result = u.Cli().run_to_file(
            [
                sys.executable,
                "-c",
                "import pathlib,sys;pathlib.Path(sys.argv[1]).touch()",
                str(marker),
            ],
            tmp_path / "conflict.log",
            timeout=1,
            deadline=_deadline(seconds=2.0, grace=0.5),
        )

        tm.fail(result)
        tm.that(marker.exists(), eq=False)

    def test_invalid_durable_sink_fails_before_spawn(self, tmp_path: Path) -> None:
        """Validate the durable sink before child code can execute."""
        sink_directory = tmp_path / "sink-directory"
        sink_directory.mkdir()
        marker = tmp_path / "must-not-spawn"

        result = u.Cli().run_to_file(
            [
                sys.executable,
                "-c",
                "import pathlib,sys;pathlib.Path(sys.argv[1]).touch()",
                str(marker),
            ],
            sink_directory,
        )

        tm.fail(result)
        tm.that(marker.exists(), eq=False)

    @pytest.mark.skipif(os.name == "nt", reason="POSIX process-group contract")
    def test_return_proves_owned_process_group_empty(self, tmp_path: Path) -> None:
        """Do not use pipe EOF as a proxy for owned process-group cleanup."""
        boundary_file = tmp_path / "boundary"
        nested = "import os,time;os.close(1);os.close(2);time.sleep(30)"
        root = (
            "import os,pathlib,subprocess,sys;"
            f"child=subprocess.Popen([sys.executable,'-c',{nested!r}]);"
            "pathlib.Path(sys.argv[1]).write_text("
            "f'{os.getpgrp()} {child.pid}')"
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

    def test_broken_live_sink_keeps_the_complete_durable_log(
        self, tmp_path: Path
    ) -> None:
        """Fail loud on live EPIPE only after preserving the child bytes."""
        output_file = tmp_path / "broken-live.log"
        child = "import os;os.write(1,b'durable-before-live\\n')"
        harness = (
            "import os,signal,sys;"
            "from flext_cli import u;"
            "signal.signal(signal.SIGPIPE,signal.SIG_IGN);"
            "read_fd,write_fd=os.pipe();os.close(read_fd);"
            "saved=os.dup(1);os.dup2(write_fd,1);os.close(write_fd);"
            f"result=u.Cli.run_to_file([sys.executable,'-c',{child!r}],"
            f"{str(output_file)!r},live=True);"
            "os.dup2(saved,1);os.close(saved);"
            "raise SystemExit(0 if result.failure else 1)"
        )

        harness_result = u.Cli().run_bytes(
            [sys.executable, "-c", harness], timeout=3
        )

        tm.ok(harness_result)
        tm.that(harness_result.value.exit_code, eq=0)
        tm.that(output_file.read_bytes(), eq=b"durable-before-live\n")

    @pytest.mark.skipif(os.name == "nt", reason="POSIX operator-signal contract")
    def test_manual_interrupt_is_forwarded_and_normalized(
        self, tmp_path: Path
    ) -> None:
        """Forward SIGINT and return its normalized 128+signal status."""
        ready = tmp_path / "child-ready"
        output_file = tmp_path / "manual-interrupt.log"
        child = (
            "import pathlib,signal,sys,time;"
            "signal.signal(signal.SIGINT,signal.SIG_IGN);"
            "pathlib.Path(sys.argv[1]).touch();time.sleep(30)"
        )
        harness = (
            "import sys,time;"
            "from flext_cli import m,u;"
            "deadline=m.Cli.ProcessDeadline("
            "expires_at_monotonic=time.monotonic()+2.5,"
            "termination_grace_seconds=1.0,timeout_exit_code=95);"
            f"result=u.Cli.run_to_file([sys.executable,'-c',{child!r},"
            f"{str(ready)!r}],{str(output_file)!r},deadline=deadline);"
            "raise SystemExit(result.value if result.success else 99)"
        )
        started = u.Cli().process_start([sys.executable, "-c", harness])
        tm.ok(started)
        managed = started.value
        ready_deadline = time.monotonic() + 1.0
        while not ready.exists() and time.monotonic() < ready_deadline:
            time.sleep(0.01)

        tm.that(ready.exists(), eq=True)
        signal_started = time.monotonic()
        os.kill(managed.pid, signal.SIGINT)
        completed = managed.wait(timeout=3.0)

        tm.ok(completed)
        tm.that(completed.value, eq=128 + signal.SIGINT)
        tm.that(time.monotonic() - signal_started, lt=3.0)

    def test_deadline_forwards_interrupt_before_forced_cleanup(
        self, tmp_path: Path
    ) -> None:
        """Give the child a soft interrupt before the forced-kill boundary."""
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
        """Escalate an ignored interrupt and leave no writing descendant."""
        output_file = tmp_path / "tree.log"
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
        started = time.monotonic()

        result = u.Cli().run_to_file(
            [sys.executable, "-c", parent, str(heartbeat)],
            output_file,
            deadline=_deadline(seconds=1.5, grace=0.7, exit_code=92),
        )

        tm.ok(result)
        tm.that(result.value, eq=92)
        tm.that(heartbeat.exists(), eq=True)
        time.sleep(0.1)
        stopped_value = heartbeat.read_text()
        time.sleep(0.2)
        tm.that(heartbeat.read_text(), eq=stopped_value)
        tm.that(time.monotonic() - started, lt=2.0)

    def test_normal_root_exit_leaves_no_descendant(self, tmp_path: Path) -> None:
        """Contain and terminate a surviving descendant after root exit."""
        output_file = tmp_path / "normal-exit.log"
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
        started = time.monotonic()

        result = u.Cli().run_to_file(
            [sys.executable, "-c", parent, str(heartbeat)],
            output_file,
        )

        tm.ok(result)
        tm.that(result.value, eq=0)
        time.sleep(0.1)
        stopped_value = heartbeat.read_text()
        time.sleep(0.2)
        tm.that(heartbeat.read_text(), eq=stopped_value)
        tm.that(time.monotonic() - started, lt=5.0)


__all__: list[str] = ["TestsFlextCliRuntimeStreamedProcess"]
