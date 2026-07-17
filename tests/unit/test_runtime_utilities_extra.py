"""Behavioral tests for ``u.Cli`` runtime command execution and output model.

Exercises the public contract of ``FlextCliUtilitiesCli`` — ``run_checked`` and
``run_to_file`` — through their observable ``r[T]`` outcomes and file side
effects, plus the ``m.Cli.CommandOutput`` model's public state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from tests import m
from tests import u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliRuntimeUtilitiesExtra:
    """Public-contract behavior for ``u.Cli`` runtime helpers and output model."""

    @pytest.mark.parametrize(
        ("stdout", "stderr", "exit_code"),
        [("out", "err", 0), ("", "", 0), ("data", "warning", 2)],
    )
    def test_command_output_exposes_constructor_values_via_public_state(
        self, stdout: str, stderr: str, exit_code: int
    ) -> None:
        # Arrange / Act
        """Verify that command output exposes constructor values via public state."""
        output = m.Cli.CommandOutput(stdout=stdout, stderr=stderr, exit_code=exit_code)

        # Assert — public fields and model_dump round-trip
        tm.that(output.stdout, eq=stdout)
        tm.that(output.stderr, eq=stderr)
        tm.that(output.exit_code, eq=exit_code)
        dumped = output.model_dump()
        tm.that(dumped["stdout"], eq=stdout)
        tm.that(dumped["stderr"], eq=stderr)
        tm.that(dumped["exit_code"], eq=exit_code)

    def test_run_checked_returns_true_on_zero_exit(self) -> None:
        # Arrange / Act
        """Verify that run checked returns true on zero exit."""
        result = u.Cli().run_checked(["echo", "test"])

        # Assert
        tm.ok(result)
        tm.that(result.value, eq=True)

    @pytest.mark.parametrize("exit_code", [1, 2, 42])
    def test_run_checked_fails_with_error_naming_failure(self, exit_code: int) -> None:
        # Arrange / Act
        """Verify that run checked fails with error naming failure."""
        result = u.Cli().run_checked(["sh", "-c", f"exit {exit_code}"])

        # Assert — failure surfaces as typed error mentioning the failure
        tm.fail(result)
        tm.that(result.error, is_=str)
        tm.that(tm.not_none(result.error).lower(), has="failed")

    def test_run_to_file_writes_stdout_and_returns_zero(self, tmp_path: Path) -> None:
        # Arrange
        """Verify that run to file writes stdout and returns zero."""
        output_file = tmp_path / "output.txt"

        # Act
        result = u.Cli().run_to_file(["echo", "hello"], output_file)

        # Assert — return value is the return code; file holds the output
        tm.ok(result)
        tm.that(result.value, eq=0)
        tm.that(output_file.exists(), eq=True)
        tm.that(output_file.read_text(), has="hello")

    def test_run_to_file_returns_nonzero_returncode_as_success(
        self, tmp_path: Path
    ) -> None:
        # Arrange
        """Verify that run to file returns nonzero returncode as success."""
        output_file = tmp_path / "output.txt"

        # Act — a nonzero exit is a completed run, not an error channel
        result = u.Cli().run_to_file(["sh", "-c", "exit 7"], output_file)

        # Assert
        tm.ok(result)
        tm.that(result.value, eq=7)
        tm.that(output_file.exists(), eq=True)

    def test_run_to_file_creates_missing_parent_directories(
        self, tmp_path: Path
    ) -> None:
        # Arrange — nested path whose parents do not yet exist
        """Verify that run to file creates missing parent directories."""
        output_file = tmp_path / "nested" / "deep" / "output.txt"

        # Act
        result = u.Cli().run_to_file(["echo", "nested"], output_file)

        # Assert
        tm.ok(result)
        tm.that(output_file.exists(), eq=True)
        tm.that(output_file.read_text(), has="nested")

    def test_run_to_file_fails_with_timeout_error_on_slow_command(
        self, tmp_path: Path
    ) -> None:
        # Arrange
        """Verify that run to file fails with timeout error on slow command."""
        output_file = tmp_path / "output.txt"

        # Act
        result = u.Cli().run_to_file(["sleep", "10"], output_file, timeout=1)

        # Assert
        tm.fail(result)
        tm.that(result.error, is_=str)
        tm.that(tm.not_none(result.error).lower(), has="timeout")

    def test_run_to_file_fails_with_execution_error_on_unwritable_target(
        self, tmp_path: Path
    ) -> None:
        # Arrange — read-only directory makes opening the output file fail
        """Verify that run to file fails with execution error on unwritable target."""
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)
        output_file = readonly_dir / "output.txt"
        try:
            # Act
            result = u.Cli().run_to_file(["echo", "test"], output_file)

            # Assert
            tm.fail(result)
            tm.that(result.error, is_=str)
            tm.that(tm.not_none(result.error).lower(), has="execution error")
        finally:
            readonly_dir.chmod(0o755)

    def test_run_to_file_fails_with_execution_error_on_invalid_env(
        self, tmp_path: Path
    ) -> None:
        # Arrange — NUL byte in an env value raises ValueError inside subprocess
        """Verify that run to file fails with execution error on invalid env."""
        output_file = tmp_path / "output.txt"

        # Act
        result = u.Cli().run_to_file(["echo", "test"], output_file, env={"BAD": "x\0y"})

        # Assert
        tm.fail(result)
        tm.that(result.error, is_=str)
        tm.that(tm.not_none(result.error).lower(), has="execution error")
