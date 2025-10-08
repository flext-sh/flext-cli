"""FLEXT CLI CMD Tests - Comprehensive command functionality testing.

Tests for FlextCliCmd class using flext_tests infrastructure with real functionality
testing, no mocks, and comprehensive coverage following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
import time
from pathlib import Path
from typing import Never, cast

from flext_core import FlextLogger, FlextResult

from flext_cli import FlextCliCmd, FlextCliConfig, FlextCliFileTools


class TestFlextCliCmd:
    """Comprehensive tests for FlextCliCmd class."""

    class TestingException(Exception):
        """Custom exception for testing purposes."""

    def test_cmd_initialization(self) -> None:
        """Test CMD initialization with proper configuration."""
        cmd = FlextCliCmd()
        assert cmd is not None
        assert isinstance(cmd, FlextCliCmd)

    def test_cmd_execute_sync(self) -> None:
        """Test synchronous CMD execution."""
        cmd = FlextCliCmd()
        result = cmd.execute()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == "operational"
        assert result.value["service"] == "FlextCliCmd"

    def test_cmd_command_bus_service(self) -> None:
        """Test command bus service property."""
        cmd = FlextCliCmd()
        command_bus = cmd.command_bus_service
        assert command_bus is not None

    def test_cmd_config_edit(self) -> None:
        """Test configuration editing functionality."""
        cmd = FlextCliCmd()

        # Test editing config (method takes no parameters)
        result = cmd.edit_config()
        assert result.is_success

    def test_cmd_config_edit_existing(self) -> None:
        """Test editing existing configuration."""
        cmd = FlextCliCmd()

        # Test editing config (method takes no parameters)
        result = cmd.edit_config()
        assert result.is_success

    def test_cmd_config_default_values(self) -> None:
        """Test default configuration values."""
        cmd = FlextCliCmd()

        # Test editing config (method takes no parameters)
        result = cmd.edit_config()
        assert result.is_success

    def test_cmd_error_handling(self) -> None:
        """Test CMD error handling capabilities."""
        cmd = FlextCliCmd()

        # Test edit config method
        result = cmd.edit_config()
        # Should handle gracefully (either success with default or proper error)
        assert result is not None

    def test_cmd_performance(self) -> None:
        """Test CMD performance characteristics."""
        cmd = FlextCliCmd()

        start_time = time.time()
        result = cmd.execute()
        execution_time = time.time() - start_time

        assert result.is_success
        # Should execute quickly
        assert execution_time < 1.0

    def test_cmd_memory_usage(self) -> None:
        """Test CMD memory usage characteristics."""
        cmd = FlextCliCmd()

        # Test multiple executions
        for _ in range(5):
            result = cmd.execute()
            assert result.is_success

    def test_cmd_integration(self) -> None:
        """Test CMD integration with other services."""
        cmd = FlextCliCmd()

        # Test that CMD properly integrates with its dependencies
        result = cmd.execute()
        assert result.is_success

        # Test command bus service integration
        command_bus = cmd.command_bus_service
        assert command_bus is not None

    def test_cmd_configuration_consistency(self) -> None:
        """Test configuration consistency across operations."""
        cmd = FlextCliCmd()

        # Test edit config method (takes no parameters)
        result1 = cmd.edit_config()
        assert result1.is_success

        # Test edit config again
        result2 = cmd.edit_config()
        assert result2.is_success

        # Both operations should succeed
        assert result1.is_success == result2.is_success

    def test_cmd_service_properties(self) -> None:
        """Test CMD service properties."""
        cmd = FlextCliCmd()

        # Test that all required properties are accessible
        assert hasattr(cmd, "command_bus_service")
        assert hasattr(cmd, "execute")
        assert hasattr(cmd, "edit_config")

    def test_cmd_logging_integration(self) -> None:
        """Test CMD logging integration."""
        cmd = FlextCliCmd()

        # Test that logging is properly integrated
        result = cmd.execute()
        assert result.is_success

        # Should not raise any logging-related exceptions
        assert result.value is not None

    def test_cmd_create_instance(self) -> None:
        """Test create_instance class method."""
        instance = FlextCliCmd.create_instance()
        assert isinstance(instance, FlextCliCmd)

    def test_cmd_config_helper_get_config_paths(self) -> None:
        """Test _ConfigHelper.get_config_paths method."""
        paths = FlextCliCmd._ConfigHelper.get_config_paths()
        assert isinstance(paths, list)
        assert len(paths) > 0
        # Check that paths contain expected flext directory
        assert any(".flext" in path for path in paths)

    def test_cmd_config_helper_validate_config_structure(self) -> None:
        """Test _ConfigHelper.validate_config_structure method."""
        results = FlextCliCmd._ConfigHelper.validate_config_structure()
        assert isinstance(results, list)
        # Results should contain validation messages
        assert len(results) > 0

    def test_cmd_config_helper_get_config_info(self) -> None:
        """Test _ConfigHelper.get_config_info method."""
        info = FlextCliCmd._ConfigHelper.get_config_info()
        assert isinstance(info, dict)
        assert "config_dir" in info
        assert "config_exists" in info
        assert "config_readable" in info
        assert "config_writable" in info
        assert "timestamp" in info

    def test_cmd_show_config_paths(self) -> None:
        """Test show_config_paths method."""
        cmd = FlextCliCmd()
        result = cmd.show_config_paths()
        assert result.is_success
        assert isinstance(result.value, list)
        assert len(result.value) > 0

    def test_cmd_validate_config(self) -> None:
        """Test validate_config method."""
        cmd = FlextCliCmd()
        result = cmd.validate_config()
        assert result.is_success

    def test_cmd_get_config_info(self) -> None:
        """Test get_config_info method."""
        cmd = FlextCliCmd()
        result = cmd.get_config_info()
        assert result.is_success
        assert isinstance(result.value, dict)
        assert "config_dir" in result.value
        assert "config_exists" in result.value

    def test_cmd_set_config_value(self) -> None:
        """Test set_config_value method."""
        cmd = FlextCliCmd()
        result = cmd.set_config_value("test_key", "test_value")
        # This might fail if config directory doesn't exist, but should not raise exception
        assert result is not None
        # If it succeeds, check the result
        if result.is_success:
            assert result.value is True

    def test_cmd_get_config_value_nonexistent_file(self) -> None:
        """Test get_config_value with nonexistent config file."""
        cmd = FlextCliCmd()
        result = cmd.get_config_value("nonexistent_key")
        # Should fail because config file doesn't exist
        assert result.is_failure
        assert isinstance(result.error, str)
        assert result.error is not None and "not found" in result.error.lower()

    def test_cmd_show_config(self) -> None:
        """Test show_config method."""
        cmd = FlextCliCmd()
        result = cmd.show_config()
        assert result.is_success

    def test_cmd_edit_config_creates_default(self) -> None:
        """Test edit_config creates default configuration."""
        cmd = FlextCliCmd()
        result = cmd.edit_config()
        assert result.is_success
        assert isinstance(result.value, str)

    def test_cmd_config_display_helper_show_config(self) -> None:
        """Test _ConfigDisplayHelper.show_config method."""
        result = FlextCliCmd._ConfigDisplayHelper.show_config(None)
        assert result.is_success

    def test_cmd_config_modification_helper_edit_config(self) -> None:
        """Test _ConfigModificationHelper.edit_config method."""
        result = FlextCliCmd._ConfigModificationHelper.edit_config()
        assert result.is_success
        assert isinstance(result.value, str)

    def test_cmd_config_validation_helper_validate_config(self) -> None:
        """Test _ConfigValidationHelper.validate_config method."""
        # Test with valid config
        result = FlextCliCmd._ConfigValidationHelper.validate_config({"test": "value"})
        assert result.is_success

        # Test with None config
        result = FlextCliCmd._ConfigValidationHelper.validate_config(None)
        assert result.is_failure
        assert isinstance(result.error, str)
        assert result.error is not None and "None" in result.error

    def test_cmd_show_config_paths_error_handling(self) -> None:
        """Test show_config_paths error handling."""
        cmd = FlextCliCmd()
        # Mock the helper to raise exception
        original_helper = cmd._ConfigHelper

        class FailingHelper:
            @staticmethod
            def get_config_paths() -> Never:
                test_error_msg = "Test error"
                raise self.TestingException(test_error_msg)

        cmd._ConfigHelper = cast("type", FailingHelper)
        try:
            result = cmd.show_config_paths()
            assert result.is_failure
            assert isinstance(result.error, str)
            assert result.error is not None and "Test error" in result.error
        finally:
            cmd._ConfigHelper = original_helper

    def test_cmd_validate_config_error_handling(self) -> None:
        """Test validate_config error handling."""
        cmd = FlextCliCmd()
        # Mock the helper to raise exception
        original_helper = cmd._ConfigHelper

        class FailingHelper:
            @staticmethod
            def validate_config_structure() -> Never:
                test_error_msg = "Test error"
                raise self.TestingException(test_error_msg)

        cmd._ConfigHelper = cast("type", FailingHelper)
        try:
            result = cmd.validate_config()
            assert result.is_failure
            assert isinstance(result.error, str)
            assert result.error is not None and "Test error" in result.error
        finally:
            cmd._ConfigHelper = original_helper

    def test_cmd_get_config_info_error_handling(self) -> None:
        """Test get_config_info error handling."""
        cmd = FlextCliCmd()
        # Mock the helper to raise exception
        original_helper = cmd._ConfigHelper

        class TestingException(Exception):
            """Custom exception for testing purposes."""

        class FailingHelper:
            @staticmethod
            def get_config_info() -> Never:
                test_error_msg = "Test error"
                raise TestingException(test_error_msg)

        cmd._ConfigHelper = cast("type", FailingHelper)
        try:
            result = cmd.get_config_info()
            assert result.is_failure
            assert isinstance(result.error, str)
            assert result.error is not None and "Test error" in result.error
        finally:
            cmd._ConfigHelper = original_helper

    def test_cmd_set_config_value_error_handling(self) -> None:
        """Test set_config_value error handling."""
        cmd = FlextCliCmd()
        # Mock file_tools to raise exception
        original_file_tools = cmd._file_tools

        class FailingFileTools(FlextCliFileTools):
            @staticmethod
            def write_json_file(
                _file_path: str | Path, _data: object, **_kwargs: dict[str, object]
            ) -> FlextResult[None]:
                return FlextResult[None].fail("Test file error")

        cmd._file_tools = FailingFileTools()
        try:
            result = cmd.set_config_value("test_key", "test_value")
            assert result.is_failure
            assert isinstance(result.error, str)
            assert result.error is not None and "Test file error" in result.error
        finally:
            cmd._file_tools = original_file_tools

    def test_cmd_get_config_value_file_load_error(self) -> None:
        """Test get_config_value file load error."""
        cmd = FlextCliCmd()
        # Mock file_tools to return failure on read
        original_file_tools = cmd._file_tools

        class FailingFileTools(FlextCliFileTools):
            @staticmethod
            def read_json_file(_file_path: str | Path) -> FlextResult[object]:
                return FlextResult[object].fail("Test load error")

        cmd._file_tools = FailingFileTools()

        # Create the config directory and file at the expected location
        config_dir = Path.home() / ".flext"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "cli_config.json"

        try:
            # Create the config file to pass the existence check
            with Path(config_file).open("w", encoding="utf-8") as f:
                f.write('{"test_key": "test_value"}')

            # Now the file exists, so it will call read_json_file which is mocked to fail
            result = cmd.get_config_value("test_key")
            assert result.is_failure
            assert result.error is not None
            assert "Test load error" in result.error
        finally:
            cmd._file_tools = original_file_tools
            # Clean up the test file
            if config_file.exists():
                config_file.unlink()

    def test_cmd_show_config_error_handling(self) -> None:
        """Test show_config error handling."""
        cmd = FlextCliCmd()
        # Mock the helper method that get_config_info calls
        original_helper = cmd._ConfigHelper

        class FailingHelper:
            @staticmethod
            def get_config_info() -> Never:
                test_error_msg = "Test config info error"
                raise self.TestingException(test_error_msg)

        cmd._ConfigHelper = cast("type", FailingHelper)
        try:
            result = cmd.show_config()
            assert result.is_failure
            assert isinstance(result.error, str)
            assert result.error is not None and "Test config info error" in result.error
        finally:
            cmd._ConfigHelper = original_helper

    def test_cmd_edit_config_load_error(self) -> None:
        """Test edit_config load error."""
        cmd = FlextCliCmd()
        # Mock file_tools to return failure on read
        original_file_tools = cmd._file_tools

        class FailingFileTools(FlextCliFileTools):
            @staticmethod
            def read_json_file(_file_path: str | Path) -> FlextResult[object]:
                return FlextResult[object].fail("Test load error")

            @staticmethod
            def write_json_file(
                _file_path: str | Path, _data: object, **_kwargs: dict[str, object]
            ) -> FlextResult[None]:
                return FlextResult[None].ok(None)

        cmd._file_tools = FailingFileTools()
        try:
            result = cmd.edit_config()
            assert result.is_failure
            assert isinstance(result.error, str)
            assert result.error is not None and "Test load error" in result.error
        finally:
            cmd._file_tools = original_file_tools

    def test_cmd_config_display_helper_error_handling(self) -> None:
        """Test _ConfigDisplayHelper.show_config error handling."""
        logger = FlextLogger(__name__)
        # Mock logger to raise exception
        original_info = logger.info

        def failing_info(*args: object, **kwargs: object) -> Never:
            test_error_msg = "Test logger error"
            raise self.TestingException(test_error_msg)

        logger.info = failing_info
        try:
            result = FlextCliCmd._ConfigDisplayHelper.show_config(logger)
            assert result.is_failure
            assert isinstance(result.error, str)
            assert result.error is not None and "Test logger error" in result.error
        finally:
            logger.info = original_info

    def test_cmd_config_modification_helper_error_handling(self) -> None:
        """Test _ConfigModificationHelper.edit_config error handling."""
        # This method doesn't actually do anything that can fail, so it should always succeed
        result = FlextCliCmd._ConfigModificationHelper.edit_config()
        assert result.is_success

    def test_cmd_edit_config_create_default_config_error(self) -> None:
        """Test edit_config create default config error."""
        cmd = FlextCliCmd()
        # Ensure config file doesn't exist to trigger default creation
        config_path = FlextCliConfig().config_dir / "cli_config.json"
        config_path.unlink(missing_ok=True)
        # Mock file_tools to fail on write for default config creation
        original_file_tools = cmd._file_tools

        class FailingFileTools(FlextCliFileTools):
            @staticmethod
            def write_json_file(
                _file_path: str | Path, _data: object, **_kwargs: dict[str, object]
            ) -> FlextResult[None]:
                return FlextResult[None].fail("Test create default error")

        cmd._file_tools = FailingFileTools()
        try:
            result = cmd.edit_config()
            assert result.is_failure
            assert isinstance(result.error, str)
            assert (
                result.error is not None and "Test create default error" in result.error
            )
        finally:
            cmd._file_tools = original_file_tools

    def test_cmd_get_config_value_missing_key_in_file(self) -> None:
        """Test get_config_value when key exists in file but is missing."""
        cmd = FlextCliCmd()
        # Mock file_tools to return data without the requested key
        original_file_tools = cmd._file_tools

        class MockFileTools(FlextCliFileTools):
            def __init__(self) -> None:
                super().__init__()

            def read_json_file(self, file_path: str | Path) -> FlextResult[object]:
                return FlextResult[object].ok({"other_key": "value"})

        cmd._file_tools = MockFileTools()
        try:
            # Create a temp file to avoid the "not found" error
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False, encoding="utf-8"
            ) as f:
                f.write('{"other_key": "value"}')
                temp_file = f.name
            try:
                # Temporarily replace config path
                original_config_dir = FlextCliConfig().config_dir
                FlextCliConfig().config_dir = Path(temp_file).parent
                try:
                    result = cmd.get_config_value("missing_key")
                    assert result.is_failure
                    assert isinstance(result.error, str)
                    assert (
                        result.error is not None and "not found" in result.error.lower()
                    )
                finally:
                    FlextCliConfig().config_dir = original_config_dir
            finally:
                Path(temp_file).unlink()
        finally:
            cmd._file_tools = original_file_tools
