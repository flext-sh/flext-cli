"""Branch coverage tests for small flext_cli utility modules."""

from __future__ import annotations

import pytest

import flext_cli._utilities.cmd as cmd_module
import flext_cli._utilities.runtime as runtime_module
import flext_cli._utilities.validation as validation_module
from flext_cli import m
from flext_cli._utilities.cmd import FlextCliUtilitiesCmd
from flext_cli._utilities.runtime import FlextCliUtilitiesRuntime
from flext_cli._utilities.validation import FlextCliUtilitiesValidation
from flext_core import r


class TestsFlextCliCmdRuntimeValidationBranchCov:
    """Exercise remaining small utility branches."""

    def test_cmd_settings_snapshot_failure(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            cmd_module.us,
            "settings_snapshot",
            lambda: (_ for _ in ()).throw(ValueError("boom")),
        )
        result = FlextCliUtilitiesCmd.cmd_settings_snapshot()
        assert result.failure
        assert "boom" in (result.error or "")

    def test_cmd_show_settings_snapshot_failure(self) -> None:
        error_message = "should not log"

        class LoggerStub:
            def info(self, *args: object, **kwargs: object) -> None:
                raise AssertionError(error_message)

        original = FlextCliUtilitiesCmd.cmd_settings_snapshot
        try:
            FlextCliUtilitiesCmd.cmd_settings_snapshot = staticmethod(
                lambda: r[m.Cli.SettingsSnapshot].fail("bad-snapshot")
            )
            result = FlextCliUtilitiesCmd.cmd_show_settings(LoggerStub())
        finally:
            FlextCliUtilitiesCmd.cmd_settings_snapshot = original
        assert result.failure
        assert "bad-snapshot" in (result.error or "")

    def test_cmd_validate_settings_failure(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class LoggerStub:
            def info(self, *args: object, **kwargs: object) -> None:
                return None

        monkeypatch.setattr(
            cmd_module.us,
            "validate_settings_structure",
            lambda: (_ for _ in ()).throw(ValueError("bad-validate")),
        )
        result = FlextCliUtilitiesCmd.cmd_validate_settings(LoggerStub())
        assert result.failure
        assert "bad-validate" in (result.error or "")

    def test_runtime_process_env_removes_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(runtime_module.os, "environ", {"KEEP": "1", "DROP": "2"})
        env = FlextCliUtilitiesRuntime.process_env(remove_keys=("DROP",))
        assert env == {"KEEP": "1"}

    def test_validation_process_mapping_skip_branch(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        debug_calls: list[str] = []
        monkeypatch.setattr(
            validation_module.FlextCliUtilitiesValidation._module_logger,
            "debug",
            lambda message, exc_info=False: debug_calls.append(message),
        )
        result = FlextCliUtilitiesValidation.process_mapping(
            {"a": 1},
            lambda key, value: (_ for _ in ()).throw(ValueError("bad-item")),
            on_error="skip",
        )
        assert result.success
        assert result.value == {}
        assert debug_calls

    def test_validation_validate_format_preserves_original_case_in_error(self) -> None:
        result = FlextCliUtilitiesValidation.validate_format("BAD")
        assert result.failure
        assert "BAD" in (result.error or "")

    def test_validation_validate_not_empty_whitespace_fails(self) -> None:
        result = FlextCliUtilitiesValidation.validate_not_empty("   ", name="field")
        assert result.failure
        assert "field" in (result.error or "")


__all__: list[str] = ["TestsFlextCliCmdRuntimeValidationBranchCov"]
