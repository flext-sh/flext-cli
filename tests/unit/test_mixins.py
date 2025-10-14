"""Test FlextCliMixins - Real functionality testing.

Tests cover:
- ValidationMixin: All validation methods with success/failure/edge cases
- BusinessRulesMixin: All business rule validation methods
- FlextCore.Result patterns throughout
- No mocks, only real functionality tests

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_cli.constants import FlextCliConstants
from flext_cli.mixins import FlextCliMixins
from flext_cli.typings import FlextCliTypes


class TestFlextCliMixinsValidation:
    """Test suite for FlextCliMixins.ValidationMixin - real functionality only."""

    # =========================================================================
    # validate_not_empty tests
    # =========================================================================

    def test_validate_not_empty_success_string(self) -> None:
        """Test validate_not_empty with valid non-empty string."""
        result = FlextCliMixins.ValidationMixin.validate_not_empty(
            "test_field", "valid_value"
        )
        assert result.is_success

    def test_validate_not_empty_failure_empty_string(self) -> None:
        """Test validate_not_empty with empty string."""
        result = FlextCliMixins.ValidationMixin.validate_not_empty("test_field", "")
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "cannot be empty" in result.error.lower()

    def test_validate_not_empty_failure_whitespace_string(self) -> None:
        """Test validate_not_empty with whitespace-only string."""
        result = FlextCliMixins.ValidationMixin.validate_not_empty("test_field", "   ")
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "cannot be empty" in result.error.lower()

    def test_validate_not_empty_success_number(self) -> None:
        """Test validate_not_empty with non-zero number."""
        result = FlextCliMixins.ValidationMixin.validate_not_empty("test_field", 42.5)
        assert result.is_success

    def test_validate_not_empty_failure_zero(self) -> None:
        """Test validate_not_empty with zero value."""
        result = FlextCliMixins.ValidationMixin.validate_not_empty("test_field", 0)
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "cannot be empty" in result.error.lower()

    def test_validate_not_empty_failure_none(self) -> None:
        """Test validate_not_empty with None."""
        result = FlextCliMixins.ValidationMixin.validate_not_empty("test_field", None)
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "cannot be empty" in result.error.lower()

    # =========================================================================
    # validate_url tests
    # =========================================================================

    def test_validate_url_success_http(self) -> None:
        """Test validate_url with valid HTTP URL."""
        result = FlextCliMixins.ValidationMixin.validate_url(
            "api_url", "http://example.com"
        )
        assert result.is_success

    def test_validate_url_success_https(self) -> None:
        """Test validate_url with valid HTTPS URL."""
        result = FlextCliMixins.ValidationMixin.validate_url(
            "api_url", "https://api.example.com/v1"
        )
        assert result.is_success

    def test_validate_url_failure_invalid_format(self) -> None:
        """Test validate_url with invalid URL format."""
        result = FlextCliMixins.ValidationMixin.validate_url(
            "api_url", "not-a-valid-url"
        )
        assert result.is_failure
        assert result.error is not None

    def test_validate_url_failure_empty(self) -> None:
        """Test validate_url with empty string."""
        result = FlextCliMixins.ValidationMixin.validate_url("api_url", "")
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "cannot be empty" in result.error.lower()

    def test_validate_url_failure_whitespace(self) -> None:
        """Test validate_url with whitespace-only string."""
        result = FlextCliMixins.ValidationMixin.validate_url("api_url", "   ")
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "cannot be empty" in result.error.lower()

    def test_validate_url_exception_handling(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test validate_url exception handler (lines 85-86)."""
        from unittest.mock import Mock

        # Create a mock that raises an exception when called
        mock_urlparse = Mock(side_effect=RuntimeError("URL parsing error"))

        # Patch urlparse to raise exception
        monkeypatch.setattr("flext_cli.mixins.urlparse", mock_urlparse)

        # This should trigger the exception handler
        result = FlextCliMixins.ValidationMixin.validate_url(
            "api_url", "http://example.com"
        )

        assert result.is_failure
        assert result.error is not None
        assert "validation failed" in (result.error or "").lower()
        assert "URL parsing error" in (result.error or "")

    # =========================================================================
    # validate_enum_value tests
    # =========================================================================

    def test_validate_enum_value_success(self) -> None:
        """Test validate_enum_value with valid enum value."""
        valid_values = ["option1", "option2", "option3"]
        result = FlextCliMixins.ValidationMixin.validate_enum_value(
            "test_enum", "option2", valid_values
        )
        assert result.is_success

    def test_validate_enum_value_failure_invalid(self) -> None:
        """Test validate_enum_value with invalid enum value."""
        valid_values = ["option1", "option2", "option3"]
        result = FlextCliMixins.ValidationMixin.validate_enum_value(
            "test_enum", "invalid_option", valid_values
        )
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "invalid" in result.error.lower()

    def test_validate_enum_value_case_sensitive(self) -> None:
        """Test validate_enum_value is case-sensitive."""
        valid_values = ["Option1", "Option2"]
        result = FlextCliMixins.ValidationMixin.validate_enum_value(
            "test_enum", "option1", valid_values
        )
        assert result.is_failure
        assert result.error is not None

    # =========================================================================
    # validate_positive_number tests
    # =========================================================================

    def test_validate_positive_number_success(self) -> None:
        """Test validate_positive_number with positive number."""
        result = FlextCliMixins.ValidationMixin.validate_positive_number(
            "test_number", 42
        )
        assert result.is_success

    def test_validate_positive_number_failure_zero(self) -> None:
        """Test validate_positive_number with zero."""
        result = FlextCliMixins.ValidationMixin.validate_positive_number(
            "test_number", 0
        )
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "must be positive" in result.error.lower()

    def test_validate_positive_number_failure_negative(self) -> None:
        """Test validate_positive_number with negative number."""
        result = FlextCliMixins.ValidationMixin.validate_positive_number(
            "test_number", -5
        )
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "must be positive" in result.error.lower()

    # =========================================================================
    # validate_non_negative_number tests
    # =========================================================================

    def test_validate_non_negative_number_success_positive(self) -> None:
        """Test validate_non_negative_number with positive number."""
        result = FlextCliMixins.ValidationMixin.validate_non_negative_number(
            "test_number", 42
        )
        assert result.is_success

    def test_validate_non_negative_number_success_zero(self) -> None:
        """Test validate_non_negative_number with zero."""
        result = FlextCliMixins.ValidationMixin.validate_non_negative_number(
            "test_number", 0
        )
        assert result.is_success

    def test_validate_non_negative_number_failure_negative(self) -> None:
        """Test validate_non_negative_number with negative number."""
        result = FlextCliMixins.ValidationMixin.validate_non_negative_number(
            "test_number", -1
        )
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "cannot be negative" in result.error.lower()

    # =========================================================================
    # validate_output_format tests
    # =========================================================================

    def test_validate_output_format_success_table(self) -> None:
        """Test validate_output_format with 'table'."""
        result = FlextCliMixins.ValidationMixin.validate_output_format("table")
        assert result.is_success

    def test_validate_output_format_success_json(self) -> None:
        """Test validate_output_format with 'json'."""
        result = FlextCliMixins.ValidationMixin.validate_output_format("json")
        assert result.is_success

    def test_validate_output_format_success_yaml(self) -> None:
        """Test validate_output_format with 'yaml'."""
        result = FlextCliMixins.ValidationMixin.validate_output_format("yaml")
        assert result.is_success

    def test_validate_output_format_failure_invalid(self) -> None:
        """Test validate_output_format with invalid format."""
        result = FlextCliMixins.ValidationMixin.validate_output_format("invalid_format")
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "invalid" in result.error.lower()

    # =========================================================================
    # validate_log_level tests
    # =========================================================================

    def test_validate_log_level_success_info(self) -> None:
        """Test validate_log_level with 'INFO'."""
        result = FlextCliMixins.ValidationMixin.validate_log_level("INFO")
        assert result.is_success

    def test_validate_log_level_success_debug(self) -> None:
        """Test validate_log_level with 'DEBUG'."""
        result = FlextCliMixins.ValidationMixin.validate_log_level("DEBUG")
        assert result.is_success

    def test_validate_log_level_success_error(self) -> None:
        """Test validate_log_level with 'ERROR'."""
        result = FlextCliMixins.ValidationMixin.validate_log_level("ERROR")
        assert result.is_success

    def test_validate_log_level_failure_invalid(self) -> None:
        """Test validate_log_level with invalid level."""
        result = FlextCliMixins.ValidationMixin.validate_log_level("INVALID")
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "invalid" in result.error.lower()

    # =========================================================================
    # validate_status tests
    # =========================================================================

    def test_validate_status_success(self) -> None:
        """Test validate_status with valid status."""
        # Test with valid statuses from FlextCliConstants
        for status in FlextCliConstants.COMMAND_STATUSES_LIST:
            result = FlextCliMixins.ValidationMixin.validate_status(status)
            assert result.is_success

    def test_validate_status_failure_invalid(self) -> None:
        """Test validate_status with invalid status."""
        result = FlextCliMixins.ValidationMixin.validate_status("INVALID_STATUS")
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "invalid" in result.error.lower()


class TestFlextCliMixinsBusinessRules:
    """Test suite for FlextCliMixins.BusinessRulesMixin - real functionality only."""

    # =========================================================================
    # validate_command_execution_state tests
    # =========================================================================

    def test_validate_command_execution_state_success(self) -> None:
        """Test validate_command_execution_state with matching states."""
        result = FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
            current_status="running", required_status="running", operation="execute"
        )
        assert result.is_success

    def test_validate_command_execution_state_failure_mismatch(self) -> None:
        """Test validate_command_execution_state with mismatched states."""
        result = FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
            current_status="pending",
            required_status="running",
            operation="execute",
        )
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "pending" in result.error.lower()
        assert result.error is not None
        assert "running" in result.error.lower()

    # =========================================================================
    # validate_session_state tests
    # =========================================================================

    def test_validate_session_state_success(self) -> None:
        """Test validate_session_state with valid state."""
        valid_states = ["active", "pending", "expired"]
        result = FlextCliMixins.BusinessRulesMixin.validate_session_state(
            current_status="active", valid_states=valid_states
        )
        assert result.is_success

    def test_validate_session_state_failure_invalid(self) -> None:
        """Test validate_session_state with invalid state."""
        valid_states = ["active", "pending", "expired"]
        result = FlextCliMixins.BusinessRulesMixin.validate_session_state(
            current_status="invalid_state", valid_states=valid_states
        )
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "invalid session status" in result.error.lower()

    # =========================================================================
    # validate_pipeline_step tests
    # =========================================================================

    def test_validate_pipeline_step_success(self) -> None:
        """Test validate_pipeline_step with valid step."""
        step: FlextCliTypes.Data.CliDataDict = {
            "name": "process_data",
            "action": "transform",
            "config": {"timeout": 30},
        }
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
        assert result.is_success

    def test_validate_pipeline_step_failure_none(self) -> None:
        """Test validate_pipeline_step with None."""
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(None)
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "non-empty dictionary" in result.error.lower()

    def test_validate_pipeline_step_failure_missing_name(self) -> None:
        """Test validate_pipeline_step with missing 'name' field."""
        step: FlextCliTypes.Data.CliDataDict = {
            "action": "transform",
            "config": {"timeout": 30},
        }
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "name" in result.error.lower()

    def test_validate_pipeline_step_failure_empty_name(self) -> None:
        """Test validate_pipeline_step with empty name."""
        step: FlextCliTypes.Data.CliDataDict = {
            "name": "",
            "action": "transform",
        }
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "cannot be empty" in result.error.lower()

    def test_validate_pipeline_step_failure_whitespace_name(self) -> None:
        """Test validate_pipeline_step with whitespace-only name."""
        step: FlextCliTypes.Data.CliDataDict = {
            "name": "   ",
            "action": "transform",
        }
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "cannot be empty" in result.error.lower()

    # =========================================================================
    # validate_configuration_consistency tests
    # =========================================================================

    def test_validate_configuration_consistency_success_all_fields(self) -> None:
        """Test validate_configuration_consistency with all required fields."""
        config_data: FlextCliTypes.Data.CliDataDict = {
            "api_endpoint": "https://api.example.com",
            "auth_token": "token123",
            "timeout": 30,
        }
        required_fields = ["api_endpoint", "auth_token", "timeout"]
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            config_data, required_fields
        )
        assert result.is_success

    def test_validate_configuration_consistency_failure_missing_fields(self) -> None:
        """Test validate_configuration_consistency with missing fields."""
        config_data: FlextCliTypes.Data.CliDataDict = {
            "api_endpoint": "https://api.example.com",
            "timeout": 30,
        }
        required_fields = ["api_endpoint", "auth_token", "timeout"]
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            config_data, required_fields
        )
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "missing required configuration fields" in result.error.lower()
        assert result.error is not None
        assert "auth_token" in result.error.lower()

    def test_validate_configuration_consistency_success_extra_fields(self) -> None:
        """Test validate_configuration_consistency with extra fields (allowed)."""
        config_data: FlextCliTypes.Data.CliDataDict = {
            "api_endpoint": "https://api.example.com",
            "auth_token": "token123",
            "timeout": 30,
            "extra_field": "extra_value",
        }
        required_fields = ["api_endpoint", "auth_token"]
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            config_data, required_fields
        )
        assert result.is_success

    def test_validate_configuration_consistency_failure_multiple_missing(self) -> None:
        """Test validate_configuration_consistency with multiple missing fields."""
        config_data: FlextCliTypes.Data.CliDataDict = {
            "timeout": 30,
        }
        required_fields = ["api_endpoint", "auth_token", "profile"]
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            config_data, required_fields
        )
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "missing required configuration fields" in result.error.lower()
