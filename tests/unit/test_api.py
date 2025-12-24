"""FLEXT CLI API Tests - Comprehensive API Validation Testing.

Tests for FlextCli covering core CLI functionality, authentication, file operations,
command execution, configuration, output formatting, error handling, concurrent operations,
token management, validation, decorators, and edge cases with 100% coverage.

Modules tested: flext_cli.FlextCli (main API), FlextCliSettings, FlextCliModels,
FlextCliConstants, FlextCliOutput, FlextCliFileTools, FlextCliCore, FlextCliPrompts, FlextCliCmd
Scope: All API operations, authentication, file operations, command execution, configuration

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import threading
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import TypedDict

import pytest
from flext import t
from flext_tests import tm

from flext_cli import (
    FlextCli,
    FlextCliAppBase,
    c,
    m,
    r,

from .._helpers import AuthHelpers, CommandHelpers, OutputHelpers

# from ..fixtures.constants import TestData  # Fixtures removed - use conftest.py and flext_tests

# ============================================================================
# TYPE DEFINITIONS
# ============================================================================


class FormatScenario(TypedDict, total=False):
    """Type definition for format test scenario."""

    data: t.GeneralValueType
    validator: Callable[[str, t.GeneralValueType], bool]


class AuthScenario(TypedDict):
    """Type definition for authentication test scenario."""

    factory: Callable[[], r[Mapping[str, str]]]
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
                validator=lambda output, _data: (
                    # Table output should be a non-empty string with table-like content
                    # The data structure will be formatted (e.g., as YAML or table)
                    # Just verify output is non-empty and contains expected structural elements
                    isinstance(output, str)
                    and len(output) > 0
                    and ("simple" in output or "headers" in output or "rows" in output)
                ),
            ),
            "yaml": FormatScenario(
                data=OutputHelpers.create_format_test_data(),
                validator=lambda output, _data: (
                    # YAML output contains number: 42 and test: data
                    "number: 42" in output and "test: data" in output
                ),
            ),
        }

    @staticmethod
    def create_auth_test_scenarios() -> dict[str, AuthScenario]:
        """Create authentication test scenarios."""
        def create_creds(**overrides: dict[str, Any]) -> r[dict[str, Any]]:
            """Create credentials without token field."""
            creds = AuthHelpers.create_test_credentials(**overrides)
            # Remove token field for credential-based auth testing
            creds.pop("token", None)
            return r.ok(creds)

        return {
            "valid_credentials": AuthScenario(
                factory=lambda: create_creds(),
                expected_success=True,
            ),
            "empty_credentials": AuthScenario(
                factory=lambda: create_creds(username="", password=""),
                expected_success=False,
            ),
            "short_username": AuthScenario(
                factory=lambda: create_creds(username="ab"),
                expected_success=False,
            ),
            "short_password": AuthScenario(
                factory=lambda: create_creds(password="short"),
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


class TestsCli:
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
        tm.ok(execute_result)
        data = execute_result.value
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
            tm.ok(result)
            assert isinstance((output := result.value), str) and validator(
                output,
                data,
            )

    def _execute_authentication_tests(self, api_service: FlextCli) -> None:
        """Execute authentication tests."""
        for config in ApiTestFactory.create_auth_test_scenarios().values():
            creds_result = config["factory"]()
            # Factory always returns success with credentials
            tm.ok(creds_result)
            creds = creds_result.value
            auth_result = api_service.authenticate(creds)
            if config["expected_success"]:
                # Valid creds should authenticate successfully
                assert auth_result.is_success
            else:
                # Invalid creds should fail authentication
                assert auth_result.is_failure

    def _execute_file_operations_tests(
        self,
        api_service: FlextCli,
        tmp_path: Path,
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
                        tm.ok(read_res)
                        assert read_res.value == "test content"
                    else:
                        assert read_res.is_failure
                case "write":
                    write_res = api_service.file_tools.write_text_file(
                        str(file),
                        "new content",
                    )
                    tm.ok(write_res)
                    assert file.read_text() == "new content"
                case "delete":
                    del_res = api_service.file_tools.delete_file(str(file))
                    if exists:
                        tm.ok(del_res)
                        assert not file.exists()
                    else:
                        assert del_res.is_failure

    def _execute_command_execution_tests(self, api_service: FlextCli) -> None:
        """Execute command execution tests."""
        cmd_result = CommandHelpers.create_command_model()
        tm.ok(cmd_result)
        cmd = cmd_result.value
        assert (
            cmd.name == "test_command"
            and cmd.status == c.Cli.CommandStatus.PENDING.value
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

        for thread in [threading.Thread(target=worker) for _ in range(5)]:
            thread.start()
            thread.join()

        assert len(results) == 5 and all(results) and len(errors) == 0

    # ========================================================================
    # AUTHENTICATION TESTS - Missing Coverage
    # ========================================================================

    def test_authenticate_with_token_success(
        self,
        flext_cli_api: FlextCli,
        temp_dir: Path,
    ) -> None:
        """Test authentication with valid token."""
        token = "test_token_abc123"
        credentials = {c.Cli.DictKeys.TOKEN: token}
        result = flext_cli_api.authenticate(credentials)
        tm.ok(result)
        assert result.value == token

    def test_authenticate_with_token_invalid(self, flext_cli_api: FlextCli) -> None:
        """Test authentication with invalid token."""
        credentials = {c.Cli.DictKeys.TOKEN: ""}
        result = flext_cli_api.authenticate(credentials)
        assert result.is_failure

    def test_authenticate_with_credentials_success(
        self,
        flext_cli_api: FlextCli,
    ) -> None:
        """Test authentication with username/password."""
        credentials = {
            c.Cli.DictKeys.USERNAME: "testuser",
            c.Cli.DictKeys.PASSWORD: "testpass123",
        }
        result = flext_cli_api.authenticate(credentials)
        tm.ok(result)
        assert isinstance(result.value, str)

    def test_authenticate_with_credentials_missing_fields(
        self,
        flext_cli_api: FlextCli,
    ) -> None:
        """Test authentication with missing credential fields."""
        # Missing username or password should fail
        credentials = {
            c.Cli.DictKeys.USERNAME: "testuser",
            # Missing password
        }
        result = flext_cli_api.authenticate(credentials)
        assert result.is_failure

    def test_authenticate_invalid_credentials_format(
        self,
        flext_cli_api: FlextCli,
    ) -> None:
        """Test authentication with invalid credential format."""
        credentials = {"invalid": "data"}
        result = flext_cli_api.authenticate(credentials)
        assert result.is_failure

    def test_validate_credentials_success(self) -> None:
        """Test credential validation with valid data."""
        result = FlextCli.validate_credentials("testuser", "testpass123")
        tm.ok(result)
        assert result.value is True

    def test_validate_credentials_with_valid_data(self) -> None:
        """Test credential validation with valid data."""
        # PasswordAuth accepts any strings including empty ones
        result = FlextCli.validate_credentials("testuser", "testpass123")
        tm.ok(result)
        assert result.value is True

    def test_save_auth_token_success(
        self,
        flext_cli_api: FlextCli,
        temp_dir: Path,
    ) -> None:
        """Test saving authentication token."""
        token = "test_token_xyz789"
        result = flext_cli_api.save_auth_token(token)
        tm.ok(result)
        assert result.value is True

    def test_save_auth_token_invalid(self, flext_cli_api: FlextCli) -> None:
        """Test saving invalid token."""
        result = flext_cli_api.save_auth_token("")
        assert result.is_failure

    def test_get_auth_token_success(
        self,
        flext_cli_api: FlextCli,
        temp_dir: Path,
    ) -> None:
        """Test getting authentication token from file."""
        token = "test_token_retrieved"
        # Save token first
        save_result = flext_cli_api.save_auth_token(token)
        tm.ok(save_result)
        # Get token
        result = flext_cli_api.get_auth_token()
        tm.ok(result)
        assert result.value == token

    def test_get_auth_token_not_found(
        self,
        flext_cli_api: FlextCli,
        temp_dir: Path,
    ) -> None:
        """Test getting token when file doesn't exist."""
        # Ensure token file doesn't exist
        token_file = flext_cli_api.config.token_file
        if token_file.exists():
            token_file.unlink()
        result = flext_cli_api.get_auth_token()
        assert result.is_failure

    def test_get_auth_token_invalid_data(
        self,
        flext_cli_api: FlextCli,
        temp_dir: Path,
    ) -> None:
        """Test getting token with invalid file data."""
        token_file = flext_cli_api.config.token_file
        # Write invalid JSON
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text("invalid json")
        result = flext_cli_api.get_auth_token()
        assert result.is_failure

    def test_get_auth_token_empty_file(
        self,
        flext_cli_api: FlextCli,
        temp_dir: Path,
    ) -> None:
        """Test getting token from empty file."""
        token_file = flext_cli_api.config.token_file
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text("{}")
        result = flext_cli_api.get_auth_token()
        assert result.is_failure

    def test_is_authenticated_true(
        self,
        flext_cli_api: FlextCli,
        temp_dir: Path,
    ) -> None:
        """Test is_authenticated returns True when token exists."""
        token = "test_token_auth_check"
        save_result = flext_cli_api.save_auth_token(token)
        tm.ok(save_result)
        assert flext_cli_api.is_authenticated() is True

    def test_is_authenticated_false(
        self,
        flext_cli_api: FlextCli,
        temp_dir: Path,
    ) -> None:
        """Test is_authenticated returns False when no token."""
        # Clear any existing tokens first to ensure clean state
        flext_cli_api.clear_auth_tokens()
        assert flext_cli_api.is_authenticated() is False

    def test_clear_auth_tokens_success(
        self,
        flext_cli_api: FlextCli,
        temp_dir: Path,
    ) -> None:
        """Test clearing authentication tokens."""
        token = "test_token_to_clear"
        save_result = flext_cli_api.save_auth_token(token)
        tm.ok(save_result)
        clear_result = flext_cli_api.clear_auth_tokens()
        tm.ok(clear_result)
        assert clear_result.value is True

    def test_clear_auth_tokens_when_no_tokens(self, flext_cli_api: FlextCli) -> None:
        """Test clearing tokens when none exist."""
        result = flext_cli_api.clear_auth_tokens()
        tm.ok(result)

    # ========================================================================
    # COMMAND REGISTRATION TESTS - Missing Coverage
    # ========================================================================

    def test_command_decorator_with_name(self, flext_cli_api: FlextCli) -> None:
        """Test command decorator with explicit name."""

        @flext_cli_api.command(name="test_cmd")
        def test_command(
            *args: t.GeneralValueType,
            **kwargs: t.GeneralValueType,
        ) -> t.GeneralValueType:
            """Test command."""
            return None

        assert "test_cmd" in flext_cli_api._commands

    def test_command_decorator_without_name(self, flext_cli_api: FlextCli) -> None:
        """Test command decorator without explicit name."""

        @flext_cli_api.command()
        def test_command_auto(
            *args: t.GeneralValueType,
            **kwargs: t.GeneralValueType,
        ) -> t.GeneralValueType:
            """Test command."""
            return None

        assert "test_command_auto" in flext_cli_api._commands

    def test_group_decorator_with_name(self, flext_cli_api: FlextCli) -> None:
        """Test group decorator with explicit name."""

        @flext_cli_api.group(name="test_group")
        def test_group_func(
            *args: t.GeneralValueType,
            **kwargs: t.GeneralValueType,
        ) -> t.GeneralValueType:
            """Test group."""
            return None

        assert "test_group" in flext_cli_api._groups

    def test_group_decorator_without_name(self, flext_cli_api: FlextCli) -> None:
        """Test group decorator without explicit name."""

        @flext_cli_api.group()
        def test_group_auto(
            *args: t.GeneralValueType,
            **kwargs: t.GeneralValueType,
        ) -> t.GeneralValueType:
            """Test group."""
            return None

        assert "test_group_auto" in flext_cli_api._groups

    # ========================================================================
    # EXECUTION TESTS - Missing Coverage
    # ========================================================================

    def test_execute_method(self, flext_cli_api: FlextCli) -> None:
        """Test execute method returns service status."""
        result = flext_cli_api.execute()
        tm.ok(result)
        data = result.value
        assert c.Cli.DictKeys.STATUS in data
        assert c.Cli.DictKeys.SERVICE in data
        assert "version" in data
        assert "components" in data

    def test_execute_cli_static(self) -> None:
        """Test static execute_cli method."""
        result = FlextCli.execute_cli()
        tm.ok(result)
        assert result.value is True

    # ========================================================================
    # CONVENIENCE METHODS TESTS - Missing Coverage
    # ========================================================================

    def test_print_method(self, flext_cli_api: FlextCli) -> None:
        """Test print convenience method."""
        result = flext_cli_api.print("Test message", style="green")
        tm.ok(result)

    def test_create_table_with_dict(self, flext_cli_api: FlextCli) -> None:
        """Test create_table with dictionary data."""
        data = {"name": "John", "age": 30}
        # dict[str, int] is compatible with Mapping[str, t.GeneralValueType]
        # Type narrowing: ensure data is dict (already checked)
        if not isinstance(data, dict):
            msg = "data must be dict"
            raise TypeError(msg)
        # dict[str, int] is structurally compatible with Mapping[str, t.GeneralValueType]
        typed_data: Mapping[str, t.GeneralValueType] = data
        result = flext_cli_api.create_table(
            typed_data,
            headers=["Name", "Age"],
        )
        tm.ok(result)
        assert isinstance(result.value, str)

    def test_create_table_with_list(self, flext_cli_api: FlextCli) -> None:
        """Test create_table with list data."""
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        # list[dict[str, int]] is compatible with Sequence[Mapping[str, t.GeneralValueType]]
        # Type narrowing: ensure data is list of dicts
        if not isinstance(data, list):
            msg = "data must be list"
            raise TypeError(msg)
        # list[dict[str, int]] is structurally compatible with Sequence[Mapping[str, t.GeneralValueType]]
        typed_data: Sequence[Mapping[str, t.GeneralValueType]] = data
        result = flext_cli_api.create_table(
            typed_data,
            headers=["name", "age"],  # Use lowercase to match dict keys
        )
        tm.ok(result)
        assert isinstance(result.value, str)

    def test_create_table_with_none(self, flext_cli_api: FlextCli) -> None:
        """Test create_table with None data."""
        result = flext_cli_api.create_table(None)
        assert result.is_failure

    def test_create_table_with_title(self, flext_cli_api: FlextCli) -> None:
        """Test create_table with title."""
        data = [{"name": "John", "age": 30}]
        # list[dict[str, int]] is compatible with Sequence[Mapping[str, t.GeneralValueType]]
        # Type narrowing: ensure data is list of dicts
        if not isinstance(data, list):
            msg = "data must be list"
            raise TypeError(msg)
        # list[dict[str, int]] is structurally compatible with Sequence[Mapping[str, t.GeneralValueType]]
        typed_data: Sequence[Mapping[str, t.GeneralValueType]] = data
        result = flext_cli_api.create_table(
            typed_data,
            headers=["name", "age"],  # Use lowercase to match dict keys
            title="Users",
        )
        tm.ok(result)

    def test_print_table_method(self, flext_cli_api: FlextCli) -> None:
        """Test print_table convenience method."""
        table_str = "| Name | Age |\n|------|-----|\n| John | 30  |"
        result = flext_cli_api.print_table(table_str)
        tm.ok(result)

    def test_create_tree_method(self, flext_cli_api: FlextCli) -> None:
        """Test create_tree convenience method."""
        result = flext_cli_api.create_tree("Root")
        tm.ok(result)
        tree = result.value
        assert hasattr(tree, "add")

    def test_get_auth_token_dict_error(
        self,
        flext_cli_api: FlextCli,
        temp_dir: Path,
    ) -> None:
        """Test get_auth_token with dict type error."""
        token_file = flext_cli_api.config.token_file
        token_file.parent.mkdir(parents=True, exist_ok=True)
        # Write data that causes dict/mapping error
        token_file.write_text('{"token": {"nested": "invalid"}}')
        result = flext_cli_api.get_auth_token()
        assert result.is_failure

    def test_get_auth_token_string_error(
        self,
        flext_cli_api: FlextCli,
        temp_dir: Path,
    ) -> None:
        """Test get_auth_token with string type error."""
        token_file = flext_cli_api.config.token_file
        token_file.parent.mkdir(parents=True, exist_ok=True)
        # Write data that causes string type error
        token_file.write_text('{"token": 123}')
        result = flext_cli_api.get_auth_token()
        assert result.is_failure

    def test_get_auth_token_other_error(
        self,
        flext_cli_api: FlextCli,
        temp_dir: Path,
    ) -> None:
        """Test get_auth_token with other validation error."""
        token_file = flext_cli_api.config.token_file
        token_file.parent.mkdir(parents=True, exist_ok=True)
        # Write invalid JSON structure
        token_file.write_text('{"invalid": "structure"}')
        result = flext_cli_api.get_auth_token()
        assert result.is_failure

    def test_clear_auth_tokens_with_delete_error(
        self,
        flext_cli_api: FlextCli,
        temp_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test clear_auth_tokens with file deletion error."""
        token = "test_token_error"
        save_result = flext_cli_api.save_auth_token(token)
        tm.ok(save_result)

        # Mock delete_file to return failure with non-file-not-found error
        original_delete = flext_cli_api.file_tools.delete_file

        def mock_delete(path: str) -> r[bool]:
            if "token.json" in path:
                return r[bool].fail("Permission denied")
            return original_delete(path)

        monkeypatch.setattr(flext_cli_api.file_tools, "delete_file", mock_delete)
        result = flext_cli_api.clear_auth_tokens()
        assert result.is_failure

    def test_clear_auth_tokens_with_refresh_delete_error(
        self,
        flext_cli_api: FlextCli,
        temp_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test clear_auth_tokens with refresh token deletion error."""
        token = "test_token_refresh_error"
        save_result = flext_cli_api.save_auth_token(token)
        tm.ok(save_result)

        # Mock delete_file to return failure for refresh token
        original_delete = flext_cli_api.file_tools.delete_file

        def mock_delete(path: str) -> r[bool]:
            if "refresh_token.json" in path:
                return r[bool].fail("Permission denied")
            return original_delete(path)

        monkeypatch.setattr(flext_cli_api.file_tools, "delete_file", mock_delete)
        result = flext_cli_api.clear_auth_tokens()
        assert result.is_failure

    def test_save_auth_token_write_failure(
        self,
        flext_cli_api: FlextCli,
        temp_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test save_auth_token with write failure."""
        token = "test_token_write_fail"

        # Mock write_json_file to return failure
        def mock_write(path: str, data: dict[str, t.GeneralValueType]) -> r[bool]:
            return r[bool].fail("Write failed")

        monkeypatch.setattr(flext_cli_api.file_tools, "write_json_file", mock_write)
        result = flext_cli_api.save_auth_token(token)
        assert result.is_failure

    def test_authenticate_with_token_save_failure(
        self,
        flext_cli_api: FlextCli,
        temp_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test authenticate with token when save fails."""
        token = "test_token_save_fail"
        credentials = {c.Cli.DictKeys.TOKEN: token}

        # Mock save_auth_token to return failure
        def mock_save(t: str) -> r[bool]:
            return r[bool].fail("Save failed")

        monkeypatch.setattr(flext_cli_api, "save_auth_token", mock_save)
        result = flext_cli_api.authenticate(credentials)
        assert result.is_failure

    def test_authenticate_with_credentials_validation_error(
        self,
        flext_cli_api: FlextCli,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test authenticate with credentials when validation fails."""
        credentials = {
            c.Cli.DictKeys.USERNAME: "testuser",
            c.Cli.DictKeys.PASSWORD: "testpass123",
        }

        # Mock model_validate to raise exception
        validation_error_msg = "Validation failed"

        def mock_validate(data: object) -> m.Cli.PasswordAuth:
            raise ValueError(validation_error_msg)

        monkeypatch.setattr(m.Cli.PasswordAuth, "model_validate", mock_validate)
        result = flext_cli_api.authenticate(credentials)
        assert result.is_failure

    def test_validate_credentials_exception(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test validate_credentials when exception occurs."""
        # Mock PasswordAuth to raise exception
        invalid_credentials_msg = "Invalid credentials"

        def mock_init(self: object, *args: object, **kwargs: object) -> None:
            raise ValueError(invalid_credentials_msg)

        monkeypatch.setattr(m.Cli.PasswordAuth, "__init__", mock_init)
        result = FlextCli.validate_credentials("testuser", "testpass")
        assert result.is_failure

    # ========================================================================
    # FLEXT CLI APP BASE TESTS - Missing Coverage
    # ========================================================================

    def test_flext_cli_app_base_resolve_cli_args_none(self) -> None:
        """Test _resolve_cli_args with None args."""
        result = FlextCliAppBase._resolve_cli_args(None)
        # Should return empty list in pytest environment or sys.argv[1:]
        assert isinstance(result, list)

    def test_flext_cli_app_base_resolve_cli_args_provided(self) -> None:
        """Test _resolve_cli_args with provided args."""
        args = ["--help", "--version"]
        result = FlextCliAppBase._resolve_cli_args(args)
        assert result == args

    def test_flext_cli_app_base_handle_pathlib_error(self) -> None:
        """Test _handle_pathlib_annotation_error with pathlib error."""
        error = NameError("name 'pathlib' is not defined")
        # Should not raise, just log warning
        FlextCliAppBase._handle_pathlib_annotation_error(error)

    def test_flext_cli_app_base_handle_non_pathlib_error(self) -> None:
        """Test _handle_pathlib_annotation_error with non-pathlib error."""
        error = NameError("name 'other' is not defined")
        # Should re-raise non-pathlib errors
        with pytest.raises(NameError):
            FlextCliAppBase._handle_pathlib_annotation_error(error)

    # ========================================================================
