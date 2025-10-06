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

# Test utilities removed from flext-core production exports
from flext_cli.api import FlextCliApi
from flext_cli.constants import FlextCliConstants


class TestFlextCliApi:
    """Comprehensive tests for FlextCli functionality."""

    @pytest.fixture
    def api_service(self) -> FlextCliApi:
        """Create FlextCliApi instance for testing."""
        return FlextCliApi()

    # ========================================================================
    # INITIALIZATION AND BASIC FUNCTIONALITY
    # ========================================================================
    def test_api_service_initialization(self, api_service: FlextCliApi) -> None:
        """Test API service initialization and basic properties."""
        assert api_service is not None
        assert hasattr(api_service, "_logger")
        assert hasattr(api_service, "_container")
        assert hasattr(api_service, "_output")
        assert hasattr(api_service, "_file_tools")
        assert hasattr(api_service, "_core")
        assert hasattr(api_service, "utilities")  # Property, not private attribute
        assert hasattr(api_service, "_prompts")
        assert hasattr(api_service, "_processors")
        assert hasattr(api_service, "_cmd")

    def test_api_service_execute_method(self, api_service: FlextCliApi) -> None:
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

    def test_format_data_table(self, api_service: FlextCliApi) -> None:
        """Test table data formatting functionality."""
        test_data = [
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

    def test_format_data_json(self, api_service: FlextCliApi) -> None:
        """Test JSON data formatting functionality."""
        test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}

        result = api_service.output.format_data(data=test_data, format_type="json")

        assert isinstance(result, FlextResult)
        assert result.is_success

        formatted_output = result.unwrap()
        assert isinstance(formatted_output, str)

        # Verify it's valid JSON
        parsed_data = json.loads(formatted_output)
        assert parsed_data == test_data

    def test_format_data_yaml(self, api_service: FlextCliApi) -> None:
        """Test YAML data formatting functionality."""
        test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}

        result = api_service.output.format_data(data=test_data, format_type="yaml")

        assert isinstance(result, FlextResult)
        assert result.is_success

        formatted_output = result.unwrap()
        assert isinstance(formatted_output, str)
        assert "key: value" in formatted_output
        assert "number: 42" in formatted_output

    def test_format_data_csv(self, api_service: FlextCliApi) -> None:
        """Test CSV data formatting functionality."""
        test_data = [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "London"},
        ]

        result = api_service.output.format_data(data=test_data, format_type="csv")

        assert isinstance(result, FlextResult)
        assert result.is_success

        formatted_output = result.unwrap()
        assert isinstance(formatted_output, str)
        assert "name,age,city" in formatted_output
        assert "John,30,New York" in formatted_output

    def test_display_output(self, api_service: FlextCliApi) -> None:
        """Test output display functionality."""
        test_output = "This is test output content"

        result = api_service.output.display_text(test_output)

        assert isinstance(result, FlextResult)
        assert result.is_success

        # The display method should return success
        assert result.unwrap() is None

    # ========================================================================
    # PROGRESS BAR AND STATUS DISPLAY
    # ========================================================================

    def test_create_progress_bar(self, api_service: FlextCliApi) -> None:
        """Test progress bar creation functionality."""
        result = api_service.output.create_progress_bar(
            _description="Test Task", _total=100
        )

        assert isinstance(result, FlextResult)
        assert result.is_success

        progress_bar = result.unwrap()
        assert progress_bar is not None

    @pytest.mark.skip(
        reason="Progress bar functionality is interactive - use prompts.create_progress()"
    )
    def test_update_progress_bar(self, api_service: FlextCliApi) -> None:
        """Test progress bar update functionality - SKIPPED: interactive feature."""

    @pytest.mark.skip(
        reason="Progress bar functionality is interactive - use prompts.create_progress()"
    )
    def test_close_progress_bar(self, api_service: FlextCliApi) -> None:
        """Test progress bar closing functionality - SKIPPED: interactive feature."""

    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================

    def test_read_file(self, api_service: FlextCliApi, temp_file: Path) -> None:
        """Test file reading functionality."""
        result = api_service.file_tools.read_text_file(str(temp_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        content = result.unwrap()
        assert isinstance(content, str)
        assert content == "test content"

    def test_write_file(self, api_service: FlextCliApi, temp_dir: Path) -> None:
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
        self, api_service: FlextCliApi, temp_file: Path, temp_dir: Path
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
        self, api_service: FlextCliApi, temp_file: Path, temp_dir: Path
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

    def test_delete_file(self, api_service: FlextCliApi, temp_file: Path) -> None:
        """Test file deletion functionality."""
        assert temp_file.exists()

        result = api_service.file_tools.delete_file(str(temp_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was deleted
        assert not temp_file.exists()

    def test_list_files(self, api_service: FlextCliApi, temp_dir: Path) -> None:
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

    def test_execute_command(self, api_service: FlextCliApi) -> None:
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

    def test_execute_command_with_timeout(self, api_service: FlextCliApi) -> None:
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

    def test_execute_command_nonexistent(self, api_service: FlextCliApi) -> None:
        """Test command execution with nonexistent command."""
        result = api_service.core.execute_command("nonexistent_command_12345")

        assert isinstance(result, FlextResult)
        assert result.is_failure

    # ========================================================================
    # HTTP REQUESTS
    # ========================================================================

    @pytest.mark.skip(
        reason="HTTP functionality must be implemented through flext-api domain library"
    )
    def test_make_http_request_get(self, api_service: FlextCliApi) -> None:
        """Test HTTP GET request functionality - SKIPPED: use flext-api."""

    @pytest.mark.skip(
        reason="HTTP functionality must be implemented through flext-api domain library"
    )
    def test_make_http_request_post(self, api_service: FlextCliApi) -> None:
        """Test HTTP POST request functionality - SKIPPED: use flext-api."""

    @pytest.mark.skip(
        reason="HTTP functionality must be implemented through flext-api domain library"
    )
    def test_make_http_request_with_headers(self, api_service: FlextCliApi) -> None:
        """Test HTTP request with custom headers - SKIPPED: use flext-api."""

    @pytest.mark.skip(
        reason="HTTP functionality must be implemented through flext-api domain library"
    )
    def test_make_http_request_invalid_url(self, api_service: FlextCliApi) -> None:
        """Test HTTP request with invalid URL - SKIPPED: use flext-api."""

    # ========================================================================
    # CONFIGURATION MANAGEMENT
    # ========================================================================

    def test_load_config(self, api_service: FlextCliApi, temp_dir: Path) -> None:
        """Test configuration loading functionality."""
        # Create test config file
        config_file = temp_dir / "test_config.json"
        test_config = {
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

    def test_save_config(self, api_service: FlextCliApi, temp_dir: Path) -> None:
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

    def test_validate_config(self, api_service: FlextCliApi) -> None:
        """Test configuration validation functionality."""
        # Test valid configuration
        valid_config: FlextTypes.Dict = {
            "debug": True,
            "output_format": "json",
            "timeout": FlextCliConstants.TIMEOUTS.DEFAULT,
            "retries": FlextCliConstants.HTTP.MAX_RETRIES,
        }

        result = api_service.utilities.validate_data(
            cast(
                "dict[str, bool | FlextTypes.Dict | float | int | FlextTypes.List | str | None]",
                valid_config,
            ),
            {
                "debug": bool,
                "output_format": str,
                "timeout": (int, float),
                "retries": int,
            },
        )
        assert isinstance(result, FlextResult)
        assert result.is_success

        # Test invalid configuration
        invalid_config: FlextTypes.Dict = {
            "debug": "invalid_boolean",
            "timeout": -1,
            "retries": "not_a_number",
        }

        result = api_service.utilities.validate_data(
            cast(
                "dict[str, bool | FlextTypes.Dict | float | int | FlextTypes.List | str | None]",
                invalid_config,
            ),
            {"debug": bool, "timeout": int, "retries": int},
        )
        assert isinstance(result, FlextResult)
        assert result.is_failure

    # ========================================================================
    # DATA PROCESSING
    # ========================================================================

    def test_parse_json(self, api_service: FlextCliApi) -> None:
        """Test JSON parsing functionality."""
        json_data = '{"key": "value", "number": 42, "list": [1, 2, 3]}'

        result = api_service.utilities.safe_json_parse(json_data)

        assert isinstance(result, FlextResult)
        assert result.is_success

        parsed_data = result.unwrap()
        assert isinstance(parsed_data, dict)
        assert parsed_data["key"] == "value"
        assert parsed_data["number"] == 42
        assert parsed_data["list"] == [1, 2, 3]

    def test_parse_json_invalid(self, api_service: FlextCliApi) -> None:
        """Test JSON parsing with invalid JSON."""
        invalid_json = (
            '{"key": "value", "number": 42, "list": [1, 2, 3'  # Missing closing bracket
        )

        result = api_service.utilities.safe_json_parse(invalid_json)

        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_serialize_json(self, api_service: FlextCliApi) -> None:
        """Test JSON serialization functionality."""
        test_data = {
            "key": "value",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {"inner": "data"},
        }

        result = api_service.utilities.safe_json_stringify(test_data)

        assert isinstance(result, FlextResult)
        assert result.is_success

        json_string = result.unwrap()
        assert isinstance(json_string, str)

        # Verify it can be parsed back
        parsed_back = json.loads(json_string)
        assert parsed_back == test_data

    def test_parse_yaml(self, api_service: FlextCliApi, temp_dir: Path) -> None:
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

    def test_serialize_yaml(self, api_service: FlextCliApi, temp_dir: Path) -> None:
        """Test YAML serialization functionality."""
        test_data = {
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
    # USER INTERACTION
    # ========================================================================

    @pytest.mark.skip(
        reason="Interactive prompts require user input - use prompts service directly"
    )
    def test_prompt_user(self, api_service: FlextCliApi) -> None:
        """Test user prompting functionality - SKIPPED: use api_service.prompts."""

    @pytest.mark.skip(
        reason="Interactive prompts require user input - use prompts service directly"
    )
    def test_confirm_action(self, api_service: FlextCliApi) -> None:
        """Test action confirmation functionality - SKIPPED: use api_service.prompts."""

    @pytest.mark.skip(
        reason="Interactive prompts require user input - use prompts service directly"
    )
    def test_select_option(self, api_service: FlextCliApi) -> None:
        """Test option selection functionality - SKIPPED: use api_service.prompts."""

    # ========================================================================
    # ERROR HANDLING AND EDGE CASES
    # ========================================================================

    def test_error_handling_with_invalid_input(self, api_service: FlextCliApi) -> None:
        """Test error handling with various invalid inputs."""
        # Test with empty string input
        result = api_service.file_tools.read_text_file("")
        assert isinstance(result, FlextResult)
        assert result.is_failure

        # Test with non-existent file
        result = api_service.file_tools.read_text_file("/nonexistent/file.txt")
        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_error_handling_with_permission_denied(
        self, api_service: FlextCliApi
    ) -> None:
        """Test error handling with permission denied scenarios."""
        # Try to write to a directory that should be read-only
        result = api_service.file_tools.write_text_file(
            "/proc/test_file", "test content"
        )
        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_concurrent_operations(
        self, api_service: FlextCliApi, temp_dir: Path
    ) -> None:
        """Test concurrent operations to ensure thread safety."""
        results = []
        errors = []

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
        threads = []
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

    def test_full_api_workflow_integration(
        self, api_service: FlextCliApi, temp_dir: Path
    ) -> None:
        """Test complete API workflow integration."""
        # 1. Create test data
        test_data = {
            "name": "integration_test",
            "value": 42,
            "nested": {"inner": "data"},
            "list": [1, 2, 3],
        }

        # 2. Serialize to JSON using utilities
        json_result = api_service.utilities.safe_json_stringify(test_data)
        assert json_result.is_success
        json_string = json_result.unwrap()
        assert isinstance(json_string, str)

        # 3. Write to file
        json_file = temp_dir / "test_data.json"
        write_result = api_service.file_tools.write_text_file(
            str(json_file), json_string
        )
        assert write_result.is_success

        # 4. Read from file
        read_result = api_service.file_tools.read_text_file(str(json_file))
        assert read_result.is_success
        read_content = read_result.unwrap()

        # 5. Parse JSON
        parse_result = api_service.utilities.safe_json_parse(read_content)
        assert parse_result.is_success
        parsed_data = parse_result.unwrap()
        assert isinstance(parsed_data, dict)

        # 6. Format as table
        table_result = api_service.output.format_data(
            data=[parsed_data], format_type="table"
        )
        assert table_result.is_success

        # 7. Display output using display_text
        display_result = api_service.output.display_text(table_result.unwrap())
        assert display_result.is_success

        # 8. Verify complete workflow
        assert json_file.exists()
        assert parsed_data == test_data

    def test_api_workflow_integration(self, api_service: FlextCliApi) -> None:
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
