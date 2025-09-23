"""Test coverage for FlextCliUtilities module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import json
import logging
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from flext_cli.utils import FlextCliUtilities
from flext_core import FlextResult


class TestFlextCliUtilities:
    """Test FlextCliUtilities class."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.utils = FlextCliUtilities()

    def test_utilities_initialization(self) -> None:
        """Test utilities initialization."""
        utils = FlextCliUtilities()
        assert utils is not None
        assert hasattr(utils, '_container')
        assert hasattr(utils, '_logger')

    def test_execute(self) -> None:
        """Test execute method."""
        result = self.utils.execute()
        assert result.is_success
        assert result.value is None

    def test_logger_property(self) -> None:
        """Test logger property."""
        logger = self.utils.logger
        assert isinstance(logger, logging.Logger)

    def test_container_property(self) -> None:
        """Test container property."""
        container = self.utils.container
        assert container is not None

    def test_get_base_config_dict(self) -> None:
        """Test get base config dict."""
        config = FlextCliUtilities.get_base_config_dict()
        assert config is not None
        assert config.validate_assignment is True
        assert config.use_enum_values is True
        assert config.arbitrary_types_allowed is True

    def test_get_strict_config_dict(self) -> None:
        """Test get strict config dict."""
        config = FlextCliUtilities.get_strict_config_dict()
        assert config is not None
        assert config.validate_assignment is True
        assert config.use_enum_values is True
        assert config.arbitrary_types_allowed is False
        assert config.str_strip_whitespace is True

    def test_home_path(self) -> None:
        """Test home path."""
        path = FlextCliUtilities.home_path()
        assert isinstance(path, Path)
        assert path.is_absolute()

    def test_config_dir_path(self) -> None:
        """Test config dir path."""
        path = FlextCliUtilities.config_dir_path()
        assert isinstance(path, Path)
        assert path.name == ".flext"

    def test_cache_dir_path(self) -> None:
        """Test cache dir path."""
        path = FlextCliUtilities.cache_dir_path()
        assert isinstance(path, Path)
        assert path.name == ".flext"

    def test_logs_dir_path(self) -> None:
        """Test logs dir path."""
        path = FlextCliUtilities.logs_dir_path()
        assert isinstance(path, Path)
        assert path.name == ".flext"

    def test_temp_dir_path(self) -> None:
        """Test temp dir path."""
        path = FlextCliUtilities.temp_dir_path()
        assert isinstance(path, Path)
        assert path.name == ".flext"

    def test_ensure_dir_exists(self) -> None:
        """Test ensure dir exists."""
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            result = FlextCliUtilities.ensure_dir_exists(Path("/tmp/test_dir"))
            assert result.is_success
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_ensure_dir_exists_existing(self) -> None:
        """Test ensure dir exists with existing directory."""
        with patch('pathlib.Path.exists', return_value=True):
            result = FlextCliUtilities.ensure_dir_exists(Path("/tmp/existing_dir"))
            assert result.is_success

    def test_ensure_dir_exists_error(self) -> None:
        """Test ensure dir exists with error."""
        with patch('pathlib.Path.mkdir', side_effect=OSError("Permission denied")):
            result = FlextCliUtilities.ensure_dir_exists(Path("/invalid/path"))
            assert result.is_failure
            assert "Permission denied" in result.error

    def test_validate_file_path(self) -> None:
        """Test validate file path."""
        result = FlextCliUtilities.validate_file_path(Path("/tmp/test.txt"))
        assert result.is_success

    def test_validate_file_path_none(self) -> None:
        """Test validate file path with None."""
        result = FlextCliUtilities.validate_file_path(None)
        assert result.is_failure
        assert "Path cannot be None" in result.error

    def test_validate_file_path_not_path(self) -> None:
        """Test validate file path with non-Path object."""
        result = FlextCliUtilities.validate_file_path("/tmp/test.txt")
        assert result.is_failure
        assert "Path must be a Path object" in result.error

    def test_validate_file_path_not_exists(self) -> None:
        """Test validate file path with non-existing file."""
        with patch('pathlib.Path.exists', return_value=False):
            result = FlextCliUtilities.validate_file_path(Path("/tmp/nonexistent.txt"))
            assert result.is_failure
            assert "File does not exist" in result.error

    def test_validate_file_path_not_file(self) -> None:
        """Test validate file path with directory."""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=False):
            result = FlextCliUtilities.validate_file_path(Path("/tmp/directory"))
            assert result.is_failure
            assert "Path is not a file" in result.error

    def test_validate_directory_path(self) -> None:
        """Test validate directory path."""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_dir', return_value=True):
            result = FlextCliUtilities.validate_directory_path(Path("/tmp/test_dir"))
            assert result.is_success

    def test_validate_directory_path_none(self) -> None:
        """Test validate directory path with None."""
        result = FlextCliUtilities.validate_directory_path(None)
        assert result.is_failure
        assert "Path cannot be None" in result.error

    def test_validate_directory_path_not_path(self) -> None:
        """Test validate directory path with non-Path object."""
        result = FlextCliUtilities.validate_directory_path("/tmp/test_dir")
        assert result.is_failure
        assert "Path must be a Path object" in result.error

    def test_validate_directory_path_not_exists(self) -> None:
        """Test validate directory path with non-existing directory."""
        with patch('pathlib.Path.exists', return_value=False):
            result = FlextCliUtilities.validate_directory_path(Path("/tmp/nonexistent"))
            assert result.is_failure
            assert "Directory does not exist" in result.error

    def test_validate_directory_path_not_dir(self) -> None:
        """Test validate directory path with file."""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_dir', return_value=False):
            result = FlextCliUtilities.validate_directory_path(Path("/tmp/file.txt"))
            assert result.is_failure
            assert "Path is not a directory" in result.error

    def test_read_json_file(self) -> None:
        """Test read JSON file."""
        test_data = {"key": "value", "number": 42}
        with patch('builtins.open', mock_open(json.dumps(test_data))):
            result = FlextCliUtilities.read_json_file(Path("/tmp/test.json"))
            assert result.is_success
            assert result.value == test_data

    def test_read_json_file_invalid_json(self) -> None:
        """Test read JSON file with invalid JSON."""
        with patch('builtins.open', mock_open("invalid json")):
            result = FlextCliUtilities.read_json_file(Path("/tmp/invalid.json"))
            assert result.is_failure
            assert "JSON decode error" in result.error

    def test_read_json_file_read_error(self) -> None:
        """Test read JSON file with read error."""
        with patch('builtins.open', side_effect=IOError("Read error")):
            result = FlextCliUtilities.read_json_file(Path("/tmp/error.json"))
            assert result.is_failure
            assert "Read error" in result.error

    def test_write_json_file(self) -> None:
        """Test write JSON file."""
        test_data = {"key": "value", "number": 42}
        with patch('builtins.open', mock_open()) as mock_file:
            result = FlextCliUtilities.write_json_file(Path("/tmp/test.json"), test_data)
            assert result.is_success
            mock_file.assert_called_once()

    def test_write_json_file_write_error(self) -> None:
        """Test write JSON file with write error."""
        test_data = {"key": "value"}
        with patch('builtins.open', side_effect=IOError("Write error")):
            result = FlextCliUtilities.write_json_file(Path("/tmp/error.json"), test_data)
            assert result.is_failure
            assert "Write error" in result.error

    def test_write_json_file_json_error(self) -> None:
        """Test write JSON file with JSON encode error."""
        # Create an object that can't be JSON serialized
        test_data = {"key": object()}
        with patch('builtins.open', mock_open()):
            result = FlextCliUtilities.write_json_file(Path("/tmp/error.json"), test_data)
            assert result.is_failure
            assert "JSON encode error" in result.error

    def test_safe_json_loads(self) -> None:
        """Test safe JSON loads."""
        test_data = {"key": "value", "number": 42}
        json_str = json.dumps(test_data)
        result = FlextCliUtilities.safe_json_loads(json_str)
        assert result.is_success
        assert result.value == test_data

    def test_safe_json_loads_invalid(self) -> None:
        """Test safe JSON loads with invalid JSON."""
        result = FlextCliUtilities.safe_json_loads("invalid json")
        assert result.is_failure
        assert "JSON decode error" in result.error

    def test_safe_json_loads_none(self) -> None:
        """Test safe JSON loads with None."""
        result = FlextCliUtilities.safe_json_loads(None)
        assert result.is_failure
        assert "Input cannot be None" in result.error

    def test_safe_json_loads_empty(self) -> None:
        """Test safe JSON loads with empty string."""
        result = FlextCliUtilities.safe_json_loads("")
        assert result.is_failure
        assert "Input cannot be empty" in result.error

    def test_safe_json_dumps(self) -> None:
        """Test safe JSON dumps."""
        test_data = {"key": "value", "number": 42}
        result = FlextCliUtilities.safe_json_dumps(test_data)
        assert result.is_success
        assert json.loads(result.value) == test_data

    def test_safe_json_dumps_invalid(self) -> None:
        """Test safe JSON dumps with invalid data."""
        test_data = {"key": object()}
        result = FlextCliUtilities.safe_json_dumps(test_data)
        assert result.is_failure
        assert "JSON encode error" in result.error

    def test_safe_json_dumps_none(self) -> None:
        """Test safe JSON dumps with None."""
        result = FlextCliUtilities.safe_json_dumps(None)
        assert result.is_failure
        assert "Input cannot be None" in result.error

    def test_format_file_size(self) -> None:
        """Test format file size."""
        assert FlextCliUtilities.format_file_size(1024) == "1.0 KB"
        assert FlextCliUtilities.format_file_size(1048576) == "1.0 MB"
        assert FlextCliUtilities.format_file_size(1073741824) == "1.0 GB"
        assert FlextCliUtilities.format_file_size(512) == "512 B"

    def test_format_file_size_zero(self) -> None:
        """Test format file size with zero."""
        assert FlextCliUtilities.format_file_size(0) == "0 B"

    def test_format_file_size_negative(self) -> None:
        """Test format file size with negative value."""
        assert FlextCliUtilities.format_file_size(-1024) == "-1.0 KB"

    def test_format_duration(self) -> None:
        """Test format duration."""
        assert FlextCliUtilities.format_duration(1.5) == "1.50s"
        assert FlextCliUtilities.format_duration(0.123) == "123ms"
        assert FlextCliUtilities.format_duration(0.001) == "1ms"
        assert FlextCliUtilities.format_duration(0.0005) == "0.5ms"

    def test_format_duration_zero(self) -> None:
        """Test format duration with zero."""
        assert FlextCliUtilities.format_duration(0) == "0ms"

    def test_format_duration_negative(self) -> None:
        """Test format duration with negative value."""
        assert FlextCliUtilities.format_duration(-1.5) == "-1.50s"

    def test_truncate_string(self) -> None:
        """Test truncate string."""
        long_string = "This is a very long string that should be truncated"
        result = FlextCliUtilities.truncate_string(long_string, 20)
        assert result == "This is a very lo..."
        assert len(result) == 20

    def test_truncate_string_short(self) -> None:
        """Test truncate string with short string."""
        short_string = "Short"
        result = FlextCliUtilities.truncate_string(short_string, 20)
        assert result == "Short"

    def test_truncate_string_none(self) -> None:
        """Test truncate string with None."""
        result = FlextCliUtilities.truncate_string(None, 20)
        assert result == "None"

    def test_truncate_string_empty(self) -> None:
        """Test truncate string with empty string."""
        result = FlextCliUtilities.truncate_string("", 20)
        assert result == ""

    def test_validate_output_format(self) -> None:
        """Test validate output format."""
        result = FlextCliUtilities.validate_output_format("table")
        assert result.is_success
        assert result.value == "table"

    def test_validate_output_format_invalid(self) -> None:
        """Test validate output format with invalid format."""
        result = FlextCliUtilities.validate_output_format("invalid")
        assert result.is_failure
        assert "Invalid output format" in result.error

    def test_validate_output_format_none(self) -> None:
        """Test validate output format with None."""
        result = FlextCliUtilities.validate_output_format(None)
        assert result.is_failure
        assert "Output format cannot be None" in result.error

    def test_validate_output_format_empty(self) -> None:
        """Test validate output format with empty string."""
        result = FlextCliUtilities.validate_output_format("")
        assert result.is_failure
        assert "Output format cannot be empty" in result.error


def mock_open(data=""):
    """Mock open function for testing."""
    from unittest.mock import mock_open as _mock_open
    return _mock_open(read_data=data)
