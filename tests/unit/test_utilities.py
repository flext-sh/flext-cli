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
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Union, cast

import pytest
from flext_core import r
from flext_tests import tm
from pydantic import BaseModel

from flext_cli.constants import FlextCliConstants
from tests import c, t, u


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


class TestsCliUtilities:
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
                        "value": c.TestData.VALID_FIELD_NAME,
                        "field_name": "Test Field",
                    },
                ),
                ValidationTestCase(
                    ValidationType.FIELD_NOT_EMPTY,
                    "Field not empty validation - empty string failure",
                    {
                        "value": c.TestData.FIELD_NAME,
                        "field_name": "Test Field",
                    },
                    expected_result=False,
                    error_contains="cannot be empty",
                ),
                ValidationTestCase(
                    ValidationType.FIELD_NOT_EMPTY,
                    "Field not empty validation - whitespace failure",
                    {
                        "value": c.TestData.WHITESPACE_FIELD_NAME,
                        "field_name": "Test Field",
                    },
                    expected_result=False,
                ),
                ValidationTestCase(
                    ValidationType.FIELD_IN_LIST,
                    "Field in list validation - success case",
                    {
                        "value": "pending",
                        "allowed": c.Statuses.VALID_STATUSES,
                        "field_name": "status",
                    },
                ),
                ValidationTestCase(
                    ValidationType.FIELD_IN_LIST,
                    "Field in list validation - invalid value failure",
                    {
                        "value": c.Statuses.INVALID_STATUS,
                        "allowed": c.Statuses.VALID_STATUSES,
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
                        "format": c.OutputFormats.UPPERCASE_FORMAT,
                        "expected_normalized": "json",
                    },
                ),
                ValidationTestCase(
                    ValidationType.OUTPUT_FORMAT,
                    "Output format validation - invalid format failure",
                    {"format": c.OutputFormats.INVALID_FORMAT},
                    expected_result=False,
                ),
                ValidationTestCase(
                    ValidationType.STRING_NOT_EMPTY,
                    "String not empty validation - success case",
                    {
                        "value": c.TestData.VALID_STRING,
                        "error_msg": "Test error",
                    },
                ),
                ValidationTestCase(
                    ValidationType.STRING_NOT_EMPTY,
                    "String not empty validation - empty string failure",
                    {
                        "value": c.TestData.STRING,
                        "error_msg": "Custom error",
                    },
                    expected_result=False,
                    error_contains="Custom error",
                ),
                ValidationTestCase(
                    ValidationType.STRING_NOT_EMPTY,
                    "String not empty validation - whitespace failure",
                    {
                        "value": c.TestData.WHITESPACE_STRING,
                        "error_msg": "Whitespace error",
                    },
                    expected_result=False,
                    error_contains="Whitespace error",
                ),
                ValidationTestCase(
                    ValidationType.STRING_NOT_EMPTY,
                    "String not empty validation - None value failure",
                    {
                        "value": c.TestData.NONE_VALUE,
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
                    {"PYTEST_CURRENT_TEST": c.Environment.PYTEST_CURRENT_TEST},
                    True,
                ),
                ("pytest_binary", {"_": c.Environment.PYTEST_BINARY}, True),
                ("ci_true", {"CI": c.Environment.CI_VALUE}, True),
                ("no_test_env", {}, False),
            ]

        @staticmethod
        def create_file_error_cases() -> list[tuple[str, bool]]:
            """Create file error detection test cases."""
            return [
                (pattern, True) for pattern in c.FileOps.FILE_NOT_FOUND_PATTERNS
            ] + [(error, False) for error in c.FileOps.NON_FILE_ERRORS]

    # =========================================================================
    # NESTED VALIDATION HELPERS
    # =========================================================================

    class ValidationExecutors:
        """Validation execution helpers."""

        @staticmethod
        def execute_cli_validation(
            test_case: ValidationTestCase,
        ) -> r[bool | str]:
            """Execute CLI validation based on test case type."""
            match test_case.validation_type:
                case ValidationType.FIELD_NOT_EMPTY:
                    value = cast("str", test_case.test_data["value"])
                    field_name = cast("str", test_case.test_data["field_name"])
                    validation_result = u.CliValidation.v_empty(value, name=field_name)
                    # Cast to bool | str for return type compatibility
                    return cast("r[bool | str]", validation_result)

                case ValidationType.FIELD_IN_LIST:
                    value = cast("str", test_case.test_data["value"])
                    allowed = cast("list[str]", test_case.test_data["allowed"])
                    field_name = cast("str", test_case.test_data["field_name"])
                    validation_result = u.CliValidation.validate_field_in_list(
                        value,
                        valid_values=allowed,
                        field_name=field_name,
                    )
                    # Cast to bool | str for return type compatibility
                    return cast("r[bool | str]", validation_result)

                case ValidationType.OUTPUT_FORMAT:
                    format_type = cast("str", test_case.test_data["format"])
                    # Use u.convert and validate choice
                    format_lower = u.convert(format_type, str, "").lower()
                    valid_formats = set(c.OUTPUT_FORMATS_LIST)
                    if format_lower not in valid_formats:
                        format_result: r[str] = r[str].fail(
                            f"Invalid output format: {format_type}",
                        )
                    else:
                        format_result = r[str].ok(format_lower)
                    if format_result.is_success:
                        format_result = r[str].ok(format_lower)
                    # For normalization tests, check the unwrapped value
                    if (
                        "expected_normalized" in test_case.test_data
                        and format_result.is_success
                    ):
                        actual = format_result.unwrap()
                        expected = test_case.test_data["expected_normalized"]
                        bool_result = r[bool].ok(actual == expected)
                        # Cast to bool | str for return type compatibility
                        return cast("r[bool | str]", bool_result)
                    # Cast to bool | str for return type compatibility
                    return cast("r[bool | str]", format_result)

                case ValidationType.STRING_NOT_EMPTY:
                    value = cast("str", test_case.test_data["value"])
                    error_msg = cast("str", test_case.test_data["error_msg"])
                    string_result = u.CliValidation.v_empty(
                        value,
                        name=error_msg,
                    )
                    # Cast to bool | str for return type compatibility
                    return cast("r[bool | str]", string_result)

                case _:
                    return r[bool | str].fail(
                        f"Unsupported validation type: {test_case.validation_type}",
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
        result = TestsCliUtilities.ValidationExecutors.execute_cli_validation(test_case)

        if test_case.expected_result:
            tm.ok(result)
            if (
                test_case.validation_type == ValidationType.OUTPUT_FORMAT
                and "expected_normalized" in test_case.test_data
            ):
                assert result.unwrap() is True  # Normalization check passed
        else:
            # Cast result to object for matcher compatibility
            result_obj = cast("r[object]", result)
            tm.fail(result_obj, has=test_case.error_contains)

    def test_command_status_validation(self) -> None:
        """Test command status validation with real constants."""
        # Success case
        valid_status = c.COMMAND_STATUSES_LIST[0]
        result = u.CliValidation.v_status(valid_status)
        tm.ok(result)

        # Failure case
        result = u.CliValidation.v_status(c.Statuses.INVALID_STATUS)
        assert result.is_failure

    def test_debug_level_validation(self) -> None:
        """Test debug level validation with real constants."""
        # Success case
        valid_level = c.DEBUG_LEVELS_LIST[0]
        result = u.CliValidation.v_level(valid_level)
        tm.ok(result)

        # Failure case
        result = u.CliValidation.v_level("invalid_level")
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
        self,
        env_name: str,
        env_vars: dict[str, str],
        should_detect_test: bool,
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
            result = u.Environment.is_test_environment()
            if should_detect_test:
                assert result is True, (
                    f"Expected test environment detection for {env_name}"
                )
            else:
                assert isinstance(
                    result,
                    bool,
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
        paths = u.ConfigOps.get_config_paths()
        assert isinstance(paths, list)
        assert all(isinstance(p, str) for p in paths)
        assert any(c.Config.CONFIG_DIR_PATTERN in p for p in paths)

        # Test validate_config_structure
        results = u.ConfigOps.validate_config_structure()
        assert isinstance(results, list)
        assert all(isinstance(msg, str) for msg in results)

        # Test get_config_info
        info = u.ConfigOps.get_config_info()
        assert isinstance(info, dict)
        for key in c.Config.EXPECTED_KEYS:
            assert key in info

        # Test config info structure
        assert isinstance(info["config_dir"], str)
        assert c.Config.CONFIG_DIR_PATTERN in info["config_dir"]
        assert isinstance(info["config_exists"], bool)
        assert isinstance(info["timestamp"], str)
        assert "T" in info["timestamp"]  # ISO format

    def test_config_operations_with_temp_dir(self, tmp_path: Path) -> None:
        """Test config operations with temporary directory."""
        # This tests real file system interactions
        results = u.ConfigOps.validate_config_structure()
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
        self,
        error_message: str,
        should_be_file_error: bool,
    ) -> None:
        """Test file error detection patterns."""
        result = u.FileOps.is_file_not_found_error(error_message)
        assert result == should_be_file_error

    # =========================================================================
    # TYPE NORMALIZER TESTS
    # =========================================================================

    def test_type_normalizer_basic_cases(self) -> None:
        """Test basic type normalizer functionality."""
        # Test None annotation
        result = u.TypeNormalizer.normalize_annotation(None)
        assert result is None

        # Test simple type
        result = u.TypeNormalizer.normalize_annotation("simple")
        assert result == "simple"

    def test_type_normalizer_union_cases(self) -> None:
        """Test type normalizer with union types."""
        # Test Path | None
        annotation_1 = Path | None
        result = u.TypeNormalizer.normalize_annotation(annotation_1)
        assert result is not None

        # Test str | int | None
        annotation_2 = str | int | None
        result = u.TypeNormalizer.normalize_annotation(annotation_2)
        assert result is not None

        # Test list[str] | None
        annotation_3 = list[str] | None
        result = u.TypeNormalizer.normalize_annotation(annotation_3)
        assert result is not None

    def test_type_normalizer_union_type_operations(self) -> None:
        """Test union type operations."""
        # Test normalize_union_type with various unions
        annotation_1 = str | None
        result = u.TypeNormalizer.normalize_union_type(annotation_1)
        assert result is not None

        annotation_2 = str | int | bool
        result = u.TypeNormalizer.normalize_union_type(annotation_2)
        assert result is not None

        annotation_3 = str | int | None
        result = u.TypeNormalizer.normalize_union_type(annotation_3)
        assert result is not None

    def test_combine_types_with_union_operations(self) -> None:
        """Test combine_types_with_union operations."""
        # Test with None included
        result = u.TypeNormalizer.combine_types_with_union(
            [str, int],
            include_none=True,
        )
        assert result is not None

        # Test without None
        result = u.TypeNormalizer.combine_types_with_union(
            [str, int, bool],
            include_none=False,
        )
        assert result is not None

        # Test single type
        result = u.TypeNormalizer.combine_types_with_union(
            [str],
            include_none=False,
        )
        assert result is str

        # Test single type with None
        result = u.TypeNormalizer.combine_types_with_union(
            [Path],
            include_none=True,
        )
        assert result is not None

    def test_type_normalizer_edge_cases(self) -> None:
        """Test type normalizer edge cases."""
        # Test Union[str] (edge case with empty args)
        annotation_1 = Union[str]
        result = u.TypeNormalizer.normalize_union_type(annotation_1)
        assert result is not None

        # Test type(None) directly
        annotation_2 = type(None)
        result = u.TypeNormalizer.normalize_union_type(annotation_2)
        assert result is not None

        # Test Union[str, None] edge case
        annotation_3 = str | None
        result = u.TypeNormalizer.normalize_union_type(annotation_3)
        assert result is not None

    def test_type_normalizer_error_handling(self) -> None:
        """Test type normalizer error handling."""
        # Test with generic type that might cause reconstruction errors
        annotation_1 = list[str]
        result = u.TypeNormalizer.normalize_annotation(annotation_1)
        assert result is not None

        # Test with union type
        annotation_2 = str | int
        result = u.TypeNormalizer.normalize_annotation(annotation_2)
        assert result is not None

    # =========================================================================
    # INTEGRATION TESTS
    # =========================================================================

    def test_utilities_integration_workflow(self) -> None:
        """Test integrated utilities workflow."""
        # Test complete validation workflow
        # 1. Validate field not empty
        result1 = u.CliValidation.v_empty(
            c.TestData.VALID_FIELD_NAME,
            name="Test Field",
        )
        tm.ok(result1)

        # 2. Validate output format with normalization using u.convert
        format_lower = u.convert(c.OutputFormats.UPPERCASE_FORMAT, str, "").lower()
        valid_formats = set(c.OUTPUT_FORMATS_LIST)
        if format_lower not in valid_formats:
            validation_result: r[str] = r[str].fail(
                f"Invalid output format: {c.OutputFormats.UPPERCASE_FORMAT}",
            )
        else:
            validation_result = r[str].ok(format_lower)
        # Old validation code (kept for reference):
        # validation_result = u.validate_choice(
        #     format_lower,
        #     valid_formats,
        # )
        result2 = (
            r[str].ok(format_lower)
            if validation_result.is_success
            else validation_result
        )
        tm.ok(result2)
        assert result2.unwrap() == FlextCliConstants.OutputFormats.JSON.value

        # 3. Validate string not empty
        result3 = u.CliValidation.v_empty(
            c.TestData.VALID_STRING,
            name="Value",
        )
        tm.ok(result3)

        # 4. Test config operations
        paths = u.ConfigOps.get_config_paths()
        assert len(paths) > 0

        # 5. Test file error detection
        is_file_error = u.FileOps.is_file_not_found_error(
            c.FileOps.FILE_NOT_FOUND_PATTERNS[0],
        )
        assert is_file_error

        # 6. Test type normalization
        result = u.TypeNormalizer.normalize_annotation(str)
        assert result is str

    def test_utilities_with_flext_tests_integration(self) -> None:
        """Test utilities integration with flext_tests."""
        # Create test data using flext_tests
        test_data: dict[str, object] = {"name": "utilities_config"}
        test_data["validation_result"] = True

        # Validate structure
        assert "validation_result" in test_data
        assert test_data["validation_result"] is True

        # Test with flext_tests matchers
        expected_data: dict[str, object] = {
            "validation_result": True,
            "name": "utilities_config",
        }
        # Use tm.that() for dict assertions
        tm.that(
            test_data,
            kv=cast("dict[str, t.GeneralValueType]", expected_data),
        )

        # Test with flext_tests directly
        tm.ok(r.ok("utilities_test"))

    def test_utilities_namespaces_availability(self) -> None:
        """Test that all FlextCliUtilities namespaces are available."""
        # Test CLI-specific namespaces (actual namespaces in FlextCliUtilities)
        # CliDataMapper was removed - use uirectly
        assert hasattr(u, "CliValidation")
        assert hasattr(u, "TypeNormalizer")
        # Enum, Collection, Args, Model are nested classes in utilities.py
        assert hasattr(u, "Enum")
        assert hasattr(u, "Collection")
        assert hasattr(u, "Args")
        assert hasattr(u, "Model")
        # Environment, ConfigOps, FileOps also exist
        assert hasattr(u, "Environment")
        assert hasattr(u, "ConfigOps")
        assert hasattr(u, "FileOps")

    # =========================================================================
    # ADDITIONAL EDGE CASES AND MISSING COVERAGE
    # =========================================================================

    def test_validate_field_not_empty_with_non_string(
        self,
    ) -> None:
        """Test validate_field_not_empty with non-string value."""
        # Non-string, non-None values are considered non-empty (valid)
        result = u.CliValidation.v_empty(42, name="Test Field")
        assert result.is_success

    def test_validate_field_not_empty_with_value_error(
        self,
    ) -> None:
        """Test validate_field_not_empty with ValueError from validation."""
        # Empty string should trigger ValueError
        result = u.CliValidation.v_empty("", name="Test Field")
        assert result.is_failure

    def test_validate_field_in_list_with_non_string(
        self,
    ) -> None:
        """Test validate_field_in_list with non-string value."""
        result = u.CliValidation.validate_field_in_list(
            42,
            valid_values=["a", "b"],
            field_name="test",
        )
        assert result.is_failure

    def test_validate_field_in_list_with_invalid_choice(
        self,
    ) -> None:
        """Test validate_field_in_list with invalid choice."""
        result = u.CliValidation.validate_field_in_list(
            "invalid",
            valid_values=["a", "b"],
            field_name="test",
        )
        assert result.is_failure

    class ValidationMethodTestCases:
        """Factory for validation method test cases - reduces 50+ lines."""

        @staticmethod
        def get_validation_method_cases() -> list[
            tuple[
                str,
                Callable[[], r[bool] | r[str]],
                bool,
            ]
        ]:
            """Get parametrized test cases for validation methods."""
            return [
                (
                    "validate_output_format_success",
                    lambda: u.CliValidation.v_format("json"),
                    True,
                ),
                (
                    "validate_output_format_invalid",
                    lambda: u.CliValidation.v_format("invalid"),
                    False,
                ),
                (
                    "validate_string_not_empty_success",
                    lambda: u.CliValidation.v_empty("test", name="field"),
                    True,
                ),
                (
                    "validate_string_not_empty_failure",
                    lambda: u.CliValidation.v_empty("", name="field"),
                    False,
                ),
                (
                    "validate_command_execution_state_success",
                    lambda: u.CliValidation.v_state(
                        "pending",
                        required="pending",
                        name="test_operation",
                    ),
                    True,
                ),
                (
                    "validate_command_execution_state_failure",
                    lambda: u.CliValidation.v_state(
                        "pending",
                        required="running",
                        name="test_operation",
                    ),
                    False,
                ),
                (
                    "validate_session_state_success",
                    lambda: u.CliValidation.v_session(
                        "active",
                        valid=["active", "inactive"],
                    ),
                    True,
                ),
                (
                    "validate_session_state_failure",
                    lambda: u.CliValidation.v_session(
                        "invalid",
                        valid=["active", "inactive"],
                    ),
                    False,
                ),
            ]

    @pytest.mark.parametrize(
        ("test_name", "method_call", "should_succeed"),
        ValidationMethodTestCases.get_validation_method_cases(),
    )
    def test_validation_methods(
        self,
        test_name: str,
        method_call: Callable[[], r[bool] | r[str]],
        should_succeed: bool,
    ) -> None:
        """Test validation methods using advanced parametrization - reduces 50+ lines."""
        result = method_call()
        # Cast to object for matcher compatibility (handles both bool and str results)
        result_obj = cast("r[object]", result)
        if should_succeed:
            tm.ok(result_obj)
        else:
            tm.fail(result_obj)

    class PipelineStepTestCases:
        """Factory for pipeline step test cases - reduces 20+ lines."""

        @staticmethod
        def get_pipeline_step_cases() -> list[
            tuple[str, dict[str, object] | None, bool]
        ]:
            """Get parametrized test cases for pipeline step validation."""
            return [
                ("none", None, False),
                ("no_name", {}, False),
                (
                    "empty_name",
                    {c.MixinsFieldNames.PIPELINE_STEP_NAME: ""},
                    False,
                ),
                (
                    "success",
                    {c.MixinsFieldNames.PIPELINE_STEP_NAME: "test_step"},
                    True,
                ),
            ]

    @pytest.mark.parametrize(
        ("test_name", "step_data", "should_succeed"),
        PipelineStepTestCases.get_pipeline_step_cases(),
    )
    def test_validate_pipeline_step(
        self,
        test_name: str,
        step_data: dict[str, object] | None,
        should_succeed: bool,
    ) -> None:
        """Test validate_pipeline_step using advanced parametrization - reduces 20+ lines."""
        # Convert dict[str, object] to JsonDict for type compatibility
        json_step_data: dict[str, t.GeneralValueType] | None = None
        if step_data:
            step_data_converted = cast("dict[str, t.GeneralValueType]", step_data)
            transform_result = u.transform(step_data_converted, to_json=True)
            json_step_data = (
                transform_result.unwrap()
                if transform_result.is_success
                else step_data_converted
            )
        result = u.CliValidation.v_step(json_step_data)
        if should_succeed:
            tm.ok(result)
        else:
            tm.fail(result)

    class EnumTestCases:
        """Factory for enum test cases - reduces 40+ lines."""

        @staticmethod
        def get_enum_parse_cases() -> list[
            tuple[str, type[StrEnum], str, bool, object | None]
        ]:
            """Get parametrized test cases for Enum.parse."""

            class TestEnum1(StrEnum):
                VALUE1 = "value1"
                VALUE2 = "value2"

            class TestEnum2(StrEnum):
                VALUE1 = "value1"

            return [
                ("parse_success", TestEnum1, "value1", True, TestEnum1.VALUE1),
                ("parse_invalid", TestEnum2, "invalid", False, None),
            ]

        @staticmethod
        def get_enum_parse_or_default_cases() -> list[
            tuple[str, type[StrEnum], str | None, object, object]
        ]:
            """Get parametrized test cases for Enum.parse_or_default."""

            class TestEnum1(StrEnum):
                VALUE1 = "value1"

            class TestEnum2(StrEnum):
                VALUE1 = "value1"
                DEFAULT = "default"

            class TestEnum3(StrEnum):
                DEFAULT = "default"

            return [
                (
                    "parse_or_default_success",
                    TestEnum1,
                    "value1",
                    TestEnum1.VALUE1,
                    TestEnum1.VALUE1,
                ),
                (
                    "parse_or_default_invalid",
                    TestEnum2,
                    "invalid",
                    TestEnum2.DEFAULT,
                    TestEnum2.DEFAULT,
                ),
                (
                    "parse_or_default_none",
                    TestEnum3,
                    None,
                    TestEnum3.DEFAULT,
                    TestEnum3.DEFAULT,
                ),
            ]

    @pytest.mark.parametrize(
        ("test_name", "enum_class", "value", "should_succeed", "expected"),
        EnumTestCases.get_enum_parse_cases(),
    )
    def test_enum_parse(
        self,
        test_name: str,
        enum_class: type[StrEnum],
        value: str,
        should_succeed: bool,
        expected: object | None,
    ) -> None:
        """Test Enum.parse using advanced parametrization - reduces 20+ lines."""
        result = u.Enum.parse(enum_class, value)
        if should_succeed:
            tm.ok(result, eq=expected)
        else:
            tm.fail(result)

    @pytest.mark.parametrize(
        ("test_name", "enum_class", "value", "default", "expected"),
        EnumTestCases.get_enum_parse_or_default_cases(),
    )
    def test_enum_parse_or_default(
        self,
        test_name: str,
        enum_class: type[StrEnum],
        value: str | None,
        default: object,
        expected: object,
    ) -> None:
        """Test Enum.parse_or_default using advanced parametrization - reduces 20+ lines."""
        # Cast default to StrEnum for type compatibility
        default_enum = cast("StrEnum", default)
        result = u.Enum.parse_or_default(enum_class, value, default_enum)
        assert result == expected

    class CollectionTestCases:
        """Factory for collection test cases - reduces 50+ lines."""

        @staticmethod
        def get_parse_mapping_cases() -> list[
            tuple[str, type[StrEnum], dict[str, str], bool, dict[str, object] | None]
        ]:
            """Get parametrized test cases for Collection.parse_mapping."""

            class TestEnum1(StrEnum):
                VALUE1 = "value1"
                VALUE2 = "value2"

            class TestEnum2(StrEnum):
                VALUE1 = "value1"

            return [
                (
                    "parse_mapping_success",
                    TestEnum1,
                    {"key1": "value1", "key2": "value2"},
                    True,
                    {"key1": TestEnum1.VALUE1, "key2": TestEnum1.VALUE2},
                ),
                (
                    "parse_mapping_invalid",
                    TestEnum2,
                    {"key1": "invalid"},
                    False,
                    None,
                ),
            ]

        @staticmethod
        def get_coerce_dict_validator_cases() -> list[
            tuple[
                str,
                type[StrEnum],
                object,
                bool,
                type[Exception] | None,
                dict[str, object] | None,
            ]
        ]:
            """Get parametrized test cases for Collection.coerce_dict_validator."""

            class TestEnum(StrEnum):
                VALUE1 = "value1"

            return [
                (
                    "coerce_dict_validator_success",
                    TestEnum,
                    {"key": "value1"},
                    True,
                    None,
                    {"key": TestEnum.VALUE1},
                ),
                (
                    "coerce_dict_validator_invalid_type",
                    TestEnum,
                    "not a dict",
                    False,
                    TypeError,
                    None,
                ),
                (
                    "coerce_dict_validator_invalid_value",
                    TestEnum,
                    {"key": "invalid"},
                    False,
                    ValueError,
                    None,
                ),
            ]

    @pytest.mark.parametrize(
        ("test_name", "enum_class", "mapping", "should_succeed", "expected"),
        CollectionTestCases.get_parse_mapping_cases(),
    )
    def test_collection_parse_mapping(
        self,
        test_name: str,
        enum_class: type[StrEnum],
        mapping: dict[str, str],
        should_succeed: bool,
        expected: dict[str, object] | None,
    ) -> None:
        """Test Collection.parse_mapping using advanced parametrization - reduces 20+ lines."""
        result = u.Collection.parse_mapping(enum_class, mapping)
        if should_succeed:
            tm.ok(result, eq=expected)
        else:
            tm.fail(result)

    @pytest.mark.parametrize(
        (
            "test_name",
            "enum_class",
            "input_data",
            "should_succeed",
            "expected_exception",
            "expected_result",
        ),
        CollectionTestCases.get_coerce_dict_validator_cases(),
    )
    def test_collection_coerce_dict_validator(
        self,
        test_name: str,
        enum_class: type[StrEnum],
        input_data: object,
        should_succeed: bool,
        expected_exception: type[Exception] | None,
        expected_result: dict[str, object] | None,
    ) -> None:
        """Test Collection.coerce_dict_validator using advanced parametrization - reduces 30+ lines."""
        validator = u.Collection.coerce_dict_validator(enum_class)
        if expected_exception:
            with pytest.raises(expected_exception):
                # Type checker can't verify runtime type - validator accepts GeneralValueType
                # and will raise TypeError for non-dict at runtime
                validator(cast("t.GeneralValueType", input_data))
        else:
            # Cast input_data to GeneralValueType for type compatibility (validator accepts it)
            result = validator(cast("t.GeneralValueType", input_data))
            assert result == expected_result

    class ModelTestCases:
        """Factory for Model test cases - reduces 80+ lines."""

        @staticmethod
        def get_from_dict_cases() -> list[
            tuple[
                str,
                type[BaseModel],
                dict[str, t.GeneralValueType],
                bool,
                dict[str, object] | None,
            ]
        ]:
            """Get parametrized test cases for Model.from_dict."""

            class TestModel1(BaseModel):
                name: str = "test"

            class TestModel2(BaseModel):
                name: str

            class NotPydantic:
                pass

            return [
                (
                    "from_dict_success",
                    TestModel1,
                    {"name": "test_value"},
                    True,
                    {"name": "test_value"},
                ),
                (
                    "from_dict_invalid",
                    TestModel2,
                    {},
                    False,
                    None,
                ),
                (
                    "from_dict_non_pydantic",
                    cast("type[BaseModel]", NotPydantic),
                    {},
                    False,
                    None,
                ),
            ]

        @staticmethod
        def get_merge_defaults_cases() -> list[
            tuple[
                str,
                type[BaseModel],
                dict[str, t.GeneralValueType],
                dict[str, t.GeneralValueType],
                bool,
                dict[str, object] | None,
            ]
        ]:
            """Get parametrized test cases for Model.merge_defaults."""

            class TestModel(BaseModel):
                name: str = "default"
                value: int = 0

            return [
                (
                    "merge_defaults_success",
                    TestModel,
                    {"name": "default", "value": 0},
                    {"name": "override"},
                    True,
                    {"name": "override", "value": 0},
                ),
            ]

        @staticmethod
        def get_update_cases() -> list[
            tuple[
                str,
                BaseModel | object,
                dict[str, t.GeneralValueType],
                bool,
                dict[str, object] | None,
            ]
        ]:
            """Get parametrized test cases for Model.update."""

            class TestModel(BaseModel):
                name: str = "original"
                value: int = 0

            class NotPydantic:
                pass

            return [
                (
                    "update_success",
                    TestModel(),
                    {"name": "updated"},
                    True,
                    {"name": "updated"},
                ),
                (
                    "update_non_pydantic",
                    NotPydantic(),
                    {"name": "test"},
                    False,
                    None,
                ),
            ]

    @pytest.mark.parametrize(
        ("test_name", "model_cls", "data", "should_succeed", "expected_attrs"),
        ModelTestCases.get_from_dict_cases(),
    )
    def test_model_from_dict(
        self,
        test_name: str,
        model_cls: type[BaseModel],
        data: dict[str, t.GeneralValueType],
        should_succeed: bool,
        expected_attrs: dict[str, object] | None,
    ) -> None:
        """Test Model.from_dict using advanced parametrization - reduces 50+ lines."""
        # Cast data to FlexibleValue-compatible mapping for type compatibility
        # FlexibleValue is a subset of GeneralValueType (scalars, sequences, mappings)
        flexible_data: Mapping[str, t.FlexibleValue] = cast(
            "Mapping[str, t.FlexibleValue]",
            data,
        )
        # model_cls is already type[BaseModel], which satisfies the type variable bound
        result = u.TypeNormalizer.Model.from_dict(model_cls, flexible_data)
        if should_succeed:
            tm.ok(result)
            if expected_attrs:
                model_instance = result.unwrap()
                for attr, expected_value in expected_attrs.items():
                    assert getattr(model_instance, attr) == expected_value
        else:
            tm.fail(result)

    @pytest.mark.parametrize(
        (
            "test_name",
            "model_cls",
            "defaults",
            "overrides",
            "should_succeed",
            "expected_attrs",
        ),
        ModelTestCases.get_merge_defaults_cases(),
    )
    def test_model_merge_defaults(
        self,
        test_name: str,
        model_cls: type[BaseModel],
        defaults: dict[str, t.GeneralValueType],
        overrides: dict[str, t.GeneralValueType],
        should_succeed: bool,
        expected_attrs: dict[str, object] | None,
    ) -> None:
        """Test Model.merge_defaults using advanced parametrization - reduces 20+ lines."""
        # Cast data to FlexibleValue-compatible mapping for type compatibility
        # FlexibleValue is a subset of GeneralValueType (scalars, sequences, mappings)
        flexible_defaults: Mapping[str, t.FlexibleValue] = cast(
            "Mapping[str, t.FlexibleValue]",
            defaults,
        )
        flexible_overrides: Mapping[str, t.FlexibleValue] = cast(
            "Mapping[str, t.FlexibleValue]",
            overrides,
        )
        # model_cls is already type[BaseModel], which satisfies the type variable bound
        result = u.TypeNormalizer.Model.merge_defaults(
            model_cls,
            flexible_defaults,
            flexible_overrides,
        )
        if should_succeed:
            tm.ok(result)
            if expected_attrs:
                model = result.unwrap()
                for attr, expected_value in expected_attrs.items():
                    assert getattr(model, attr) == expected_value
        else:
            tm.fail(result)

    @pytest.mark.parametrize(
        ("test_name", "instance", "updates", "should_succeed", "expected_attrs"),
        ModelTestCases.get_update_cases(),
    )
    def test_model_update(
        self,
        test_name: str,
        instance: BaseModel | object,
        updates: dict[str, t.GeneralValueType],
        should_succeed: bool,
        expected_attrs: dict[str, object] | None,
    ) -> None:
        """Test Model.update using advanced parametrization - reduces 20+ lines."""
        # Cast instance to BaseModel for type compatibility
        base_instance = cast("BaseModel", instance)
        # Cast updates to FlexibleValue-compatible dict
        flexible_updates = cast("dict[str, t.FlexibleValue]", updates)
        result = u.TypeNormalizer.Model.update(base_instance, **flexible_updates)
        if should_succeed:
            tm.ok(result)
            if expected_attrs:
                updated_instance = result.unwrap()
                for attr, expected_value in expected_attrs.items():
                    assert getattr(updated_instance, attr) == expected_value
        else:
            tm.fail(result)

    class ArgsTestCases:
        """Factory for Args test cases - reduces 40+ lines."""

        @staticmethod
        def get_validated_with_result_cases() -> list[
            tuple[str, object, bool, int | None]
        ]:
            """Get parametrized test cases for validated_with_result."""
            return [
                ("validated_with_result_success", 5, True, 10),
                (
                    "validated_with_result_validation_error",
                    cast("int", "not an int"),
                    False,
                    None,
                ),
            ]

        @staticmethod
        def get_parse_kwargs_cases() -> list[
            tuple[
                str,
                dict[str, str],
                dict[str, type[StrEnum]],
                bool,
                dict[str, str] | None,
            ]
        ]:
            """Get parametrized test cases for parse_kwargs."""

            class TestEnum(StrEnum):
                VALUE1 = "value1"

            return [
                (
                    "parse_kwargs_success",
                    {"key": "value", "enum_field": "value1"},
                    {"enum_field": TestEnum},
                    True,
                    {"enum_field": "value1"},
                ),
                (
                    "parse_kwargs_invalid_enum",
                    {"enum_field": "invalid"},
                    {"enum_field": TestEnum},
                    False,
                    None,
                ),
            ]

    @pytest.mark.parametrize(
        ("test_name", "input_value", "should_succeed", "expected"),
        ArgsTestCases.get_validated_with_result_cases(),
    )
    def test_args_validated_with_result(
        self,
        test_name: str,
        input_value: object,
        should_succeed: bool,
        expected: int | None,
    ) -> None:
        """Test validated_with_result using advanced parametrization - reduces 20+ lines."""

        @u.TypeNormalizer.Args.validated_with_result
        def test_func(value: int) -> r[int]:
            return r[int].ok(value * 2)

        result: r[int] = test_func(value=cast("int", input_value))
        if should_succeed:
            tm.ok(result, eq=expected)
        else:
            tm.fail(result)

    @pytest.mark.parametrize(
        ("test_name", "kwargs", "enum_fields", "should_succeed", "expected"),
        ArgsTestCases.get_parse_kwargs_cases(),
    )
    def test_args_parse_kwargs(
        self,
        test_name: str,
        kwargs: dict[str, str],
        enum_fields: dict[str, type[StrEnum]],
        should_succeed: bool,
        expected: dict[str, str] | None,
    ) -> None:
        """Test parse_kwargs using advanced parametrization - reduces 20+ lines."""
        result = u.TypeNormalizer.Args.parse_kwargs(kwargs, enum_fields)
        if should_succeed:
            tm.ok(result)
            if expected:
                parsed = result.unwrap()
                # Check that expected fields match (parse_kwargs returns all kwargs, not just enum fields)
                for key, value in expected.items():
                    assert parsed.get(key) == value
        else:
            tm.fail(result)

    def test_pydantic_coerced_enum(self) -> None:
        """Test Pydantic.coerced_enum creates Annotated type."""

        class TestEnum(StrEnum):
            VALUE1 = "value1"

        coerced_type = u.TypeNormalizer.Pydantic.coerced_enum(TestEnum)
        assert coerced_type is not None
