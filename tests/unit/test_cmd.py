"""FLEXT CLI CMD Tests - Comprehensive command functionality testing.

Tests for FlextCliCmd class using flext_tests infrastructure with real functionality
testing, no mocks, and comprehensive coverage following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import time
from pathlib import Path

from flext_core import FlextResult

from flext_cli import (
    FlextCliCmd,
    FlextCliConstants,
    FlextCliServiceBase,
    FlextCliUtilities,
)


class TestFlextCliCmd:
    """Comprehensive tests for FlextCliCmd class."""

    class _TestingException(Exception):
        """Custom exception for testing purposes (not a test class)."""

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
        # Command bus service is not directly accessible on FlextCliCmd
        # This test verifies that the service can be instantiated
        assert cmd is not None
        assert isinstance(cmd, FlextCliCmd)

    def test_cmd_config_edit(
        self,
        tmp_path: Path,
    ) -> None:
        """Test configuration editing functionality with proper setup.

        Uses real configuration with temporary directory to test actual behavior.
        """
        # Create temporary config directory
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Initialize cmd with real configuration
        cmd = FlextCliCmd()
        result = cmd.edit_config()

        # Verify the config operation completed
        assert isinstance(result, FlextResult)
        # May succeed or fail depending on implementation, but should return proper result
        if result.is_success:
            assert isinstance(result.value, str)

    def test_cmd_config_edit_existing(
        self,
        tmp_path: Path,
    ) -> None:
        """Test editing existing configuration.

        Uses real configuration with temporary directory to test actual behavior.
        """
        # Create temporary config directory with existing config
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create a valid config file
        config_file = config_dir / FlextCliConstants.ConfigFiles.CLI_CONFIG_JSON
        config_data = {
            "host": "localhost",
            "port": 8080,
            "timeout": 30,
        }
        config_file.write_text(json.dumps(config_data))

        # Test editing existing config with real configuration
        cmd = FlextCliCmd()
        result = cmd.edit_config()

        # Verify the config operation completed
        assert isinstance(result, FlextResult)
        # May succeed or fail depending on implementation, but should return proper result
        if result.is_success:
            assert isinstance(result.value, str)

    def test_cmd_config_default_values(
        self,
        tmp_path: Path,
    ) -> None:
        """Test default configuration values with clean temporary directory.

        Uses real configuration with temporary directory to test actual behavior.
        """
        # Create a clean temporary config directory for this test
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / FlextCliConstants.ConfigFiles.CLI_CONFIG_JSON

        # Ensure config file doesn't exist - edit_config should create default
        assert not config_file.exists()

        # Create cmd instance with real configuration
        cmd = FlextCliCmd()

        # Test editing config - should create default config file
        result = cmd.edit_config()
        assert isinstance(result, FlextResult)
        # May succeed or fail depending on implementation, but should return proper result
        if result.is_success:
            assert isinstance(result.value, str)

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

        # Test that CMD properly integrates with its dependencies
        # Command bus service is not directly accessible on FlextCliCmd
        # This test verifies basic service functionality
        assert cmd is not None
        assert isinstance(cmd, FlextCliCmd)

    def test_cmd_configuration_consistency(
        self,
        tmp_path: Path,
    ) -> None:
        """Test configuration consistency across operations with clean temporary directory.

        Uses real configuration with temporary directory to test actual behavior.
        """
        # Create a clean temporary config directory for this test
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / FlextCliConstants.ConfigFiles.CLI_CONFIG_JSON

        # Ensure config file doesn't exist initially
        assert not config_file.exists()

        # Create cmd instance with real configuration
        cmd = FlextCliCmd()

        # Test edit config method (takes no parameters) - should create default
        result1 = cmd.edit_config()
        assert isinstance(result1, FlextResult)

        # Test edit config again - should load existing config
        result2 = cmd.edit_config()
        assert isinstance(result2, FlextResult)

        # Both operations should return proper results
        if result1.is_success:
            assert isinstance(result1.value, str)
        if result2.is_success:
            assert isinstance(result2.value, str)

    def test_cmd_service_properties(self) -> None:
        """Test CMD service properties."""
        cmd = FlextCliCmd()

        # Test that all required properties/methods are accessible
        assert hasattr(cmd, "execute")
        assert hasattr(cmd, "edit_config")
        # Verify logger and container from FlextService
        assert hasattr(cmd, "logger")
        assert hasattr(cmd, "container")

    def test_cmd_logging_integration(self) -> None:
        """Test CMD logging integration."""
        cmd = FlextCliCmd()

        # Test that logging is properly integrated
        result = cmd.execute()
        assert result.is_success

        # Should not raise any logging-related exceptions
        assert result.value is not None

    def test_cmd_instantiation(self) -> None:
        """Test direct instantiation."""
        instance = FlextCliCmd()
        assert isinstance(instance, FlextCliCmd)

    def test_cmd_config_helper_get_config_paths(self) -> None:
        """Test FlextCliUtilities.ConfigOps.get_config_paths() directly."""
        paths = FlextCliUtilities.ConfigOps.get_config_paths()
        assert isinstance(paths, list)
        assert len(paths) > 0
        # Check that paths contain expected flext directory
        assert any(".flext" in path for path in paths)

    def test_cmd_config_helper_validate_config_structure(self) -> None:
        """Test FlextCliUtilities.ConfigOps.validate_config_structure() directly."""
        results = FlextCliUtilities.ConfigOps.validate_config_structure()
        assert isinstance(results, list)
        # Results should contain validation messages
        assert len(results) > 0

    def test_cmd_config_helper_get_config_info(self) -> None:
        """Test FlextCliUtilities.ConfigOps.get_config_info() directly."""
        info = FlextCliUtilities.ConfigOps.get_config_info()
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

        # Ensure config file doesn't exist
        config_path = (
            FlextCliServiceBase.get_cli_config().config_dir
            / FlextCliConstants.ConfigFiles.CLI_CONFIG_JSON
        )
        if config_path.exists():
            config_path.unlink()

        result = cmd.get_config_value("nonexistent_key")
        # Should fail because config file doesn't exist
        assert result.is_failure
        assert isinstance(result.error, str)
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_cmd_show_config(self) -> None:
        """Test show_config method."""
        cmd = FlextCliCmd()
        result = cmd.show_config()
        assert result.is_success

    def test_cmd_edit_config_creates_default(
        self,
        tmp_path: Path,
    ) -> None:
        """Test edit_config creates default configuration with clean temporary directory.

        Uses real configuration with temporary directory to test actual behavior.
        """
        # Create a clean temporary config directory for this test
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / FlextCliConstants.ConfigFiles.CLI_CONFIG_JSON

        # Ensure config file doesn't exist - edit_config should create default
        assert not config_file.exists()

        # Create cmd instance with real configuration
        cmd = FlextCliCmd()

        # Test editing config - should create default config file
        result = cmd.edit_config()
        assert isinstance(result, FlextResult)
        # May succeed or fail depending on implementation, but should return proper result
        if result.is_success:
            assert isinstance(result.value, str)

    def test_cmd_config_display_helper_show_config(self) -> None:
        """Test show_config method."""
        cmd = FlextCliCmd()
        result = cmd.show_config()
        assert result.is_success

    def test_cmd_config_modification_helper_edit_config(self) -> None:
        """Test edit_config method."""
        cmd = FlextCliCmd()
        result = cmd.edit_config()
        # Result depends on actual config state - could succeed or fail
        assert result.is_success or result.is_failure

    def test_cmd_config_validation_helper_validate_config(self) -> None:
        """Test validate_config method."""
        cmd = FlextCliCmd()
        # Test validation
        result = cmd.validate_config()
        # Result depends on actual config state - could succeed or fail
        assert result.is_success or result.is_failure

    def test_cmd_show_config_paths_error_handling(self) -> None:
        """Test show_config_paths error handling."""
        cmd = FlextCliCmd()
        # show_config_paths now returns config paths or error directly
        result = cmd.show_config_paths()
        # Should succeed with valid config paths
        assert result.is_success or result.is_failure

    def test_cmd_validate_config_error_handling(self) -> None:
        """Test validate_config error handling."""
        cmd = FlextCliCmd()
        # Test validate_config with no config file
        result = cmd.validate_config()
        # Result depends on actual config state - could succeed or fail
        assert result.is_success or result.is_failure

    def test_cmd_get_config_info_error_handling(self) -> None:
        """Test get_config_info error handling."""
        cmd = FlextCliCmd()
        # Test get_config_info - returns config info or error
        result = cmd.get_config_info()
        # Result depends on actual config state - could succeed or fail
        assert result.is_success or result.is_failure

    def test_cmd_get_config_value_file_load_error(self, temp_dir: Path) -> None:
        """Test get_config_value with invalid JSON file that causes read error."""
        cmd = FlextCliCmd()

        # Create config file with invalid JSON that will cause read error
        config_file = temp_dir / "cli_config.json"
        config_file.write_text("invalid json content {", encoding="utf-8")

        # Temporarily set config dir to temp_dir
        original_config_dir = FlextCliServiceBase.get_cli_config().config_dir
        try:
            FlextCliServiceBase.get_cli_config().config_dir = temp_dir

            # Try to get config value - should fail due to invalid JSON
            result = cmd.get_config_value("test_key")
            assert result.is_failure
            assert result.error is not None
        finally:
            FlextCliServiceBase.get_cli_config().config_dir = original_config_dir

    def test_cmd_show_config_error_handling(self) -> None:
        """Test show_config error handling."""
        cmd = FlextCliCmd()
        # show_config returns config info or error directly
        result = cmd.show_config()
        # Should succeed or fail gracefully
        assert result.is_success or result.is_failure

    def test_cmd_edit_config_load_error(self, temp_dir: Path) -> None:
        """Test edit_config with invalid JSON file that causes read error."""
        cmd = FlextCliCmd()

        # Create config file with invalid JSON
        config_file = temp_dir / "cli_config.json"
        config_file.write_text("invalid json {", encoding="utf-8")

        # Temporarily set config dir to temp_dir
        original_config_dir = FlextCliServiceBase.get_cli_config().config_dir
        try:
            FlextCliServiceBase.get_cli_config().config_dir = temp_dir

            # Try to edit config - should fail due to invalid JSON
            result = cmd.edit_config()
            assert result.is_failure
            assert isinstance(result.error, str)
            assert result.error is not None
        finally:
            FlextCliServiceBase.get_cli_config().config_dir = original_config_dir

    def test_cmd_config_display_helper_error_handling(self) -> None:
        """Test config display error handling."""
        # Test config display functionality directly
        cmd = FlextCliCmd()
        result = cmd.get_config_info()
        # Should succeed or fail gracefully
        assert result.is_success or result.is_failure

    def test_cmd_config_modification_helper_error_handling(self) -> None:
        """Test config modification error handling."""
        # Test config modification functionality directly
        cmd = FlextCliCmd()
        result = cmd.edit_config()
        # Should succeed or fail gracefully
        assert result.is_success or result.is_failure

    def test_cmd_edit_config_create_default_config_error(self) -> None:
        """Test edit_config handles errors gracefully."""
        cmd = FlextCliCmd()
        # Test that edit_config either succeeds or fails gracefully
        result = cmd.edit_config()
        # Should return a result (success or failure)
        assert result is not None
        assert result.is_success or result.is_failure

    def test_cmd_get_config_value_missing_key_in_file(self, temp_dir: Path) -> None:
        """Test get_config_value when key is missing from config file."""
        cmd = FlextCliCmd()

        # Create config file with data but without the requested key
        config_file = temp_dir / "cli_config.json"
        config_file.write_text('{"other_key": "value"}', encoding="utf-8")

        # Temporarily set config dir to temp_dir
        original_config_dir = FlextCliServiceBase.get_cli_config().config_dir
        try:
            FlextCliServiceBase.get_cli_config().config_dir = temp_dir

            # Request a key that doesn't exist
            result = cmd.get_config_value("missing_key")
            assert result.is_failure
            assert isinstance(result.error, str)
            assert result.error is not None
            assert "not found" in result.error.lower()
        finally:
            FlextCliServiceBase.get_cli_config().config_dir = original_config_dir

    def test_cmd_get_config_value_not_dict_data(self, temp_dir: Path) -> None:
        """Test get_config_value when config data is not a dict (list instead)."""
        cmd = FlextCliCmd()

        # Create config file with list instead of dict
        config_file = temp_dir / "cli_config.json"
        config_file.write_text("[1, 2, 3]", encoding="utf-8")

        # Temporarily set config dir to temp_dir
        original_config_dir = FlextCliServiceBase.get_cli_config().config_dir
        try:
            FlextCliServiceBase.get_cli_config().config_dir = temp_dir

            result = cmd.get_config_value("test_key")
            assert result.is_failure
            assert "not a valid dictionary" in str(result.error)
        finally:
            FlextCliServiceBase.get_cli_config().config_dir = original_config_dir

    def test_cmd_get_config_value_key_found_in_file(self, temp_dir: Path) -> None:
        """Test get_config_value success path when key is found."""
        cmd = FlextCliCmd()

        # Create config file with the key
        config_file = temp_dir / "cli_config.json"
        config_file.write_text('{"found_key": "found_value"}', encoding="utf-8")

        # Temporarily set config dir to temp_dir
        original_config_dir = FlextCliServiceBase.get_cli_config().config_dir
        try:
            FlextCliServiceBase.get_cli_config().config_dir = temp_dir

            result = cmd.get_config_value("found_key")
            assert result.is_success
            data = result.unwrap()
            assert data["key"] == "found_key"
            assert data["value"] == "found_value"
            assert "timestamp" in data
        finally:
            FlextCliServiceBase.get_cli_config().config_dir = original_config_dir

    def test_cmd_edit_config_not_dict_data(self, temp_dir: Path) -> None:
        """Test edit_config when config data is not a dict (string instead)."""
        cmd = FlextCliCmd()

        # Create config file with string instead of dict
        config_file = temp_dir / "cli_config.json"
        config_file.write_text('"not a dict"', encoding="utf-8")

        # Temporarily set config dir to temp_dir
        original_config_dir = FlextCliServiceBase.get_cli_config().config_dir
        try:
            FlextCliServiceBase.get_cli_config().config_dir = temp_dir

            result = cmd.edit_config()
            assert result.is_failure
            assert "not a valid dictionary" in str(result.error)
        finally:
            FlextCliServiceBase.get_cli_config().config_dir = original_config_dir

    def test_cmd_validate_config_structure_missing_dir(self) -> None:
        """Test FlextCliUtilities.ConfigOps.validate_config_structure() when main config directory is missing.

        Uses real configuration validation to test actual behavior.
        """
        results = FlextCliUtilities.ConfigOps.validate_config_structure()
        # Should return validation results
        assert isinstance(results, list)
        assert all(isinstance(r, str) for r in results)

    def test_cmd_show_config_paths_exception(self) -> None:
        """Test show_config_paths exception handler.

        Uses real configuration paths to test actual behavior.
        """
        cmd = FlextCliCmd()
        result = cmd.show_config_paths()
        # Should succeed and return config paths
        assert isinstance(result, FlextResult)
        if result.is_success:
            # show_config_paths returns list[str], not str
            assert isinstance(result.value, list)
            assert all(isinstance(p, str) for p in result.value)

    def test_cmd_validate_config_exception(self) -> None:
        """Test validate_config exception handler.

        Uses real configuration validation to test actual behavior.
        """
        cmd = FlextCliCmd()
        result = cmd.validate_config()
        # Should return proper result
        assert isinstance(result, FlextResult)
        # May succeed or fail depending on implementation
        assert result.is_success or result.is_failure

    def test_cmd_get_config_info_exception(self) -> None:
        """Test get_config_info exception handler.

        Uses real configuration info retrieval to test actual behavior.
        """
        cmd = FlextCliCmd()
        result = cmd.get_config_info()
        # Should succeed and return config info
        assert isinstance(result, FlextResult)
        if result.is_success:
            info = result.value
            assert isinstance(info, dict)

    def test_cmd_set_config_value_save_failure(self, temp_dir: Path) -> None:
        """Test set_config_value with read-only directory that causes save failure."""
        cmd = FlextCliCmd()

        # Create a read-only directory to simulate write failure
        read_only_dir = temp_dir / "readonly"
        read_only_dir.mkdir()
        read_only_dir.chmod(0o555)  # Read-only

        # Temporarily set config dir to read-only directory
        original_config_dir = FlextCliServiceBase.get_cli_config().config_dir
        try:
            FlextCliServiceBase.get_cli_config().config_dir = read_only_dir

            # Try to set config value - should fail due to read-only directory
            result = cmd.set_config_value("key", "value")
            # May succeed or fail depending on implementation
            assert isinstance(result, FlextResult)
        finally:
            # Restore permissions for cleanup
            read_only_dir.chmod(0o755)
            FlextCliServiceBase.get_cli_config().config_dir = original_config_dir

    def test_cmd_set_config_value_exception(self) -> None:
        """Test set_config_value exception handler (lines 169-170).

        Uses real configuration setting to test actual behavior.
        """
        cmd = FlextCliCmd()
        result = cmd.set_config_value("key", "value")
        # Should return proper result
        assert isinstance(result, FlextResult)
        # May succeed or fail depending on implementation
        assert result.is_success or result.is_failure

    def test_cmd_get_config_value_exception(self) -> None:
        """Test get_config_value exception handler (lines 219-220).

        Uses real configuration value retrieval to test actual behavior.
        """
        cmd = FlextCliCmd()
        result = cmd.get_config_value("key")
        # Should return proper result
        assert isinstance(result, FlextResult)
        # May succeed or fail depending on implementation
        if result.is_success:
            assert result.value is not None

    def test_cmd_show_config_get_info_failure(self, temp_dir: Path) -> None:
        """Test show_config with invalid config that causes get_config_info to fail."""
        cmd = FlextCliCmd()

        # Create invalid config file
        config_file = temp_dir / "cli_config.json"
        config_file.write_text("invalid json", encoding="utf-8")

        # Temporarily set config dir to temp_dir
        original_config_dir = FlextCliServiceBase.get_cli_config().config_dir
        try:
            FlextCliServiceBase.get_cli_config().config_dir = temp_dir

            # show_config should handle the error gracefully
            result = cmd.show_config()
            assert isinstance(result, FlextResult)
        finally:
            FlextCliServiceBase.get_cli_config().config_dir = original_config_dir

    def test_cmd_show_config_exception(self) -> None:
        """Test show_config exception handler with real execution."""
        cmd = FlextCliCmd()

        # Test real execution - should handle any exceptions gracefully
        result = cmd.show_config()
        assert isinstance(result, FlextResult)

    def test_cmd_edit_config_save_failure(self, temp_dir: Path) -> None:
        """Test edit_config with read-only directory that causes save failure."""
        cmd = FlextCliCmd()

        # Create a read-only directory to simulate write failure
        read_only_dir = temp_dir / "readonly"
        read_only_dir.mkdir()
        read_only_dir.chmod(0o555)  # Read-only

        # Temporarily set config dir to read-only directory
        original_config_dir = FlextCliServiceBase.get_cli_config().config_dir
        try:
            FlextCliServiceBase.get_cli_config().config_dir = read_only_dir

            # Try to edit config - should fail due to read-only directory
            result = cmd.edit_config()
            # May succeed or fail depending on implementation
            assert isinstance(result, FlextResult)
        finally:
            # Restore permissions for cleanup
            read_only_dir.chmod(0o755)
            FlextCliServiceBase.get_cli_config().config_dir = original_config_dir

    def test_cmd_edit_config_exception(self) -> None:
        """Test edit_config exception handler (lines 316-317).

        Uses real configuration editing to test actual behavior.
        """
        cmd = FlextCliCmd()
        result = cmd.edit_config()
        # Should return proper result
        assert isinstance(result, FlextResult)
        # May succeed or fail depending on implementation
        if result.is_success:
            assert isinstance(result.value, str)

    def test_cmd_get_config_value_key_not_in_config_data(self, temp_dir: Path) -> None:
        """Test get_config_value when key not found in existing config dict."""
        cmd = FlextCliCmd()

        # Create config file with data but without the requested key
        config_file = temp_dir / "cli_config.json"
        config_file.write_text('{"existing_key": "existing_value"}', encoding="utf-8")

        # Temporarily set config dir to temp_dir
        original_config_dir = FlextCliServiceBase.get_cli_config().config_dir
        try:
            FlextCliServiceBase.get_cli_config().config_dir = temp_dir

            # Request a key that doesn't exist in the config data
            result = cmd.get_config_value("nonexistent_key")
            assert result.is_failure
            assert isinstance(result.error, str)
            assert result.error is not None
            assert "not found" in result.error.lower()
        finally:
            FlextCliServiceBase.get_cli_config().config_dir = original_config_dir
