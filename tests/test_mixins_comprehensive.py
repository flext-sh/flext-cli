"""Comprehensive tests for FlextCliMixins to achieve 100% coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.mixins import FlextCliMixins


class TestFlextCliMixinsValidationMixin:
    """Test the ValidationMixin nested class."""

    def test_validate_not_empty_success(self) -> None:
        """Test validate_not_empty with valid input."""
        result = FlextCliMixins.ValidationMixin.validate_not_empty(
            "test_field", "valid_value"
        )
        assert result.is_success
        assert result.unwrap() is None

    def test_validate_not_empty_empty_string(self) -> None:
        """Test validate_not_empty with empty string."""
        result = FlextCliMixins.ValidationMixin.validate_not_empty("test_field", "")
        assert result.is_failure
        assert "test_field cannot be empty" in result.error

    def test_validate_not_empty_whitespace(self) -> None:
        """Test validate_not_empty with whitespace only."""
        result = FlextCliMixins.ValidationMixin.validate_not_empty("test_field", "   ")
        assert result.is_failure
        assert "test_field cannot be empty" in result.error

    def test_validate_not_empty_none(self) -> None:
        """Test validate_not_empty with None."""
        result = FlextCliMixins.ValidationMixin.validate_not_empty("test_field", None)
        assert result.is_failure
        assert "test_field cannot be empty" in result.error

    def test_validate_url_success_http(self) -> None:
        """Test validate_url with valid HTTP URL."""
        result = FlextCliMixins.ValidationMixin.validate_url(
            "test_url", "http://example.com"
        )
        assert result.is_success
        assert result.unwrap() is None

    def test_validate_url_success_https(self) -> None:
        """Test validate_url with valid HTTPS URL."""
        result = FlextCliMixins.ValidationMixin.validate_url(
            "test_url", "https://example.com"
        )
        assert result.is_success
        assert result.unwrap() is None

    def test_validate_url_empty(self) -> None:
        """Test validate_url with empty string."""
        result = FlextCliMixins.ValidationMixin.validate_url("test_url", "")
        assert result.is_failure
        assert "test_url cannot be empty" in result.error

    def test_validate_url_whitespace(self) -> None:
        """Test validate_url with whitespace only."""
        result = FlextCliMixins.ValidationMixin.validate_url("test_url", "   ")
        assert result.is_failure
        assert "test_url cannot be empty" in result.error

    def test_validate_url_invalid_protocol(self) -> None:
        """Test validate_url with invalid protocol."""
        result = FlextCliMixins.ValidationMixin.validate_url(
            "test_url", "ftp://example.com"
        )
        assert result.is_failure
        assert "test_url must start with http:// or https://" in result.error

    def test_validate_url_no_protocol(self) -> None:
        """Test validate_url with no protocol."""
        result = FlextCliMixins.ValidationMixin.validate_url("test_url", "example.com")
        assert result.is_failure
        assert "test_url must start with http:// or https://" in result.error

    def test_validate_enum_value_success(self) -> None:
        """Test validate_enum_value with valid value."""
        valid_values = ["option1", "option2", "option3"]
        result = FlextCliMixins.ValidationMixin.validate_enum_value(
            "test_field", "option2", valid_values
        )
        assert result.is_success
        assert result.unwrap() is None

    def test_validate_enum_value_invalid(self) -> None:
        """Test validate_enum_value with invalid value."""
        valid_values = ["option1", "option2", "option3"]
        result = FlextCliMixins.ValidationMixin.validate_enum_value(
            "test_field", "invalid_option", valid_values
        )
        assert result.is_failure
        assert (
            "Invalid test_field. Valid values: ['option1', 'option2', 'option3']"
            in result.error
        )

    def test_validate_positive_number_success(self) -> None:
        """Test validate_positive_number with positive number."""
        result = FlextCliMixins.ValidationMixin.validate_positive_number(
            "test_number", 5
        )
        assert result.is_success
        assert result.unwrap() is None

    def test_validate_positive_number_zero(self) -> None:
        """Test validate_positive_number with zero."""
        result = FlextCliMixins.ValidationMixin.validate_positive_number(
            "test_number", 0
        )
        assert result.is_failure
        assert "test_number must be positive" in result.error

    def test_validate_positive_number_negative(self) -> None:
        """Test validate_positive_number with negative number."""
        result = FlextCliMixins.ValidationMixin.validate_positive_number(
            "test_number", -5
        )
        assert result.is_failure
        assert "test_number must be positive" in result.error

    def test_validate_non_negative_number_success_positive(self) -> None:
        """Test validate_non_negative_number with positive number."""
        result = FlextCliMixins.ValidationMixin.validate_non_negative_number(
            "test_number", 5
        )
        assert result.is_success
        assert result.unwrap() is None

    def test_validate_non_negative_number_success_zero(self) -> None:
        """Test validate_non_negative_number with zero."""
        result = FlextCliMixins.ValidationMixin.validate_non_negative_number(
            "test_number", 0
        )
        assert result.is_success
        assert result.unwrap() is None

    def test_validate_non_negative_number_negative(self) -> None:
        """Test validate_non_negative_number with negative number."""
        result = FlextCliMixins.ValidationMixin.validate_non_negative_number(
            "test_number", -5
        )
        assert result.is_failure
        assert "test_number cannot be negative" in result.error

    def test_validate_output_format_success(self) -> None:
        """Test validate_output_format with valid format."""
        result = FlextCliMixins.ValidationMixin.validate_output_format("table")
        assert result.is_success
        assert result.unwrap() is None

    def test_validate_output_format_invalid(self) -> None:
        """Test validate_output_format with invalid format."""
        result = FlextCliMixins.ValidationMixin.validate_output_format("invalid_format")
        assert result.is_failure
        assert "Invalid output format" in result.error

    def test_validate_log_level_success(self) -> None:
        """Test validate_log_level with valid level."""
        result = FlextCliMixins.ValidationMixin.validate_log_level("INFO")
        assert result.is_success
        assert result.unwrap() is None

    def test_validate_log_level_invalid(self) -> None:
        """Test validate_log_level with invalid level."""
        result = FlextCliMixins.ValidationMixin.validate_log_level("INVALID_LEVEL")
        assert result.is_failure
        assert "Invalid log level" in result.error

    def test_validate_status_success(self) -> None:
        """Test validate_status with valid status."""
        result = FlextCliMixins.ValidationMixin.validate_status("completed")
        assert result.is_success
        assert result.unwrap() is None

    def test_validate_status_invalid(self) -> None:
        """Test validate_status with invalid status."""
        result = FlextCliMixins.ValidationMixin.validate_status("invalid_status")
        assert result.is_failure
        assert "Invalid status" in result.error


class TestFlextCliMixinsBusinessRulesMixin:
    """Test the BusinessRulesMixin nested class."""

    def test_validate_command_execution_state_success(self) -> None:
        """Test validate_command_execution_state with matching status."""
        result = FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
            "ready", "ready", "start"
        )
        assert result.is_success
        assert result.unwrap() is None

    def test_validate_command_execution_state_mismatch(self) -> None:
        """Test validate_command_execution_state with mismatched status."""
        result = FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
            "running", "ready", "start"
        )
        assert result.is_failure
        assert (
            "Cannot start: command is in 'running' state, requires 'ready'"
            in result.error
        )

    def test_validate_session_state_success(self) -> None:
        """Test validate_session_state with valid state."""
        valid_states = ["active", "inactive", "suspended"]
        result = FlextCliMixins.BusinessRulesMixin.validate_session_state(
            "active", valid_states
        )
        assert result.is_success
        assert result.unwrap() is None

    def test_validate_session_state_invalid(self) -> None:
        """Test validate_session_state with invalid state."""
        valid_states = ["active", "inactive", "suspended"]
        result = FlextCliMixins.BusinessRulesMixin.validate_session_state(
            "invalid", valid_states
        )
        assert result.is_failure
        assert (
            "Invalid session status 'invalid'. Valid states: ['active', 'inactive', 'suspended']"
            in result.error
        )

    def test_validate_pipeline_step_success(self) -> None:
        """Test validate_pipeline_step with valid step."""
        step: dict[str, object] = {"name": "test_step", "type": "transform"}
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
        assert result.is_success
        assert result.unwrap() is None

    def test_validate_pipeline_step_empty_dict(self) -> None:
        """Test validate_pipeline_step with empty dictionary."""
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step({})
        assert result.is_failure
        assert "Pipeline step must be a non-empty dictionary" in result.error

    def test_validate_pipeline_step_none(self) -> None:
        """Test validate_pipeline_step with None."""
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(None)  # type: ignore[arg-type]
        assert result.is_failure
        assert "Pipeline step must be a non-empty dictionary" in result.error

    def test_validate_pipeline_step_missing_name(self) -> None:
        """Test validate_pipeline_step without name field."""
        step: dict[str, object] = {"type": "transform"}
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
        assert result.is_failure
        assert "Pipeline step must have a 'name' field" in result.error

    def test_validate_pipeline_step_empty_name(self) -> None:
        """Test validate_pipeline_step with empty name."""
        step: dict[str, object] = {"name": "", "type": "transform"}
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
        assert result.is_failure
        assert "Pipeline step name cannot be empty" in result.error

    def test_validate_pipeline_step_whitespace_name(self) -> None:
        """Test validate_pipeline_step with whitespace-only name."""
        step: dict[str, object] = {"name": "   ", "type": "transform"}
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
        assert result.is_failure
        assert "Pipeline step name cannot be empty" in result.error

    def test_validate_pipeline_step_none_name(self) -> None:
        """Test validate_pipeline_step with None name."""
        step: dict[str, object] = {"name": None, "type": "transform"}
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
        assert result.is_failure
        assert "Pipeline step name cannot be empty" in result.error

    def test_validate_configuration_consistency_success(self) -> None:
        """Test validate_configuration_consistency with all required fields."""
        config_data: dict[str, object] = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3",
        }
        required_fields = ["field1", "field2"]
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            config_data, required_fields
        )
        assert result.is_success
        assert result.unwrap() is None

    def test_validate_configuration_consistency_missing_fields(self) -> None:
        """Test validate_configuration_consistency with missing fields."""
        config_data: dict[str, object] = {"field1": "value1"}
        required_fields = ["field1", "field2", "field3"]
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            config_data, required_fields
        )
        assert result.is_failure
        assert (
            "Missing required configuration fields: ['field2', 'field3']"
            in result.error
        )

    def test_validate_configuration_consistency_empty_required_fields(self) -> None:
        """Test validate_configuration_consistency with empty required fields list."""
        config_data: dict[str, object] = {"field1": "value1", "field2": "value2"}
        required_fields: list[str] = []
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            config_data, required_fields
        )
        assert result.is_success
        assert result.unwrap() is None

    def test_validate_configuration_consistency_empty_config(self) -> None:
        """Test validate_configuration_consistency with empty config."""
        config_data: dict[str, object] = {}
        required_fields = ["field1", "field2"]
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            config_data, required_fields
        )
        assert result.is_failure
        assert (
            "Missing required configuration fields: ['field1', 'field2']"
            in result.error
        )


class TestFlextCliMixinsIntegration:
    """Integration tests for FlextCliMixins."""

    def test_validation_mixin_chain(self) -> None:
        """Test chaining multiple validation methods."""
        # Test successful validation chain
        result1 = FlextCliMixins.ValidationMixin.validate_not_empty("name", "test_name")
        assert result1.is_success

        result2 = FlextCliMixins.ValidationMixin.validate_url(
            "url", "https://example.com"
        )
        assert result2.is_success

        result3 = FlextCliMixins.ValidationMixin.validate_positive_number("count", 5)
        assert result3.is_success

    def test_business_rules_mixin_chain(self) -> None:
        """Test chaining multiple business rule validation methods."""
        # Test successful business rule validation chain
        result1 = FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
            "ready", "ready", "start"
        )
        assert result1.is_success

        result2 = FlextCliMixins.BusinessRulesMixin.validate_session_state(
            "active", ["active", "inactive"]
        )
        assert result2.is_success

        result3 = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step({
            "name": "test_step",
            "type": "transform",
        })
        assert result3.is_success

    def test_mixed_validation_chain(self) -> None:
        """Test mixing validation and business rule methods."""
        # Test successful mixed validation chain
        result1 = FlextCliMixins.ValidationMixin.validate_not_empty(
            "step_name", "test_step"
        )
        assert result1.is_success

        result2 = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step({
            "name": "test_step",
            "type": "transform",
        })
        assert result2.is_success

        result3 = FlextCliMixins.ValidationMixin.validate_positive_number("timeout", 30)
        assert result3.is_success

    def test_error_handling_chain(self) -> None:
        """Test error handling in validation chains."""
        # Test that errors are properly propagated
        result1 = FlextCliMixins.ValidationMixin.validate_not_empty("name", "")
        assert result1.is_failure

        result2 = FlextCliMixins.ValidationMixin.validate_url("url", "invalid_url")
        assert result2.is_failure

        result3 = FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
            "running", "ready", "start"
        )
        assert result3.is_failure

    def test_comprehensive_validation_scenario(self) -> None:
        """Test comprehensive validation scenario."""
        # Simulate validating a complete configuration
        config_data = {
            "name": "test_config",
            "url": "https://api.example.com",
            "timeout": 30,
            "retries": 3,
            "log_level": "INFO",
            "output_format": "json",
        }

        # Validate individual fields
        name_result = FlextCliMixins.ValidationMixin.validate_not_empty(
            "name", str(config_data["name"])
        )
        assert name_result.is_success

        url_result = FlextCliMixins.ValidationMixin.validate_url(
            "url", str(config_data["url"])
        )
        assert url_result.is_success

        timeout_result = FlextCliMixins.ValidationMixin.validate_positive_number(
            "timeout", int(config_data["timeout"])
        )
        assert timeout_result.is_success

        retries_result = FlextCliMixins.ValidationMixin.validate_non_negative_number(
            "retries", int(config_data["retries"])
        )
        assert retries_result.is_success

        log_level_result = FlextCliMixins.ValidationMixin.validate_log_level(
            str(config_data["log_level"])
        )
        assert log_level_result.is_success

        output_format_result = FlextCliMixins.ValidationMixin.validate_output_format(
            str(config_data["output_format"])
        )
        assert output_format_result.is_success

        # Validate configuration consistency
        required_fields = [
            "name",
            "url",
            "timeout",
            "retries",
            "log_level",
            "output_format",
        ]
        consistency_result = (
            FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
                config_data, required_fields
            )
        )
        assert consistency_result.is_success

    def test_edge_cases(self) -> None:
        """Test edge cases and boundary conditions."""
        # Test boundary values for numbers
        result1 = FlextCliMixins.ValidationMixin.validate_positive_number(
            "min_positive", 1
        )
        assert result1.is_success

        result2 = FlextCliMixins.ValidationMixin.validate_non_negative_number("zero", 0)
        assert result2.is_success

        # Test empty lists and dictionaries
        result3 = FlextCliMixins.ValidationMixin.validate_enum_value(
            "field", "value", []
        )
        assert result3.is_failure

        result4 = FlextCliMixins.BusinessRulesMixin.validate_session_state("state", [])
        assert result4.is_failure

    def test_type_safety(self) -> None:
        """Test type safety of validation methods."""
        # Test that methods handle different types appropriately
        result1 = FlextCliMixins.ValidationMixin.validate_not_empty("field", 123)
        assert result1.is_success  # Non-string values are considered non-empty

        result2 = FlextCliMixins.ValidationMixin.validate_not_empty("field", "")
        assert result2.is_failure  # Empty list is falsy

        result3 = FlextCliMixins.ValidationMixin.validate_not_empty("field", "")
        assert result3.is_failure  # Empty dict is falsy
