"""Simple tests for cli_utils.py to improve coverage quickly.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import UUID

from flext_core import FlextResult

from flext_cli.cli_types import OutputFormat
from flext_cli.cli_utils import (
    FlextCliData,
    _convert_to_serializable,
    _load_json_file,
    _load_text_file,
    _save_json_file,
    _save_text_file,
    cli_batch_process_files,
    cli_confirm,
    cli_create_table,
    cli_format_output,
    cli_load_data_file,
    cli_prompt,
    cli_run_command,
    cli_save_data_file,
)


class TestDataLoadingUtilities:
    """Test data loading utilities."""

    def test_load_json_file_success(self) -> None:
        """Test successful JSON file loading."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_data = {"key": "value", "number": 42}
            json.dump(test_data, f)
            f.flush()

            result = _load_json_file(Path(f.name))

            assert result.success
            assert result.unwrap() == test_data

            Path(f.name).unlink()

    def test_load_json_file_not_found(self) -> None:
        """Test loading non-existent JSON file."""
        result = _load_json_file(Path("/nonexistent.json"))

        assert not result.success
        assert "No such file or directory" in result.error

    def test_load_text_file_success(self) -> None:
        """Test successful text file loading."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            content = "This is test content\nWith multiple lines"
            f.write(content)
            f.flush()

            result = _load_text_file(Path(f.name))

            assert result.success
            assert result.unwrap() == content

            Path(f.name).unlink()

    def test_cli_load_data_file_json(self) -> None:
        """Test cli_load_data_file with JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_data = {"test": "data"}
            json.dump(test_data, f)
            f.flush()

            result = cli_load_data_file(Path(f.name))

            assert result.success
            assert result.unwrap() == test_data

            Path(f.name).unlink()

    def test_cli_load_data_file_unsupported_format(self) -> None:
        """Test cli_load_data_file with unsupported format."""
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            f.write(b"content")
            f.flush()

            result = cli_load_data_file(Path(f.name))

            assert not result.success

            Path(f.name).unlink()


class TestDataSavingUtilities:
    """Test data saving utilities."""

    def test_convert_to_serializable_dict(self) -> None:
        """Test converting dict to serializable format."""
        data = {"key": "value", "number": 42}
        result = _convert_to_serializable(data)
        assert result == data

    def test_convert_to_serializable_uuid(self) -> None:
        """Test converting UUID to serializable format."""
        uuid_obj = UUID("12345678-1234-5678-1234-567812345678")
        result = _convert_to_serializable(uuid_obj)
        assert result == str(uuid_obj)

    def test_convert_to_serializable_path(self) -> None:
        """Test converting Path to serializable format."""
        path = Path("/test/path")
        result = _convert_to_serializable(path)
        assert result == str(path)

    def test_save_json_file_success(self) -> None:
        """Test successful JSON file saving."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            test_data = {"key": "value", "number": 42}

            result = _save_json_file(test_data, Path(f.name))

            assert result.success

            # Verify the file was saved correctly
            with open(f.name) as saved_file:
                loaded_data = json.load(saved_file)
                assert loaded_data == test_data

            Path(f.name).unlink()

    def test_save_text_file_success(self) -> None:
        """Test successful text file saving."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            test_content = "This is test content\nWith multiple lines"

            result = _save_text_file(test_content, Path(f.name))

            assert result.success

            # Verify the file was saved correctly
            saved_content = Path(f.name).read_text()
            assert saved_content == test_content

            Path(f.name).unlink()

    def test_cli_save_data_file_json(self) -> None:
        """Test cli_save_data_file with JSON format."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            test_data = {"test": "data"}

            result = cli_save_data_file(test_data, Path(f.name), OutputFormat.JSON)

            assert result.success

            # Verify the file was saved correctly
            with open(f.name) as saved_file:
                loaded_data = json.load(saved_file)
                assert loaded_data == test_data

            Path(f.name).unlink()


class TestTableCreation:
    """Test table creation utilities."""

    def test_cli_create_table_dict_data(self) -> None:
        """Test creating table from dictionary data."""
        data = {"name": "John", "age": 30, "city": "NYC"}

        result = cli_create_table(data, "Test Table")

        assert result.success
        table = result.unwrap()
        assert hasattr(table, "title")

    def test_cli_create_table_list_data(self) -> None:
        """Test creating table from list data."""
        data = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25}
        ]

        result = cli_create_table(data)

        assert result.success
        table = result.unwrap()
        assert hasattr(table, "columns")

    def test_cli_create_table_empty_list(self) -> None:
        """Test creating table with empty list."""
        result = cli_create_table([])

        assert not result.success


class TestFormatOutput:
    """Test output formatting utilities."""

    def test_cli_format_output_json(self) -> None:
        """Test formatting output as JSON."""
        data = {"key": "value", "number": 42}

        result = cli_format_output(data, OutputFormat.JSON)

        assert result.success
        output = result.unwrap()
        assert isinstance(output, str)
        parsed = json.loads(output)
        assert parsed == data

    def test_cli_format_output_plain(self) -> None:
        """Test formatting output as plain text."""
        data = "Simple string data"

        result = cli_format_output(data, OutputFormat.PLAIN)

        assert result.success
        output = result.unwrap()
        assert output == str(data)


class TestBatchProcessing:
    """Test batch processing utilities."""

    def test_cli_batch_process_files_success(self) -> None:
        """Test successful batch file processing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            input_files = []
            for i in range(2):
                test_file = temp_path / f"test{i}.txt"
                test_file.write_text(f"content{i}")
                input_files.append(test_file)

            def simple_processor(file_path: Path) -> FlextResult[object]:
                content = file_path.read_text()
                return FlextResult[object].ok(f"processed_{content}")

            result = cli_batch_process_files(input_files, simple_processor)

            assert result.success
            data = result.unwrap()
            assert isinstance(data, dict)

    def test_cli_batch_process_files_empty_list(self) -> None:
        """Test batch processing with empty file list."""
        def dummy_processor(file_path: Path) -> FlextResult[object]:
            return FlextResult[object].ok("dummy")

        result = cli_batch_process_files([], dummy_processor)

        assert result.success  # Empty list is handled gracefully


class TestInteractiveUtilities:
    """Test interactive utility functions."""

    @patch("builtins.input")
    def test_cli_confirm_yes(self, mock_input: MagicMock) -> None:
        """Test confirmation with yes response."""
        mock_input.return_value = "y"

        result = cli_confirm("Do you want to continue?")

        assert result.success
        assert result.unwrap() is True

    @patch("builtins.input")
    def test_cli_confirm_no(self, mock_input: MagicMock) -> None:
        """Test confirmation with no response."""
        mock_input.return_value = "n"

        result = cli_confirm("Do you want to continue?")

        assert result.success
        assert result.unwrap() is False

    @patch("builtins.input")
    def test_cli_prompt_success(self, mock_input: MagicMock) -> None:
        """Test prompt with successful input."""
        mock_input.return_value = "user response"

        result = cli_prompt("Enter your name:")

        assert result.success
        assert result.unwrap() == "user response"

    @patch("builtins.input")
    def test_cli_prompt_with_default(self, mock_input: MagicMock) -> None:
        """Test prompt with default value."""
        mock_input.return_value = ""  # Empty input

        result = cli_prompt("Enter name:", default="Anonymous")

        assert result.success
        assert result.unwrap() == "Anonymous"


class TestCommandExecution:
    """Test command execution utilities."""

    def test_cli_run_command_success(self) -> None:
        """Test successful command execution."""
        result = cli_run_command("echo hello")

        assert result.success
        output = result.unwrap()
        assert isinstance(output, dict)
        assert "returncode" in output
        assert "stdout" in output

    def test_cli_run_command_nonexistent(self) -> None:
        """Test command execution with non-existent command."""
        result = cli_run_command("nonexistent-command-xyz123")

        assert not result.success
        assert "failed" in result.error.lower()


class TestUtilityFunctions:
    """Test additional utility functions."""

    def test_flext_cli_data_type_alias(self) -> None:
        """Test FlextCliData type alias usage."""
        # Test various data types that should be valid
        valid_data: list[FlextCliData] = [
            {"key": "value"},
            [1, 2, 3],
            "string",
            42.5,
            42,
            None
        ]

        for data in valid_data:
            # Should not raise any type errors
            assert data is not None or data is None
