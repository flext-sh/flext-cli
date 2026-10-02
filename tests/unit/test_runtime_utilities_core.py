"""Tests for ``u.Cli`` runtime core run/capture operations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import signal
import socket
import sys
import time
from pathlib import Path

import pytest
from flext_tests import tm

from tests import c, m, u


def fixtures_path(name: str) -> str:
    """Return the absolute path of one tests/fixtures helper script.

    Returns:
        The absolute path of one tests/fixtures helper script.

    """
    return str(Path(__file__).resolve().parent.parent / "fixtures" / name)


def read_recorded_pid(pid_file: Path) -> int:
    """Return the descendant pid a leader recorded before exiting.

    Returns:
        The descendant pid a leader recorded before exiting.

    """
    deadline = time.monotonic() + 10
    while not pid_file.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    return int(pid_file.read_text(encoding="utf-8").strip())


class TestsFlextCliRuntimeUtilitiesCore:
    """Behavior contract for test_runtime_utilities_core."""

    @pytest.fixture
    @staticmethod
    def runner() -> u.Cli:
        """Define the runner test contract.

        Returns:
            The resulting ``u.Cli``.

        """
        return u.Cli()

    @staticmethod
    def test_run_raw_remove_env_keys_strips_inherited_values(
        runner: u.Cli,
    ) -> None:
        """Verify that run raw remove env keys strips inherited values."""
        result = runner.run_raw(
            ["sh", "-c", 'printf %s "${TEST_RUNTIME_INHERITED:-missing}"'],
            env={"TEST_RUNTIME_INHERITED": "should-not-leak"},
            remove_env_keys=("TEST_RUNTIME_INHERITED",),
        )

        output = m.Cli.CommandOutput.model_validate(tm.ok(result))
        tm.that(output.stdout, eq="missing")

    @pytest.mark.parametrize(
        "case",
        m.Tests.RuntimeCommandCase.run_raw_cases(),
        ids=m.Tests.RuntimeCommandCase.id_for,
    )
    def test_run_raw_cases(
        self,
        runner: u.Cli,
        tmp_path: Path,
        case: m.Tests.RuntimeCommandCase,
    ) -> None:
        """Verify that run raw cases."""
        cwd = tmp_path if case.use_tmp_path else None
        result = runner.run_raw(
            case.command,
            cwd=cwd,
            timeout=case.timeout,
            env=case.env,
            input_data=case.input_data,
        )
        if case.expect_success:
            output = m.Cli.CommandOutput.model_validate(tm.ok(result))
            if case.stdout_has:
                tm.that(output.stdout, has=case.stdout_has)
            if case.stderr_has:
                tm.that(output.stderr, has=case.stderr_has)
            if case.use_tmp_path:
                tm.that(output.stdout.strip(), eq=str(tmp_path))
            if case.exit_code is not None:
                tm.that(
                    (
                        u.Cli.process_succeeded(output.outcome),
                        output.outcome.raw_return_code,
                    ),
                    eq=(case.exit_code == c.Cli.EXIT_CODE_SUCCESS, case.exit_code),
                )

            tm.that(output.outcome.timed_out, eq=case.timed_out)
            return
        tm.fail(result, has=case.error_has)

    @pytest.mark.parametrize(
        "case",
        m.Tests.RuntimeCommandCase.output_cases(),
        ids=m.Tests.RuntimeCommandCase.id_for,
    )
    def test_run_cases(
        self,
        runner: u.Cli,
        tmp_path: Path,
        case: m.Tests.RuntimeCommandCase,
    ) -> None:
        """Verify that run cases."""
        cwd = tmp_path if case.use_tmp_path else None
        result = runner.run(
            case.command,
            cwd=cwd,
            timeout=case.timeout,
            env=case.env,
            input_data=case.input_data,
        )
        if case.expect_success:
            output = m.Cli.CommandOutput.model_validate(tm.ok(result))
            if case.stdout_has:
                tm.that(output.stdout, has=case.stdout_has)
            if case.use_tmp_path:
                tm.that(output.stdout.strip(), eq=str(tmp_path))
            tm.that(output.outcome.timed_out, eq=case.timed_out)
            return
        tm.fail(result, has=case.error_has)

    @pytest.mark.parametrize(
        "case",
        m.Tests.RuntimeCommandCase.output_cases(),
        ids=m.Tests.RuntimeCommandCase.id_for,
    )
    def test_capture_cases(
        self,
        runner: u.Cli,
        tmp_path: Path,
        case: m.Tests.RuntimeCommandCase,
    ) -> None:
        """Verify that capture cases."""
        cwd = tmp_path if case.use_tmp_path else None
        result = runner.capture(
            case.command,
            cwd=cwd,
            timeout=case.timeout,
            env=case.env,
            input_data=case.input_data,
        )
        if case.expect_success:
            output = u.type_adapter(str).validate_python(tm.ok(result))
            if case.use_tmp_path:
                tm.that(output, eq=str(tmp_path))
                return
            tm.that(output, eq=case.expected)
            return
        tm.fail(result, has=case.error_has)

    @staticmethod
    def test_run_bytes_accepts_text_and_binary_stdin(runner: u.Cli) -> None:
        """Verify run_bytes accepts str or bytes stdin and echoes byte-exact."""
        text_out = m.Cli.CommandBytesOutput.model_validate(
            tm.ok(runner.run_bytes(("cat",), input_data="text-payload")),
        )
        tm.that(text_out.stdout, eq=b"text-payload")
        binary_out = m.Cli.CommandBytesOutput.model_validate(
            tm.ok(runner.run_bytes(("cat",), input_data=b"\x00\xff\x01")),
        )
        tm.that(binary_out.stdout, eq=b"\x00\xff\x01")

    @staticmethod
    def test_run_checked_rejects_a_real_timeout(runner: u.Cli) -> None:
        """A terminated child cannot become a successful boolean receipt."""
        result = runner.run_checked(
            [sys.executable, "-c", "import time; time.sleep(10)"],
            timeout=1,
        )
        tm.fail(result, has="timed_out=True")

    @staticmethod
    def test_run_capture_false_empties_captured_output(runner: u.Cli) -> None:
        """Verify run(capture=False) streams live: captured stdout is empty, exit ok."""
        result = runner.run(("sh", "-c", "echo streamed-line"), capture=False)
        output = m.Cli.CommandOutput.model_validate(tm.ok(result))
        tm.that(u.Cli.process_succeeded(output.outcome), eq=True)
        tm.that(output.stdout, eq="")
        tm.that(output.stderr, eq="")

    @staticmethod
    def test_run_capture_true_default_still_captures(runner: u.Cli) -> None:
        """Verify run() default capture=True still captures stdout."""
        result = runner.run(("echo", "captured-line"))
        output = m.Cli.CommandOutput.model_validate(tm.ok(result))
        tm.that(output.stdout, has="captured-line")

    @staticmethod
    def test_run_live_alias_streams_and_exit_checks(runner: u.Cli) -> None:
        """Verify run_live streams (empty captured) and fails closed on non-zero exit."""
        ok_result = runner.run_live(("sh", "-c", "echo live-ok"))
        ok_output = m.Cli.CommandOutput.model_validate(tm.ok(ok_result))
        tm.that(ok_output.stdout, eq="")
        tm.that(u.Cli.process_succeeded(ok_output.outcome), eq=True)
        tm.fail(runner.run_live(("sh", "-c", "exit 7")), has="failed")

    @staticmethod
    def test_process_start_wait_captures_stdout(runner: u.Cli) -> None:
        """Verify that process start wait captures stdout."""
        result = runner.process_start([sys.executable, "-c", "print('managed-ok')"])
        tm.ok(result)
        process = result.value

        tm.that(process.pid > 0, eq=True)
        tm.that(process.poll(), eq=None)
        wait_result = process.wait(timeout=5)
        tm.ok(wait_result)
        tm.that(wait_result.value, eq=0)
        tm.that(process.returncode, eq=0)
        tm.that(process.stdout.strip(), eq="managed-ok")
        tm.that(process.stderr, eq="")

    @staticmethod
    def test_process_start_inherits_streams(runner: u.Cli) -> None:
        """A supervised child consumes inherited input and forwards both outputs."""
        script = (
            "import sys; from flext_cli import u; "
            "child = u.Cli.process_start("
            "[sys.executable, '-c', "
            '"import sys; print(sys.stdin.readline().strip()); '
            "print('inherited-error', file=sys.stderr)\"], "
            "capture=False, start_new_session=True).unwrap(); "
            "status = child.wait(timeout=5).unwrap(); "
            "print(repr(child.stdout), repr(child.stderr)); sys.exit(status)"
        )
        output = tm.ok(
            runner.run_raw(
                [sys.executable, "-c", script],
                input_data="inherited-input\n",
            ),
        )
        tm.that(u.Cli.process_succeeded(output.outcome), eq=True)
        tm.that(output.stdout.splitlines(), eq=["inherited-input", "'' ''"])
        tm.that(output.stderr.strip(), eq="inherited-error")

    @pytest.mark.parametrize("start_new_session", [False, True])
    def test_process_start_session_ownership(
        self,
        runner: u.Cli,
        *,
        start_new_session: bool,
    ) -> None:
        """The public child boundary either retains or owns its POSIX session."""
        child = tm.ok(
            runner.process_start(
                [sys.executable, "-c", "import os; print(os.getsid(0), os.getpgrp())"],
                start_new_session=start_new_session,
            ),
        )
        tm.that(tm.ok(child.wait(timeout=5)), eq=0)
        session, group = (int(value) for value in child.stdout.split())
        tm.that(session, eq=child.pid if start_new_session else os.getsid(0))
        tm.that(group, eq=child.pid if start_new_session else os.getpgrp())

    @staticmethod
    def test_process_start_passes_only_the_declared_descriptors(
        runner: u.Cli,
    ) -> None:
        """A child inherits exactly the descriptors the caller declares."""
        parent_end, child_end = socket.socketpair()
        try:
            script = (
                "import socket, sys; "
                "conn = socket.socket(fileno=int(sys.argv[1])); "
                "conn.sendall(b'ready'); conn.close()"
            )
            result = runner.process_start(
                [sys.executable, "-c", script, str(child_end.fileno())],
                pass_fds=(child_end.fileno(),),
            )
            tm.ok(result)
            process = result.value
            child_end.close()
            parent_end.settimeout(5)
            tm.that(parent_end.recv(16), eq=b"ready")
            wait_result = process.wait(timeout=5)
            tm.ok(wait_result)
            tm.that(wait_result.value, eq=0)
        finally:
            parent_end.close()

    @staticmethod
    def test_process_start_honors_cwd_env_and_stderr(
        runner: u.Cli,
        tmp_path: Path,
    ) -> None:
        """Verify that process start honors cwd env and stderr."""
        script = (
            "import os, pathlib, sys; "
            "print(pathlib.Path.cwd()); "
            "print(os.environ['FLEXT_CLI_PROCESS_TEST']); "
            "print('err-marker', file=sys.stderr)"
        )
        result = runner.process_start(
            [sys.executable, "-c", script],
            cwd=tmp_path,
            env={"FLEXT_CLI_PROCESS_TEST": "env-ok"},
        )
        tm.ok(result)
        process = result.value

        tm.that(process.cwd, eq=tmp_path)
        process_env = process.env
        process_env = tm.not_none(process_env)
        tm.that(process_env["FLEXT_CLI_PROCESS_TEST"], eq="env-ok")
        wait_result = process.wait(timeout=5)
        tm.ok(wait_result)
        stdout_lines = process.stdout.splitlines()
        tm.that(stdout_lines[0], eq=str(tmp_path))
        tm.that(stdout_lines[1], eq="env-ok")
        tm.that(process.stderr.strip(), eq="err-marker")

    @staticmethod
    def test_process_start_forwards_passed_file_descriptors(
        runner: u.Cli,
    ) -> None:
        """Verify the public process owner forwards one inherited descriptor."""
        read_fd, write_fd = os.pipe()
        try:
            script = "import os, sys; os.write(int(sys.argv[1]), b'fd-forwarded')"
            result = runner.process_start(
                [sys.executable, "-c", script, str(write_fd)],
                pass_fds=(write_fd,),
            )
            os.close(write_fd)
            write_fd = -1
            process = tm.ok(result)
            tm.that(tm.ok(process.wait(timeout=5)), eq=0)
            tm.that(os.read(read_fd, len(b"fd-forwarded")), eq=b"fd-forwarded")
        finally:
            os.close(read_fd)
            if write_fd >= 0:
                os.close(write_fd)

    @staticmethod
    def test_process_start_supports_binary_interactive_exchange(
        runner: u.Cli,
    ) -> None:
        """Exchange exact framed bytes without closing stdin between messages."""
        script = (
            "import sys; "
            "first = sys.stdin.buffer.read(4); "
            "sys.stdout.buffer.write(b'Length: 3\\r\\n\\r\\n' + first[:3]); "
            "sys.stdout.buffer.flush(); "
            "second = sys.stdin.buffer.read(2); "
            "sys.stdout.buffer.write(second); "
            "sys.stdout.buffer.flush()"
        )
        started = runner.process_start([sys.executable, "-c", script])
        process = tm.ok(started)

        tm.ok(process.stdin_write(b"abcd"))
        tm.that(
            tm.ok(process.stdout_read_until(b"\r\n\r\n", timeout=5)),
            eq=b"Length: 3\r\n\r\n",
        )
        tm.that(tm.ok(process.stdout_read_exact(3, timeout=5)), eq=b"abc")
        tm.ok(process.stdin_write(b"ef"))
        tm.that(tm.ok(process.stdout_read_exact(2, timeout=5)), eq=b"ef")
        tm.that(tm.ok(process.wait(timeout=5)), eq=0)
        tm.that(process.stdout, eq="")
        tm.that(process.stderr, eq="")

    @staticmethod
    def test_process_start_timeout_then_terminate(runner: u.Cli) -> None:
        """Verify that process start timeout then terminate."""
        result = runner.process_start([
            sys.executable,
            "-c",
            "import time; time.sleep(10)",
        ])
        tm.ok(result)
        process = result.value

        timeout_result = process.wait(timeout=0.01)
        tm.fail(timeout_result, has="timeout")
        tm.that(process.poll(), eq=None)
        tm.ok(process.terminate())
        wait_result = process.wait(timeout=5)
        tm.ok(wait_result)
        tm.that(process.returncode is not None, eq=True)

    @staticmethod
    def test_process_start_kill_lifecycle(runner: u.Cli) -> None:
        """Verify that process start kill lifecycle."""
        result = runner.process_start([
            sys.executable,
            "-c",
            "import time; time.sleep(10)",
        ])
        tm.ok(result)
        process = result.value

        tm.ok(process.kill())
        wait_result = process.wait(timeout=5)
        tm.ok(wait_result)
        tm.that(process.returncode is not None, eq=True)

    @staticmethod
    def test_process_start_terminate_reaches_leader_exited_descendants(
        runner: u.Cli,
        tmp_path: Path,
    ) -> None:
        """Verify session-leader terminate reaches descendants after leader exit."""
        sentinel = tmp_path / "terminated"
        pid_file = tmp_path / "descendant.pid"
        result = runner.process_start(
            [
                sys.executable,
                fixtures_path("process_session_descendant.py"),
                str(sentinel),
                "terminate",
                str(pid_file),
            ],
            start_new_session=True,
        )
        tm.ok(result)
        process = result.value

        tm.ok(process.wait(timeout=10))
        descendant_pid = read_recorded_pid(pid_file)
        tm.that(descendant_pid > 0, eq=True)
        tm.ok(process.terminate())

        deadline = time.monotonic() + 10
        while not sentinel.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        tm.that(sentinel.exists(), eq=True)
        tm.ok(process.kill())

    @staticmethod
    def test_process_start_kill_stops_leader_exited_descendants(
        runner: u.Cli,
        tmp_path: Path,
    ) -> None:
        """Verify session-leader kill stops descendants after leader exit."""
        pid_file = tmp_path / "descendant.pid"
        result = runner.process_start(
            [
                sys.executable,
                fixtures_path("process_session_descendant.py"),
                str(tmp_path / "unused"),
                "sleep",
                str(pid_file),
            ],
            start_new_session=True,
        )
        tm.ok(result)
        process = result.value

        tm.ok(process.wait(timeout=10))
        descendant_pid = read_recorded_pid(pid_file)
        tm.that(descendant_pid > 0, eq=True)
        tm.ok(process.kill())

        deadline = time.monotonic() + 10
        gone = False
        while time.monotonic() < deadline:
            try:
                os.kill(descendant_pid, 0)
            except ProcessLookupError:
                gone = True
                break
            time.sleep(0.05)
        tm.that(gone, eq=True)

    @staticmethod
    def test_process_start_terminate_without_session_leaves_descendants(
        runner: u.Cli,
        tmp_path: Path,
    ) -> None:
        """Verify a non-session terminate targets only the exited leader."""
        sentinel = tmp_path / "terminated"
        pid_file = tmp_path / "descendant.pid"
        result = runner.process_start([
            sys.executable,
            fixtures_path("process_session_descendant.py"),
            str(sentinel),
            "terminate",
            str(pid_file),
        ])
        tm.ok(result)
        process = result.value

        tm.ok(process.wait(timeout=10))
        descendant_pid = read_recorded_pid(pid_file)
        tm.that(descendant_pid > 0, eq=True)
        tm.ok(process.terminate())

        time.sleep(0.5)
        tm.that(sentinel.exists(), eq=False)
        os.kill(descendant_pid, signal.SIGKILL)
