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


def _deadline(
    *, seconds: float, grace: float, exit_code: int = 124
) -> m.Cli.ProcessDeadline:
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
        script = "import os;os.write(1,b'stdout-one\\n');os.write(2,b'stderr-two\\n')"
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
            [sys.executable, "-c", "raise SystemExit(37)"], tmp_path / "exit.log"
        )

        tm.ok(result)
        tm.that(result.value, eq=37)

    def test_existing_input_data_contract_is_preserved(self, tmp_path: Path) -> None:
        """Feed binary stdin through the same canonical run-to-file path."""
        output_file = tmp_path / "stdin.log"
        payload = b"stdin-\x00-bytes\n"

        result = u.Cli().run_to_file(
            [
                sys.executable,
                "-c",
                "import sys;sys.stdout.buffer.write(sys.stdin.buffer.read())",
            ],
            output_file,
            input_data=payload,
        )

        tm.ok(result)
        tm.that(result.value, eq=0)
        tm.that(output_file.read_bytes(), eq=payload)

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

    @pytest.mark.skipif(os.name == "nt", reason="POSIX EPIPE contract")
    def test_broken_live_sink_keeps_the_complete_durable_log(
        self, tmp_path: Path
    ) -> None:
        """Treat live EPIPE as nonfatal after preserving the child bytes."""
        output_file = tmp_path / "broken-live.log"
        child = "import os;os.write(1,b'durable-before-live\\n')"
        previous_sigpipe = signal.getsignal(signal.SIGPIPE)
        read_fd, write_fd = os.pipe()
        os.close(read_fd)
        saved_stdout = os.dup(1)
        signal.signal(signal.SIGPIPE, signal.SIG_IGN)
        try:
            os.dup2(write_fd, 1)
            os.close(write_fd)
            result = u.Cli().run_to_file(
                [sys.executable, "-c", child], output_file, live=True
            )
        finally:
            os.dup2(saved_stdout, 1)
            os.close(saved_stdout)
            signal.signal(signal.SIGPIPE, previous_sigpipe)

        tm.ok(result)
        tm.that(result.value, eq=0)
        tm.that(output_file.read_bytes(), eq=b"durable-before-live\n")


__all__: list[str] = ["TestsFlextCliRuntimeStreamedProcess"]
