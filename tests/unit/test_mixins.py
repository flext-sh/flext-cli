"""FLEXT CLI Mixins - Comprehensive test suite for validation mixins.

Tests for all mixin validation methods with 100% coverage.
All tests use proper type safety and cover both success and failure paths.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from flext_cli.mixins import FlextCliMixins


class TestFlextCliMixinsBusinessRulesMixin:
    """Test suite for BusinessRulesMixin validation methods."""

    def test_validate_command_execution_state_valid(self) -> None:
        """Test validate_command_execution_state with valid states."""
        result = FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
            current_status="running", required_status="running", operation="test"
        )
        assert result.is_success

    def test_validate_command_execution_state_invalid(self) -> None:
        """Test validate_command_execution_state with invalid states."""
        result = FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
            current_status="stopped", required_status="running", operation="migrate"
        )
        assert result.is_failure
        assert "migrate" in result.error
        assert "stopped" in result.error
        assert "running" in result.error

    def test_validate_session_state_valid(self) -> None:
        """Test validate_session_state with valid state."""
        result = FlextCliMixins.BusinessRulesMixin.validate_session_state(
            current_status="active", valid_states=["active", "idle"]
        )
        assert result.is_success

    def test_validate_session_state_invalid(self) -> None:
        """Test validate_session_state with invalid state."""
        result = FlextCliMixins.BusinessRulesMixin.validate_session_state(
            current_status="error", valid_states=["active", "idle"]
        )
        assert result.is_failure
        assert "error" in result.error
        assert "active" in result.error
        assert "idle" in result.error

    def test_validate_pipeline_step_valid(self) -> None:
        """Test validate_pipeline_step with valid step."""
        step = {"name": "migration", "type": "batch"}
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
        assert result.is_success

    def test_validate_pipeline_step_empty(self) -> None:
        """Test validate_pipeline_step with empty step."""
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(None)
        assert result.is_failure
        assert "empty" in result.error.lower()

    def test_validate_pipeline_step_no_name(self) -> None:
        """Test validate_pipeline_step without name field."""
        step = {"type": "batch", "config": {}}
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
        assert result.is_failure
        assert "name" in result.error.lower()

    def test_validate_pipeline_step_name_empty(self) -> None:
        """Test validate_pipeline_step with empty name."""
        step = {"name": "", "type": "batch"}
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
        assert result.is_failure
        assert "name" in result.error.lower()

    def test_validate_pipeline_step_name_whitespace(self) -> None:
        """Test validate_pipeline_step with whitespace-only name."""
        step = {"name": "   ", "type": "batch"}
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
        assert result.is_failure
        assert "name" in result.error.lower()

    def test_validate_configuration_consistency_valid(self) -> None:
        """Test validate_configuration_consistency with valid config."""
        config = {"field1": "value1", "field2": "value2"}
        required_fields = ["field1", "field2"]
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            config, required_fields
        )
        assert result.is_success

    def test_validate_configuration_consistency_missing_fields(self) -> None:
        """Test validate_configuration_consistency with missing fields."""
        config = {"field1": "value1"}
        required_fields = ["field1", "field2", "field3"]
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            config, required_fields
        )
        assert result.is_failure
        assert "field2" in result.error
        assert "field3" in result.error

    def test_validate_configuration_consistency_none_config(self) -> None:
        """Test validate_configuration_consistency with None config."""
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            None, ["field1"]
        )
        # Fast-fail: None config should fail when required fields are specified
        assert result.is_failure
        assert "field1" in (result.error or "")


class TestFlextCliMixinsCliCommandMixin:
    """Test suite for CliCommandMixin decorator composition."""

    def test_execute_with_cli_context_success(self) -> None:
        """Test execute_with_cli_context with successful handler."""
        from flext_core import FlextResult, FlextTypes

        def mock_handler(
            **kwargs: FlextTypes.JsonValue,
        ) -> FlextResult[FlextTypes.JsonValue]:
            return FlextResult[FlextTypes.JsonValue].ok({"result": "success", **kwargs})

        result = FlextCliMixins.CliCommandMixin.execute_with_cli_context(
            operation="test_operation", handler=mock_handler, test_param="test_value"
        )

        assert result.is_success
        data = result.unwrap()
        assert data["result"] == "success"
        assert data["test_param"] == "test_value"

    def test_execute_with_cli_context_failure(self) -> None:
        """Test execute_with_cli_context with failing handler."""
        from flext_core import FlextResult, FlextTypes

        test_error_msg = "Test error"

        def mock_handler(
            **kwargs: FlextTypes.JsonValue,
        ) -> FlextResult[FlextTypes.JsonValue]:
            return FlextResult[FlextTypes.JsonValue].fail(test_error_msg)

        result = FlextCliMixins.CliCommandMixin.execute_with_cli_context(
            operation="test_operation", handler=mock_handler
        )

        assert result.is_failure
        assert test_error_msg in (result.error or "")
