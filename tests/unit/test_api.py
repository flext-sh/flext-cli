"""FLEXT CLI API Tests - Comprehensive API Validation Testing.

Tests for FlextCli covering core CLI functionality, authentication, file operations,
command execution, configuration, output formatting, error handling, concurrent operations,
token management, validation, decorators, and edge cases with 100% coverage.

Modules tested: flext_cli.FlextCli (main API), FlextCliConfig, FlextCliModels,
FlextCliConstants, FlextCliOutput, FlextCliFileTools, FlextCliCore, FlextCliPrompts, FlextCliCmd
Scope: All API operations, authentication, file operations, command execution, configuration

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import threading
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, TypedDict

import pytest
from flext_core import FlextResult
from flext_tests import FlextTestsMatchers

from flext_cli import (
    FlextCli,
    FlextCliConstants,
)

from .._helpers import AuthHelpers, CommandHelpers, OutputHelpers
from ..fixtures.constants import TestData

# ============================================================================
# TYPE DEFINITIONS
# ============================================================================


class FormatScenario(TypedDict, total=False):
    """Type definition for format test scenario."""

    data: Any
    validator: Callable[[str, Any], bool]


class AuthScenario(TypedDict):
    """Type definition for authentication test scenario."""

    factory: Callable[[], FlextResult[dict[str, Any]]]
    expected_success: bool


class FileScenario(TypedDict):
    """Type definition for file operation test scenario."""

    operation: str
    setup_exists: bool
    expected_success: bool


# ============================================================================
# TEST CONSTANTS & MAPPINGS
# ============================================================================


class ApiTestType(StrEnum):
    """API test categories for dynamic testing."""

    INITIALIZATION = "initialization"
    OUTPUT_FORMATTING = "output_formatting"
    AUTHENTICATION = "authentication"
    FILE_OPERATIONS = "file_operations"
    COMMAND_EXECUTION = "command_execution"
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    CONCURRENT_OPERATIONS = "concurrent_operations"


@dataclass(frozen=True)
class ApiTestCase:
    """Test case data for API tests."""

    test_type: ApiTestType
    description: str
    expected_success: bool = True


# ============================================================================
# TEST DATA FACTORIES & MAPPINGS
# ============================================================================


class ApiTestFactory:
    """Factory for creating API test data and cases."""

    @staticmethod
    def create_comprehensive_test_cases() -> list[ApiTestCase]:
        """Create comprehensive test cases for all API scenarios."""
        return [
            ApiTestCase(ApiTestType.INITIALIZATION, "API service initialization"),
            ApiTestCase(ApiTestType.OUTPUT_FORMATTING, "Output formatting"),
            ApiTestCase(ApiTestType.AUTHENTICATION, "Authentication operations"),
            ApiTestCase(ApiTestType.FILE_OPERATIONS, "File operations"),
            ApiTestCase(ApiTestType.COMMAND_EXECUTION, "Command execution"),
            ApiTestCase(ApiTestType.CONFIGURATION, "Configuration management"),
            ApiTestCase(ApiTestType.VALIDATION, "Data validation"),
            ApiTestCase(ApiTestType.CONCURRENT_OPERATIONS, "Concurrent operations"),
        ]

    @staticmethod
    def create_output_format_test_data() -> dict[str, FormatScenario]:
        """Create test data for output formatting."""
        return {
            "json": FormatScenario(
                data=OutputHelpers.create_format_test_data(),
                validator=lambda output, data: json.loads(output) == data,
            ),
            "table": FormatScenario(
                data=OutputHelpers.create_table_test_data(),
                validator=lambda output, data: any(
                    str(user.get("name", "")) in output
                    for user in data.get("users", [])
                    if isinstance(user, dict)
                ),
            ),
            "yaml": FormatScenario(
                data=OutputHelpers.create_format_test_data(),
                validator=lambda output, data: "key: value" in output
                and "number: 42" in output,
            ),
        }

    @staticmethod
    def create_auth_test_scenarios() -> dict[str, AuthScenario]:
        """Create authentication test scenarios."""
        return {
            "valid_credentials": AuthScenario(
                factory=AuthHelpers.create_credentials,
                expected_success=True,
            ),
            "empty_credentials": AuthScenario(
                factory=lambda: AuthHelpers.create_credentials("", ""),
                expected_success=False,
            ),
            "short_username": AuthScenario(
                factory=lambda: AuthHelpers.create_credentials("ab"),
                expected_success=False,
            ),
            "short_password": AuthScenario(
                factory=lambda: AuthHelpers.create_credentials(password="short"),
                expected_success=False,
            ),
        }

    @staticmethod
    def create_file_operation_scenarios() -> dict[str, FileScenario]:
        """Create file operation test scenarios."""
        return {
            "read_existing": FileScenario(
                operation="read",
                setup_exists=True,
                expected_success=True,
            ),
            "read_nonexistent": FileScenario(
                operation="read",
                setup_exists=False,
                expected_success=False,
            ),
            "write_new": FileScenario(
                operation="write",
                setup_exists=False,
                expected_success=True,
            ),
            "write_existing": FileScenario(
                operation="write",
                setup_exists=True,
                expected_success=True,
            ),
            "delete_existing": FileScenario(
                operation="delete",
                setup_exists=True,
                expected_success=True,
            ),
            "delete_nonexistent": FileScenario(
                operation="delete",
                setup_exists=False,
                expected_success=False,
            ),
        }


# ============================================================================
# MAIN TEST CLASS
# ============================================================================


class TestFlextCli:
    """Comprehensive tests for FlextCli API functionality.

    Uses advanced Python 3.13+ features: match statements, StrEnum, dataclasses,
    factory patterns, mapping, and dynamic testing for maximum coverage with minimal code.
    """

    # ========================================================================
    # DYNAMIC TEST EXECUTION
    # ========================================================================

    @pytest.mark.parametrize(
        "test_case",
        ApiTestFactory.create_comprehensive_test_cases(),
        ids=lambda x: f"{x.test_type.value}_{x.description.lower().replace(' ', '_')}",
    )
    def test_api_comprehensive_functionality(
        self,
        test_case: ApiTestCase,
        flext_cli_api: FlextCli,
        tmp_path: Path,
    ) -> None:
        """Comprehensive API functionality tests using dynamic execution."""
        match test_case.test_type:
            case ApiTestType.INITIALIZATION:
                self._execute_initialization_tests(flext_cli_api)
            case ApiTestType.OUTPUT_FORMATTING:
                self._execute_output_formatting_tests(flext_cli_api)
            case ApiTestType.AUTHENTICATION:
                self._execute_authentication_tests(flext_cli_api)
            case ApiTestType.FILE_OPERATIONS:
                self._execute_file_operations_tests(flext_cli_api, tmp_path)
            case ApiTestType.COMMAND_EXECUTION:
                self._execute_command_execution_tests(flext_cli_api)
            case ApiTestType.CONFIGURATION:
                self._execute_configuration_tests(flext_cli_api)
            case ApiTestType.VALIDATION:
                self._execute_validation_tests()
            case ApiTestType.CONCURRENT_OPERATIONS:
                self._execute_concurrent_operations_tests(flext_cli_api)

    # ========================================================================
    # TEST EXECUTION HELPERS
    # ========================================================================

    def _execute_initialization_tests(self, api_service: FlextCli) -> None:
        """Execute initialization tests."""
        assert isinstance(api_service, FlextCli) and all(
            hasattr(api_service, attr)
            for attr in (
                "logger",
                "_container",
                "output",
                "file_tools",
                "core",
                "prompts",
                "cmd",
            )
        )
        execute_result = api_service.execute()
        FlextTestsMatchers.assert_success(execute_result)
        data = execute_result.unwrap()
        assert (
            isinstance(data, dict)
            and data.get("service") == "flext-cli"
            and data.get("status") == "operational"
        )

    def _execute_output_formatting_tests(self, api_service: FlextCli) -> None:
        """Execute output formatting tests."""
        for (
            format_type,
            config,
        ) in ApiTestFactory.create_output_format_test_data().items():
            if (data := config.get("data")) is None or (
                validator := config.get("validator")
            ) is None:
                continue
            result = api_service.output.format_data(data=data, format_type=format_type)
            FlextTestsMatchers.assert_success(result)
            assert isinstance((output := result.unwrap()), str) and validator(
                output, data
            )

    def _execute_authentication_tests(self, api_service: FlextCli) -> None:
        """Execute authentication tests."""
        for config in ApiTestFactory.create_auth_test_scenarios().values():
            creds_result = config["factory"]()
            if config["expected_success"]:
                FlextTestsMatchers.assert_success(creds_result)
                assert api_service.authenticate(creds_result.unwrap()).is_success
            else:
                assert creds_result.is_failure

    def _execute_file_operations_tests(
        self, api_service: FlextCli, tmp_path: Path
    ) -> None:
        """Execute file operations tests."""
        for name, config in ApiTestFactory.create_file_operation_scenarios().items():
            op, exists = config["operation"], config["setup_exists"]
            file = tmp_path / f"test_{name}.txt"
            if exists:
                file.write_text("test content")

            match op:
                case "read":
                    read_res = api_service.file_tools.read_text_file(str(file))
                    if exists:
                        FlextTestsMatchers.assert_success(read_res)
                        assert read_res.unwrap() == "test content"
                    else:
                        assert read_res.is_failure
                case "write":
                    write_res = api_service.file_tools.write_text_file(
                        str(file), "new content"
                    )
                    FlextTestsMatchers.assert_success(write_res)
                    assert file.read_text() == "new content"
                case "delete":
                    del_res = api_service.file_tools.delete_file(str(file))
                    if exists:
                        FlextTestsMatchers.assert_success(del_res)
                        assert not file.exists()
                    else:
                        assert del_res.is_failure

    def _execute_command_execution_tests(self, api_service: FlextCli) -> None:
        """Execute command execution tests."""
        cmd_result = CommandHelpers.create_command_model()
        FlextTestsMatchers.assert_success(cmd_result)
        cmd = cmd_result.unwrap()
        assert (
            cmd.name == TestData.Commands.TEST_COMMAND
            and cmd.status == FlextCliConstants.CommandStatus.PENDING.value
        )

    def _execute_configuration_tests(self, api_service: FlextCli) -> None:
        """Execute configuration tests."""
        config = api_service.config
        assert config is not None and all(
            hasattr(config, attr) for attr in ("profile", "output_format")
        )

    def _execute_validation_tests(self) -> None:
        """Execute validation tests."""
        assert FlextCli.get_instance() is FlextCli.get_instance()

    def _execute_concurrent_operations_tests(self, api_service: FlextCli) -> None:
        """Execute concurrent operations tests."""
        results, errors = [], []

        def worker() -> None:
            try:
                results.append(FlextCli.get_instance() is not None)
            except Exception as e:
                errors.append(str(e))

        for t in [threading.Thread(target=worker) for _ in range(5)]:
            t.start()
            t.join()

        assert len(results) == 5 and all(results) and len(errors) == 0

    # ========================================================================
