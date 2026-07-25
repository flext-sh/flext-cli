"""Tests for ``u.Cli`` runtime core run/capture operations."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from flext_tests import tm

from tests.models import m
from tests.typings import t
from tests.utilities import u


class TestsFlextCliRuntimeUtilitiesCore:
    """Behavior contract for test_runtime_utilities_core."""

    @pytest.fixture
    @staticmethod
    def runner() -> u.Cli:
        return u.Cli()

    def test_run_raw_remove_env_keys_strips_inherited_values(
        self,
        runner: u.Cli,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("TEST_RUNTIME_INHERITED", "should-not-leak")

        result = runner.run_raw(
            ["sh", "-c", 'printf %s "${TEST_RUNTIME_INHERITED:-missing}"'],
            remove_env_keys=("TEST_RUNTIME_INHERITED",),
        )

        output_raw: t.JsonPayload | None = tm.ok(result)
        assert isinstance(output_raw, m.Cli.CommandOutput)
        tm.that(output_raw.stdout, eq="missing")

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
        cwd = tmp_path if case.use_tmp_path else None
        result = runner.run_raw(
            case.command,
            cwd=cwd,
            timeout=case.timeout,
            env=case.env,
            input_data=case.input_data,
        )
        if case.expect_success:
            output_raw: t.JsonPayload | None = tm.ok(result)
            assert isinstance(output_raw, m.Cli.CommandOutput)
            output: m.Cli.CommandOutput = output_raw
            if case.stdout_has:
                tm.that(output.stdout, has=case.stdout_has)
            if case.stderr_has:
                tm.that(output.stderr, has=case.stderr_has)
            if case.use_tmp_path:
                tm.that(output.stdout.strip(), eq=str(tmp_path))
            if case.exit_code is not None:
                tm.that(output.exit_code, eq=case.exit_code)
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
        cwd = tmp_path if case.use_tmp_path else None
        result = runner.run(case.command, cwd=cwd, timeout=case.timeout, env=case.env)
        if case.expect_success:
            output_raw: t.JsonPayload | None = tm.ok(result)
            assert isinstance(output_raw, m.Cli.CommandOutput)
            output: m.Cli.CommandOutput = output_raw
            if case.stdout_has:
                tm.that(output.stdout, has=case.stdout_has)
            if case.use_tmp_path:
                tm.that(output.stdout.strip(), eq=str(tmp_path))
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
        cwd = tmp_path if case.use_tmp_path else None
        result = runner.capture(
            case.command,
            cwd=cwd,
            timeout=case.timeout,
            env=case.env,
        )
        if case.expect_success:
            output_raw: t.JsonPayload | None = tm.ok(result)
            assert isinstance(output_raw, str)
            output: str = output_raw
            if case.use_tmp_path:
                tm.that(output, eq=str(tmp_path))
                return
            tm.that(output, eq=case.expected)
            return
        tm.fail(result, has=case.error_has)

    def test_process_start_wait_captures_stdout(self, runner: u.Cli) -> None:
        result = runner.process_start(
            [sys.executable, "-c", "print('managed-ok')"],
        )
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

    def test_process_start_honors_cwd_env_and_stderr(
        self, runner: u.Cli, tmp_path: Path
    ) -> None:
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
        assert process_env is not None
        tm.that(process_env["FLEXT_CLI_PROCESS_TEST"], eq="env-ok")
        wait_result = process.wait(timeout=5)
        tm.ok(wait_result)
        stdout_lines = process.stdout.splitlines()
        tm.that(stdout_lines[0], eq=str(tmp_path))
        tm.that(stdout_lines[1], eq="env-ok")
        tm.that(process.stderr.strip(), eq="err-marker")

    def test_process_start_timeout_then_terminate(self, runner: u.Cli) -> None:
        result = runner.process_start(
            [sys.executable, "-c", "import time; time.sleep(10)"],
        )
        tm.ok(result)
        process = result.value

        timeout_result = process.wait(timeout=0.01)
        tm.fail(timeout_result, has="timeout")
        tm.that(process.poll(), eq=None)
        tm.ok(process.terminate())
        wait_result = process.wait(timeout=5)
        tm.ok(wait_result)
        tm.that(process.returncode is not None, eq=True)

    def test_process_start_kill_lifecycle(self, runner: u.Cli) -> None:
        result = runner.process_start(
            [sys.executable, "-c", "import time; time.sleep(10)"],
        )
        tm.ok(result)
        process = result.value

        tm.ok(process.kill())
        wait_result = process.wait(timeout=5)
        tm.ok(wait_result)
        tm.that(process.returncode is not None, eq=True)
