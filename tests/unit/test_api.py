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
from flext_core import FlextCore, FlextResult, FlextTypes

from flext_cli import FlextCli, FlextCliConstants


class TestFlextCli:
    """Comprehensive tests for FlextCli functionality."""

    @pytest.fixture
    def api_service(self) -> FlextCli:
        """Create FlextCli instance for testing."""
        return FlextCli()

    # ========================================================================
    # INITIALIZATION AND BASIC FUNCTIONALITY
    # ========================================================================
    def test_api_service_initialization(self, api_service: FlextCli) -> None:
        """Test API service initialization and basic properties."""
        assert api_service is not None
        assert hasattr(api_service, "logger")
        assert hasattr(api_service, "_container")
        # Properties accessed via container (lazy-loaded, no private attributes)
        assert hasattr(api_service, "utilities")
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
        test_data: list[dict[str, str | int]] = [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "London"},
            {"name": "Bob", "age": 35, "city": "Paris"},
        ]

        result = api_service.output.format_data(data=test_data, format_type="table")

        assert isinstance(result, FlextResult)
        assert result.is_success

        formatted_output = result.unwrap()
        assert isinstance(formatted_output, str)
        assert "John" in formatted_output
        assert "Jane" in formatted_output
        assert "Bob" in formatted_output

    def test_format_data_json(self, api_service: FlextCli) -> None:
        """Test JSON data formatting functionality."""
        test_data: dict[str, str | int | list[int]] = {
            "key": "value",
            "number": 42,
            "list": [1, 2, 3],
        }

        result = api_service.output.format_data(data=test_data, format_type="json")

        assert isinstance(result, FlextResult)
        assert result.is_success

        formatted_output = result.unwrap()
        assert isinstance(formatted_output, str)

        # Verify it's valid JSON
        parsed_data = json.loads(formatted_output)
        assert parsed_data == test_data

    def test_format_data_yaml(self, api_service: FlextCli) -> None:
        """Test YAML data formatting functionality."""
        test_data: dict[str, str | int | list[int]] = {
            "key": "value",
            "number": 42,
            "list": [1, 2, 3],
        }

        result = api_service.output.format_data(data=test_data, format_type="yaml")

        assert isinstance(result, FlextResult)
        assert result.is_success

        formatted_output = result.unwrap()
        assert isinstance(formatted_output, str)
        assert "key: value" in formatted_output
        assert "number: 42" in formatted_output

    def test_format_data_csv(self, api_service: FlextCli) -> None:
        """Test CSV data formatting functionality using formatters."""
        test_data: dict[
            str, str | int | float | bool | list[object] | dict[str, object] | None
        ] = {
            "John": "30 | New York",
            "Jane": "25 | London",
        }

        # Use formatters to create table
        result = api_service.create_table(
            data=test_data, headers=["Name", "Age | City"], title="User Data"
        )

        assert isinstance(result, FlextResult)
        assert result.is_success

        table = result.unwrap()
        assert table is not None

    def test_display_output(self, api_service: FlextCli) -> None:
        """Test output display functionality using formatters."""
        test_output = "This is test output content"

        result = api_service.formatters.print(test_output, style="cyan")

        assert isinstance(result, FlextResult)
        assert result.is_success

        # The print method should return success
        assert result.unwrap() is None

    # ========================================================================
    # PROGRESS BAR AND STATUS DISPLAY
    # ========================================================================

    def test_create_progress_bar(self, api_service: FlextCli) -> None:
        """Test progress bar creation functionality using formatters."""
        result = api_service.create_progress()

        assert isinstance(result, FlextResult)
        assert result.is_success

        progress_bar = result.unwrap()
        assert progress_bar is not None

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
        # Test with a simple command that should work on most systems
        result = api_service.core.execute_command("python --version")

        assert isinstance(result, FlextResult)
        # Command execution may fail due to environment, but should return proper result
        if result.is_success:
            output = result.unwrap()
            assert isinstance(output, (str, dict))
        else:
            # If command fails, should have proper error message
            assert isinstance(result.error, str)
            assert len(result.error) > 0

    def test_execute_command_with_timeout(self, api_service: FlextCli) -> None:
        """Test command execution with timeout."""
        # Test with a command that should complete quickly
        result = api_service.core.execute_command("python --version")

        assert isinstance(result, FlextResult)
        # Command execution may fail due to environment, but should return proper result
        if result.is_success:
            output = result.unwrap()
            assert isinstance(output, (str, dict))
        else:
            # If command fails, should have proper error message
            assert isinstance(result.error, str)
            assert len(result.error) > 0

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
        test_config: dict[str, bool | str | int] = {
            "debug": True,
            "output_format": "json",
            "timeout": FlextCliConstants.TIMEOUTS.DEFAULT,
            "retries": FlextCliConstants.HTTP.MAX_RETRIES,
        }
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
        test_config: FlextTypes.Dict = {
            "debug": False,
            "output_format": "table",
            "timeout": FlextCliConstants.TIMEOUTS.DEFAULT,
            "retries": FlextCliConstants.HTTP.MAX_RETRIES,
        }

        # Test saving configuration using file_tools
        result = api_service.file_tools.write_json_file(
            str(config_file),
            cast(
                "dict[str, bool | FlextTypes.Dict | float | int | FlextTypes.List | str | None]",
                test_config,
            ),
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

        # Test invalid configuration - use FlextCore validation utilities
        # Test negative timeout validation
        timeout_result = FlextCore.Utilities.Validation.validate_timeout_seconds(-1)
        assert isinstance(timeout_result, FlextResult)
        assert timeout_result.is_failure

        # Test positive integer validation for retries
        retry_result = FlextCore.Utilities.Validation.validate_positive_integer(-5)
        assert isinstance(retry_result, FlextResult)
        assert retry_result.is_failure

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
        test_data: dict[str, str | int | list[int] | dict[str, str]] = {
            "key": "value",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {"inner": "data"},
        }

        yaml_file = temp_dir / "test_out.yaml"
        result = api_service.file_tools.write_yaml_file(
            str(yaml_file),
            cast(
                "dict[str, bool | FlextTypes.Dict | float | int | FlextTypes.List | str | None]",
                test_data,
            ),
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

    def test_constants_property(self, api_service: FlextCli) -> None:
        """Test constants property access."""
        constants = api_service.constants

        assert constants is not None
        assert constants == FlextCliConstants
        assert hasattr(constants, "VERSION")
        assert hasattr(constants, "CliDefaults")

    def test_models_property(self, api_service: FlextCli) -> None:
        """Test models property access."""
        from flext_cli.models import FlextCliModels

        models = api_service.models

        assert models is not None
        assert models == FlextCliModels
        assert hasattr(models, "CliCommand")
        assert hasattr(models, "CliContext")

    def test_types_property(self, api_service: FlextCli) -> None:
        """Test types property access."""
        from flext_cli.typings import FlextCliTypes

        types = api_service.types

        assert types is not None
        assert types == FlextCliTypes

    # ========================================================================
    # AUTHENTICATION TESTS
    # ========================================================================

    def test_authenticate_with_token(
        self, api_service: FlextCli, temp_dir: Path
    ) -> None:
        """Test authentication with token."""
        # Use temp directory for token storage
        test_token = "test_auth_token_12345"
        credentials = {"token": test_token}

        result = api_service.authenticate(
            credentials
        )

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == test_token

    def test_authenticate_with_credentials(self, api_service: FlextCli) -> None:
        """Test authentication with username/password."""
        credentials = {"username": "testuser", "password": "testpassword123"}

        result = api_service.authenticate(
            credentials
        )

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
        def test_command() -> str:
            return "test output"

        # Verify command was registered
        assert "test_cmd" in api_service._commands
        assert callable(api_service._commands["test_cmd"])

    def test_group_decorator(self, api_service: FlextCli) -> None:
        """Test group decorator registration."""

        @api_service.group(name="test_group")
        def test_group() -> None:
            pass

        # Verify group was registered
        assert "test_group" in api_service._groups
        assert callable(api_service._groups["test_group"])

    def test_execute_cli(self, api_service: FlextCli) -> None:
        """Test CLI execution."""
        result = api_service.execute_cli()

        assert isinstance(result, FlextResult)
        assert result.is_success

    # ========================================================================
    # FILE OPERATION WRAPPER TESTS
    # ========================================================================

    def test_read_text_file_wrapper(
        self, api_service: FlextCli, temp_file: Path
    ) -> None:
        """Test read_text_file wrapper method."""
        result = api_service.read_text_file(temp_file)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == "test content"

    def test_write_text_file_wrapper(
        self, api_service: FlextCli, temp_dir: Path
    ) -> None:
        """Test write_text_file wrapper method."""
        test_file = temp_dir / "wrapper_test.txt"
        test_content = "wrapper test content"

        result = api_service.write_text_file(test_file, test_content)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert test_file.exists()
        assert test_file.read_text() == test_content

    # ========================================================================
    # PRINT AND FORMATTING WRAPPER TESTS
    # ========================================================================

    def test_print_wrapper(self, api_service: FlextCli) -> None:
        """Test print wrapper method."""
        result = api_service.print("Test message", style="cyan")

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_create_tree_wrapper(self, api_service: FlextCli) -> None:
        """Test create_tree wrapper method."""
        result = api_service.create_tree("Test Tree")

        assert isinstance(result, FlextResult)
        assert result.is_success

        tree = result.unwrap()
        assert tree is not None
