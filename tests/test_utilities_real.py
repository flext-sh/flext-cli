"""Real functional tests for utilities module - NO MOCKS!

Tests the new utility classes with static methods, following user requirement:
"criar utilities classes com métodos estáticos"

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from flext_core import FlextResult

from flext_cli.config import FlextCliSettings
from flext_cli.utilities import (
    FlextCliFileUtilities,
    FlextCliFormattingUtilities,
    FlextCliSystemUtilities,
    FlextCliTimeUtilities,
    FlextCliValidationUtilities,
)


class TestFlextCliValidationUtilitiesReal:
    """Real tests for FlextCliValidationUtilities static methods."""

    def test_validate_email_real(self) -> None:
        """Test email validation with real functionality."""
        # Valid emails
        valid_result = FlextCliValidationUtilities.validate_email("test@example.com")
        assert isinstance(valid_result, FlextResult)
        assert valid_result.is_success
        assert valid_result.value is True

        # Invalid emails
        invalid_result = FlextCliValidationUtilities.validate_email("invalid-email")
        assert isinstance(invalid_result, FlextResult)
        assert not invalid_result.is_success
        assert "Invalid email format" in invalid_result.error

        # Empty email
        empty_result = FlextCliValidationUtilities.validate_email("")
        assert isinstance(empty_result, FlextResult)
        assert not empty_result.is_success

    def test_validate_path_real(self) -> None:
        """Test path validation with real functionality."""
        # Valid path string
        path_result = FlextCliValidationUtilities.validate_path("/tmp/test")
        assert isinstance(path_result, FlextResult)
        assert path_result.is_success
        assert isinstance(path_result.value, Path)

        # Valid Path object
        path_obj_result = FlextCliValidationUtilities.validate_path(Path("/tmp/test"))
        assert isinstance(path_obj_result, FlextResult)
        assert path_obj_result.is_success

        # Invalid path
        invalid_result = FlextCliValidationUtilities.validate_path(123)  # type: ignore
        assert isinstance(invalid_result, FlextResult)
        assert not invalid_result.is_success

    def test_validate_config_real(self) -> None:
        """Test config validation with real functionality."""
        # Valid FlextCliSettings
        config = FlextCliSettings()
        config_result = FlextCliValidationUtilities.validate_config(config)
        assert isinstance(config_result, FlextResult)
        assert config_result.is_success

        # None config
        none_result = FlextCliValidationUtilities.validate_config(None)
        assert isinstance(none_result, FlextResult)
        assert not none_result.is_success

    def test_validate_json_string_real(self) -> None:
        """Test JSON string validation with real functionality."""
        # Valid JSON
        valid_json = '{"key": "value", "number": 123}'
        json_result = FlextCliValidationUtilities.validate_json_string(valid_json)
        assert isinstance(json_result, FlextResult)
        assert json_result.is_success
        assert json_result.value["key"] == "value"

        # Invalid JSON
        invalid_result = FlextCliValidationUtilities.validate_json_string(
            "invalid json"
        )
        assert isinstance(invalid_result, FlextResult)
        assert not invalid_result.is_success


class TestFlextCliFileUtilitiesReal:
    """Real tests for FlextCliFileUtilities static methods."""

    def setup_method(self) -> None:
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ensure_directory_exists_real(self) -> None:
        """Test directory creation with real functionality."""
        test_dir = self.temp_path / "new_directory"
        result = FlextCliFileUtilities.ensure_directory_exists(test_dir)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_read_write_text_file_real(self) -> None:
        """Test file read/write operations with real functionality."""
        test_file = self.temp_path / "test.txt"
        test_content = "Hello, FLEXT CLI utilities!"

        # Write file
        write_result = FlextCliFileUtilities.write_text_file(test_file, test_content)
        assert isinstance(write_result, FlextResult)
        assert write_result.is_success

        # Read file
        read_result = FlextCliFileUtilities.read_text_file(test_file)
        assert isinstance(read_result, FlextResult)
        assert read_result.is_success
        assert read_result.value == test_content

        # Read non-existent file
        missing_result = FlextCliFileUtilities.read_text_file(
            self.temp_path / "missing.txt"
        )
        assert isinstance(missing_result, FlextResult)
        assert not missing_result.is_success

    def test_get_file_info_real(self) -> None:
        """Test file info retrieval with real functionality."""
        test_file = self.temp_path / "info_test.txt"
        test_file.write_text("test content")

        info_result = FlextCliFileUtilities.get_file_info(test_file)
        assert isinstance(info_result, FlextResult)
        assert info_result.is_success

        info = info_result.value
        assert info["is_file"] is True
        assert info["is_directory"] is False
        assert "size" in info
        assert "modified" in info


class TestFlextCliFormattingUtilitiesReal:
    """Real tests for FlextCliFormattingUtilities static methods."""

    def test_format_json_pretty_real(self) -> None:
        """Test JSON formatting with real functionality."""
        test_data = {"name": "test", "value": 123, "active": True}
        result = FlextCliFormattingUtilities.format_json_pretty(test_data)

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify it's valid JSON
        parsed = json.loads(result.value)
        assert parsed["name"] == "test"
        assert parsed["value"] == 123

    def test_create_table_real(self) -> None:
        """Test table creation with real functionality."""
        headers = ["Name", "Age", "City"]
        rows = [
            ["Alice", "30", "New York"],
            ["Bob", "25", "London"],
        ]

        table_result = FlextCliFormattingUtilities.create_table(
            "Test Table", headers, rows
        )
        assert isinstance(table_result, FlextResult)
        assert table_result.is_success

        # Table should have title and columns
        table = table_result.value
        assert table.title == "Test Table"

        # Test invalid row length
        invalid_rows = [["Alice", "30"]]  # Missing city
        invalid_result = FlextCliFormattingUtilities.create_table(
            "Test", headers, invalid_rows
        )
        assert isinstance(invalid_result, FlextResult)
        assert not invalid_result.is_success

    def test_format_duration_real(self) -> None:
        """Test duration formatting with real functionality."""
        # Milliseconds
        ms_result = FlextCliFormattingUtilities.format_duration(0.5)
        assert isinstance(ms_result, FlextResult)
        assert ms_result.is_success
        assert "ms" in ms_result.value

        # Seconds
        sec_result = FlextCliFormattingUtilities.format_duration(45.2)
        assert isinstance(sec_result, FlextResult)
        assert sec_result.is_success
        assert "s" in sec_result.value

        # Minutes
        min_result = FlextCliFormattingUtilities.format_duration(125.0)
        assert isinstance(min_result, FlextResult)
        assert min_result.is_success
        assert "m" in min_result.value

        # Negative duration
        neg_result = FlextCliFormattingUtilities.format_duration(-10)
        assert isinstance(neg_result, FlextResult)
        assert not neg_result.is_success

    def test_truncate_string_real(self) -> None:
        """Test string truncation with real functionality."""
        # No truncation needed
        short_result = FlextCliFormattingUtilities.truncate_string("short", 10)
        assert isinstance(short_result, FlextResult)
        assert short_result.is_success
        assert short_result.value == "short"

        # Truncation needed
        long_result = FlextCliFormattingUtilities.truncate_string(
            "very long string", 10
        )
        assert isinstance(long_result, FlextResult)
        assert long_result.is_success
        assert len(long_result.value) == 10
        assert long_result.value.endswith("...")


class TestFlextCliSystemUtilitiesReal:
    """Real tests for FlextCliSystemUtilities static methods."""

    def test_environment_variable_operations_real(self) -> None:
        """Test environment variable operations with real functionality."""
        var_name = "FLEXT_CLI_TEST_VAR"
        test_value = "test_value_123"

        # Set environment variable
        set_result = FlextCliSystemUtilities.set_environment_variable(
            var_name, test_value
        )
        assert isinstance(set_result, FlextResult)
        assert set_result.is_success

        # Get environment variable
        get_result = FlextCliSystemUtilities.get_environment_variable(var_name)
        assert isinstance(get_result, FlextResult)
        assert get_result.is_success
        assert get_result.value == test_value

        # Get non-existent variable with default
        default_result = FlextCliSystemUtilities.get_environment_variable(
            "NONEXISTENT_VAR", "default"
        )
        assert isinstance(default_result, FlextResult)
        assert default_result.is_success
        assert default_result.value == "default"

        # Get non-existent variable without default
        missing_result = FlextCliSystemUtilities.get_environment_variable(
            "NONEXISTENT_VAR"
        )
        assert isinstance(missing_result, FlextResult)
        assert not missing_result.is_success

    def test_get_current_working_directory_real(self) -> None:
        """Test current working directory retrieval with real functionality."""
        cwd_result = FlextCliSystemUtilities.get_current_working_directory()
        assert isinstance(cwd_result, FlextResult)
        assert cwd_result.is_success
        assert isinstance(cwd_result.value, Path)
        assert cwd_result.value.exists()

    def test_check_file_permissions_real(self) -> None:
        """Test file permission checking with real functionality."""
        # Create a temporary file
        temp_file = Path(tempfile.mktemp())
        temp_file.write_text("test content", encoding="utf-8")

        try:
            # Check read permission
            read_result = FlextCliSystemUtilities.check_file_permissions(temp_file, "r")
            assert isinstance(read_result, FlextResult)
            assert read_result.is_success
            assert read_result.value is True

            # Check write permission
            write_result = FlextCliSystemUtilities.check_file_permissions(
                temp_file, "w"
            )
            assert isinstance(write_result, FlextResult)
            assert write_result.is_success

            # Check invalid permission mode
            invalid_result = FlextCliSystemUtilities.check_file_permissions(
                temp_file, "z"
            )
            assert isinstance(invalid_result, FlextResult)
            assert not invalid_result.is_success

        finally:
            temp_file.unlink(missing_ok=True)


class TestFlextCliTimeUtilitiesReal:
    """Real tests for FlextCliTimeUtilities static methods."""

    def test_get_current_timestamp_real(self) -> None:
        """Test current timestamp retrieval with real functionality."""
        timestamp_result = FlextCliTimeUtilities.get_current_timestamp()
        assert isinstance(timestamp_result, FlextResult)
        assert timestamp_result.is_success
        assert isinstance(timestamp_result.value, datetime)
        assert timestamp_result.value.tzinfo == UTC

    def test_format_timestamp_real(self) -> None:
        """Test timestamp formatting with real functionality."""
        test_dt = datetime(2025, 1, 15, 12, 30, 45, tzinfo=UTC)
        format_result = FlextCliTimeUtilities.format_timestamp(test_dt)

        assert isinstance(format_result, FlextResult)
        assert format_result.is_success
        assert "2025-01-15" in format_result.value
        assert "12:30:45" in format_result.value

        # Custom format
        custom_result = FlextCliTimeUtilities.format_timestamp(test_dt, "%Y/%m/%d")
        assert isinstance(custom_result, FlextResult)
        assert custom_result.is_success
        assert custom_result.value == "2025/01/15"

        # Invalid input
        invalid_result = FlextCliTimeUtilities.format_timestamp("not a datetime")  # type: ignore
        assert isinstance(invalid_result, FlextResult)
        assert not invalid_result.is_success

    def test_parse_timestamp_real(self) -> None:
        """Test timestamp parsing with real functionality."""
        timestamp_str = "2025-01-15 12:30:45"
        parse_result = FlextCliTimeUtilities.parse_timestamp(timestamp_str)

        assert isinstance(parse_result, FlextResult)
        assert parse_result.is_success
        assert isinstance(parse_result.value, datetime)
        assert parse_result.value.year == 2025
        assert parse_result.value.month == 1
        assert parse_result.value.day == 15

        # Invalid format
        invalid_result = FlextCliTimeUtilities.parse_timestamp("invalid date")
        assert isinstance(invalid_result, FlextResult)
        assert not invalid_result.is_success

    def test_get_time_difference_real(self) -> None:
        """Test time difference calculation with real functionality."""
        start = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        end = datetime(2025, 1, 15, 12, 0, 30, tzinfo=UTC)

        diff_result = FlextCliTimeUtilities.get_time_difference(start, end)
        assert isinstance(diff_result, FlextResult)
        assert diff_result.is_success
        assert diff_result.value == 30.0  # 30 seconds

        # Invalid inputs
        invalid_result = FlextCliTimeUtilities.get_time_difference("not datetime", end)  # type: ignore
        assert isinstance(invalid_result, FlextResult)
        assert not invalid_result.is_success


class TestUtilitiesIntegrationReal:
    """Integration tests for utility classes working together."""

    def test_utilities_integration_workflow_real(self) -> None:
        """Test utilities working together in a real workflow."""
        # 1. Get current timestamp
        timestamp_result = FlextCliTimeUtilities.get_current_timestamp()
        assert timestamp_result.is_success

        # 2. Format timestamp
        format_result = FlextCliTimeUtilities.format_timestamp(timestamp_result.value)
        assert format_result.is_success

        # 3. Create JSON data with timestamp
        data = {"timestamp": format_result.value, "status": "active"}
        json_result = FlextCliFormattingUtilities.format_json_pretty(data)
        assert json_result.is_success

        # 4. Write to temporary file
        temp_file = Path(tempfile.mktemp(suffix=".json"))
        try:
            write_result = FlextCliFileUtilities.write_text_file(
                temp_file, json_result.value
            )
            assert write_result.is_success

            # 5. Read back and validate
            read_result = FlextCliFileUtilities.read_text_file(temp_file)
            assert read_result.is_success

            # 6. Validate JSON content
            validation_result = FlextCliValidationUtilities.validate_json_string(
                read_result.value
            )
            assert validation_result.is_success
            assert validation_result.value["status"] == "active"

        finally:
            temp_file.unlink(missing_ok=True)

    def test_all_utility_classes_static_methods_real(self) -> None:
        """Test that all utility classes have working static methods."""
        # All methods should be callable as static methods
        assert callable(FlextCliValidationUtilities.validate_email)
        assert callable(FlextCliFileUtilities.ensure_directory_exists)
        assert callable(FlextCliFormattingUtilities.format_json_pretty)
        assert callable(FlextCliSystemUtilities.get_current_working_directory)
        assert callable(FlextCliTimeUtilities.get_current_timestamp)

        # All methods should return FlextResult objects
        email_result = FlextCliValidationUtilities.validate_email("test@example.com")
        cwd_result = FlextCliSystemUtilities.get_current_working_directory()
        time_result = FlextCliTimeUtilities.get_current_timestamp()

        assert isinstance(email_result, FlextResult)
        assert isinstance(cwd_result, FlextResult)
        assert isinstance(time_result, FlextResult)


if __name__ == "__main__":
    # Allow running tests directly
    import pytest

    pytest.main([__file__, "-v"])
