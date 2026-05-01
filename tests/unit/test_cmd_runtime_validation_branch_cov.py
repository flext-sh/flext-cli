"""Branch coverage tests for small flext_cli utility modules."""

from __future__ import annotations

from flext_cli._utilities.cmd import FlextCliUtilitiesCmd
from flext_cli._utilities.runtime import FlextCliUtilitiesRuntime
from flext_cli._utilities.validation import FlextCliUtilitiesValidation


class TestsFlextCliCmdRuntimeValidationBranchCov:
    """Exercise remaining small utility branches."""

    def test_cmd_settings_snapshot_success(self) -> None:
        result = FlextCliUtilitiesCmd.cmd_settings_snapshot()
        assert result.success
        assert result.value is not None

    def test_runtime_process_env_removes_unknown_key(self) -> None:
        env = FlextCliUtilitiesRuntime.process_env(remove_keys=("__missing__",))
        assert isinstance(env, dict)

    def test_validation_process_mapping_collect_branch(self) -> None:
        result = FlextCliUtilitiesValidation.process_mapping(
            {"a": 1},
            lambda key, value: (_ for _ in ()).throw(ValueError("bad-item")),
            on_error="collect",
        )
        assert result.failure
        assert "a: bad-item" in (result.error or "")

    def test_validation_validate_format_preserves_original_case_in_error(self) -> None:
        result = FlextCliUtilitiesValidation.validate_format("BAD")
        assert result.failure
        assert "BAD" in (result.error or "")

    def test_validation_validate_not_empty_whitespace_fails(self) -> None:
        result = FlextCliUtilitiesValidation.validate_not_empty("   ", name="field")
        assert result.failure
        assert "field" in (result.error or "")


__all__: list[str] = ["TestsFlextCliCmdRuntimeValidationBranchCov"]
