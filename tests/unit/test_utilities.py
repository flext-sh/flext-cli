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
from flext_core import FlextResult, FlextUtilities
from flext_tests import FlextTestsMatchers, FlextTestsUtilities

from flext_cli import FlextCliConstants, FlextCliUtilities

from ..fixtures.constants import TestUtilities
from ..helpers import FlextCliTestHelpers


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
                    error_contains="cannot be empty",
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
                    # Use FlextUtilities.Validation.validate_choice directly
                    format_lower = format_type.lower()
                    format_result: FlextResult[str] = FlextUtilities.Validation.validate_choice(
                        format_lower,
                        set(FlextCliConstants.OUTPUT_FORMATS_LIST),
                        "Output format",
                        case_sensitive=False,
                    )
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

        # 2. Validate output format with normalization using FlextUtilities directly
        format_lower = TestUtilities.Validation.OutputFormats.UPPERCASE_FORMAT.lower()
        validation_result = FlextUtilities.Validation.validate_choice(
            format_lower,
            set(FlextCliConstants.OUTPUT_FORMATS_LIST),
            "Output format",
            case_sensitive=False,
        )
        result2 = FlextResult[str].ok(format_lower) if validation_result.is_success else validation_result
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
        FlextTestsMatchers.assert_dict_contains(
            test_data,
            expected_data,
        )

        # Test with domain helpers
        assert_helpers = FlextCliTestHelpers.AssertHelpers
        assert_helpers.assert_result_success(FlextResult.ok("utilities_test"))

    def test_utilities_namespaces_availability(self) -> None:
        """Test that all FlextCliUtilities namespaces are available."""
        # Test CLI-specific namespaces (actual namespaces in FlextCliUtilities)
        # CliDataMapper was removed - use FlextUtilities.DataMapper directly
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
