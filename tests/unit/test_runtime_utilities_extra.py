"""Behavioral tests for ``u.Cli`` runtime command execution and output model.

Exercises the public contract of ``FlextCliUtilitiesCli`` — ``run_checked`` and
``run_to_file`` — through their observable ``r[T]`` outcomes and file side
effects, plus the ``m.Cli.CommandOutput`` model's public state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from tests.models import m
from tests.utilities import u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliRuntimeUtilitiesExtra:
    """Public-contract behavior for ``u.Cli`` runtime helpers and output model."""

    @pytest.mark.parametrize(
        ("stdout", "stderr", "exit_code"),
        [
            ("out", "err", 0),
            ("", "", 0),
            ("data", "warning", 2),
        ],
    )
    def test_command_output_exposes_constructor_values_via_public_state(
        self,
        stdout: str,
        stderr: str,
        exit_code: int,
    ) -> None:
        # Arrange / Act
        output = m.Cli.CommandOutput(
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
        )

        # Assert — public fields and model_dump round-trip
        assert output.stdout == stdout
        assert output.stderr == stderr
        assert output.exit_code == exit_code
        dumped = output.model_dump()
        assert dumped["stdout"] == stdout
        assert dumped["stderr"] == stderr
        assert dumped["exit_code"] == exit_code

    def test_run_checked_returns_true_on_zero_exit(self) -> None:
        # Arrange / Act
        result = u.Cli().run_checked(["echo", "test"])

        # Assert
        tm.ok(result)
        assert result.value is True

    @pytest.mark.parametrize("exit_code", [1, 2, 42])
    def test_run_checked_fails_with_error_naming_failure(
        self,
        exit_code: int,
    ) -> None:
        # Arrange / Act
        result = u.Cli().run_checked(["sh", "-c", f"exit {exit_code}"])

        # Assert — failure surfaces as typed error mentioning the failure
        tm.fail(result)
        assert isinstance(result.error, str)
        assert "failed" in result.error.lower()

    def test_run_to_file_writes_stdout_and_returns_zero(
        self,
        tmp_path: Path,
    ) -> None:
        # Arrange
        output_file = tmp_path / "output.txt"

        # Act
        result = u.Cli().run_to_file(["echo", "hello"], output_file)

        # Assert — return value is the return code; file holds the output
        tm.ok(result)
        assert result.value == 0
        assert output_file.exists()
        assert "hello" in output_file.read_text()

    def test_run_to_file_returns_nonzero_returncode_as_success(
        self,
        tmp_path: Path,
    ) -> None:
        # Arrange
        output_file = tmp_path / "output.txt"

        # Act — a nonzero exit is a completed run, not an error channel
        result = u.Cli().run_to_file(["sh", "-c", "exit 7"], output_file)

        # Assert
        tm.ok(result)
        assert result.value == 7
        assert output_file.exists()

    def test_run_to_file_creates_missing_parent_directories(
        self,
        tmp_path: Path,
    ) -> None:
        # Arrange — nested path whose parents do not yet exist
        output_file = tmp_path / "nested" / "deep" / "output.txt"

        # Act
        result = u.Cli().run_to_file(["echo", "nested"], output_file)

        # Assert
        tm.ok(result)
        assert output_file.exists()
        assert "nested" in output_file.read_text()

    def test_run_to_file_fails_with_timeout_error_on_slow_command(
        self,
        tmp_path: Path,
    ) -> None:
        # Arrange
        output_file = tmp_path / "output.txt"

        # Act
        result = u.Cli().run_to_file(["sleep", "10"], output_file, timeout=1)

        # Assert
        tm.fail(result)
        assert isinstance(result.error, str)
        assert "timeout" in result.error.lower()

    def test_run_to_file_fails_with_execution_error_on_unwritable_target(
        self,
        tmp_path: Path,
    ) -> None:
        # Arrange — read-only directory makes opening the output file fail
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)
        output_file = readonly_dir / "output.txt"
        try:
            # Act
            result = u.Cli().run_to_file(["echo", "test"], output_file)

            # Assert
            tm.fail(result)
            assert isinstance(result.error, str)
            assert "execution error" in result.error.lower()
        finally:
            readonly_dir.chmod(0o755)

    def test_run_to_file_fails_with_execution_error_on_invalid_env(
        self,
        tmp_path: Path,
    ) -> None:
        # Arrange — NUL byte in an env value raises ValueError inside subprocess
        output_file = tmp_path / "output.txt"

        # Act
        result = u.Cli().run_to_file(
            ["echo", "test"],
            output_file,
            env={"BAD": "x\0y"},
        )

        # Assert
        tm.fail(result)
        assert isinstance(result.error, str)
        assert "execution error" in result.error.lower()
