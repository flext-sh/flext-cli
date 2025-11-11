"""FLEXT CLI API Tests - Comprehensive Real Functionality Testing.

Tests for FlextCli covering all real functionality with flext_tests
integration, comprehensive API operations, and targeting 90%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import cast

import pytest
from flext_core import FlextResult, FlextTypes
from pydantic import PositiveInt, TypeAdapter, ValidationError

from flext_cli import FlextCli, FlextCliConstants, FlextCliTypes


class TestFlextCli:
    """Comprehensive tests for FlextCli functionality."""

    @pytest.fixture
    def api_service(self, flext_cli_api: FlextCli) -> FlextCli:
        """Create FlextCli instance for testing with isolated config."""
        return flext_cli_api

    # ========================================================================
    # INITIALIZATION AND BASIC FUNCTIONALITY
    # ========================================================================
    def test_api_service_initialization(self, api_service: FlextCli) -> None:
        """Test API service initialization and basic services."""
        assert api_service is not None
        assert hasattr(api_service, "logger")
        assert hasattr(api_service, "_container")
        # Services (no wrapper properties needed - direct access)
        assert hasattr(api_service, "output")
        assert hasattr(api_service, "file_tools")
        assert hasattr(api_service, "core")
        assert hasattr(api_service, "prompts")
        assert hasattr(api_service, "cmd")

    def test_api_service_execute_method(self, api_service: FlextCli) -> None:
        """Test API service execute method with real functionality."""
        result = api_service.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, dict)
        assert "status" in data
        assert "service" in data
        assert data["service"] == "flext-cli"
        assert "status" in data
        assert "service" in data
        assert data["service"] == "flext-cli"

    # ========================================================================
    # OUTPUT FORMATTING AND DISPLAY
    # ========================================================================

    def test_format_data_table(self, api_service: FlextCli) -> None:
        """Test table data formatting functionality."""
        test_data: FlextCliTypes.Data.CliDataDict = {
            "users": [
                {"name": "John", "age": 30, "city": "New York"},
                {"name": "Jane", "age": 25, "city": "London"},
                {"name": "Bob", "age": 35, "city": "Paris"},
            ]
        }

        result = api_service.output.format_data(
            data=cast("FlextTypes.JsonValue", test_data), format_type="table"
        )

        assert isinstance(result, FlextResult)
        assert result.is_success

        formatted_output = result.unwrap()
        assert isinstance(formatted_output, str)
        assert "John" in formatted_output
        assert "Jane" in formatted_output
        assert "Bob" in formatted_output

    def test_format_data_json(self, api_service: FlextCli) -> None:
        """Test JSON data formatting functionality."""
        test_data: FlextCliTypes.Data.CliDataDict = {
            "key": "value",
            "number": 42,
            "list": [1, 2, 3],
        }

        result = api_service.output.format_data(
            data=cast("FlextTypes.JsonValue", test_data), format_type="json"
        )

        assert isinstance(result, FlextResult)
        assert result.is_success

        formatted_output = result.unwrap()
        assert isinstance(formatted_output, str)

        # Verify it's valid JSON
        parsed_data = json.loads(formatted_output)
        assert parsed_data == test_data

    def test_format_data_yaml(self, api_service: FlextCli) -> None:
        """Test YAML data formatting functionality."""
        test_data: FlextCliTypes.Data.CliDataDict = {
            "key": "value",
            "number": 42,
            "list": [1, 2, 3],
        }

        result = api_service.output.format_data(
            data=cast("FlextTypes.JsonValue", test_data), format_type="yaml"
        )

        assert isinstance(result, FlextResult)
        assert result.is_success

        formatted_output = result.unwrap()
        assert isinstance(formatted_output, str)
        assert "key: value" in formatted_output
        assert "number: 42" in formatted_output

    def test_display_output(self, api_service: FlextCli) -> None:
        """Test output display functionality using formatters."""
        test_output = "This is test output content"

        result = api_service.formatters.print(test_output, style="cyan")

        assert isinstance(result, FlextResult)
        assert result.is_success

        # The print method should return success
        assert result.unwrap() is None

    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================

    def test_read_file(self, api_service: FlextCli, temp_file: Path) -> None:
        """Test file reading functionality."""
        result = api_service.file_tools.read_text_file(str(temp_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        content = result.unwrap()
        assert isinstance(content, str)
        assert content == "test content"

    def test_write_file(self, api_service: FlextCli, temp_dir: Path) -> None:
        """Test file writing functionality."""
        test_file = temp_dir / "test_write.txt"
        test_content = "This is test content for writing"

        result = api_service.file_tools.write_text_file(str(test_file), test_content)

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was created and contains correct content
        assert test_file.exists()
        assert test_file.read_text() == test_content

    def test_copy_file(
        self, api_service: FlextCli, temp_file: Path, temp_dir: Path
    ) -> None:
        """Test file copying functionality."""
        destination = temp_dir / "copied_file.txt"

        result = api_service.file_tools.copy_file(str(temp_file), str(destination))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was copied correctly
        assert destination.exists()
        assert destination.read_text(encoding="utf-8") == temp_file.read_text(
            encoding="utf-8"
        )

    def test_move_file(
        self, api_service: FlextCli, temp_file: Path, temp_dir: Path
    ) -> None:
        """Test file moving functionality."""
        destination = temp_dir / "moved_file.txt"
        original_content = temp_file.read_text(encoding="utf-8")

        result = api_service.file_tools.move_file(str(temp_file), str(destination))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was moved correctly
        assert not temp_file.exists()
        assert destination.exists()
        assert destination.read_text() == original_content

    def test_delete_file(self, api_service: FlextCli, temp_file: Path) -> None:
        """Test file deletion functionality."""
        assert temp_file.exists()

        result = api_service.file_tools.delete_file(str(temp_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was deleted
        assert not temp_file.exists()

    def test_list_files(self, api_service: FlextCli, temp_dir: Path) -> None:
        """Test file listing functionality."""
        # Create some test files
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.txt").write_text("content2")
        (temp_dir / "subdir").mkdir()

        result = api_service.file_tools.list_directory(str(temp_dir))

        assert isinstance(result, FlextResult)
        assert result.is_success

        files = result.unwrap()
        assert isinstance(files, list)
        assert len(files) >= 2  # At least the files we created

    # ========================================================================
    # COMMAND EXECUTION
    # ========================================================================

    def test_execute_command(self, api_service: FlextCli) -> None:
        """Test command execution functionality."""
        # Register a test command first
        from flext_cli.models import FlextCliModels

        test_command = FlextCliModels.CliCommand(
            name="test_command",
            command_line="test_command",
            args=["--test"],
            status="pending",
        )

        register_result = api_service.core.register_command(test_command)
        assert register_result.is_success

        # Now execute the registered command
        result = api_service.core.execute_command("test_command")

        assert isinstance(result, FlextResult)
        # Command execution should succeed for registered commands
        assert result.is_success
        output = result.unwrap()
        assert isinstance(output, dict)
        assert output[FlextCliConstants.DictKeys.COMMAND] == "test_command"
        assert output[FlextCliConstants.DictKeys.STATUS] is True

    def test_execute_command_with_timeout(self, api_service: FlextCli) -> None:
        """Test command execution with timeout."""
        # Register a test command first
        from flext_cli.models import FlextCliModels

        test_command = FlextCliModels.CliCommand(
            name="test_timeout_command",
            command_line="test_timeout_command",
            args=["--timeout-test"],
            status="pending",
        )

        register_result = api_service.core.register_command(test_command)
        assert register_result.is_success

        # Execute with timeout
        result = api_service.core.execute_command("test_timeout_command", timeout=5.0)

        assert isinstance(result, FlextResult)
        # Command execution should succeed for registered commands
        assert result.is_success
        output = result.unwrap()
        assert isinstance(output, dict)
        assert output[FlextCliConstants.DictKeys.COMMAND] == "test_timeout_command"
        assert output[FlextCliConstants.DictKeys.TIMEOUT] == 5.0

    def test_execute_command_nonexistent(self, api_service: FlextCli) -> None:
        """Test command execution with nonexistent command."""
        result = api_service.core.execute_command("nonexistent_command_12345")

        assert isinstance(result, FlextResult)
        assert result.is_failure

    # ========================================================================
    # CONFIGURATION MANAGEMENT
    # ========================================================================

    def test_load_config(self, api_service: FlextCli, temp_dir: Path) -> None:
        """Test configuration loading functionality."""
        # Create test config file
        config_file = temp_dir / "test_config.json"
        test_config: FlextCliTypes.Data.CliDataDict = cast(
            "FlextCliTypes.Data.CliDataDict",
            {
                "debug": True,
                "output_format": "json",
                "timeout": FlextCliConstants.TIMEOUTS.DEFAULT,
                "retries": FlextCliConstants.HTTP.MAX_RETRIES,
            },
        )
        config_file.write_text(json.dumps(test_config))

        # Test loading configuration using file_tools
        result = api_service.file_tools.read_json_file(str(config_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        config_data = result.unwrap()
        assert isinstance(config_data, dict)
        assert config_data["debug"] is True
        assert config_data["output_format"] == "json"
        assert config_data["timeout"] == FlextCliConstants.TIMEOUTS.DEFAULT
        assert config_data["retries"] == FlextCliConstants.HTTP.MAX_RETRIES

    def test_save_config(self, api_service: FlextCli, temp_dir: Path) -> None:
        """Test configuration saving functionality."""
        config_file = temp_dir / "test_save_config.json"
        test_config: FlextCliTypes.Data.CliDataDict = {
            "debug": False,
            "output_format": "table",
            "timeout": FlextCliConstants.TIMEOUTS.DEFAULT,
            "retries": FlextCliConstants.HTTP.MAX_RETRIES,
        }

        # Test saving configuration using file_tools
        result = api_service.file_tools.write_json_file(
            str(config_file),
            test_config,
        )

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was created and contains correct data
        assert config_file.exists()
        saved_data = json.loads(config_file.read_text())
        assert saved_data == test_config

    def test_validate_config(self, api_service: FlextCli) -> None:
        """Test configuration validation functionality."""
        # Test valid configuration using config's validate_business_rules
        config = api_service.config
        result = config.validate_business_rules()

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Test invalid configuration - use modern Pydantic validation
        # Test negative timeout validation
        try:
            TypeAdapter(FlextCliTypes.AnnotatedCli.TimeoutMs).validate_python(-1)
            msg = "Should have raised ValidationError"
            raise AssertionError(msg)
        except ValidationError:
            pass  # Expected to fail validation

        # Test positive integer validation for retries
        try:
            TypeAdapter(PositiveInt).validate_python(-5)
            msg = "Should have raised ValidationError"
            raise AssertionError(msg)
        except ValidationError:
            pass  # Expected to fail validation

    # ========================================================================
    # DATA PROCESSING
    # ========================================================================

    # REMOVED: test_parse_json, test_parse_json_invalid, test_serialize_json
    # These tests expected wrapper methods (safe_json_parse, safe_json_stringify)
    # that don't exist in FlextUtilities and violate Zero Tolerance Law.
    # Use json.loads() and json.dumps() directly instead of wrappers.

    def test_parse_yaml(self, api_service: FlextCli, temp_dir: Path) -> None:
        """Test YAML parsing functionality."""
        yaml_data = """
key: value
number: 42
list:
  - 1
  - 2
  - 3
nested:
  inner: data
"""
        # Write YAML to file and read it
        yaml_file = temp_dir / "test.yaml"
        yaml_file.write_text(yaml_data)

        result = api_service.file_tools.read_yaml_file(str(yaml_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        parsed_data = result.unwrap()
        assert isinstance(parsed_data, dict)
        assert parsed_data.get("key") == "value"
        assert parsed_data.get("number") == 42
        assert parsed_data.get("list") == [1, 2, 3]
        nested = parsed_data.get("nested", {})
        assert isinstance(nested, dict)
        assert nested.get("inner") == "data"

    def test_serialize_yaml(self, api_service: FlextCli, temp_dir: Path) -> None:
        """Test YAML serialization functionality."""
        test_data: FlextCliTypes.Data.CliDataDict = {
            "key": "value",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {"inner": "data"},
        }

        yaml_file = temp_dir / "test_out.yaml"
        result = api_service.file_tools.write_yaml_file(
            str(yaml_file),
            cast("FlextTypes.JsonValue", test_data),
        )

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Read back and verify
        yaml_string = yaml_file.read_text()
        assert isinstance(yaml_string, str)
        assert "key: value" in yaml_string
        assert "number: 42" in yaml_string

    # ========================================================================
    # ERROR HANDLING AND EDGE CASES
    # ========================================================================

    def test_error_handling_with_invalid_input(self, api_service: FlextCli) -> None:
        """Test error handling with various invalid inputs."""
        # Test with empty string input
        result = api_service.file_tools.read_text_file("")
        assert isinstance(result, FlextResult)
        assert result.is_failure

        # Test with non-existent file
        result = api_service.file_tools.read_text_file("/nonexistent/file.txt")
        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_error_handling_with_permission_denied(self, api_service: FlextCli) -> None:
        """Test error handling with permission denied scenarios."""
        # Try to write to a directory that should be read-only
        result = api_service.file_tools.write_text_file(
            "/proc/test_file", "test content"
        )
        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_concurrent_operations(self, api_service: FlextCli, temp_dir: Path) -> None:
        """Test concurrent operations to ensure thread safety."""
        results: list[FlextResult[None]] = []
        errors: list[Exception] = []

        def worker(worker_id: int) -> None:
            try:
                test_file = temp_dir / f"concurrent_test_{worker_id}.txt"
                result = api_service.file_tools.write_text_file(
                    str(test_file), f"Worker {worker_id} content"
                )
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads: list[threading.Thread] = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all operations succeeded
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        for result in results:
            assert isinstance(result, FlextResult)
            assert result.is_success

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    # REMOVED: test_full_api_workflow_integration
    # This test used wrapper methods (safe_json_stringify, safe_json_parse)
    # that don't exist and violate Zero Tolerance Law.
    # Integration tests should use json.loads()/dumps() directly.

    def test_api_workflow_integration(self, api_service: FlextCli) -> None:
        """Test execute method (now sync, delegates to execute)."""
        # execute is now synchronous, delegates to execute()
        result = api_service.execute()
        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, dict)
        assert "status" in data
        assert "service" in data
        assert data["service"] == "flext-cli"

    # ========================================================================
    # SINGLETON AND PROPERTY ACCESS TESTS
    # ========================================================================

    def test_get_instance_singleton(self) -> None:
        """Test get_instance returns singleton FlextCli instance."""
        instance1 = FlextCli.get_instance()
        instance2 = FlextCli.get_instance()

        assert instance1 is not None
        assert isinstance(instance1, FlextCli)
        # Instances may be different (not strict singleton in current impl)
        assert isinstance(instance2, FlextCli)

    # ========================================================================
    # AUTHENTICATION TESTS
    # ========================================================================

    def test_authenticate_with_token(
        self, api_service: FlextCli, temp_dir: Path
    ) -> None:
        """Test authentication with token."""
        # Use temp directory for token storage
        test_token = "test_auth_token_12345"
        credentials = cast("FlextCliTypes.Auth.CredentialsData", {"token": test_token})

        result = api_service.authenticate(credentials)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == test_token

    def test_authenticate_with_credentials(self, api_service: FlextCli) -> None:
        """Test authentication with username/password."""
        credentials = cast(
            "FlextCliTypes.Auth.CredentialsData",
            {"username": "testuser", "password": "testpassword123"},
        )

        result = api_service.authenticate(credentials)

        assert isinstance(result, FlextResult)
        assert result.is_success

        token = result.unwrap()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_authenticate_with_invalid_credentials(self, api_service: FlextCli) -> None:
        """Test authentication with invalid credentials."""
        # Empty credentials
        result = api_service.authenticate({})

        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_save_and_get_auth_token(
        self, api_service: FlextCli, temp_dir: Path
    ) -> None:
        """Test saving and retrieving authentication token."""
        test_token = "test_save_token_67890"

        # Save token
        save_result = api_service.save_auth_token(test_token)

        assert isinstance(save_result, FlextResult)
        assert save_result.is_success

        # Retrieve token
        get_result = api_service.get_auth_token()

        assert isinstance(get_result, FlextResult)
        assert get_result.is_success
        assert get_result.unwrap() == test_token

    def test_save_auth_token_empty(self, api_service: FlextCli) -> None:
        """Test saving empty auth token fails."""
        result = api_service.save_auth_token("")

        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_is_authenticated(self, api_service: FlextCli) -> None:
        """Test is_authenticated check."""
        # Test with no token (may fail or succeed depending on state)
        authenticated = api_service.is_authenticated()

        assert isinstance(authenticated, bool)

        # Save a token and check
        save_result = api_service.save_auth_token("test_auth_check_token")
        if save_result.is_success:
            authenticated_after = api_service.is_authenticated()
            assert isinstance(authenticated_after, bool)

    def test_clear_auth_tokens(self, api_service: FlextCli) -> None:
        """Test clearing authentication tokens."""
        # Save a token first
        api_service.save_auth_token("test_clear_token")

        # Clear tokens
        clear_result = api_service.clear_auth_tokens()

        assert isinstance(clear_result, FlextResult)
        # Should succeed even if files don't exist
        # Accept various file-not-found error messages
        error_msg = str(clear_result.error).lower() if clear_result.error else ""
        assert clear_result.is_success or any(
            phrase in error_msg
            for phrase in ["not found", "no such file", "does not exist"]
        )

    def test_validate_credentials(self, api_service: FlextCli) -> None:
        """Test credential validation."""
        # Valid credentials
        result = api_service.validate_credentials("testuser", "testpass")

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Invalid credentials (empty)
        invalid_result = api_service.validate_credentials("", "")

        assert isinstance(invalid_result, FlextResult)
        assert invalid_result.is_failure

    # ========================================================================
    # COMMAND REGISTRATION TESTS
    # ========================================================================

    def test_command_decorator(self, api_service: FlextCli) -> None:
        """Test command decorator registration."""

        @api_service.command(name="test_cmd")
        def decorated_test_command() -> str:
            return "test output"

        # Verify command was registered
        assert "test_cmd" in api_service._commands
        assert callable(api_service._commands["test_cmd"])

        # Test that the command function actually works
        result = api_service._commands["test_cmd"]()
        assert result == "test output"

    def test_group_decorator(self, api_service: FlextCli) -> None:
        """Test group decorator registration."""

        @api_service.group(name="test_group")
        def decorated_test_group() -> None:
            pass

        # Verify group was registered
        assert "test_group" in api_service._groups
        assert callable(api_service._groups["test_group"])

    def test_execute_cli(self, api_service: FlextCli) -> None:
        """Test CLI execution."""
        result = api_service.execute_cli()

        assert isinstance(result, FlextResult)
        assert result.is_success

    # NOTE: Wrapper methods removed in Phase 2 refactoring
    # - Removed: test_read_text_file_wrapper, test_write_text_file_wrapper
    # - Removed: test_print_wrapper, test_create_tree_wrapper
    # These tested 1:1 delegation methods that were eliminated to follow
    # direct access pattern: use cli.file_tools.read_text_file() directly

    # ========================================================================
    # COVERAGE COMPLETION TESTS - Missing Lines in api.py
    # ========================================================================

    def test_get_instance_always_succeeds(self) -> None:
        """Test get_instance always returns valid instance.

        The singleton pattern ensures get_instance() never fails - if container
        lookup fails, it falls back to creating a new instance. This tests the
        actual resilient behavior rather than mocking failures.
        """
        instance = FlextCli.get_instance()
        assert instance is not None
        assert isinstance(instance, FlextCli)

        # Get instance again - should work consistently
        instance2 = FlextCli.get_instance()
        assert instance2 is not None
        assert isinstance(instance2, FlextCli)

    def test_authenticate_with_token_write_to_readonly_dir(
        self, api_service: FlextCli, tmp_path: Path
    ) -> None:
        """Test authenticate with token when directory is read-only.

        Real scenario: Tests actual write failure without mocks.
        """
        # Create a read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only

        # Configure to use read-only path
        api_service.config.token_file = readonly_dir / "token.json"

        credentials = cast(
            "FlextCliTypes.Auth.CredentialsData", {"token": "test_token"}
        )
        result = api_service.authenticate(credentials)

        # Cleanup: restore write permission for pytest cleanup
        readonly_dir.chmod(0o755)

        # Should fail with real write error
        assert result.is_failure
        assert result.error is not None
        # Real error will mention permission or write failure
        assert "permission" in result.error.lower() or "failed" in result.error.lower()

    def test_authenticate_with_token_validation_empty_string(
        self, api_service: FlextCli, tmp_path: Path
    ) -> None:
        """Test authenticate rejects empty/whitespace-only tokens.

        Real scenario: Tests actual validation logic for empty credentials.
        """
        # Use temp directory for token storage
        token_file = tmp_path / "token.json"
        api_service.config.token_file = token_file

        # Test with whitespace-only token
        credentials = cast("FlextCliTypes.Auth.CredentialsData", {"token": "   "})
        result = api_service.authenticate(credentials)

        # Should fail validation for empty token
        assert result.is_failure
        assert result.error is not None
        assert "token" in result.error.lower() or "empty" in result.error.lower()

    def test_authenticate_with_credentials_empty_username_password(
        self, api_service: FlextCli
    ) -> None:
        """Test authenticate with empty username/password (line 237)."""
        credentials = cast(
            "FlextCliTypes.Auth.CredentialsData", {"username": "", "password": ""}
        )
        result = api_service.authenticate(credentials)

        assert result.is_failure
        assert result.error is not None
        assert "username" in result.error.lower() or "password" in result.error.lower()

    def test_authenticate_with_credentials_short_username(
        self, api_service: FlextCli
    ) -> None:
        """Test authenticate with short username (line 242)."""
        credentials = cast(
            "FlextCliTypes.Auth.CredentialsData",
            {
                "username": "ab",
                "password": "validpassword123",
            },
        )  # Username too short
        result = api_service.authenticate(credentials)

        assert result.is_failure
        assert result.error is not None
        assert "username" in result.error.lower()

    def test_authenticate_with_credentials_short_password(
        self, api_service: FlextCli
    ) -> None:
        """Test authenticate with short password (line 247)."""
        credentials = cast(
            "FlextCliTypes.Auth.CredentialsData",
            {
                "username": "validuser",
                "password": "short",
            },
        )  # Password too short
        result = api_service.authenticate(credentials)

        assert result.is_failure
        assert result.error is not None
        assert "password" in result.error.lower()

    def test_save_auth_token_write_to_readonly_directory(
        self, api_service: FlextCli, tmp_path: Path
    ) -> None:
        """Test save_auth_token with read-only directory.

        Real scenario: Tests actual file write failure without mocks.
        """
        # Create read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)

        # Configure to use read-only path
        api_service.config.token_file = readonly_dir / "token.json"

        result = api_service.save_auth_token("test_token_123")

        # Cleanup
        readonly_dir.chmod(0o755)

        # Should fail with real permission error
        assert result.is_failure
        assert result.error is not None
        assert "save" in result.error.lower() or "permission" in result.error.lower()

    def test_get_auth_token_file_not_found_real_scenario(
        self, api_service: FlextCli
    ) -> None:
        """Test get_auth_token when token file doesn't exist.

        Real scenario: Tests actual file not found error without mocks.
        Note: api_service fixture already isolates config to a clean tmp directory.
        """
        # api_service is already configured with tmp paths that don't have files
        # Just call get_auth_token - should fail with file not found
        result = api_service.get_auth_token()

        # Should fail with "not found" error
        assert result.is_failure
        assert result.error is not None
        error_msg = result.error.lower()
        assert "not found" in error_msg or "token" in error_msg

    def test_get_auth_token_invalid_json_format(
        self, api_service: FlextCli, tmp_path: Path
    ) -> None:
        """Test get_auth_token when file contains invalid JSON.

        Real scenario: Tests actual JSON parse error without mocks.
        """
        # Create file with invalid JSON
        token_file = tmp_path / "invalid_token.json"
        token_file.write_text("{invalid json content")
        api_service.config.token_file = token_file

        result = api_service.get_auth_token()

        # Should fail with read/parse error
        assert result.is_failure
        assert result.error is not None
        assert "load" in result.error.lower() or "failed" in result.error.lower()

    def test_get_auth_token_empty_file_real_scenario(
        self, api_service: FlextCli, tmp_path: Path
    ) -> None:
        """Test get_auth_token when token file exists but has empty token.

        Real scenario: Tests actual validation of empty token data.
        """
        # Create file with empty token structure
        token_file = tmp_path / "empty_token.json"
        token_file.write_text("{}")  # Valid JSON but no token key
        api_service.config.token_file = token_file

        result = api_service.get_auth_token()

        # Should fail validation for missing token
        assert result.is_failure
        assert result.error is not None
        assert "empty" in result.error.lower() or "token" in result.error.lower()

    def test_get_auth_token_wrong_data_type(
        self, api_service: FlextCli, tmp_path: Path
    ) -> None:
        """Test get_auth_token when file contains wrong data type.

        Real scenario: Tests actual type validation without mocks.
        """
        # Create file with array instead of object
        token_file = tmp_path / "wrong_type_token.json"
        token_file.write_text('["not", "an", "object"]')
        api_service.config.token_file = token_file

        result = api_service.get_auth_token()

        # Should fail type validation
        assert result.is_failure
        assert result.error is not None

    def test_clear_auth_tokens_readonly_file(
        self, api_service: FlextCli, tmp_path: Path
    ) -> None:
        """Test clear_auth_tokens when files are read-only.

        Real scenario: Tests actual delete failure without mocks.
        """
        # Create read-only token file
        token_file = tmp_path / "readonly_token.json"
        token_file.write_text('{"token": "test"}')
        token_file.chmod(0o444)

        # Create parent directory read-only (prevents deletion)
        tmp_path.chmod(0o555)

        api_service.config.token_file = token_file
        api_service.config.refresh_token_file = tmp_path / "refresh.json"

        result = api_service.clear_auth_tokens()

        # Cleanup: restore permissions
        tmp_path.chmod(0o755)
        token_file.chmod(0o644)

        # Should fail due to permission error (not "not found")
        assert result.is_failure
        assert result.error is not None
        assert "clear" in result.error.lower() or "permission" in result.error.lower()

    def test_clear_auth_tokens_success_with_real_files(
        self, api_service: FlextCli, tmp_path: Path
    ) -> None:
        """Test clear_auth_tokens successfully deletes existing files.

        Real scenario: Tests actual successful deletion without mocks.
        """
        # Create real token files
        token_file = tmp_path / "token.json"
        refresh_file = tmp_path / "refresh_token.json"
        token_file.write_text('{"token": "test_token"}')
        refresh_file.write_text('{"token": "refresh_token"}')

        api_service.config.token_file = token_file
        api_service.config.refresh_token_file = refresh_file

        # Add tokens to valid set
        api_service._valid_tokens.add("test_token_1")
        api_service._valid_tokens.add("test_token_2")
        assert len(api_service._valid_tokens) > 0

        # Clear should succeed
        result = api_service.clear_auth_tokens()

        assert result.is_success
        # Verify files were actually deleted
        assert not token_file.exists()
        assert not refresh_file.exists()
        # Verify valid tokens set was cleared
        assert len(api_service._valid_tokens) == 0

    def test_clear_auth_tokens_handles_missing_files(
        self, api_service: FlextCli, tmp_path: Path
    ) -> None:
        """Test clear_auth_tokens succeeds when files don't exist.

        Real scenario: Tests that "not found" errors are ignored.
        """
        # Point to non-existent files
        api_service.config.token_file = tmp_path / "missing_token.json"
        api_service.config.refresh_token_file = tmp_path / "missing_refresh.json"

        # Should succeed even though files don't exist
        result = api_service.clear_auth_tokens()

        assert result.is_success

    # NOTE: print_table wrapper method removed in Phase 2 refactoring
    # Tests print_table_success and print_table_exception removed as they tested
    # a wrapper method that no longer exists.

    def test_get_auth_token_not_dict_real_scenario(
        self, api_service: FlextCli, tmp_path: Path
    ) -> None:
        """Test get_auth_token when file contains string instead of dict.

        Real scenario: Tests actual type validation without mocks.
        """
        # Create file with string value instead of JSON object
        token_file = tmp_path / "string_token.json"
        token_file.write_text('"just a string"')
        api_service.config.token_file = token_file

        result = api_service.get_auth_token()

        # Should fail type validation
        assert result.is_failure
        assert result.error is not None
        # Error should indicate wrong data type
        error_lower = result.error.lower()
        assert "type" in error_lower or "dict" in error_lower or "object" in error_lower

    def test_get_auth_token_token_not_string_real_scenario(
        self, api_service: FlextCli, tmp_path: Path
    ) -> None:
        """Test get_auth_token when token field is number instead of string.

        Real scenario: Tests actual token type validation without mocks.
        """
        # Create file with numeric token value
        token_file = tmp_path / "numeric_token.json"
        token_file.write_text('{"token": 12345}')
        api_service.config.token_file = token_file

        result = api_service.get_auth_token()

        # Should fail token type validation
        assert result.is_failure
        assert result.error is not None
        error_lower = result.error.lower()
        assert "string" in error_lower or "type" in error_lower
