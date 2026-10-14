"""Portable public-contract tests for streamed process execution.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import signal
import sys
import threading
import time
from typing import TYPE_CHECKING

import pytest

from tests import c, m, tm, u

if TYPE_CHECKING:
    from pathlib import Path


def _deadline(*, seconds: float, grace: float) -> m.Cli.ProcessDeadline:
    """Build an absolute deadline with a bounded cleanup reserve.

    Returns:
        The resulting ``m.Cli.ProcessDeadline``.

    """
    return m.Cli.ProcessDeadline(
        expires_at_monotonic=time.monotonic() + seconds,
        termination_grace_seconds=grace,
    )


class TestsFlextCliRuntimeStreamedProcess:
    """Prove streaming, deadlines, exact exits, and descendant cleanup."""

    @staticmethod
    def _live_threads() -> frozenset[threading.Thread]:
        """Snapshot live threads so a run can be proven to leak none.

        Returns:
            The resulting ``frozenset[threading.Thread]``.

        """
        return frozenset(threading.enumerate())

    @staticmethod
    def test_combined_output_is_byte_exact_and_live(
        tmp_path: Path,
        capfd: pytest.CaptureFixture[str],
    ) -> None:
        """Copy one combined byte stream to the terminal and durable log."""
        output_file = tmp_path / "combined.log"
        script = "import os;os.write(1,b'stdout-one\\n');os.write(2,b'stderr-two\\n')"
        stdout_was_blocking = os.get_blocking(sys.stdout.fileno())

        result = u.Cli().run_to_file(
            [sys.executable, "-c", script],
            output_file,
            options=m.Cli.ProcessOptions(live=True),
        )

        captured = capfd.readouterr()
        expected = b"stdout-one\nstderr-two\n"
        tm.ok(result)
        outcome = tm.ok(result)
        tm.that(u.Cli.process_succeeded(outcome), eq=True)
        tm.that(outcome.raw_return_code, eq=c.Cli.EXIT_CODE_SUCCESS)
        tm.that(outcome.timed_out, eq=False)
        tm.that(outcome.forwarded_signal, is_=None)

        tm.that(output_file.read_bytes(), eq=expected)
        tm.that(captured.out.encode(), eq=expected)
        tm.that(os.get_blocking(sys.stdout.fileno()), eq=stdout_was_blocking)
        tm.that(
            any(
                thread.name == "flext-cli-process-output"
                for thread in threading.enumerate()
            ),
            eq=False,
        )

    @pytest.mark.parametrize("live", [False, True])
    def test_separate_output_drains_parallel_binary_streams(
        self,
        tmp_path: Path,
        capfd: pytest.CaptureFixture[str],
        live: bool,
    ) -> None:
        """Keep concurrent native pipes distinct without decoding their bytes."""
        stdout_file = tmp_path / "stdout.bin"
        stderr_file = tmp_path / "stderr.bin"
        payload = b"native-\x00\xff-\xc3\xa9\n" * 65_536
        script = (
            "import sys, threading\n"
            "payload = sys.stdin.buffer.read()\n"
            "threads = [\n"
            "    threading.Thread(target=stream.write, args=(data,))\n"
            "    for stream, data in (\n"
            "        (sys.stdout.buffer, payload),\n"
            "        (sys.stderr.buffer, payload[::-1]),\n"
            "    )\n"
            "]\n"
            "for thread in threads: thread.start()\n"
            "for thread in threads: thread.join()\n"
        )
        threads_before = self._live_threads()
        outcome = tm.ok(
            u.Cli().run_to_file(
                [sys.executable, "-c", script],
                stdout_file,
                options=m.Cli.ProcessOptions(
                    input_data=payload,
                    live=live,
                    deadline=_deadline(seconds=5.0, grace=1.0),
                    stderr_file=stderr_file,
                ),
            ),
        )
        captured = capfd.readouterr()
        tm.that(u.Cli.process_succeeded(outcome), eq=True)
        tm.that(stdout_file.read_bytes(), eq=payload)
        tm.that(stderr_file.read_bytes(), eq=payload[::-1])
        if live:
            tm.that(captured.out, eq=payload.decode(errors="replace"))
            tm.that(captured.err, eq=payload[::-1].decode(errors="replace"))
        else:
            tm.that(captured.out, eq="")
            tm.that(captured.err, eq="")
        tm.that(self._live_threads() - threads_before, empty=True)

    @staticmethod
    @pytest.mark.parametrize("alias", ["identical", "relative", "hardlink"])
    def test_output_aliases_are_rejected_before_effects(
        tmp_path: Path,
        alias: str,
    ) -> None:
        """A shared physical destination cannot destroy its earlier contents."""
        stdout_file = tmp_path / "stdout.bin"
        stderr_file = stdout_file
        before = b"preserved native output"
        stdout_file.write_bytes(before)
        if alias == "relative":
            stderr_file = tmp_path / "." / stdout_file.name
        elif alias == "hardlink":
            stderr_file = tmp_path / "stderr.bin"
            os.link(stdout_file, stderr_file)
        marker = tmp_path / "child-started"
        result = u.Cli().run_to_file(
            [
                sys.executable,
                "-c",
                "from pathlib import Path; import sys; Path(sys.argv[1]).touch()",
                str(marker),
            ],
            stdout_file,
            options=m.Cli.ProcessOptions(stderr_file=stderr_file),
        )
        tm.that(result.failure, eq=True)
        tm.that(stdout_file.read_bytes(), eq=before)
        tm.that(marker.exists(), eq=False)

    @staticmethod
    def test_separate_output_preserves_nonzero_exit(tmp_path: Path) -> None:
        """Transport success retains the child's nonzero outcome and both streams."""
        stdout_file = tmp_path / "stdout.bin"
        stderr_file = tmp_path / "stderr.bin"
        outcome = tm.ok(
            u.Cli().run_to_file(
                [
                    sys.executable,
                    "-c",
                    (
                        "import os; os.write(1, b'out\\x00'); "
                        "os.write(2, b'err\\xff'); raise SystemExit(37)"
                    ),
                ],
                stdout_file,
                options=m.Cli.ProcessOptions(stderr_file=stderr_file),
            ),
        )
        tm.that(outcome.raw_return_code, eq=37)
        tm.that(u.Cli.process_succeeded(outcome), eq=False)
        tm.that(stdout_file.read_bytes(), eq=b"out\x00")
        tm.that(stderr_file.read_bytes(), eq=b"err\xff")

    def test_separate_output_timeout_drains_both_streams(self, tmp_path: Path) -> None:
        """A deadline stops the child and retains its already-emitted native bytes."""
        stdout_file = tmp_path / "stdout.bin"
        stderr_file = tmp_path / "stderr.bin"
        threads_before = self._live_threads()
        result = u.Cli().run_to_file(
            [
                sys.executable,
                "-c",
                (
                    "import os, time; os.write(1, b'out\\x00'); "
                    "os.write(2, b'err\\xff'); time.sleep(30)"
                ),
            ],
            stdout_file,
            options=m.Cli.ProcessOptions(
                deadline=_deadline(seconds=1.0, grace=0.4),
                stderr_file=stderr_file,
            ),
        )
        outcome = tm.ok(result)
        tm.that(outcome.timed_out, eq=True)
        tm.that(u.Cli.process_succeeded(outcome), eq=False)
        tm.that(stdout_file.read_bytes(), eq=b"out\x00")
        stderr = stderr_file.read_bytes()
        tm.that(stderr.startswith(b"err\xff"), eq=True)
        tm.that(stderr.count(b"err\xff"), eq=1)
        tm.that(self._live_threads() - threads_before, empty=True)

    def test_invalid_stderr_sink_fails_before_spawn(self, tmp_path: Path) -> None:
        """Close the first sink when the second destination cannot be opened."""
        stdout_file = tmp_path / "stdout.bin"
        stderr_directory = tmp_path / "stderr-directory"
        stderr_directory.mkdir()
        marker = tmp_path / "child-started"
        threads_before = self._live_threads()
        result = u.Cli().run_to_file(
            [
                sys.executable,
                "-c",
                "from pathlib import Path; import sys; Path(sys.argv[1]).touch()",
                str(marker),
            ],
            stdout_file,
            options=m.Cli.ProcessOptions(stderr_file=stderr_directory),
        )
        tm.that(result.failure, eq=True)
        tm.that(marker.exists(), eq=False)
        tm.that(self._live_threads() - threads_before, empty=True)
        stdout_file.unlink()

    @staticmethod
    def test_silent_live_process_emits_progress_only_to_stderr(
        tmp_path: Path,
        capfd: pytest.CaptureFixture[str],
    ) -> None:
        """Keep silent children observable without contaminating durable bytes."""
        output_file = tmp_path / "silent.log"

        result = u.Cli().run_to_file(
            [sys.executable, "-c", "import time;time.sleep(.08)"],
            output_file,
            options=m.Cli.ProcessOptions(live=True, heartbeat_seconds=0.02),
        )

        captured = capfd.readouterr()
        tm.ok(result)
        tm.that(result.value.raw_return_code, eq=0)
        tm.that(output_file.read_bytes(), eq=b"")
        tm.that(captured.out, eq="")
        tm.that(captured.err, has=c.Cli.CLI_PROCESS_HEARTBEAT_MESSAGE)

    @staticmethod
    def test_completed_nonzero_exit_is_returned_exactly(tmp_path: Path) -> None:
        """Keep a completed nonzero status in the success channel."""
        result = u.Cli().run_to_file(
            [sys.executable, "-c", "raise SystemExit(37)"],
            tmp_path / "exit.log",
        )

        tm.ok(result)
        tm.that(result.value.raw_return_code, eq=37)

    @staticmethod
    def test_existing_input_data_contract_is_preserved(tmp_path: Path) -> None:
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
            options=m.Cli.ProcessOptions(input_data=payload),
        )

        tm.ok(result)
        tm.that(result.value.raw_return_code, eq=0)
        tm.that(output_file.read_bytes(), eq=payload)

    @pytest.mark.parametrize(
        "payload",
        [
            pytest.param(b"binary-pipe\x00" * 131_072, id="binary"),
            pytest.param("texto-pipe-á" * 131_072, id="text"),
        ],
    )
    def test_input_larger_than_pipe_capacity_is_streamed_without_deadlock(
        self,
        tmp_path: Path,
        payload: str | bytes,
    ) -> None:
        """Stream binary and text payloads instead of pre-filling the pipe."""
        output_file = tmp_path / "large-stdin.log"
        expected_bytes = (
            payload.encode("utf-8") if isinstance(payload, str) else payload
        )
        threads_before = self._live_threads()

        result = u.Cli().run_to_file(
            [
                sys.executable,
                "-c",
                "import sys;sys.stdout.buffer.write(sys.stdin.buffer.read())",
            ],
            output_file,
            options=m.Cli.ProcessOptions(
                input_data=payload,
                deadline=_deadline(seconds=5.0, grace=1.0),
            ),
        )

        tm.ok(result)
        tm.that(result.value.raw_return_code, eq=0)
        tm.that(output_file.read_bytes(), eq=expected_bytes)
        tm.that(self._live_threads() - threads_before, empty=True)

    def test_zero_length_input_publishes_eof(self, tmp_path: Path) -> None:
        """An explicitly empty payload still owns a pipe and closes its writer."""
        output_file = tmp_path / "empty-stdin.log"
        threads_before = self._live_threads()
        result = u.Cli().run_to_file(
            [
                sys.executable,
                "-c",
                "import sys;sys.stdout.write(str(len(sys.stdin.buffer.read())))",
            ],
            output_file,
            options=m.Cli.ProcessOptions(input_data=b""),
        )

        tm.ok(result)
        tm.that(result.value.raw_return_code, eq=0)
        tm.that(output_file.read_text(encoding="utf-8"), eq="0")
        tm.that(self._live_threads() - threads_before, empty=True)

    def test_child_early_exit_preserves_its_exact_status(self, tmp_path: Path) -> None:
        """A secondary broken input pipe cannot replace the child's real exit."""
        threads_before = self._live_threads()
        result = u.Cli().run_to_file(
            [sys.executable, "-c", "raise SystemExit(23)"],
            tmp_path / "early-exit.log",
            options=m.Cli.ProcessOptions(input_data=b"unread" * 131_072),
        )

        tm.ok(result)
        tm.that(result.value.raw_return_code, eq=23)
        tm.that(self._live_threads() - threads_before, empty=True)

    def test_nonreading_child_timeout_unblocks_the_input_writer(
        self,
        tmp_path: Path,
    ) -> None:
        """Killing the child removes the last reader and releases a full writer."""
        threads_before = self._live_threads()
        result = u.Cli().run_to_file(
            [sys.executable, "-c", "import time;time.sleep(30)"],
            tmp_path / "timeout-input.log",
            options=m.Cli.ProcessOptions(input_data=b"blocked-writer" * 131_072),
            timeout=1,
        )

        tm.ok(result)
        tm.that(result.value.timed_out, eq=True)
        tm.that(self._live_threads() - threads_before, empty=True)

    @staticmethod
    def test_deadline_timeout_reports_causal_outcome(tmp_path: Path) -> None:
        """Deadline expiry reports its causal outcome instead of failing."""
        result = u.Cli().run_to_file(
            [sys.executable, "-c", "import time;time.sleep(30)"],
            tmp_path / "legacy-timeout.log",
            timeout=1,
        )

        tm.ok(result)
        tm.that(result.value.timed_out, eq=True)

    @staticmethod
    def test_conflicting_deadlines_fail_before_spawn(tmp_path: Path) -> None:
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
            options=m.Cli.ProcessOptions(deadline=_deadline(seconds=2.0, grace=0.5)),
        )

        tm.fail(result)
        tm.that(marker.exists(), eq=False)

    @staticmethod
    def test_invalid_durable_sink_fails_before_spawn(tmp_path: Path) -> None:
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

    @staticmethod
    def test_broken_live_sink_fails_after_complete_durable_log(
        tmp_path: Path,
    ) -> None:
        """Surface a broken live sink after preserving the durable child bytes."""
        output_file = tmp_path / "broken-live.log"
        child = "import os;os.write(1,b'durable-before-live\\n')"
        sigpipe = getattr(signal, "SIGPIPE", None)
        previous_sigpipe = signal.getsignal(sigpipe) if sigpipe is not None else None
        read_fd, write_fd = os.pipe()
        os.close(read_fd)
        saved_stdout = os.dup(1)
        if sigpipe is not None:
            signal.signal(sigpipe, signal.SIG_IGN)
        try:
            os.dup2(write_fd, 1)
            os.close(write_fd)
            result = u.Cli().run_to_file(
                [sys.executable, "-c", child],
                output_file,
                options=m.Cli.ProcessOptions(live=True),
            )
        finally:
            os.dup2(saved_stdout, 1)
            os.close(saved_stdout)
            if sigpipe is not None and previous_sigpipe is not None:
                signal.signal(sigpipe, previous_sigpipe)

        tm.fail(result)
        tm.that(tm.not_none(result.error), has="live output")
        tm.that(output_file.read_bytes(), eq=b"durable-before-live\n")
