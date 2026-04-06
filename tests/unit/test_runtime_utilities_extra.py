"""Tests for ``u.Cli`` runtime model, checked, and file operations."""

from __future__ import annotations

from pathlib import Path

import pytest
from flext_tests import tm

from tests import m, t, u


class TestCliRuntimeUtilitiesExtra:
    """Extra runtime behavior tests for ``u.Cli``."""

    def test_command_output_model(self) -> None:
        output = m.Cli.CommandOutput(stdout="out", stderr="err", exit_code=0)
        assert output.stdout == "out"
        assert output.stderr == "err"
        assert output.exit_code == 0

    def test_run_checked_success(self) -> None:
        result = u.Cli().run_checked(["echo", "test"])
        tm.ok(result)
        assert result.value is True

    def test_run_checked_failure(self) -> None:
        result = u.Cli().run_checked(["sh", "-c", "exit 1"])
        tm.fail(result)
        assert isinstance(result.error, str)
        assert "failed" in result.error.lower()

    def test_run_to_file_success(self, tmp_path: Path) -> None:
        output_file = tmp_path / "output.txt"
        result = u.Cli().run_to_file(["echo", "hello"], output_file)
        tm.ok(result)
        assert result.value == 0
        assert output_file.exists()
        assert "hello" in output_file.read_text()

    def test_run_to_file_timeout(self, tmp_path: Path) -> None:
        output_file = tmp_path / "output.txt"
        result = u.Cli().run_to_file(["sleep", "10"], output_file, timeout=1)
        tm.fail(result)
        assert isinstance(result.error, str)
        assert "timeout" in result.error.lower()

    def test_run_to_file_oserror(self, tmp_path: Path) -> None:
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(292)
        output_file = readonly_dir / "output.txt"
        try:
            result = u.Cli().run_to_file(["echo", "test"], output_file)
            tm.fail(result)
            assert isinstance(result.error, str)
            assert "execution error" in result.error.lower()
        finally:
            readonly_dir.chmod(493)

    def test_run_to_file_valueerror(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        output_file = tmp_path / "output.txt"

        def mock_run(*args: t.Scalar, **kwargs: t.Scalar) -> None:
            _ = args, kwargs
            msg = "Invalid argument"
            raise ValueError(msg)

        monkeypatch.setattr("flext_cli._utilities.runtime.subprocess.run", mock_run)
        result = u.Cli().run_to_file(["echo", "test"], output_file)
        tm.fail(result)
        assert isinstance(result.error, str)
        assert "execution error" in result.error.lower()
