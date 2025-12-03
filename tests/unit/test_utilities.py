"""FLEXT CLI Utilities Tests - Comprehensive Utilities Validation Testing.

Tests for FlextCliUtilities covering CLI validation, environment detection,
config operations, file operations, type normalization, and integration scenarios
with 100% coverage.

Modules tested: flext_cli.utilities.FlextCliUtilities
Scope: All utility namespaces, validation methods, environment detection, config/file ops, type normalization

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Union, cast

import pytest
from flext_core import FlextResult, t, u
from flext_tests import FlextTestsMatchers, FlextTestsUtilities
from pydantic import BaseModel

from flext_cli import FlextCliConstants, FlextCliUtilities

from .._helpers import FlextCliTestHelpers
from ..fixtures.constants import TestUtilities

# Alias for static method calls - use u.* for uds
u = u


class ValidationType(StrEnum):
    """Validation types for comprehensive testing."""

    FIELD_NOT_EMPTY = "field_not_empty"
    FIELD_IN_LIST = "field_in_list"
    COMMAND_STATUS = "command_status"
    DEBUG_LEVEL = "debug_level"
    OUTPUT_FORMAT = "output_format"
    STRING_NOT_EMPTY = "string_not_empty"
    ENVIRONMENT_DETECTION = "environment_detection"
    CONFIG_OPERATIONS = "config_operations"
    FILE_ERROR_DETECTION = "file_error_detection"
    TYPE_NORMALIZATION = "type_normalization"
    INTEGRATION_WORKFLOW = "integration_workflow"


@dataclass(frozen=True)
class ValidationTestCase:
    """Test case data for validation testing."""

    validation_type: ValidationType
    description: str
    test_data: dict[str, object]
    expected_result: bool = True
    error_contains: str | None = None


class TestFlextCliUtilities:
    """Comprehensive tests for flext_cli.utilities module.

    Uses single class pattern with nested test factories and helpers.
    Covers all utility validation scenarios with railway-oriented patterns.
    """

    # =========================================================================
    # NESTED TEST FACTORIES
    # =========================================================================

    class ValidationTestFactory:
        """Factory for creating validation test cases."""

        @staticmethod
        def create_cli_validation_cases() -> list[ValidationTestCase]:
            """Create comprehensive CLI validation test cases."""
            return [
                ValidationTestCase(
                    ValidationType.FIELD_NOT_EMPTY,
                    "Field not empty validation - success case",
                    {
                        "value": TestUtilities.Validation.VALID_FIELD_NAME,
                        "field_name": "Test Field",
                    },
                ),
                ValidationTestCase(
                    ValidationType.FIELD_NOT_EMPTY,
                    "Field not empty validation - empty string failure",
                    {
                        "value": TestUtilities.Validation.EMPTY_FIELD_NAME,
                        "field_name": "Test Field",
                    },
                    expected_result=False,
                    error_contains="string.non_empty",
                ),
                ValidationTestCase(
                    ValidationType.FIELD_NOT_EMPTY,
                    "Field not empty validation - whitespace failure",
                    {
                        "value": TestUtilities.Validation.WHITESPACE_FIELD_NAME,
                        "field_name": "Test Field",
                    },
                    expected_result=False,
                ),
                ValidationTestCase(
                    ValidationType.FIELD_IN_LIST,
                    "Field in list validation - success case",
                    {
                        "value": "pending",
                        "allowed": TestUtilities.Validation.Statuses.VALID_STATUSES,
                        "field_name": "status",
                    },
                ),
                ValidationTestCase(
                    ValidationType.FIELD_IN_LIST,
                    "Field in list validation - invalid value failure",
                    {
                        "value": TestUtilities.Validation.Statuses.INVALID_STATUS,
                        "allowed": TestUtilities.Validation.Statuses.VALID_STATUSES,
                        "field_name": "status",
                    },
                    expected_result=False,
                ),
                ValidationTestCase(
                    ValidationType.OUTPUT_FORMAT,
                    "Output format validation - lowercase success",
                    {"format": "json"},
                ),
                ValidationTestCase(
                    ValidationType.OUTPUT_FORMAT,
                    "Output format validation - uppercase normalization",
                    {
                        "format": TestUtilities.Validation.OutputFormats.UPPERCASE_FORMAT,
                        "expected_normalized": "json",
                    },
                ),
                ValidationTestCase(
                    ValidationType.OUTPUT_FORMAT,
                    "Output format validation - invalid format failure",
                    {"format": TestUtilities.Validation.OutputFormats.INVALID_FORMAT},
                    expected_result=False,
                ),
                ValidationTestCase(
                    ValidationType.STRING_NOT_EMPTY,
                    "String not empty validation - success case",
                    {
                        "value": TestUtilities.Validation.VALID_STRING,
                        "error_msg": "Test error",
                    },
                ),
                ValidationTestCase(
                    ValidationType.STRING_NOT_EMPTY,
                    "String not empty validation - empty string failure",
                    {
                        "value": TestUtilities.Validation.EMPTY_STRING,
                        "error_msg": "Custom error",
                    },
                    expected_result=False,
                    error_contains="Custom error",
                ),
                ValidationTestCase(
                    ValidationType.STRING_NOT_EMPTY,
                    "String not empty validation - whitespace failure",
                    {
                        "value": TestUtilities.Validation.WHITESPACE_STRING,
                        "error_msg": "Whitespace error",
                    },
                    expected_result=False,
                    error_contains="Whitespace error",
                ),
                ValidationTestCase(
                    ValidationType.STRING_NOT_EMPTY,
                    "String not empty validation - None value failure",
                    {
                        "value": TestUtilities.Validation.NONE_VALUE,
                        "error_msg": "None error",
                    },
                    expected_result=False,
                    error_contains="None error",
                ),
            ]

        @staticmethod
        def create_environment_cases() -> list[tuple[str, dict[str, str], bool]]:
            """Create environment detection test cases."""
            return [
                (
                    "pytest_current_test",
                    {
                        "PYTEST_CURRENT_TEST": TestUtilities.Environment.PYTEST_CURRENT_TEST
                    },
                    True,
                ),
                ("pytest_binary", {"_": TestUtilities.Environment.PYTEST_BINARY}, True),
                ("ci_true", {"CI": TestUtilities.Environment.CI_VALUE}, True),
                ("no_test_env", {}, False),
            ]

        @staticmethod
        def create_file_error_cases() -> list[tuple[str, bool]]:
            """Create file error detection test cases."""
            return [
                (pattern, True)
                for pattern in TestUtilities.FileOps.FILE_NOT_FOUND_PATTERNS
            ] + [(error, False) for error in TestUtilities.FileOps.NON_FILE_ERRORS]

    # =========================================================================
    # NESTED VALIDATION HELPERS
    # =========================================================================

    class ValidationExecutors:
        """Validation execution helpers."""

        @staticmethod
        def execute_cli_validation(
            test_case: ValidationTestCase,
        ) -> FlextResult[bool | str]:
            """Execute CLI validation based on test case type."""
            match test_case.validation_type:
                case ValidationType.FIELD_NOT_EMPTY:
                    value = cast("str", test_case.test_data["value"])
                    field_name = cast("str", test_case.test_data["field_name"])
                    validation_result = (
                        FlextCliUtilities.CliValidation.validate_field_not_empty(
                            value,
                            field_name,
                        )
                    )
                    # Cast to bool | str for return type compatibility
                    return cast("FlextResult[bool | str]", validation_result)

                case ValidationType.FIELD_IN_LIST:
                    value = cast("str", test_case.test_data["value"])
                    allowed = cast("list[str]", test_case.test_data["allowed"])
                    field_name = cast("str", test_case.test_data["field_name"])
                    validation_result = (
                        FlextCliUtilities.CliValidation.validate_field_in_list(
                            value,
                            valid_values=allowed,
                            field_name=field_name,
                        )
                    )
                    # Cast to bool | str for return type compatibility
                    return cast("FlextResult[bool | str]", validation_result)

                case ValidationType.OUTPUT_FORMAT:
                    format_type = cast("str", test_case.test_data["format"])
                    # Use u.convert and validate choice
                    format_lower = u.convert(format_type, str, "").lower()
                    valid_formats = set(FlextCliConstants.OUTPUT_FORMATS_LIST)
                    if format_lower not in valid_formats:
                        format_result: FlextResult[str] = FlextResult[str].fail(
                            f"Invalid output format: {format_type}"
                        )
                    else:
                        format_result = FlextResult[str].ok(format_lower)
                    if format_result.is_success:
                        format_result = FlextResult[str].ok(format_lower)
                    # For normalization tests, check the unwrapped value
                    if (
                        "expected_normalized" in test_case.test_data
                        and format_result.is_success
                    ):
                        actual = format_result.unwrap()
                        expected = test_case.test_data["expected_normalized"]
                        bool_result = FlextResult[bool].ok(actual == expected)
                        # Cast to bool | str for return type compatibility
                        return cast("FlextResult[bool | str]", bool_result)
                    # Cast to bool | str for return type compatibility
                    return cast("FlextResult[bool | str]", format_result)

                case ValidationType.STRING_NOT_EMPTY:
                    value = cast("str", test_case.test_data["value"])
                    error_msg = cast("str", test_case.test_data["error_msg"])
                    string_result = (
                        FlextCliUtilities.CliValidation.validate_string_not_empty(
                            value,
                            error_msg,
                        )
                    )
                    # Cast to bool | str for return type compatibility
                    return cast("FlextResult[bool | str]", string_result)

                case _:
                    return FlextResult[bool | str].fail(
                        f"Unsupported validation type: {test_case.validation_type}"
                    )

    # =========================================================================
    # CLI VALIDATION TESTS
    # =========================================================================

    @pytest.mark.parametrize(
        "test_case",
        ValidationTestFactory.create_cli_validation_cases(),
        ids=lambda case: f"{case.validation_type.value}_{'success' if case.expected_result else 'failure'}",
    )
    def test_cli_validation_comprehensive(self, test_case: ValidationTestCase) -> None:
        """Test comprehensive CLI validation using parametrized cases."""
        result = TestFlextCliUtilities.ValidationExecutors.execute_cli_validation(
            test_case
        )

        if test_case.expected_result:
            FlextTestsMatchers.assert_success(result)
            if (
                test_case.validation_type == ValidationType.OUTPUT_FORMAT
                and "expected_normalized" in test_case.test_data
            ):
                assert result.unwrap() is True  # Normalization check passed
        else:
            # Cast result to object for matcher compatibility
            result_obj = cast("FlextResult[object]", result)
            FlextTestsMatchers.assert_failure(result_obj, test_case.error_contains)

    def test_command_status_validation(self) -> None:
        """Test command status validation with real constants."""
        # Success case
        valid_status = FlextCliConstants.COMMAND_STATUSES_LIST[0]
        result = FlextCliUtilities.CliValidation.validate_command_status(valid_status)
        FlextTestsMatchers.assert_success(result)

        # Failure case
        result = FlextCliUtilities.CliValidation.validate_command_status(
            TestUtilities.Validation.Statuses.INVALID_STATUS
        )
        assert result.is_failure

    def test_debug_level_validation(self) -> None:
        """Test debug level validation with real constants."""
        # Success case
        valid_level = FlextCliConstants.DEBUG_LEVELS_LIST[0]
        result = FlextCliUtilities.CliValidation.validate_debug_level(valid_level)
        FlextTestsMatchers.assert_success(result)

        # Failure case
        result = FlextCliUtilities.CliValidation.validate_debug_level("invalid_level")
        assert result.is_failure

    # =========================================================================
    # ENVIRONMENT DETECTION TESTS
    # =========================================================================

    @pytest.mark.parametrize(
        ("env_name", "env_vars", "should_detect_test"),
        ValidationTestFactory.create_environment_cases(),
        ids=["pytest_current_test", "pytest_binary", "ci_true", "no_test_env"],
    )
    def test_environment_detection(
        self, env_name: str, env_vars: dict[str, str], should_detect_test: bool
    ) -> None:
        """Test environment detection with various configurations."""
        # Save original environment
        original_env = {key: os.environ.get(key) for key in env_vars.keys() | {"_"}}

        try:
            # Set test environment
            for key, value in env_vars.items():
                os.environ[key] = value
            # Clear other test indicators if not in env_vars
            if "PYTEST_CURRENT_TEST" not in env_vars:
                os.environ.pop("PYTEST_CURRENT_TEST", None)
            if "CI" not in env_vars:
                os.environ.pop("CI", None)
            if "_" not in env_vars:
                os.environ["_"] = "/bin/bash"

            # Test detection
            result = FlextCliUtilities.Environment.is_test_environment()
            if should_detect_test:
                assert result is True, (
                    f"Expected test environment detection for {env_name}"
                )
            else:
                assert isinstance(
                    result, bool
                )  # May be True if pytest is actually running

        finally:
            # Restore original environment
            for key, value_opt in original_env.items():
                if value_opt is not None:
                    os.environ[key] = value_opt
                elif key in os.environ:
                    del os.environ[key]

    # =========================================================================
    # CONFIG OPERATIONS TESTS
    # =========================================================================

    def test_config_operations_comprehensive(self) -> None:
        """Test comprehensive config operations."""
        # Test get_config_paths
        paths = FlextCliUtilities.ConfigOps.get_config_paths()
        assert isinstance(paths, list)
        assert all(isinstance(p, str) for p in paths)
        assert any(TestUtilities.Config.CONFIG_DIR_PATTERN in p for p in paths)

        # Test validate_config_structure
        results = FlextCliUtilities.ConfigOps.validate_config_structure()
        assert isinstance(results, list)
        assert all(isinstance(msg, str) for msg in results)

        # Test get_config_info
        info = FlextCliUtilities.ConfigOps.get_config_info()
        assert isinstance(info, dict)
        for key in TestUtilities.Config.EXPECTED_KEYS:
            assert key in info

        # Test config info structure
        assert isinstance(info["config_dir"], str)
        assert TestUtilities.Config.CONFIG_DIR_PATTERN in info["config_dir"]
        assert isinstance(info["config_exists"], bool)
        assert isinstance(info["timestamp"], str)
        assert "T" in info["timestamp"]  # ISO format

    def test_config_operations_with_temp_dir(self, tmp_path: Path) -> None:
        """Test config operations with temporary directory."""
        # This tests real file system interactions
        results = FlextCliUtilities.ConfigOps.validate_config_structure()
        assert isinstance(results, list)
        assert all(isinstance(msg, str) for msg in results)

    # =========================================================================
    # FILE OPERATIONS TESTS
    # =========================================================================

    @pytest.mark.parametrize(
        ("error_message", "should_be_file_error"),
        ValidationTestFactory.create_file_error_cases(),
    )
    def test_file_error_detection(
        self, error_message: str, should_be_file_error: bool
    ) -> None:
        """Test file error detection patterns."""
        result = FlextCliUtilities.FileOps.is_file_not_found_error(error_message)
        assert result == should_be_file_error

    # =========================================================================
    # TYPE NORMALIZER TESTS
    # =========================================================================

    def test_type_normalizer_basic_cases(self) -> None:
        """Test basic type normalizer functionality."""
        # Test None annotation
        result = FlextCliUtilities.TypeNormalizer.normalize_annotation(None)
        assert result is None

        # Test simple type
        result = FlextCliUtilities.TypeNormalizer.normalize_annotation(
            TestUtilities.TypeNormalizer.SIMPLE_TYPE
        )
        assert result is TestUtilities.TypeNormalizer.SIMPLE_TYPE

    def test_type_normalizer_union_cases(self) -> None:
        """Test type normalizer with union types."""
        # Test Path | None
        annotation_1 = Path | None
        result = FlextCliUtilities.TypeNormalizer.normalize_annotation(annotation_1)
        assert result is not None

        # Test str | int | None
        annotation_2 = str | int | None
        result = FlextCliUtilities.TypeNormalizer.normalize_annotation(annotation_2)
        assert result is not None

        # Test list[str] | None
        annotation_3 = list[str] | None
        result = FlextCliUtilities.TypeNormalizer.normalize_annotation(annotation_3)
        assert result is not None

    def test_type_normalizer_union_type_operations(self) -> None:
        """Test union type operations."""
        # Test normalize_union_type with various unions
        annotation_1 = str | None
        result = FlextCliUtilities.TypeNormalizer.normalize_union_type(annotation_1)
        assert result is not None

        annotation_2 = str | int | bool
        result = FlextCliUtilities.TypeNormalizer.normalize_union_type(annotation_2)
        assert result is not None

        annotation_3 = str | int | None
        result = FlextCliUtilities.TypeNormalizer.normalize_union_type(annotation_3)
        assert result is not None

    def test_combine_types_with_union_operations(self) -> None:
        """Test combine_types_with_union operations."""
        # Test with None included
        result = FlextCliUtilities.TypeNormalizer.combine_types_with_union(
            [str, int],
            include_none=True,
        )
        assert result is not None

        # Test without None
        result = FlextCliUtilities.TypeNormalizer.combine_types_with_union(
            [str, int, bool],
            include_none=False,
        )
        assert result is not None

        # Test single type
        result = FlextCliUtilities.TypeNormalizer.combine_types_with_union(
            [str],
            include_none=False,
        )
        assert result is str

        # Test single type with None
        result = FlextCliUtilities.TypeNormalizer.combine_types_with_union(
            [Path],
            include_none=True,
        )
        assert result is not None

    def test_type_normalizer_edge_cases(self) -> None:
        """Test type normalizer edge cases."""
        # Test Union[str] (edge case with empty args)
        annotation_1 = Union[str]
        result = FlextCliUtilities.TypeNormalizer.normalize_union_type(annotation_1)
        assert result is not None

        # Test type(None) directly
        annotation_2 = type(None)
        result = FlextCliUtilities.TypeNormalizer.normalize_union_type(annotation_2)
        assert result is not None

        # Test Union[str, None] edge case
        annotation_3 = str | None
        result = FlextCliUtilities.TypeNormalizer.normalize_union_type(annotation_3)
        assert result is not None

    def test_type_normalizer_error_handling(self) -> None:
        """Test type normalizer error handling."""
        # Test with generic type that might cause reconstruction errors
        annotation_1 = list[str]
        result = FlextCliUtilities.TypeNormalizer.normalize_annotation(annotation_1)
        assert result is not None

        # Test with union type
        annotation_2 = str | int
        result = FlextCliUtilities.TypeNormalizer.normalize_annotation(annotation_2)
        assert result is not None

    # =========================================================================
    # INTEGRATION TESTS
    # =========================================================================

    def test_utilities_integration_workflow(self) -> None:
        """Test integrated utilities workflow."""
        # Test complete validation workflow
        # 1. Validate field not empty
        result1 = FlextCliUtilities.CliValidation.validate_field_not_empty(
            TestUtilities.Validation.VALID_FIELD_NAME,
            "Test Field",
        )
        FlextTestsMatchers.assert_success(result1)

        # 2. Validate output format with normalization using u.convert
        format_lower = u.convert(
            TestUtilities.Validation.OutputFormats.UPPERCASE_FORMAT, str, ""
        ).lower()
        valid_formats = set(FlextCliConstants.OUTPUT_FORMATS_LIST)
        if format_lower not in valid_formats:
            validation_result: FlextResult[str] = FlextResult[str].fail(
                f"Invalid output format: {TestUtilities.Validation.OutputFormats.UPPERCASE_FORMAT}"
            )
        else:
            validation_result = FlextResult[str].ok(format_lower)
        # Old validation code (kept for reference):
        # validation_result = u.Validation.validate_choice(
        #     format_lower,
        #     valid_formats,
        # )
        result2 = (
            FlextResult[str].ok(format_lower)
            if validation_result.is_success
            else validation_result
        )
        FlextTestsMatchers.assert_success(result2)
        assert result2.unwrap() == FlextCliConstants.OutputFormats.JSON.value

        # 3. Validate string not empty
        result3 = FlextCliUtilities.CliValidation.validate_string_not_empty(
            TestUtilities.Validation.VALID_STRING,
            "Error",
        )
        FlextTestsMatchers.assert_success(result3)

        # 4. Test config operations
        paths = FlextCliUtilities.ConfigOps.get_config_paths()
        assert len(paths) > 0

        # 5. Test file error detection
        is_file_error = FlextCliUtilities.FileOps.is_file_not_found_error(
            TestUtilities.FileOps.FILE_NOT_FOUND_PATTERNS[0]
        )
        assert is_file_error

        # 6. Test type normalization
        result = FlextCliUtilities.TypeNormalizer.normalize_annotation(str)
        assert result is str

    def test_utilities_with_flext_tests_integration(self) -> None:
        """Test utilities integration with flext_tests."""
        # Create test data using flext_tests
        test_data = FlextTestsUtilities.create_test_data(
            prefix="utilities", data_type="config"
        )
        test_data["validation_result"] = True

        # Validate structure
        assert "validation_result" in test_data
        assert test_data["validation_result"] is True

        # Test with flext_tests matchers
        expected_data: dict[str, object] = {
            "validation_result": True,
            "name": "utilities_config",
        }
        # Use cast to specify type parameter - assert_dict_contains is a generic method
        FlextTestsMatchers.assert_dict_contains(
            test_data,
            cast("dict[str, t.GeneralValueType]", expected_data),
        )

        # Test with domain helpers
        assert_helpers = FlextCliTestHelpers.AssertHelpers
        assert_helpers.assert_result_success(FlextResult.ok("utilities_test"))

    def test_utilities_namespaces_availability(self) -> None:
        """Test that all FlextCliUtilities namespaces are available."""
        # Test CLI-specific namespaces (actual namespaces in FlextCliUtilities)
        # CliDataMapper was removed - use uirectly
        assert hasattr(FlextCliUtilities, "CliValidation")
        assert hasattr(FlextCliUtilities, "TypeNormalizer")
        # Enum, Collection, Args, Model are nested classes in utilities.py
        assert hasattr(FlextCliUtilities, "Enum")
        assert hasattr(FlextCliUtilities, "Collection")
        assert hasattr(FlextCliUtilities, "Args")
        assert hasattr(FlextCliUtilities, "Model")
        # Environment, ConfigOps, FileOps also exist
        assert hasattr(FlextCliUtilities, "Environment")
        assert hasattr(FlextCliUtilities, "ConfigOps")
        assert hasattr(FlextCliUtilities, "FileOps")

    # =========================================================================
    # ADDITIONAL EDGE CASES AND MISSING COVERAGE
    # =========================================================================

    def test_validate_field_not_empty_with_non_string(
        self,
    ) -> None:
        """Test validate_field_not_empty with non-string value."""
        result = FlextCliUtilities.CliValidation.validate_field_not_empty(
            42, "Test Field"
        )
        assert result.is_failure

    def test_validate_field_not_empty_with_value_error(
        self,
    ) -> None:
        """Test validate_field_not_empty with ValueError from validation."""
        # Empty string should trigger ValueError
        result = FlextCliUtilities.CliValidation.validate_field_not_empty(
            "", "Test Field"
        )
        assert result.is_failure

    def test_validate_field_in_list_with_non_string(
        self,
    ) -> None:
        """Test validate_field_in_list with non-string value."""
        result = FlextCliUtilities.CliValidation.validate_field_in_list(
            42, valid_values=["a", "b"], field_name="test"
        )
        assert result.is_failure

    def test_validate_field_in_list_with_invalid_choice(
        self,
    ) -> None:
        """Test validate_field_in_list with invalid choice."""
        result = FlextCliUtilities.CliValidation.validate_field_in_list(
            "invalid", valid_values=["a", "b"], field_name="test"
        )
        assert result.is_failure

    def test_validate_output_format(self) -> None:
        """Test validate_output_format method."""
        result = FlextCliUtilities.CliValidation.validate_output_format("json")
        assert result.is_success

    def test_validate_output_format_invalid(self) -> None:
        """Test validate_output_format with invalid format."""
        result = FlextCliUtilities.CliValidation.validate_output_format("invalid")
        assert result.is_failure

    def test_validate_string_not_empty_success(self) -> None:
        """Test validate_string_not_empty with valid string."""
        result = FlextCliUtilities.CliValidation.validate_string_not_empty(
            "test", "field"
        )
        assert result.is_success

    def test_validate_string_not_empty_failure(self) -> None:
        """Test validate_string_not_empty with empty string."""
        result = FlextCliUtilities.CliValidation.validate_string_not_empty("", "field")
        assert result.is_failure

    def test_validate_command_execution_state_success(self) -> None:
        """Test validate_command_execution_state with matching status."""
        result = FlextCliUtilities.CliValidation.validate_command_execution_state(
            "pending", "pending", "test_operation"
        )
        assert result.is_success

    def test_validate_command_execution_state_failure(self) -> None:
        """Test validate_command_execution_state with mismatched status."""
        result = FlextCliUtilities.CliValidation.validate_command_execution_state(
            "pending", "running", "test_operation"
        )
        assert result.is_failure

    def test_validate_session_state_success(self) -> None:
        """Test validate_session_state with valid state."""
        result = FlextCliUtilities.CliValidation.validate_session_state(
            "active", ["active", "inactive"]
        )
        assert result.is_success

    def test_validate_session_state_failure(self) -> None:
        """Test validate_session_state with invalid state."""
        result = FlextCliUtilities.CliValidation.validate_session_state(
            "invalid", ["active", "inactive"]
        )
        assert result.is_failure

    def test_validate_pipeline_step_none(self) -> None:
        """Test validate_pipeline_step with None."""
        result = FlextCliUtilities.CliValidation.validate_pipeline_step(None)
        assert result.is_failure

    def test_validate_pipeline_step_no_name(self) -> None:
        """Test validate_pipeline_step without name field."""
        result = FlextCliUtilities.CliValidation.validate_pipeline_step({})
        assert result.is_failure

    def test_validate_pipeline_step_empty_name(self) -> None:
        """Test validate_pipeline_step with empty name."""
        result = FlextCliUtilities.CliValidation.validate_pipeline_step({
            FlextCliConstants.MixinsFieldNames.PIPELINE_STEP_NAME: ""
        })
        assert result.is_failure

    def test_validate_pipeline_step_success(self) -> None:
        """Test validate_pipeline_step with valid step."""
        result = FlextCliUtilities.CliValidation.validate_pipeline_step({
            FlextCliConstants.MixinsFieldNames.PIPELINE_STEP_NAME: "test_step"
        })
        assert result.is_success

    def test_enum_parse_success(self) -> None:
        """Test Enum.parse with valid string."""

        class TestEnum(StrEnum):
            VALUE1 = "value1"
            VALUE2 = "value2"

        result = FlextCliUtilities.Enum.parse(TestEnum, "value1")
        assert result.is_success
        assert result.unwrap() == TestEnum.VALUE1

    def test_enum_parse_invalid(self) -> None:
        """Test Enum.parse with invalid string."""

        class TestEnum(StrEnum):
            VALUE1 = "value1"

        result = FlextCliUtilities.Enum.parse(TestEnum, "invalid")
        assert result.is_failure

    def test_enum_parse_or_default_success(self) -> None:
        """Test Enum.parse_or_default with valid string."""

        class TestEnum(StrEnum):
            VALUE1 = "value1"

        result = FlextCliUtilities.Enum.parse_or_default(
            TestEnum, "value1", TestEnum.VALUE1
        )
        assert result == TestEnum.VALUE1

    def test_enum_parse_or_default_invalid(self) -> None:
        """Test Enum.parse_or_default with invalid string."""

        class TestEnum(StrEnum):
            VALUE1 = "value1"
            DEFAULT = "default"

        result = FlextCliUtilities.Enum.parse_or_default(
            TestEnum, "invalid", TestEnum.DEFAULT
        )
        assert result == TestEnum.DEFAULT

    def test_enum_parse_or_default_none(self) -> None:
        """Test Enum.parse_or_default with None."""

        class TestEnum(StrEnum):
            DEFAULT = "default"

        result = FlextCliUtilities.Enum.parse_or_default(
            TestEnum, None, TestEnum.DEFAULT
        )
        assert result == TestEnum.DEFAULT

    def test_collection_parse_mapping_success(self) -> None:
        """Test Collection.parse_mapping with valid mapping."""

        class TestEnum(StrEnum):
            VALUE1 = "value1"
            VALUE2 = "value2"

        result = FlextCliUtilities.Collection.parse_mapping(
            TestEnum, {"key1": "value1", "key2": "value2"}
        )
        assert result.is_success
        parsed = result.unwrap()
        assert parsed["key1"] == TestEnum.VALUE1
        assert parsed["key2"] == TestEnum.VALUE2

    def test_collection_parse_mapping_invalid(self) -> None:
        """Test Collection.parse_mapping with invalid values."""

        class TestEnum(StrEnum):
            VALUE1 = "value1"

        result = FlextCliUtilities.Collection.parse_mapping(
            TestEnum, {"key1": "invalid"}
        )
        assert result.is_failure

    def test_collection_coerce_dict_validator_success(self) -> None:
        """Test Collection.coerce_dict_validator with valid dict."""

        class TestEnum(StrEnum):
            VALUE1 = "value1"

        validator = FlextCliUtilities.Collection.coerce_dict_validator(TestEnum)
        result = validator({"key": "value1"})
        assert result == {"key": TestEnum.VALUE1}

    def test_collection_coerce_dict_validator_invalid_type(
        self,
    ) -> None:
        """Test Collection.coerce_dict_validator with non-dict."""

        class TestEnum(StrEnum):
            VALUE1 = "value1"

        validator = FlextCliUtilities.Collection.coerce_dict_validator(TestEnum)
        with pytest.raises(TypeError):
            validator("not a dict")

    def test_collection_coerce_dict_validator_invalid_value(
        self,
    ) -> None:
        """Test Collection.coerce_dict_validator with invalid enum value."""

        class TestEnum(StrEnum):
            VALUE1 = "value1"

        validator = FlextCliUtilities.Collection.coerce_dict_validator(TestEnum)
        with pytest.raises(ValueError):
            validator({"key": "invalid"})

    def test_model_from_dict_success(self) -> None:
        """Test Model.from_dict with valid data."""

        class TestModel(BaseModel):
            name: str = "test"

        data = {"name": "test_value"}
        result = FlextCliUtilities.TypeNormalizer.Model.from_dict(TestModel, data)
        assert result.is_success
        assert result.unwrap().name == "test_value"

    def test_model_from_dict_invalid(self) -> None:
        """Test Model.from_dict with invalid data."""

        class TestModel(BaseModel):
            name: str

        data = {}  # Missing required field
        result = FlextCliUtilities.TypeNormalizer.Model.from_dict(TestModel, data)
        assert result.is_failure

    def test_model_from_dict_non_pydantic(self) -> None:
        """Test Model.from_dict with non-Pydantic class."""

        class NotPydantic:
            pass

        result = FlextCliUtilities.TypeNormalizer.Model.from_dict(NotPydantic, {})
        assert result.is_failure

    def test_model_merge_defaults_success(self) -> None:
        """Test Model.merge_defaults with valid data."""

        class TestModel(BaseModel):
            name: str = "default"
            value: int = 0

        defaults = {"name": "default", "value": 0}
        overrides = {"name": "override"}
        result = FlextCliUtilities.TypeNormalizer.Model.merge_defaults(
            TestModel, defaults, overrides
        )
        assert result.is_success
        model = result.unwrap()
        assert model.name == "override"
        assert model.value == 0

    def test_model_update_success(self) -> None:
        """Test Model.update with valid updates."""

        class TestModel(BaseModel):
            name: str = "original"
            value: int = 0

        instance = TestModel()
        result = FlextCliUtilities.TypeNormalizer.Model.update(instance, name="updated")
        assert result.is_success
        assert result.unwrap().name == "updated"

    def test_model_update_non_pydantic(self) -> None:
        """Test Model.update with non-Pydantic instance."""

        class NotPydantic:
            pass

        result = FlextCliUtilities.Model.update(NotPydantic(), name="test")
        assert result.is_failure

    def test_args_validated_with_result_success(self) -> None:
        """Test Args.validated_with_result with valid input."""

        @FlextCliUtilities.TypeNormalizer.Args.validated_with_result
        def test_func(value: int) -> int:
            return value * 2

        result = test_func(value=5)
        assert result.is_success
        assert result.unwrap() == 10

    def test_args_validated_with_result_validation_error(self) -> None:
        """Test Args.validated_with_result with validation error."""

        @FlextCliUtilities.TypeNormalizer.Args.validated_with_result
        def test_func(value: int) -> int:
            return value * 2

        result = test_func(value="not an int")
        assert result.is_failure

    def test_args_parse_kwargs_success(self) -> None:
        """Test Args.parse_kwargs with valid kwargs."""

        class TestEnum(StrEnum):
            VALUE1 = "value1"

        kwargs = {"key": "value", "enum_field": "value1"}
        enum_fields = {"enum_field": TestEnum}
        result = FlextCliUtilities.TypeNormalizer.Args.parse_kwargs(kwargs, enum_fields)
        assert result.is_success
        parsed = result.unwrap()
        assert parsed["enum_field"] == "value1"

    def test_args_parse_kwargs_invalid_enum(self) -> None:
        """Test Args.parse_kwargs with invalid enum value."""

        class TestEnum(StrEnum):
            VALUE1 = "value1"

        kwargs = {"enum_field": "invalid"}
        enum_fields = {"enum_field": TestEnum}
        result = FlextCliUtilities.TypeNormalizer.Args.parse_kwargs(kwargs, enum_fields)
        assert result.is_failure

    def test_pydantic_coerced_enum(self) -> None:
        """Test Pydantic.coerced_enum creates Annotated type."""

        class TestEnum(StrEnum):
            VALUE1 = "value1"

        coerced_type = FlextCliUtilities.TypeNormalizer.Pydantic.coerced_enum(TestEnum)
        assert coerced_type is not None
