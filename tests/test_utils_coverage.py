"""Test coverage for FlextCliUtilities module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

from pydantic import BaseModel

from flext_cli import FlextCliUtilities
from flext_core import FlextLogger, FlextResult


def get_temp_file(suffix: str = ".txt") -> str:
    """Get a temporary file path."""
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
        return tmp_file.name


def get_temp_dir() -> str:
    """Get a temporary directory path."""
    return tempfile.mkdtemp()


class TestFlextCliUtilities:
    """Test FlextCliUtilities class."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.utils = FlextCliUtilities()

    def test_utilities_initialization(self) -> None:
        """Test utilities initialization."""
        utils = FlextCliUtilities()
        assert utils is not None
        assert hasattr(utils, "_container")
        assert hasattr(utils, "_logger")

    def test_execute(self) -> None:
        """Test execute method."""
        result = self.utils.execute()
        assert result.is_success
        assert result.value is None

    def test_logger_property(self) -> None:
        """Test logger property."""
        logger = self.utils.logger
        # FlextLogger is the correct type, not logging.Logger
        assert isinstance(logger, FlextLogger)

    def test_container_property(self) -> None:
        """Test container property."""
        container = self.utils.container
        assert container is not None

    def test_get_base_config_dict(self) -> None:
        """Test get base config dict."""
        config = FlextCliUtilities.get_base_config_dict()
        assert config is not None
        assert config.get("validate_assignment") is True
        assert config.get("use_enum_values") is True
        assert config.get("arbitrary_types_allowed") is True

    def test_get_strict_config_dict(self) -> None:
        """Test get strict config dict."""
        config = FlextCliUtilities.get_strict_config_dict()
        assert config is not None
        assert config.get("validate_assignment") is True
        assert config.get("use_enum_values") is True
        assert config.get("arbitrary_types_allowed") is False
        assert config.get("str_strip_whitespace") is True

    def test_home_path(self) -> None:
        """Test home path."""
        path = FlextCliUtilities.home_path()
        assert isinstance(path, Path)
        assert path.is_absolute()

    def test_token_file_path(self) -> None:
        """Test token file path."""
        path = FlextCliUtilities.token_file_path()
        assert isinstance(path, Path)
        assert path.name == "token.json"

    def test_refresh_token_file_path(self) -> None:
        """Test refresh token file path."""
        path = FlextCliUtilities.refresh_token_file_path()
        assert isinstance(path, Path)
        assert path.name == "refresh_token.json"

    def test_get_settings_config_dict(self) -> None:
        """Test get settings config dict."""
        config = FlextCliUtilities.get_settings_config_dict()
        assert config is not None
        assert isinstance(config, dict)

    def test_validate_with_pydantic_model(self) -> None:
        """Test validate with pydantic model."""

        class TestModel(BaseModel):
            name: str
            age: int

        test_data = {"name": "test", "age": 25}
        result = FlextCliUtilities.validate_with_pydantic_model(test_data, TestModel)
        assert result.is_success
        assert isinstance(result.value, TestModel)
        assert result.value.name == "test"
        assert result.value.age == 25

    def test_validate_data(self) -> None:
        """Test validate data."""
        test_data = {"name": "test", "age": 25}
        validator_dict = {"name": str, "age": int}
        result = FlextCliUtilities.validate_data(test_data, validator_dict)
        assert result.is_success
        assert result.value is True

    def test_safe_json_stringify(self) -> None:
        """Test safe JSON stringify."""
        test_data = {"key": "value", "number": 42}
        result = FlextCliUtilities.safe_json_stringify(test_data)
        assert isinstance(result, str)
        assert "key" in result
        assert "value" in result

    def test_json_stringify_with_result(self) -> None:
        """Test JSON stringify with result."""
        test_data = {"key": "value", "number": 42}
        result = FlextCliUtilities.json_stringify_with_result(test_data)
        assert result.is_success
        assert isinstance(result.value, str)
        assert "key" in result.value

    def test_safe_json_stringify_flext_result(self) -> None:
        """Test safe JSON stringify with FlextResult."""
        test_data: dict[str, object] = {"key": "value", "number": 42}
        flext_result = FlextResult[object].ok(test_data)
        result = FlextCliUtilities.safe_json_stringify_flext_result(flext_result)
        assert isinstance(result, str)
        assert "key" in result

    def test_file_operations_file_exists(self) -> None:
        """Test file operations file exists."""
        with patch("pathlib.Path.exists", return_value=True):
            result = FlextCliUtilities.FileOperations.file_exists(get_temp_file(".txt"))
            assert result is True

    def test_file_operations_get_file_size(self) -> None:
        """Test file operations get file size."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.stat") as mock_stat,
        ):
            mock_stat.return_value.st_size = 1024
            result = FlextCliUtilities.FileOperations.get_file_size(
                get_temp_file(".txt")
            )
            assert result.is_success
            assert result.value == 1024

    def test_file_operations_save_json_file(self) -> None:
        """Test file operations save JSON file."""
        test_data: dict[str, object] = {"key": "value", "number": 42}
        with patch("pathlib.Path.open", mock_open()) as mock_file:
            result = FlextCliUtilities.FileOperations.save_json_file(
                get_temp_file(".json"), test_data
            )
            assert result.is_success
            mock_file.assert_called_once()

    def test_file_operations_load_json_file(self) -> None:
        """Test file operations load JSON file."""
        test_data = {"key": "value", "number": 42}
        with patch("pathlib.Path.open", mock_open(read_data=json.dumps(test_data))):
            result = FlextCliUtilities.FileOperations.load_json_file(
                get_temp_file(".json")
            )
            assert result.is_success
            assert result.value == test_data

    def test_formatting_format_json(self) -> None:
        """Test formatting format JSON."""
        test_data = {"key": "value", "number": 42}
        result = FlextCliUtilities.Formatting.format_json(test_data)
        assert result.is_success
        assert isinstance(result.value, str)
        assert "key" in result.value

    def test_formatting_format_yaml(self) -> None:
        """Test formatting format YAML."""
        test_data = {"key": "value", "number": 42}
        result = FlextCliUtilities.Formatting.format_yaml(test_data)
        assert result.is_success
        assert isinstance(result.value, str)
        assert "key" in result.value

    def test_formatting_format_csv(self) -> None:
        """Test formatting format CSV."""
        test_data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        result = FlextCliUtilities.Formatting.format_csv(test_data)
        assert result.is_success
        assert isinstance(result.value, str)
        assert "John" in result.value

    def test_formatting_format_table(self) -> None:
        """Test formatting format table."""
        test_data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        result = FlextCliUtilities.Formatting.format_table(test_data)
        assert result.is_success
        assert isinstance(result.value, str)
        assert "John" in result.value
