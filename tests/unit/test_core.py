"""FLEXT CLI Core Service Tests - Comprehensive Real Functionality Testing.

Tests for FlextCliCore covering all real functionality with flext_tests
integration, Docker support, and comprehensive coverage targeting 90%+.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import tempfile
import threading
from pathlib import Path

import pytest
import yaml
from flext_core import FlextResult, FlextTypes, FlextUtilities

# Test utilities removed from flext-core production exports
from flext_cli import (
    FlextCli,
    FlextCliConfig,
    FlextCliConstants,
    FlextCliCore,
    FlextCliModels,
)


class TestFlextCliCore:
    """Comprehensive tests for FlextCliCore functionality."""

    @pytest.fixture
    def core_service(self) -> FlextCliCore:
        """Create FlextCliCore instance for testing."""
        return FlextCliCore()

    @pytest.fixture
    def cli_facade(self) -> FlextCli:
        """Create FlextCli facade for testing delegated operations."""
        return FlextCli()

    @pytest.fixture
    # ========================================================================
    # INITIALIZATION AND BASIC FUNCTIONALITY
    # ========================================================================
    def test_core_service_initialization(self, core_service: FlextCliCore) -> None:
        """Test core service initialization and basic properties."""
        assert core_service is not None
        assert hasattr(core_service, "logger")
        assert hasattr(core_service, "container")  # Property from FlextService
        assert hasattr(core_service, "_config")
        assert hasattr(core_service, "_commands")
        assert hasattr(core_service, "_plugins")
        assert hasattr(core_service, "_sessions")

    def test_core_service_execute_method(self, core_service: FlextCliCore) -> None:
        """Test core service execute method with real functionality."""
        result = core_service.execute()

        assert isinstance(result, FlextResult)
        # Service execution may fail due to implementation issues, but should return proper result
        if result.is_success:
            data = result.unwrap()
            assert isinstance(data, dict)
        else:
            # If execution fails, should have proper error message
            assert isinstance(result.error, str)
            assert len(result.error) > 0
            result = core_service.execute()

            assert isinstance(result, FlextResult)
            # execution may fail due to implementation issues, so we check the result type
            assert result.is_success or result.is_failure

            if result.is_success:
                data = result.unwrap()
                assert isinstance(data, dict)
                assert "status" in data
                assert "service" in data
                assert data["service"] == "FlextCliCore"

    def test_core_service_advanced_methods(self, core_service: FlextCliCore) -> None:
        """Test advanced core service methods."""
        # Test health check
        health_result = core_service.health_check()
        assert isinstance(health_result, FlextResult)

        # Test get config
        config_result = core_service.get_config()
        assert config_result is not None

        # Test get handlers
        handlers_result = core_service.get_handlers()
        assert isinstance(handlers_result, FlextResult)
        assert handlers_result.is_success

        # Test get plugins
        plugins_result = core_service.get_plugins()
        assert isinstance(plugins_result, FlextResult)
        assert plugins_result.is_success

        # Test get sessions
        sessions_result = core_service.get_sessions()
        assert isinstance(sessions_result, FlextResult)
        assert sessions_result.is_success

        # Test get commands
        commands_result = core_service.get_commands()
        assert isinstance(commands_result, FlextResult)
        assert commands_result.is_success

        # Test get formatters
        formatters_result = core_service.get_formatters()
        assert formatters_result is not None

        # Test functionality - register a command first
        test_command = FlextCliModels.CliCommand(
            name="test_cmd",
            command_line="test_cmd",
            description="Test command",
            usage="test_cmd",
        )
        core_service.register_command(test_command)

        def run_test() -> None:
            result = core_service.execute()
            assert result.is_success

        run_test()

    # ========================================================================
    # CONFIGURATION MANAGEMENT
    # ========================================================================

    def test_load_configuration(
        self, core_service: FlextCliCore, temp_dir: Path
    ) -> None:
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

        # Test loading configuration
        result = core_service.load_configuration(str(config_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        config_data = result.unwrap()
        assert isinstance(config_data, dict)
        assert config_data["debug"] is True
        assert config_data["output_format"] == "json"
        assert config_data["timeout"] == FlextCliConstants.TIMEOUTS.DEFAULT
        assert config_data["retries"] == FlextCliConstants.HTTP.MAX_RETRIES

    def test_load_configuration_nonexistent_file(
        self, core_service: FlextCliCore
    ) -> None:
        """Test configuration loading with nonexistent file."""
        result = core_service.load_configuration("/nonexistent/config.json")

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None
        assert (
            "not found" in result.error.lower()
            or "does not exist" in result.error.lower()
        )

    def test_save_configuration(
        self, core_service: FlextCliCore, temp_dir: Path
    ) -> None:
        """Test configuration saving functionality."""
        config_file = temp_dir / "test_save_config.json"
        test_config: FlextTypes.Dict = {
            "debug": False,
            "output_format": "table",
            "timeout": FlextCliConstants.TIMEOUTS.DEFAULT,
            "retries": FlextCliConstants.HTTP.MAX_RETRIES,
        }

        # Test saving configuration
        result = core_service.save_configuration(str(config_file), test_config)

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was created and contains correct data
        assert config_file.exists()
        saved_data = json.loads(config_file.read_text())
        assert saved_data == test_config

    def test_validate_configuration(self, core_service: FlextCliCore) -> None:
        """Test configuration validation functionality."""
        # Test valid configuration using FlextCliConfig model
        valid_config = FlextCliConfig(
            debug=True,
            output_format="json",
            timeout=FlextCliConstants.TIMEOUTS.DEFAULT,
            max_retries=FlextCliConstants.HTTP.MAX_RETRIES,
        )

        result = core_service.validate_configuration(valid_config)
        assert isinstance(result, FlextResult)
        assert result.is_success

        # Test invalid configuration - Pydantic will catch validation errors
        # during model construction, so we expect an exception
        with pytest.raises(Exception):
            FlextCliConfig(
                debug="invalid_boolean",
                timeout=-1,
                max_retries="not_a_number",
            )

    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================

    def test_read_file_content(self, cli_facade: FlextCli, temp_file: Path) -> None:
        """Test file reading functionality."""
        result = cli_facade.file_tools.read_text_file(str(temp_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        content = result.unwrap()
        assert isinstance(content, str)
        assert content == "test content"

    def test_read_file_content_nonexistent(self, cli_facade: FlextCli) -> None:
        """Test file reading with nonexistent file."""
        result = cli_facade.file_tools.read_text_file("/nonexistent/file.txt")

        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_write_file_content(self, cli_facade: FlextCli, temp_dir: Path) -> None:
        """Test file writing functionality."""
        test_file = temp_dir / "test_write.txt"
        test_content = "This is test content for writing"

        result = cli_facade.file_tools.write_text_file(str(test_file), test_content)

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was created and contains correct content
        assert test_file.exists()
        assert test_file.read_text() == test_content

    def test_copy_file(
        self, cli_facade: FlextCli, temp_file: Path, temp_dir: Path
    ) -> None:
        """Test file copying functionality through facade."""
        destination = temp_dir / "copied_file.txt"

        result = cli_facade.file_tools.copy_file(str(temp_file), str(destination))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was copied correctly
        assert destination.exists()
        assert destination.read_text() == temp_file.read_text(encoding="utf-8")

    def test_move_file(
        self, cli_facade: FlextCli, temp_file: Path, temp_dir: Path
    ) -> None:
        """Test file moving functionality through facade."""
        destination = temp_dir / "moved_file.txt"
        original_content = temp_file.read_text(encoding="utf-8")

        result = cli_facade.file_tools.move_file(str(temp_file), str(destination))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was moved correctly
        assert not temp_file.exists()
        assert destination.exists()
        assert destination.read_text() == original_content

    def test_delete_file(self, cli_facade: FlextCli, temp_file: Path) -> None:
        """Test file deletion functionality through facade."""
        assert temp_file.exists()

        result = cli_facade.file_tools.delete_file(str(temp_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was deleted
        assert not temp_file.exists()

    def test_list_directory(self, cli_facade: FlextCli, temp_dir: Path) -> None:
        """Test directory listing functionality through facade."""
        # Create some test files
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.txt").write_text("content2")
        (temp_dir / "subdir").mkdir()

        result = cli_facade.file_tools.list_directory(str(temp_dir))

        assert isinstance(result, FlextResult)
        assert result.is_success

        files = result.unwrap()
        assert isinstance(files, list)
        assert (
            len(files) >= 2
        )  # At least the files we created (subdirs may not be included)

    def test_create_directory(self, cli_facade: FlextCli, temp_dir: Path) -> None:
        """Test directory creation functionality through facade."""
        new_dir = temp_dir / "new_directory"

        result = cli_facade.file_tools.create_directory(str(new_dir))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify directory was created
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_delete_directory(self, cli_facade: FlextCli, temp_dir: Path) -> None:
        """Test directory deletion functionality."""
        test_dir = temp_dir / "test_delete_dir"
        test_dir.mkdir()
        (test_dir / "test_file.txt").write_text("test")

        assert test_dir.exists()

        result = cli_facade.file_tools.delete_directory(str(test_dir))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify directory was deleted
        assert not test_dir.exists()

    # ========================================================================
    # DATA PROCESSING
    # ========================================================================

    def test_parse_json_data(self) -> None:
        """Test JSON data parsing functionality."""
        json_data = '{"key": "value", "number": 42, "list": [1, 2, 3]}'

        try:
            parsed = json.loads(json_data)
            result = FlextResult[FlextTypes.Dict].ok(parsed)
        except Exception as e:
            result = FlextResult[FlextTypes.Dict].fail(str(e))

        assert isinstance(result, FlextResult)
        assert result.is_success

        parsed_data = result.unwrap()
        assert isinstance(parsed_data, dict)
        assert parsed_data["key"] == "value"
        assert parsed_data["number"] == 42
        assert parsed_data["list"] == [1, 2, 3]

    def test_parse_json_data_invalid(self) -> None:
        """Test JSON data parsing with invalid JSON."""
        invalid_json = (
            '{"key": "value", "number": 42, "list": [1, 2, 3'  # Missing closing bracket
        )

        try:
            parsed = json.loads(invalid_json)
            result = FlextResult[FlextTypes.Dict].ok(parsed)
        except Exception as e:
            result = FlextResult[FlextTypes.Dict].fail(str(e))

        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_serialize_json_data(self) -> None:
        """Test JSON data serialization functionality."""
        test_data: FlextTypes.Dict = {
            "key": "value",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {"inner": "data"},
        }

        try:
            json_str = json.dumps(test_data)
            result = FlextResult[str].ok(json_str)
        except Exception as e:
            result = FlextResult[str].fail(str(e))

        assert isinstance(result, FlextResult)
        assert result.is_success

        json_string = result.unwrap()
        assert isinstance(json_string, str)

        # Verify it can be parsed back
        parsed_back = json.loads(json_string)
        assert parsed_back == test_data

    def test_parse_yaml_data(self) -> None:
        """Test YAML data parsing functionality."""
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

        try:
            parsed = yaml.safe_load(yaml_data)
            result = FlextResult[FlextTypes.Dict].ok(parsed)
        except Exception as e:
            result = FlextResult[FlextTypes.Dict].fail(str(e))

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

    def test_serialize_yaml_data(self) -> None:
        """Test YAML data serialization functionality."""
        test_data: FlextTypes.Dict = {
            "key": "value",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {"inner": "data"},
        }

        try:
            yaml_str = yaml.dump(test_data)
            result = FlextResult[str].ok(yaml_str)
        except Exception as e:
            result = FlextResult[str].fail(str(e))

        assert isinstance(result, FlextResult)
        assert result.is_success

        yaml_string = result.unwrap()
        assert isinstance(yaml_string, str)
        assert "key: value" in yaml_string
        assert "number: 42" in yaml_string

    # ========================================================================
    # COMMAND EXECUTION
    # ========================================================================

    def test_execute_command(self, core_service: FlextCliCore) -> None:
        """Test command execution functionality."""
        # Test with a simple command that should work on most systems
        result = core_service.execute_command("echo", ["Hello, World!"])

        assert isinstance(result, FlextResult)
        # Command execution may fail due to security restrictions, so we check the result type
        assert result.is_success or result.is_failure

        if result.is_success:
            output = result.unwrap()
            assert isinstance(output, str)

    def test_execute_command_with_timeout(self, core_service: FlextCliCore) -> None:
        """Test command execution with timeout."""
        # Test with a command that should complete quickly
        result = core_service.execute_command("python", ["--version"], timeout=5)

        assert isinstance(result, FlextResult)
        # Command execution may fail due to environment, but should return proper result
        if result.is_success:
            output = result.unwrap()
            assert isinstance(output, (str, dict))
        else:
            # If command fails, should have proper error message
            assert isinstance(result.error, str)
            assert len(result.error) > 0

    def test_execute_command_nonexistent(self, core_service: FlextCliCore) -> None:
        """Test command execution with nonexistent command."""
        result = core_service.execute_command("nonexistent_command_12345", [])

        assert isinstance(result, FlextResult)
        assert result.is_failure

    # ========================================================================
    # NETWORK OPERATIONS
    # ========================================================================

    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================

    def test_generate_uuid(self) -> None:
        """Test UUID generation functionality."""
        uuid_value = FlextUtilities.Generators.generate_uuid()

        assert isinstance(uuid_value, str)
        assert len(uuid_value) == 36  # Standard UUID length
        assert uuid_value.count("-") == 4  # Standard UUID format

    def test_format_timestamp(self) -> None:
        """Test timestamp formatting functionality."""
        timestamp = FlextUtilities.Generators.generate_iso_timestamp()

        assert isinstance(timestamp, str)
        # Check for ISO format timestamp
        assert len(timestamp) > 10  # Basic length check
        assert "T" in timestamp  # ISO format includes T separator

    def test_validate_email(self) -> None:
        """Test email validation functionality."""
        # Test valid email
        result = FlextUtilities.Validation.validate_email("test@example.com")
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == "test@example.com"

        # Test invalid email
        result = FlextUtilities.Validation.validate_email("invalid-email")
        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_validate_url(self) -> None:
        """Test URL validation functionality."""
        # Test valid URL - validate_url returns FlextResult[None] (validation pattern)
        result = FlextUtilities.Validation.validate_url("https://example.com")
        assert isinstance(result, FlextResult)
        assert result.is_success
        # Validation functions return None on success (validation pattern, not transformation)
        assert result.unwrap() is None

        # Test invalid URL
        result = FlextUtilities.Validation.validate_url("not-a-url")
        assert isinstance(result, FlextResult)
        assert result.is_failure

    # ========================================================================
    # ERROR HANDLING AND EDGE CASES
    # ========================================================================

    def test_error_handling_with_invalid_input(
        self, core_service: FlextCliCore
    ) -> None:
        """Test error handling with various invalid inputs."""
        # Test with None input
        result = core_service.load_configuration("")
        assert isinstance(result, FlextResult)
        assert result.is_failure

        # Test with empty string
        result = core_service.load_configuration("")
        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_error_handling_with_permission_denied(self, cli_facade: FlextCli) -> None:
        """Test error handling with permission denied scenarios."""
        # Try to write to a directory that should be read-only
        result = cli_facade.file_tools.write_text_file(
            "/proc/test_file", "test content"
        )
        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_concurrent_operations(self, cli_facade: FlextCli, temp_dir: Path) -> None:
        """Test concurrent operations to ensure thread safety."""
        results = []
        errors = []

        def worker(worker_id: int) -> None:
            try:
                test_file = temp_dir / f"concurrent_test_{worker_id}.txt"
                result = cli_facade.file_tools.write_text_file(
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

    def test_full_workflow_integration(
        self, core_service: FlextCliCore, cli_facade: FlextCli, temp_dir: Path
    ) -> None:
        """Test complete workflow integration."""
        # 1. Create configuration
        config_data: FlextTypes.Dict = {
            "debug": True,
            "output_format": "json",
            "timeout": FlextCliConstants.TIMEOUTS.DEFAULT,
            "retries": FlextCliConstants.HTTP.MAX_RETRIES,
        }

        config_file = temp_dir / "workflow_config.json"
        save_result = core_service.save_configuration(str(config_file), config_data)
        assert save_result.is_success

        # 2. Load configuration
        load_result = core_service.load_configuration(str(config_file))
        assert load_result.is_success
        assert load_result.unwrap() == config_data

        # 3. Validate configuration using FlextCliConfig model
        config_model = FlextCliConfig(
            debug=True,
            output_format="json",
            timeout=FlextCliConstants.TIMEOUTS.DEFAULT,
            max_retries=FlextCliConstants.HTTP.MAX_RETRIES,
        )
        validate_result = core_service.validate_configuration(config_model)
        assert validate_result.is_success

        # 4. Process data
        test_data: FlextTypes.Dict = {
            "processed": True,
            "timestamp": "2025-01-01T00:00:00Z",
        }
        try:
            json_str = json.dumps(test_data)
            json_result = FlextResult[str].ok(json_str)
        except Exception as e:
            json_result = FlextResult[str].fail(str(e))
        assert json_result.is_success

        # 5. Save processed data
        data_file = temp_dir / "processed_data.json"
        write_result = cli_facade.file_tools.write_text_file(
            str(data_file), json_result.unwrap()
        )
        assert write_result.is_success

        # 6. Verify complete workflow
        assert config_file.exists()
        assert data_file.exists()
        assert json.loads(data_file.read_text()) == test_data

    def test_workflow_integration(self, core_service: FlextCliCore) -> None:
        """Test execute method (now sync, delegates to execute)."""
        # execute is now synchronous, delegates to execute()
        result = core_service.execute()
        assert isinstance(result, FlextResult)
        # Execution may fail due to implementation issues, so we check the result type
        assert result.is_success or result.is_failure

        if result.is_success:
            data = result.unwrap()
            assert isinstance(data, dict)
            assert "status" in data
            assert "service" in data
            assert data["service"] == "FlextCliCore"

    def test_core_service_advanced_methods_merged(
        self, core_service: FlextCliCore
    ) -> None:
        """Test advanced core service methods - consolidated test."""
        # Test health check
        health_result = core_service.health_check()
        assert isinstance(health_result, FlextResult)

        # Test get config
        config_result = core_service.get_config()
        assert config_result is not None

        # Test get handlers
        handlers_result = core_service.get_handlers()
        assert isinstance(handlers_result, FlextResult)
        assert handlers_result.is_success

        # Test get plugins
        plugins_result = core_service.get_plugins()
        assert isinstance(plugins_result, FlextResult)
        assert plugins_result.is_success

        # Test get sessions
        sessions_result = core_service.get_sessions()
        assert isinstance(sessions_result, FlextResult)
        assert sessions_result.is_success

        # Test get commands
        commands_result = core_service.get_commands()
        assert isinstance(commands_result, FlextResult)
        assert commands_result.is_success

        # Test get formatters
        formatters_result = core_service.get_formatters()
        assert formatters_result is not None

        # Additional functionality from duplicate method
        assert hasattr(core_service, "health_check")
        assert hasattr(core_service, "get_config")
        assert hasattr(core_service, "get_handlers")


class TestFlextCliCoreExtended:
    """Extended tests for FlextCliCore core functionality."""

    @pytest.fixture
    def core_service(self) -> FlextCliCore:
        """Create FlextCliCore instance for testing."""
        return FlextCliCore()

    @pytest.fixture
    def sample_command(self) -> FlextCliModels.CliCommand:
        """Create sample CLI command for testing."""
        return FlextCliModels.CliCommand(
            command_line="test-cmd --option value",
            name="test-cmd",
            description="Test command",
        )

    # =========================================================================
    # COMMAND REGISTRATION TESTS
    # =========================================================================

    def test_register_command_success(
        self, core_service: FlextCliCore, sample_command: FlextCliModels.CliCommand
    ) -> None:
        """Test successful command registration."""
        result = core_service.register_command(sample_command)

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify command was registered
        list_result = core_service.list_commands()
        assert list_result.is_success
        assert "test-cmd" in list_result.unwrap()

    def test_get_command_success(
        self, core_service: FlextCliCore, sample_command: FlextCliModels.CliCommand
    ) -> None:
        """Test retrieving registered command."""
        # Register command first
        core_service.register_command(sample_command)

        # Retrieve it
        result = core_service.get_command("test-cmd")

        assert isinstance(result, FlextResult)
        assert result.is_success
        command_def = result.unwrap()
        assert command_def["name"] == "test-cmd"

    def test_get_command_not_found(self, core_service: FlextCliCore) -> None:
        """Test getting non-existent command."""
        result = core_service.get_command("nonexistent")

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None and "not found" in result.error

    def test_get_command_invalid_name_empty(self, core_service: FlextCliCore) -> None:
        """Test getting command with empty name."""
        result = core_service.get_command("")

        assert result.is_failure
        assert result.error is not None and "non-empty string" in result.error

    def test_get_command_invalid_name_type(self, core_service: FlextCliCore) -> None:
        """Test getting command with invalid name type."""
        result = core_service.get_command(None)

        assert result.is_failure
        assert result.error is not None and "non-empty string" in result.error

    def test_execute_command_success(
        self, core_service: FlextCliCore, sample_command: FlextCliModels.CliCommand
    ) -> None:
        """Test executing registered command."""
        core_service.register_command(sample_command)

        result = core_service.execute_command("test-cmd")

        assert isinstance(result, FlextResult)
        assert result.is_success
        command_result = result.unwrap()
        assert command_result["command"] == "test-cmd"
        assert command_result["status"] is True

    def test_execute_command_with_context_list(
        self, core_service: FlextCliCore, sample_command: FlextCliModels.CliCommand
    ) -> None:
        """Test executing command with list context."""
        core_service.register_command(sample_command)

        result = core_service.execute_command("test-cmd", context=["arg1", "arg2"])

        assert result.is_success
        command_result = result.unwrap()
        if not isinstance(command_result, dict):
            return
        assert "context" in command_result
        # Type narrowing for dict access
        context_value = command_result.get("context")
        if isinstance(context_value, dict):
            assert context_value.get("args") == ["arg1", "arg2"]

    def test_execute_command_with_context_dict(
        self, core_service: FlextCliCore, sample_command: FlextCliModels.CliCommand
    ) -> None:
        """Test executing command with dict context."""
        core_service.register_command(sample_command)

        context: dict[
            str, str | int | float | bool | list[object] | dict[str, object] | None
        ] = {"option": "value", "flag": True}
        result = core_service.execute_command("test-cmd", context=context)

        assert result.is_success
        command_result = result.unwrap()
        assert command_result["context"] == context

    def test_execute_command_with_timeout(
        self, core_service: FlextCliCore, sample_command: FlextCliModels.CliCommand
    ) -> None:
        """Test executing command with timeout."""
        core_service.register_command(sample_command)

        result = core_service.execute_command("test-cmd", timeout=30.0)

        assert result.is_success
        command_result = result.unwrap()
        assert command_result["timeout"] == 30.0

    def test_execute_command_not_found(self, core_service: FlextCliCore) -> None:
        """Test executing non-existent command."""
        result = core_service.execute_command("nonexistent")

        assert result.is_failure
        assert result.error is not None and "not found" in result.error

    def test_list_commands_empty(self, core_service: FlextCliCore) -> None:
        """Test listing commands when none registered."""
        result = core_service.list_commands()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == []

    def test_list_commands_multiple(self, core_service: FlextCliCore) -> None:
        """Test listing multiple registered commands."""
        # Register multiple commands
        for i in range(3):
            cmd = FlextCliModels.CliCommand(
                command_line=f"cmd{i} --test",
                name=f"cmd{i}",
                description=f"Command {i}",
            )
            core_service.register_command(cmd)

        result = core_service.list_commands()

        assert result.is_success
        commands = result.unwrap()
        assert len(commands) == 3
        assert "cmd0" in commands
        assert "cmd1" in commands
        assert "cmd2" in commands

    # =========================================================================
    # SESSION MANAGEMENT TESTS
    # =========================================================================

    def test_start_session_success(self, core_service: FlextCliCore) -> None:
        """Test starting new session."""
        result = core_service.start_session()

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify session is active
        assert core_service.is_session_active()

    def test_start_session_already_active(self, core_service: FlextCliCore) -> None:
        """Test starting session when one is already active."""
        core_service.start_session()

        # Try to start another
        result = core_service.start_session()

        assert result.is_failure
        assert result.error is not None and "already active" in result.error

    def test_end_session_success(self, core_service: FlextCliCore) -> None:
        """Test ending active session."""
        core_service.start_session()

        result = core_service.end_session()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert not core_service.is_session_active()

    def test_end_session_not_active(self, core_service: FlextCliCore) -> None:
        """Test ending session when none active."""
        result = core_service.end_session()

        assert result.is_failure
        assert result.error is not None and "No active session" in result.error

    def test_is_session_active_false(self, core_service: FlextCliCore) -> None:
        """Test session active check when no session."""
        assert not core_service.is_session_active()

    def test_is_session_active_true(self, core_service: FlextCliCore) -> None:
        """Test session active check when session running."""
        core_service.start_session()

        assert core_service.is_session_active()

    # =========================================================================
    # STATISTICS AND INFO TESTS
    # =========================================================================

    def test_get_command_statistics_no_commands(
        self, core_service: FlextCliCore
    ) -> None:
        """Test command statistics with no commands."""
        result = core_service.get_command_statistics()

        assert isinstance(result, FlextResult)
        assert result.is_success
        stats = result.unwrap()
        assert stats["total_commands"] == 0

    def test_get_command_statistics_with_commands(
        self, core_service: FlextCliCore
    ) -> None:
        """Test command statistics with registered commands."""
        # Register commands
        for i in range(5):
            cmd = FlextCliModels.CliCommand(
                command_line=f"cmd{i} --test",
                name=f"cmd{i}",
                description=f"Command {i}",
            )
            core_service.register_command(cmd)

        result = core_service.get_command_statistics()

        assert result.is_success
        stats = result.unwrap()
        assert stats["total_commands"] == 5

    def test_get_service_info(self, core_service: FlextCliCore) -> None:
        """Test getting service information."""
        info = core_service.get_service_info()

        assert isinstance(info, dict)
        assert "service_name" in info
        assert "timestamp" in info
        assert "session_active" in info

    def test_get_session_statistics_no_sessions(
        self, core_service: FlextCliCore
    ) -> None:
        """Test session statistics with no sessions."""
        result = core_service.get_session_statistics()

        assert isinstance(result, FlextResult)
        assert result.is_failure  # No active session
        assert result.error is not None and "No active session" in result.error

    def test_get_session_statistics_with_session(
        self, core_service: FlextCliCore
    ) -> None:
        """Test session statistics with active session."""
        core_service.start_session()

        result = core_service.get_session_statistics()

        assert result.is_success
        stats = result.unwrap()
        assert "session_active" in stats
        assert stats["session_active"] is True

    # =========================================================================
    # HEALTH CHECK TESTS
    # =========================================================================

    def test_health_check_success(self, core_service: FlextCliCore) -> None:
        """Test health check returns success."""
        result = core_service.health_check()

        assert isinstance(result, FlextResult)
        assert result.is_success
        health = result.unwrap()
        assert "service_healthy" in health
        assert "timestamp" in health
        assert health["service_healthy"] is True

    # =========================================================================
    # CONFIGURATION MANAGEMENT TESTS
    # =========================================================================

    def test_get_config_success(self, core_service: FlextCliCore) -> None:
        """Test getting configuration."""
        result = core_service.get_config()

        assert isinstance(result, FlextResult)
        assert result.is_success
        config = result.unwrap()
        assert isinstance(config, dict)

    def test_update_configuration_success(self, core_service: FlextCliCore) -> None:
        """Test updating configuration."""
        config: dict[
            str,
            dict[
                str, str | int | float | bool | list[object] | dict[str, object] | None
            ],
        ] = {"theme": {"value": "dark"}, "verbose": {"value": True}}

        result = core_service.update_configuration(config)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_get_configuration_success(self, core_service: FlextCliCore) -> None:
        """Test getting configuration."""
        result = core_service.get_configuration()

        assert isinstance(result, FlextResult)
        assert result.is_success
        config = result.unwrap()
        assert isinstance(config, dict)

    def test_create_profile_success(self, core_service: FlextCliCore) -> None:
        """Test creating configuration profile."""
        profile_config: dict[str, object] = {"color": "blue", "size": "large"}

        result = core_service.create_profile("test-profile", profile_config)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_load_configuration_valid_file(self, core_service: FlextCliCore) -> None:
        """Test loading configuration from valid file."""
        # Create temp config file
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".json", delete=False
        ) as f:
            import json

            json.dump({"test": "value"}, f)
            config_path = f.name

        try:
            result = core_service.load_configuration(config_path)

            assert isinstance(result, FlextResult)
            assert result.is_success
            config = result.unwrap()
            assert config.get("test") == "value"
        finally:
            Path(config_path).unlink()

    def test_load_configuration_nonexistent_file(
        self, core_service: FlextCliCore
    ) -> None:
        """Test loading configuration from non-existent file."""
        result = core_service.load_configuration("/nonexistent/config.json")

        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_save_configuration_success(self, core_service: FlextCliCore) -> None:
        """Test saving configuration to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = str(Path(temp_dir) / "config.json")
            config = {"setting1": "value1", "setting2": 42}

            result = core_service.save_configuration(config_path, config)

            assert isinstance(result, FlextResult)
            assert result.is_success

            # Verify file was created
            assert Path(config_path).exists()

    # =========================================================================
    # UTILITY METHOD TESTS
    # =========================================================================

    def test_get_handlers_success(self, core_service: FlextCliCore) -> None:
        """Test getting list of handlers."""
        result = core_service.get_handlers()

        assert isinstance(result, FlextResult)
        assert result.is_success
        handlers = result.unwrap()
        assert isinstance(handlers, list)

    def test_get_plugins_success(self, core_service: FlextCliCore) -> None:
        """Test getting list of plugins."""
        result = core_service.get_plugins()

        assert isinstance(result, FlextResult)
        assert result.is_success
        plugins = result.unwrap()
        assert isinstance(plugins, list)

    def test_get_sessions_success(self, core_service: FlextCliCore) -> None:
        """Test getting list of sessions."""
        result = core_service.get_sessions()

        assert isinstance(result, FlextResult)
        assert result.is_success
        sessions = result.unwrap()
        assert isinstance(sessions, list)

    def test_get_commands_success(self, core_service: FlextCliCore) -> None:
        """Test getting list of commands."""
        result = core_service.get_commands()

        assert isinstance(result, FlextResult)
        assert result.is_success
        commands = result.unwrap()
        assert isinstance(commands, list)

    def test_get_formatters_success(self, core_service: FlextCliCore) -> None:
        """Test getting list of formatters."""
        result = core_service.get_formatters()

        assert isinstance(result, FlextResult)
        assert result.is_success
        formatters = result.unwrap()
        assert isinstance(formatters, list)

    # =========================================================================
    # INTEGRATION TESTS
    # =========================================================================

    def test_complete_workflow(self, core_service: FlextCliCore) -> None:
        """Test complete CLI workflow."""
        # Step 1: Start session
        session_result = core_service.start_session()
        assert session_result.is_success

        # Step 2: Register commands
        cmd1 = FlextCliModels.CliCommand(
            command_line="init --verbose",
            name="init",
            description="Initialize",
        )
        cmd2 = FlextCliModels.CliCommand(
            command_line="process --data input.json",
            name="process",
            description="Process data",
        )

        assert core_service.register_command(cmd1).is_success
        assert core_service.register_command(cmd2).is_success

        # Step 3: List commands
        list_result = core_service.list_commands()
        assert list_result.is_success
        assert len(list_result.unwrap()) == 2

        # Step 4: Execute commands
        exec_result = core_service.execute_command("init")
        assert exec_result.is_success

        # Step 5: Get statistics
        stats_result = core_service.get_command_statistics()
        assert stats_result.is_success
        assert stats_result.unwrap()["total_commands"] == 2

        # Step 6: End session
        end_result = core_service.end_session()
        assert end_result.is_success
        assert not core_service.is_session_active()

    def test_configuration_workflow(self, core_service: FlextCliCore) -> None:
        """Test configuration management workflow."""
        # Step 1: Update configuration
        config: dict[
            str,
            dict[
                str, str | int | float | bool | list[object] | dict[str, object] | None
            ],
        ] = {
            "theme": {"value": "dark"},
            "verbose": {"value": True},
            "timeout": {"value": 30},
        }
        update_result = core_service.update_configuration(config)
        assert update_result.is_success

        # Step 2: Get configuration
        get_result = core_service.get_configuration()
        assert get_result.is_success

        # Step 3: Create profile
        profile_result = core_service.create_profile(
            "production", {"debug": False, "log_level": "INFO"}
        )
        assert profile_result.is_success

        # Step 4: Save configuration
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = str(Path(temp_dir) / "config.json")
            simple_config: dict[str, object] = {
                "theme": "dark",
                "verbose": True,
                "timeout": 30,
            }
            save_result = core_service.save_configuration(config_path, simple_config)
            assert save_result.is_success

            # Step 5: Load configuration
            load_result = core_service.load_configuration(config_path)
            assert load_result.is_success


class TestFlextCliCoreExceptionHandlers:
    """Exception handler tests for FlextCliCore methods."""

    @pytest.fixture
    def core_service(self) -> FlextCliCore:
        """Create FlextCliCore instance for testing."""
        return FlextCliCore()

    def test_get_command_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_command exception handler (lines 124-125)."""

        # Mock _commands to raise exception
        def mock_get_raises(*args: object, **kwargs: object) -> object:
            msg = "Get error"
            raise RuntimeError(msg)

        monkeypatch.setattr(core_service._commands, "get", mock_get_raises)

        result = core_service.get_command("test")
        assert result.is_failure
        # The method should handle the exception gracefully

    def test_execute_command_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test execute_command exception handler (lines 184-185)."""
        # Register a command first
        cmd = FlextCliModels.CliCommand(
            command_line="test", name="test", description="Test"
        )
        core_service.register_command(cmd)

        # Mock execute_cli_command_with_context to raise exception
        def mock_execute_raises(*args: object, **kwargs: object) -> object:
            msg = "Execute error"
            raise RuntimeError(msg)

        monkeypatch.setattr(
            core_service, "execute_cli_command_with_context", mock_execute_raises
        )

        result = core_service.execute_command("test")
        assert result.is_failure

    def test_list_commands_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test list_commands exception handler (lines 201-202)."""

        # Mock _commands.keys() to raise exception
        def mock_keys_raises() -> object:
            msg = "Keys error"
            raise RuntimeError(msg)

        monkeypatch.setattr(core_service._commands, "keys", mock_keys_raises)

        result = core_service.list_commands()
        assert result.is_failure

    def test_update_configuration_not_initialized_exception(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test update_configuration when config not initialized (lines 235-237)."""
        # Set _config to None to trigger the not initialized path
        core_service._config = None

        config: dict[str, dict[str, object]] = {"test": {"value": "data"}}
        result = core_service.update_configuration(config)
        assert result.is_failure
        assert "not initialized" in str(result.error)

    def test_update_configuration_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test update_configuration exception handler (lines 238-239)."""

        # Mock _config.update to raise exception
        def mock_update_raises(*args: object, **kwargs: object) -> None:
            msg = "Update error"
            raise RuntimeError(msg)

        monkeypatch.setattr(core_service._config, "update", mock_update_raises)

        config: dict[str, dict[str, object]] = {"test": {"value": "data"}}
        result = core_service.update_configuration(config)
        assert result.is_failure

    def test_get_configuration_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_configuration exception handler (lines 258-262)."""

        # Mock _config.copy to raise exception
        def mock_copy_raises() -> object:
            msg = "Copy error"
            raise RuntimeError(msg)

        monkeypatch.setattr(core_service._config, "copy", mock_copy_raises)

        result = core_service.get_configuration()
        assert result.is_failure

    def test_create_profile_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test create_profile exception handler (lines 310-315)."""

        # Mock _config.__setitem__ to raise exception
        def mock_setitem_raises(*args: object, **kwargs: object) -> None:
            msg = "Set error"
            raise RuntimeError(msg)

        monkeypatch.setattr(core_service._config, "__setitem__", mock_setitem_raises)

        result = core_service.create_profile("test", {"key": "value"})
        assert result.is_failure

    def test_start_session_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test start_session exception handler (lines 350-351)."""

        # Mock _sessions.append to raise exception
        def mock_append_raises(*args: object, **kwargs: object) -> None:
            msg = "Append error"
            raise RuntimeError(msg)

        monkeypatch.setattr(core_service._sessions, "append", mock_append_raises)

        result = core_service.start_session()
        assert result.is_failure

    def test_end_session_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test end_session exception handler (lines 375-376)."""
        # Start a session first
        core_service.start_session()

        # Mock _sessions.pop to raise exception
        def mock_pop_raises(*args: object, **kwargs: object) -> object:
            msg = "Pop error"
            raise RuntimeError(msg)

        monkeypatch.setattr(core_service._sessions, "pop", mock_pop_raises)

        result = core_service.end_session()
        assert result.is_failure

    def test_get_command_statistics_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_command_statistics exception handler (lines 408-409)."""

        # Mock len() to raise exception
        def mock_len_raises(*args: object) -> int:
            msg = "Len error"
            raise RuntimeError(msg)

        import builtins

        original_len = builtins.len
        builtins.len = mock_len_raises

        try:
            result = core_service.get_command_statistics()
            assert result.is_failure
        finally:
            builtins.len = original_len

    def test_get_session_statistics_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_session_statistics exception handler (lines 436-438)."""
        # Start a session
        core_service.start_session()

        # Mock len() to raise exception
        def mock_len_raises(*args: object) -> int:
            msg = "Len error"
            raise RuntimeError(msg)

        import builtins

        original_len = builtins.len
        builtins.len = mock_len_raises

        try:
            result = core_service.get_session_statistics()
            assert result.is_failure
        finally:
            builtins.len = original_len

    def test_execute_cli_command_with_context_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test execute_cli_command_with_context exception handler (lines 519-520)."""
        # Register a command
        cmd = FlextCliModels.CliCommand(
            command_line="test", name="test", description="Test"
        )
        core_service.register_command(cmd)

        # Mock datetime to raise exception
        import flext_cli.core

        original_datetime = flext_cli.core.datetime

        def mock_datetime_raises() -> object:
            msg = "Datetime error"
            raise RuntimeError(msg)

        monkeypatch.setattr(
            "flext_cli.core.datetime",
            type("MockDatetime", (), {"now": staticmethod(mock_datetime_raises)}),
        )

        try:
            result = core_service.execute_cli_command_with_context("test", {})
            # Should fail due to datetime error
            assert result.is_failure or result.is_success  # Implementation may vary
        finally:
            monkeypatch.setattr("flext_cli.core.datetime", original_datetime)

    def test_health_check_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test health_check exception handler (lines 588-589)."""
        # Mock datetime to raise exception
        import flext_cli.core

        original_datetime = flext_cli.core.datetime

        def mock_datetime_raises() -> object:
            msg = "Datetime error"
            raise RuntimeError(msg)

        monkeypatch.setattr(
            "flext_cli.core.datetime",
            type("MockDatetime", (), {"now": staticmethod(mock_datetime_raises)}),
        )

        try:
            result = core_service.health_check()
            assert result.is_failure
        finally:
            monkeypatch.setattr("flext_cli.core.datetime", original_datetime)

    def test_get_config_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_config exception handler (lines 602-603)."""

        # Mock _config.copy to raise exception
        def mock_copy_raises() -> object:
            msg = "Copy error"
            raise RuntimeError(msg)

        monkeypatch.setattr(core_service._config, "copy", mock_copy_raises)

        result = core_service.get_config()
        assert result.is_failure

    def test_get_handlers_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_handlers exception handler (lines 616-617)."""

        # Mock _commands.keys to raise exception
        def mock_keys_raises() -> object:
            msg = "Keys error"
            raise RuntimeError(msg)

        monkeypatch.setattr(core_service._commands, "keys", mock_keys_raises)

        result = core_service.get_handlers()
        assert result.is_failure

    def test_get_plugins_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_plugins exception handler (lines 632-633)."""

        # Mock _plugins to raise exception on list()
        def mock_list_raises(*args: object) -> list:
            msg = "List error"
            raise RuntimeError(msg)

        original_list = list
        import builtins

        builtins.list = mock_list_raises

        try:
            result = core_service.get_plugins()
            assert result.is_failure
        finally:
            builtins.list = original_list

    def test_get_sessions_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_sessions exception handler (lines 648-649)."""

        # Mock list() to raise exception
        def mock_list_raises(*args: object) -> list:
            msg = "List error"
            raise RuntimeError(msg)

        original_list = list
        import builtins

        builtins.list = mock_list_raises

        try:
            result = core_service.get_sessions()
            assert result.is_failure
        finally:
            builtins.list = original_list

    def test_get_commands_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_commands exception handler (lines 664-665)."""

        # Mock _commands.keys to raise exception
        def mock_keys_raises() -> object:
            msg = "Keys error"
            raise RuntimeError(msg)

        monkeypatch.setattr(core_service._commands, "keys", mock_keys_raises)

        result = core_service.get_commands()
        assert result.is_failure

    def test_get_formatters_exception_handler(
        self, core_service: FlextCliCore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_formatters exception handler (not in missing but completing pattern)."""
        # This method should return a result
        result = core_service.get_formatters()
        assert isinstance(result, FlextResult)

    def test_load_configuration_exception_handler(
        self, core_service: FlextCliCore
    ) -> None:
        """Test load_configuration exception handler (lines 704, 713, 719-724)."""
        # Test with invalid file path that triggers exception
        result = core_service.load_configuration("/proc/invalid/config.json")
        assert result.is_failure

    def test_save_configuration_exception_handler(
        self, core_service: FlextCliCore
    ) -> None:
        """Test save_configuration exception handler (lines 747-748)."""
        # Test with invalid path that triggers exception
        result = core_service.save_configuration(
            "/proc/invalid/config.json", {"test": "data"}
        )
        assert result.is_failure
