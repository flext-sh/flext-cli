"""Tests for FlextCli Zero-Boilerplate Utility Functions.

This module provides comprehensive tests for FlextCli utility functions that
eliminate boilerplate code and provide zero-configuration setup patterns.

Test Coverage:
    - Quick setup and auto configuration functions
    - Batch validation and confirmation utilities
    - File operations with automatic format detection
    - Output formatting and table creation
    - Batch execution with progress tracking

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml
from flext_core import FlextResult
from rich.console import Console
from rich.table import Table

# Import private functions from their actual module location
from flext_cli.utils_core import (
    _current_timestamp,
    _generate_session_id,
    # _get_version,  # Function removed - not available in new API
    _load_config_file,
    _load_env_overrides,
)

# Import public API functions from main package
from flext_cli import (
    flext_cli_auto_config,
    flext_cli_batch_execute,
    flext_cli_create_table,
    flext_cli_load_file,
    flext_cli_output_data,
    flext_cli_quick_setup,
    flext_cli_require_all,
    flext_cli_save_file,
    flext_cli_validate_all,
)


class TestFlextCliQuickSetup:
    """Test suite for flext_cli_quick_setup function."""

    def test_quick_setup_minimal_config(self) -> None:
        """Test quick setup with minimal configuration."""
        config = {"profile": "test"}

        result = flext_cli_quick_setup(config)

        assert result.success
        cli_context = result.data
        assert cli_context["config"]["profile"] == "test"
        assert cli_context["config"]["debug"] is False  # default
        assert "console" in cli_context
        assert "session_id" in cli_context
        assert cli_context["initialized"] is True

    def test_quick_setup_full_config(self) -> None:
        """Test quick setup with full configuration."""
        config = {
            "profile": "development",
            "debug": True,
            "log_level": "debug",
            "output_format": "json",
            "commands": ["auth", "config"],
            "api_timeout": 60,
            "console_width": 120,
        }

        result = flext_cli_quick_setup(config)

        assert result.success
        cli_context = result.data
        assert cli_context["config"]["profile"] == "development"
        assert cli_context["config"]["debug"] is True
        assert cli_context["config"]["log_level"] == "debug"
        assert cli_context["config"]["output_format"] == "json"
        assert cli_context["config"]["api_timeout"] == 60
        assert isinstance(cli_context["console"], Console)

    def test_quick_setup_default_overrides(self) -> None:
        """Test that user config overrides defaults."""
        config = {"debug": True, "retry_count": 5}

        result = flext_cli_quick_setup(config)

        assert result.success
        cli_context = result.data
        assert cli_context["config"]["debug"] is True  # overridden
        assert cli_context["config"]["retry_count"] == 5  # overridden
        assert cli_context["config"]["profile"] == "default"  # default kept

    def test_quick_setup_console_configuration(self) -> None:
        """Test console configuration in quick setup."""
        config = {"console_width": 100, "color_system": "256", "debug": True}

        result = flext_cli_quick_setup(config)

        assert result.success
        console = result.data["console"]
        assert isinstance(console, Console)

    def test_quick_setup_exception_handling(self) -> None:
        """Test quick setup exception handling."""
        # Mock Console to raise exception
        with patch(
            "flext_cli.core.utils.Console",
            side_effect=Exception("Console init failed"),
        ):
            result = flext_cli_quick_setup({})

            assert not result.success
            assert "CLI setup failed" in result.error
            assert "Console init failed" in result.error


class TestFlextCliAutoConfig:
    """Test suite for flext_cli_auto_config function."""

    def test_auto_config_default_profile(self, tmp_path: Path) -> None:
        """Test auto config with default profile."""
        # Create test config file
        config_file = tmp_path / "flext.yml"
        config_data = {"profile": "test", "debug": True}
        config_file.write_text(yaml.dump(config_data))

        with patch("flext_cli.core.utils._load_env_overrides", return_value={}):
            result = flext_cli_auto_config("default", [str(config_file)])

        assert result.success
        loaded_config = result.data
        assert loaded_config["profile"] == "default"  # profile override
        assert loaded_config["debug"] is True
        assert loaded_config["config_source"] == str(config_file)

    def test_auto_config_custom_profile(self, tmp_path: Path) -> None:
        """Test auto config with custom profile."""
        config_file = tmp_path / "flext-prod.yml"
        config_data = {"api_url": "https://prod.api.flext.sh", "timeout": 30}
        config_file.write_text(yaml.dump(config_data))

        with patch("flext_cli.core.utils._load_env_overrides", return_value={}):
            result = flext_cli_auto_config("production", [str(config_file)])

        assert result.success
        loaded_config = result.data
        assert loaded_config["profile"] == "production"
        assert loaded_config["api_url"] == "https://prod.api.flext.sh"

    def test_auto_config_env_overrides(self, tmp_path: Path) -> None:
        """Test auto config with environment overrides."""
        config_file = tmp_path / "flext.yml"
        config_data = {"debug": False, "api_url": "https://dev.api.flext.sh"}
        config_file.write_text(yaml.dump(config_data))

        env_overrides = {"debug": True, "api_url": "https://override.api.flext.sh"}

        with patch(
            "flext_cli.core.utils._load_env_overrides",
            return_value=env_overrides,
        ):
            result = flext_cli_auto_config("default", [str(config_file)])

        assert result.success
        loaded_config = result.data
        assert loaded_config["debug"] is True  # overridden
        assert loaded_config["api_url"] == "https://override.api.flext.sh"  # overridden
        assert "debug" in loaded_config["env_overrides"]

    def test_auto_config_no_files_found(self) -> None:
        """Test auto config when no config files are found."""
        with patch("flext_cli.core.utils._load_env_overrides", return_value={}):
            result = flext_cli_auto_config("default", ["/nonexistent/config.yml"])

        assert result.success
        loaded_config = result.data
        assert loaded_config["profile"] == "default"
        assert loaded_config["config_source"] is None
        assert "loaded_at" in loaded_config

    def test_auto_config_json_format(self, tmp_path: Path) -> None:
        """Test auto config with JSON format."""
        config_file = tmp_path / "flext.json"
        config_data = {"profile": "json_test", "features": ["auth", "config"]}
        config_file.write_text(json.dumps(config_data))

        with patch("flext_cli.core.utils._load_env_overrides", return_value={}):
            result = flext_cli_auto_config("default", [str(config_file)])

        assert result.success
        loaded_config = result.data
        assert loaded_config["features"] == ["auth", "config"]


class TestFlextCliValidateAll:
    """Test suite for flext_cli_validate_all function."""

    def test_validate_all_success(self) -> None:
        """Test successful validation of all inputs."""
        validations = {
            "email": ("user@example.com", "email"),
            "url": ("https://api.flext.sh", "url"),
        }

        result = flext_cli_validate_all(validations)

        assert result.success
        assert "email" in result.data
        assert "url" in result.data
        assert result.data["email"] == "user@example.com"

    def test_validate_all_failure(self) -> None:
        """Test validation with failure."""
        validations = {
            "email": ("invalid-email", "email"),
            "url": ("https://api.flext.sh", "url"),
        }

        result = flext_cli_validate_all(validations)

        assert not result.success
        assert "Validation failed for email" in result.error

    def test_validate_all_path_types(self, tmp_path: Path) -> None:
        """Test validation with path types."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        validations = {
            "base_path": (str(tmp_path), "path"),
            "config_file": (str(test_file), "file"),
            "data_dir": (str(test_dir), "dir"),
            "new_filename": ("test<>file.txt", "filename"),
        }

        result = flext_cli_validate_all(validations)

        assert result.success
        assert len(result.data) == 4
        assert isinstance(result.data["base_path"], Path)
        assert result.data["new_filename"] == "test__file.txt"

    def test_validate_all_unknown_type(self) -> None:
        """Test validation with unknown type."""
        validations = {
            "test": ("value", "unknown_type"),
        }

        result = flext_cli_validate_all(validations)

        assert not result.success
        assert "Unknown validation type" in result.error


class TestFlextCliRequireAll:
    """Test suite for flext_cli_require_all function."""

    @patch("flext_cli.core.helpers.FlextCliHelper")
    def test_require_all_success(self, mock_helper_class: MagicMock) -> None:
        """Test successful multiple confirmations."""
        mock_helper = mock_helper_class.return_value
        mock_helper.flext_cli_confirm.side_effect = [
            FlextResult[None].ok(True),
            FlextResult[None].ok(True),
            FlextResult[None].ok(True),
        ]

        confirmations = [
            ("Delete data?", False),
            ("Are you sure?", False),
            ("This cannot be undone", False),
        ]

        result = flext_cli_require_all(confirmations)

        assert result.success
        assert result.data is True
        assert mock_helper.flext_cli_confirm.call_count == 3

    @patch("flext_cli.core.helpers.FlextCliHelper")
    def test_require_all_denial(self, mock_helper_class: MagicMock) -> None:
        """Test multiple confirmations with user denial."""
        mock_helper = mock_helper_class.return_value
        mock_helper.flext_cli_confirm.side_effect = [
            FlextResult[None].ok(True),
            FlextResult[None].ok(False),  # User denies second confirmation
        ]

        confirmations = [
            ("Delete data?", False),
            ("Are you sure?", False),
            ("This should not be asked", False),
        ]

        result = flext_cli_require_all(confirmations)

        assert result.success
        assert result.data is False  # User cancelled
        assert mock_helper.flext_cli_confirm.call_count == 2  # Stopped after denial

    @patch("flext_cli.core.helpers.FlextCliHelper")
    def test_require_all_confirmation_failure(
        self,
        mock_helper_class: MagicMock,
    ) -> None:
        """Test multiple confirmations with confirmation failure."""
        mock_helper = mock_helper_class.return_value
        mock_helper.flext_cli_confirm.return_value = FlextResult[None].fail(
            "Confirmation failed",
        )

        confirmations = [("Test?", True)]

        result = flext_cli_require_all(confirmations)

        assert not result.success
        assert "Confirmation failed" in result.error


class TestFlextCliOutputData:
    """Test suite for flext_cli_output_data function."""

    def setup_method(self) -> None:
        """Setup test environment."""
        self.console_mock = MagicMock(spec=Console)

    def test_output_json_format(self) -> None:
        """Test JSON output format."""
        data = {"name": "test", "value": 123}

        result = flext_cli_output_data(data, "json", console=self.console_mock)

        assert result.success
        self.console_mock.print.assert_called_once()
        printed_data = self.console_mock.print.call_args[0][0]
        assert "test" in printed_data
        assert "123" in printed_data

    def test_output_yaml_format(self) -> None:
        """Test YAML output format."""
        data = {"name": "test", "items": ["a", "b", "c"]}

        result = flext_cli_output_data(data, "yaml", console=self.console_mock)

        assert result.success
        self.console_mock.print.assert_called_once()
        printed_data = self.console_mock.print.call_args[0][0]
        assert "name: test" in printed_data

    def test_output_table_format(self) -> None:
        """Test table output format."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]

        result = flext_cli_output_data(data, "table", console=self.console_mock)

        assert result.success
        self.console_mock.print.assert_called_once()
        # Should print a Rich Table
        printed_table = self.console_mock.print.call_args[0][0]
        assert isinstance(printed_table, Table)

    def test_output_csv_format(self) -> None:
        """Test CSV output format."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]

        result = flext_cli_output_data(data, "csv", console=self.console_mock)

        assert result.success
        self.console_mock.print.assert_called_once()
        printed_data = self.console_mock.print.call_args[0][0]
        assert "name,age" in printed_data
        assert "Alice,30" in printed_data

    def test_output_text_format(self) -> None:
        """Test text output format."""
        data = ["item1", "item2", "item3"]

        result = flext_cli_output_data(data, "text", console=self.console_mock)

        assert result.success
        # Should call print for each item
        assert self.console_mock.print.call_count == 3

    def test_output_fallback_format(self) -> None:
        """Test fallback output format."""
        data = {"test": "data"}

        result = flext_cli_output_data(
            data,
            "unknown_format",
            console=self.console_mock,
        )

        assert result.success
        self.console_mock.print.assert_called_once_with(data)

    def test_output_with_format_options(self) -> None:
        """Test output with format-specific options."""
        data = {"test": "data"}

        result = flext_cli_output_data(
            data,
            "json",
            console=self.console_mock,
            indent=4,
        )

        assert result.success
        self.console_mock.print.assert_called_once()


class TestFlextCliCreateTable:
    """Test suite for flext_cli_create_table function."""

    def test_create_table_basic(self) -> None:
        """Test basic table creation."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]

        table = flext_cli_create_table(data, title="Users")

        assert isinstance(table, Table)
        assert table.title == "Users"

    def test_create_table_custom_columns(self) -> None:
        """Test table creation with custom columns."""
        data = [
            {"name": "Alice", "age": 30, "email": "alice@example.com"},
            {"name": "Bob", "age": 25, "email": "bob@example.com"},
        ]

        table = flext_cli_create_table(data, columns=["name", "email"])

        assert isinstance(table, Table)
        # Table should only have the specified columns

    def test_create_table_empty_data(self) -> None:
        """Test table creation with empty data."""
        table = flext_cli_create_table([])

        assert isinstance(table, Table)
        # Should have a "No Data" column

    def test_create_table_non_dict_data(self) -> None:
        """Test table creation with non-dictionary data."""
        data = ["item1", "item2", "item3"]

        table = flext_cli_create_table(data)

        assert isinstance(table, Table)


class TestFlextCliFileOperations:
    """Test suite for file operation utilities."""

    def test_load_file_json(self, tmp_path: Path) -> None:
        """Test loading JSON file."""
        test_file = tmp_path / "test.json"
        test_data = {"name": "test", "value": 123}
        test_file.write_text(json.dumps(test_data))

        result = flext_cli_load_file(test_file)

        assert result.success
        assert result.data == test_data

    def test_load_file_yaml(self, tmp_path: Path) -> None:
        """Test loading YAML file."""
        test_file = tmp_path / "test.yml"
        test_data = {"name": "test", "items": ["a", "b", "c"]}
        test_file.write_text(yaml.dump(test_data))

        result = flext_cli_load_file(test_file)

        assert result.success
        assert result.data == test_data

    def test_load_file_text(self, tmp_path: Path) -> None:
        """Test loading text file."""
        test_file = tmp_path / "test.txt"
        test_content = "This is test content"
        test_file.write_text(test_content)

        result = flext_cli_load_file(test_file, format_type="text")

        assert result.success
        assert result.data == test_content

    def test_load_file_nonexistent(self) -> None:
        """Test loading nonexistent file."""
        result = flext_cli_load_file("/nonexistent/file.txt")

        assert not result.success
        assert "File not found" in result.error

    def test_save_file_json(self, tmp_path: Path) -> None:
        """Test saving JSON file."""
        test_file = tmp_path / "output.json"
        test_data = {"name": "test", "value": 456}

        result = flext_cli_save_file(test_data, test_file)

        assert result.success
        assert test_file.exists()

        # Verify content
        with test_file.open() as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data

    def test_save_file_yaml(self, tmp_path: Path) -> None:
        """Test saving YAML file."""
        test_file = tmp_path / "output.yml"
        test_data = {"name": "test", "config": {"debug": True}}

        result = flext_cli_save_file(test_data, test_file)

        assert result.success
        assert test_file.exists()

        # Verify content
        with test_file.open() as f:
            loaded_data = yaml.safe_load(f)
        assert loaded_data == test_data

    def test_save_file_creates_directories(self, tmp_path: Path) -> None:
        """Test that save_file creates parent directories."""
        test_file = tmp_path / "subdir" / "nested" / "file.json"
        test_data = {"test": "data"}

        result = flext_cli_save_file(test_data, test_file)

        assert result.success
        assert test_file.exists()
        assert test_file.parent.exists()


class TestFlextCliBatchExecute:
    """Test suite for flext_cli_batch_execute function."""

    @patch("flext_cli.core.utils.track")
    def test_batch_execute_success(self, mock_track: MagicMock) -> None:
        """Test successful batch execution."""
        operations = [
            ("op1", lambda: FlextResult[None].ok("result1")),
            ("op2", lambda: FlextResult[None].ok("result2")),
            ("op3", lambda: FlextResult[None].ok("result3")),
        ]
        mock_track.return_value = operations

        result = flext_cli_batch_execute(operations)

        assert result.success
        results = result.data
        assert results["op1"]["success"] is True
        assert results["op1"]["data"] == "result1"
        assert results["op2"]["success"] is True
        assert results["op3"]["success"] is True

    @patch("flext_cli.core.utils.track")
    def test_batch_execute_with_failure_stop(self, mock_track: MagicMock) -> None:
        """Test batch execution with failure and stop_on_error=True."""
        operations = [
            ("op1", lambda: FlextResult[None].ok("result1")),
            ("op2", lambda: FlextResult[None].fail("operation failed")),
            ("op3", lambda: FlextResult[None].ok("result3")),  # Should not execute
        ]
        mock_track.return_value = operations

        result = flext_cli_batch_execute(operations, stop_on_error=True)

        assert not result.success
        assert "Operation op2 failed" in result.error

    @patch("flext_cli.core.utils.track")
    def test_batch_execute_with_failure_continue(self, mock_track: MagicMock) -> None:
        """Test batch execution with failure and stop_on_error=False."""
        operations = [
            ("op1", lambda: FlextResult[None].ok("result1")),
            ("op2", lambda: FlextResult[None].fail("operation failed")),
            ("op3", lambda: FlextResult[None].ok("result3")),
        ]
        mock_track.return_value = operations

        result = flext_cli_batch_execute(operations, stop_on_error=False)

        assert result.success
        results = result.data
        assert results["op1"]["success"] is True
        assert results["op2"]["success"] is False
        assert results["op2"]["error"] == "operation failed"
        assert results["op3"]["success"] is True

    @patch("flext_cli.core.utils.track")
    def test_batch_execute_with_exception(self, mock_track: MagicMock) -> None:
        """Test batch execution with raised exception."""

        def failing_operation() -> FlextResult[str]:
            msg = "Something went wrong"
            raise ValueError(msg)

        operations = [
            ("op1", lambda: FlextResult[None].ok("result1")),
            ("op2", failing_operation),
        ]
        mock_track.return_value = operations

        result = flext_cli_batch_execute(operations, stop_on_error=True)

        assert not result.success
        assert "Operation op2 raised exception" in result.error
        assert "Something went wrong" in result.error


class TestPrivateHelperFunctions:
    """Test suite for private helper functions."""

    def test_generate_session_id(self) -> None:
        """Test session ID generation."""
        session_id = _generate_session_id()

        assert isinstance(session_id, str)
        assert len(session_id) == 8  # UUID first 8 characters

    # def test_get_version(self) -> None:
    #     """Test version retrieval - REMOVED: _get_version function not available in new API."""
    #     pass

    def test_current_timestamp(self) -> None:
        """Test timestamp generation."""
        timestamp = _current_timestamp()

        assert isinstance(timestamp, str)
        # Should be ISO format
        assert "T" in timestamp

    def test_load_env_overrides(self) -> None:
        """Test environment variable loading."""
        test_env = {
            "FLEXT_PROFILE": "test_profile",
            "FLEXT_DEBUG": "true",
            "FLEXT_TIMEOUT": "45",
        }

        with patch.dict(os.environ, test_env):
            overrides = _load_env_overrides()

        assert overrides["profile"] == "test_profile"
        assert overrides["debug"] is True
        assert overrides["timeout"] == 45

    def test_load_config_file_yaml(self, tmp_path: Path) -> None:
        """Test config file loading with YAML."""
        config_file = tmp_path / "test.yml"
        test_data = {"test": "value"}
        config_file.write_text(yaml.dump(test_data))

        result = _load_config_file(config_file)

        assert result.success
        assert result.data == test_data

    def test_load_config_file_json(self, tmp_path: Path) -> None:
        """Test config file loading with JSON."""
        config_file = tmp_path / "test.json"
        test_data = {"test": "value"}
        config_file.write_text(json.dumps(test_data))

        result = _load_config_file(config_file)

        assert result.success
        assert result.data == test_data

    def test_load_config_file_unsupported(self, tmp_path: Path) -> None:
        """Test config file loading with unsupported format."""
        config_file = tmp_path / "test.xml"
        config_file.write_text("<config></config>")

        result = _load_config_file(config_file)

        assert not result.success
        assert "Unsupported config format" in result.error


if __name__ == "__main__":
    pytest.main([__file__])
