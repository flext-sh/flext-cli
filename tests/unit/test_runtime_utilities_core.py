"""Tests for ``u.Cli`` runtime core run/capture operations."""

from __future__ import annotations

from pathlib import Path

import pytest
from flext_tests import tm

from tests import m, t, u


@pytest.fixture
def runner() -> u.Cli:
    return u.Cli()


@pytest.mark.parametrize(
    (
        "command",
        "timeout",
        "env",
        "use_tmp_path",
        "input_data",
        "expect_success",
        "stdout_has",
        "stderr_has",
        "exit_code",
        "error_has",
    ),
    [
        (["echo", "hello"], None, None, False, None, True, "hello", "", 0, ""),
        (
            ["sh", "-c", "echo error >&2"],
            None,
            None,
            False,
            None,
            True,
            "",
            "error",
            0,
            "",
        ),
        (["sh", "-c", "exit 42"], None, None, False, None, True, "", "", 42, ""),
        (["pwd"], None, None, True, None, True, "", "", 0, ""),
        (
            ["sh", "-c", "echo $TEST_VAR"],
            None,
            {"TEST_VAR": "raw_value"},
            False,
            None,
            True,
            "raw_value",
            "",
            0,
            "",
        ),
        (
            ["cat"],
            None,
            None,
            False,
            b'{"type":"RECORD"}',
            True,
            '{"type":"RECORD"}',
            "",
            0,
            "",
        ),
        (["sleep", "10"], 1, None, False, None, False, "", "", None, "timeout"),
        (
            ["nonexistent_command_xyz"],
            None,
            None,
            False,
            None,
            False,
            "",
            "",
            None,
            "execution error",
        ),
    ],
    ids=[
        "echo",
        "stderr",
        "nonzero-exit",
        "cwd",
        "env",
        "input",
        "timeout",
        "invalid-command",
    ],
)
def test_run_raw_cases(
    runner: u.Cli,
    tmp_path: Path,
    command: t.StrSequence,
    timeout: int | None,
    env: t.Cli.StrEnvMapping | None,
    use_tmp_path: bool,
    input_data: bytes | None,
    expect_success: bool,
    stdout_has: str,
    stderr_has: str,
    exit_code: int | None,
    error_has: str,
) -> None:
    cwd = tmp_path if use_tmp_path else None
    result = runner.run_raw(
        command,
        cwd=cwd,
        timeout=timeout,
        env=env,
        input_data=input_data,
    )
    if expect_success:
        output = tm.ok(result)
        assert isinstance(output, m.Cli.CommandOutput)
        if stdout_has:
            tm.that(output.stdout, has=stdout_has)
        if stderr_has:
            tm.that(output.stderr, has=stderr_has)
        if use_tmp_path:
            tm.that(output.stdout.strip(), eq=str(tmp_path))
        if exit_code is not None:
            tm.that(output.exit_code, eq=exit_code)
        return
    tm.fail(result, has=error_has)


@pytest.mark.parametrize(
    (
        "command",
        "timeout",
        "env",
        "use_tmp_path",
        "expect_success",
        "stdout_has",
        "error_has",
    ),
    [
        (["echo", "hello"], None, None, False, True, "hello", ""),
        (["pwd"], None, None, True, True, "", ""),
        (
            ["sh", "-c", "echo $TEST_VAR"],
            None,
            {"TEST_VAR": "test_value"},
            False,
            True,
            "test_value",
            "",
        ),
        (["sh", "-c", "exit 1"], None, None, False, False, "", "failed"),
        (["sleep", "10"], 1, None, False, False, "", "timeout"),
    ],
    ids=["success", "cwd", "env", "nonzero-failure", "timeout"],
)
def test_run_cases(
    runner: u.Cli,
    tmp_path: Path,
    command: t.StrSequence,
    timeout: int | None,
    env: t.Cli.StrEnvMapping | None,
    use_tmp_path: bool,
    expect_success: bool,
    stdout_has: str,
    error_has: str,
) -> None:
    cwd = tmp_path if use_tmp_path else None
    result = runner.run(command, cwd=cwd, timeout=timeout, env=env)
    if expect_success:
        output = tm.ok(result)
        if stdout_has:
            tm.that(output.stdout, has=stdout_has)
        if use_tmp_path:
            tm.that(output.stdout.strip(), eq=str(tmp_path))
        return
    tm.fail(result, has=error_has)


@pytest.mark.parametrize(
    (
        "command",
        "timeout",
        "env",
        "use_tmp_path",
        "expect_success",
        "expected",
        "error_has",
    ),
    [
        (["echo", "captured"], None, None, False, True, "captured", ""),
        (["pwd"], None, None, True, True, "", ""),
        (
            ["sh", "-c", "echo $TEST_VAR"],
            None,
            {"TEST_VAR": "captured_value"},
            False,
            True,
            "captured_value",
            "",
        ),
        (["sh", "-c", "exit 1"], None, None, False, False, "", "failed"),
        (["sleep", "10"], 1, None, False, False, "", "timeout"),
    ],
    ids=["success", "cwd", "env", "nonzero-failure", "timeout"],
)
def test_capture_cases(
    runner: u.Cli,
    tmp_path: Path,
    command: t.StrSequence,
    timeout: int | None,
    env: t.Cli.StrEnvMapping | None,
    use_tmp_path: bool,
    expect_success: bool,
    expected: str,
    error_has: str,
) -> None:
    cwd = tmp_path if use_tmp_path else None
    result = runner.capture(command, cwd=cwd, timeout=timeout, env=env)
    if expect_success:
        output = tm.ok(result)
        if use_tmp_path:
            tm.that(output, eq=str(tmp_path))
            return
        tm.that(output, eq=expected)
        return
    tm.fail(result, has=error_has)
