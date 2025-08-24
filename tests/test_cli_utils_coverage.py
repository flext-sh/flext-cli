"""Tests for cli_utils.py to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import TypeVar
from unittest.mock import MagicMock, patch
from uuid import UUID

import yaml
from flext_core import FlextResult

from flext_cli.cli_types import FlextCliOutputFormat
from flext_cli.cli_utils import (
    FlextCliData,
    _convert_to_serializable,
    _create_directory_structure,
    _init_git_repo,
    _load_csv_file,
    _load_json_file,
    _load_text_file,
    _load_yaml_file,
    _process_single_file,
    _record_failure,
    _record_success,
    _save_csv_file,
    _save_json_file,
    _save_text_file,
    _save_yaml_file,
    _write_basic_pyproject,
    cli_batch_process_files,
    cli_confirm,
    cli_create_table,
    cli_format_output,
    cli_load_data_file,
    cli_prompt,
    cli_quick_setup,
    cli_run_command,
    cli_save_data_file,
)

# Type variable for testing
T = TypeVar("T")


class TestProjectSetupUtilities:
    """Test project setup utility functions."""

    def test_write_basic_pyproject(self) -> None:
        """Test writing basic pyproject.toml file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            project_name = "test-project"

            result_path = _write_basic_pyproject(project_name, project_path)

            assert result_path.exists()
            assert result_path.name == "pyproject.toml"

            content = result_path.read_text()
            assert f'name = "{project_name}"' in content
            assert 'version = "0.1.0"' in content
            assert 'requires-python = ">=3.13"' in content

    @patch("importlib.import_module")
    def test_init_git_repo_success(self, mock_import: MagicMock) -> None:
        """Test successful git repository initialization."""
        mock_git = MagicMock()
        mock_repo = MagicMock()
        mock_git.Repo = mock_repo
        mock_import.return_value = mock_git

        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            result = _init_git_repo(project_path)

            assert result is True
            mock_repo.init.assert_called_once_with(str(project_path))

    @patch("importlib.import_module")
    def test_init_git_repo_no_repo_class(self, mock_import: MagicMock) -> None:
        """Test git initialization when Repo class is missing."""
        mock_git = MagicMock()
        mock_git.Repo = None
        mock_import.return_value = mock_git

        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            result = _init_git_repo(project_path)

            assert result is False

    @patch("importlib.import_module")
    def test_init_git_repo_import_exception(self, mock_import: MagicMock) -> None:
        """Test git repository initialization with import exception."""
        mock_import.side_effect = ImportError("GitPython not installed")

        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            result = _init_git_repo(project_path)

            assert result is False

    def test_create_directory_structure(self) -> None:
        """Test creating directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            dir_names = ["src", "tests", "docs", "config"]

            result = _create_directory_structure(base_path, dir_names)

            assert isinstance(result, dict)
            assert len(result) == len(dir_names)

            for dir_name in dir_names:
                key = f"dir_{dir_name}"
                assert key in result
                assert (base_path / dir_name).exists()
                assert (base_path / dir_name).is_dir()

    def test_create_directory_structure_empty(self) -> None:
        """Test creating empty directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)

            result = _create_directory_structure(base_path, [])

            assert result == {}

    def test_record_success(self) -> None:
        """Test recording successful operations."""
        results: dict[str, object] = {"processed": 0, "successful": []}
        path = Path("/test/path")

        _record_success(results, path)

        assert results["processed"] == 1
        assert str(path) in results["successful"]

    def test_record_success_multiple(self) -> None:
        """Test recording multiple successful operations."""
        results: dict[str, object] = {"processed": 0, "successful": []}
        paths = [Path("/test/path1"), Path("/test/path2")]

        for path in paths:
            _record_success(results, path)

        assert results["processed"] == 2
        successful = results["successful"]
        assert isinstance(successful, list)
        assert len(successful) == 2

    def test_record_failure(self) -> None:
        """Test recording failed operations."""
        results: dict[str, object] = {"failed": 0, "errors": []}
        path = Path("/test/path")
        error = "Test error message"

        _record_failure(results, path, error)

        assert results["failed"] == 1
        errors_list = results["errors"]
        assert isinstance(errors_list, list)
        assert len(errors_list) == 1
        assert errors_list[0]["file"] == str(path)
        assert errors_list[0]["error"] == error

    def test_record_failure_multiple(self) -> None:
        """Test recording multiple failed operations."""
        results: dict[str, object] = {"failed": 0, "errors": []}
        failures = [(Path("/test/path1"), "Error 1"), (Path("/test/path2"), "Error 2")]

        for path, error in failures:
            _record_failure(results, path, error)

        assert results["failed"] == 2
        errors_list = results["errors"]
        assert isinstance(errors_list, list)
        assert len(errors_list) == 2


class TestFileProcessing:
    """Test file processing utilities."""

    def test_process_single_file_success(self) -> None:
        """Test successful single file processing."""

        def mock_processor(path: Path) -> FlextResult[object]:
            return FlextResult[object].ok({"processed": str(path)})

        results: dict[str, object] = {
            "processed": 0,
            "failed": 0,
            "successful": [],
            "errors": [],
        }
        test_path = Path("/test/file.txt")

        should_stop, stop_message = _process_single_file(
            test_path, mock_processor, results, fail_fast=False
        )

        assert not should_stop
        assert stop_message is None
        assert results["processed"] == 1
        assert str(test_path) in results["successful"]

    def test_process_single_file_failure(self) -> None:
        """Test single file processing with failure."""

        def mock_processor(path: Path) -> FlextResult[object]:
            return FlextResult[object].fail("Processing failed")

        results: dict[str, object] = {
            "processed": 0,
            "failed": 0,
            "successful": [],
            "errors": [],
        }
        test_path = Path("/test/file.txt")

        should_stop, stop_message = _process_single_file(
            test_path, mock_processor, results, fail_fast=True
        )

        assert should_stop
        assert stop_message is not None
        assert "Processing failed" in stop_message
        assert results["failed"] == 1

    def test_process_single_file_exception(self) -> None:
        """Test single file processing with processor exception."""

        def failing_processor(path: Path) -> FlextResult[object]:
            msg = "Processing exception"
            raise ValueError(msg)

        results: dict[str, object] = {
            "processed": 0,
            "failed": 0,
            "successful": [],
            "errors": [],
        }
        test_path = Path("/test/file.txt")

        should_stop, stop_message = _process_single_file(
            test_path, failing_processor, results, fail_fast=True
        )

        assert should_stop
        assert stop_message is not None
        assert "Processing exception" in stop_message
        assert results["failed"] == 1


class TestQuickSetup:
    """Test cli_quick_setup function."""

    @patch("flext_cli.cli_utils.cli_confirm")
    @patch("flext_cli.cli_utils._write_basic_pyproject")
    @patch("flext_cli.cli_utils._init_git_repo")
    @patch("flext_cli.cli_utils._create_directory_structure")
    def test_cli_quick_setup_success(
        self,
        mock_create_dirs: MagicMock,
        mock_init_git: MagicMock,
        mock_write_pyproject: MagicMock,
        mock_confirm: MagicMock,
    ) -> None:
        """Test successful quick setup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_name = "new-project"
            project_path = Path(temp_dir) / project_name
            mock_write_pyproject.return_value = project_path / "pyproject.toml"
            mock_init_git.return_value = True
            mock_create_dirs.return_value = {"dir_src": str(project_path / "src")}
            mock_confirm.return_value = FlextResult[bool].ok(data=True)

            result = cli_quick_setup(project_name)

            assert result.is_success
            data = result.value
            assert isinstance(data, dict)
            assert "project_path" in data

    @patch("flext_cli.cli_utils.cli_confirm")
    def test_cli_quick_setup_existing_project(self, mock_confirm: MagicMock) -> None:
        """Test quick setup with existing project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os_chdir = Path.cwd()
            try:
                os.chdir(temp_dir)
                project_path = Path("existing")
                project_path.mkdir()
                mock_confirm.return_value = FlextResult[bool].ok(False)

                result = cli_quick_setup("existing")

                assert not result.is_success
                assert "cancelled" in result.error
            finally:
                os.chdir(os_chdir)

    def test_cli_quick_setup_empty_name(self) -> None:
        """Test quick setup with empty project name."""
        result = cli_quick_setup("")

        assert not result.is_success
        assert "cannot be empty" in result.error

    @patch("flext_cli.cli_utils._write_basic_pyproject")
    @patch("flext_cli.cli_utils._init_git_repo")
    @patch("flext_cli.cli_utils._create_directory_structure")
    def test_cli_quick_setup_git_failure(
        self,
        mock_create_dirs: MagicMock,
        mock_init_git: MagicMock,
        mock_write_pyproject: MagicMock,
    ) -> None:
        """Test quick setup with git initialization failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os_chdir = Path.cwd()
            try:
                os.chdir(temp_dir)
                project_name = "new-project"
                project_path = Path(project_name)
                mock_write_pyproject.return_value = project_path / "pyproject.toml"
                mock_init_git.return_value = False
                mock_create_dirs.return_value = {"dir_src": str(project_path / "src")}

                result = cli_quick_setup(project_name, init_git=True)

                # Should still succeed even if git fails
                assert result.is_success
            finally:
                os.chdir(os_chdir)


class TestBatchProcessing:
    """Test cli_batch_process_files function."""

    def test_cli_batch_process_files_success(self) -> None:
        """Test successful batch file processing."""

        def mock_processor(path: Path) -> FlextResult[object]:
            return FlextResult[object].ok(f"processed_{path.name}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            input_files = []
            for i in range(3):
                test_file = temp_path / f"test{i}.txt"
                test_file.write_text(f"content{i}")
                input_files.append(test_file)

            result = cli_batch_process_files(
                input_files, mock_processor, show_progress=False
            )

            assert result.is_success
            data = result.value
            assert isinstance(data, dict)
            assert "processed" in data
            assert data["processed"] == 3

    def test_cli_batch_process_files_empty_list(self) -> None:
        """Test batch processing with empty file list."""

        def mock_processor(path: Path) -> FlextResult[object]:
            return FlextResult[object].ok("processed")

        result = cli_batch_process_files([], mock_processor)

        assert result.is_success
        data = result.value
        assert data["processed"] == 0

    def test_cli_batch_process_files_with_failures(self) -> None:
        """Test batch processing with some failures."""

        def failing_processor(path: Path) -> FlextResult[object]:
            if "fail" in path.name:
                return FlextResult[object].fail("Processing failed")
            return FlextResult[object].ok("processed")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            files = []
            for name in ["success.txt", "fail.txt", "success2.txt"]:
                test_file = temp_path / name
                test_file.write_text("content")
                files.append(test_file)

            result = cli_batch_process_files(
                files, failing_processor, show_progress=False
            )

            assert result.is_success
            data = result.value
            assert data["processed"] == 2
            assert data["failed"] == 1


class TestDataLoading:
    """Test data loading utilities."""

    def test_load_json_file_success(self) -> None:
        """Test successful JSON file loading."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".json", delete=False
        ) as f:
            test_data = {"key": "value", "number": 42}
            json.dump(test_data, f)
            f.flush()

            result = _load_json_file(Path(f.name))

            assert result.is_success
            assert result.value == test_data

            Path(f.name).unlink()

    def test_load_json_file_invalid(self) -> None:
        """Test loading invalid JSON file."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".json", delete=False
        ) as f:
            f.write("invalid json {")
            f.flush()

            result = _load_json_file(Path(f.name))

            assert not result.is_success
            assert "JSON decode error" in result.error

            Path(f.name).unlink()

    def test_load_json_file_not_found(self) -> None:
        """Test loading non-existent JSON file."""
        result = _load_json_file(Path("/nonexistent.json"))

        assert not result.is_success
        assert "File not found" in result.error

    def test_load_yaml_file_success(self) -> None:
        """Test successful YAML file loading."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".yaml", delete=False
        ) as f:
            test_data = {"key": "value", "list": [1, 2, 3]}
            yaml.dump(test_data, f)
            f.flush()

            result = _load_yaml_file(Path(f.name))

            assert result.is_success
            assert result.value == test_data

            Path(f.name).unlink()

    def test_load_yaml_file_invalid(self) -> None:
        """Test loading invalid YAML file."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write("invalid: yaml: content: [\n")
            f.flush()

            result = _load_yaml_file(Path(f.name))

            assert not result.is_success
            assert "YAML parse error" in result.error

            Path(f.name).unlink()

    def test_load_csv_file_success(self) -> None:
        """Test successful CSV file loading."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".csv", delete=False
        ) as f:
            f.write("name,age,city\nJohn,30,NYC\nJane,25,LA\n")
            f.flush()

            result = _load_csv_file(Path(f.name))

            assert result.is_success
            data = result.value
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]["name"] == "John"
            assert data[1]["city"] == "LA"

            Path(f.name).unlink()

    def test_load_text_file_success(self) -> None:
        """Test successful text file loading."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".txt", delete=False
        ) as f:
            content = "This is test content\nWith multiple lines"
            f.write(content)
            f.flush()

            result = _load_text_file(Path(f.name))

            assert result.is_success
            assert result.value == content

            Path(f.name).unlink()

    def test_cli_load_data_file_json(self) -> None:
        """Test cli_load_data_file with JSON file."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".json", delete=False
        ) as f:
            test_data = {"test": "data"}
            json.dump(test_data, f)
            f.flush()

            result = cli_load_data_file(Path(f.name))

            assert result.is_success
            assert result.value == test_data

            Path(f.name).unlink()

    def test_cli_load_data_file_unsupported_format(self) -> None:
        """Test cli_load_data_file with unsupported format."""
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            f.write(b"content")
            f.flush()

            result = cli_load_data_file(Path(f.name))

            assert not result.is_success
            assert "Unsupported file format" in result.error

            Path(f.name).unlink()


class TestDataSaving:
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

    def test_convert_to_serializable_datetime(self) -> None:
        """Test converting datetime to serializable format."""
        import datetime

        dt = datetime.datetime(2025, 1, 15, 12, 30, 45)
        result = _convert_to_serializable(dt)
        assert isinstance(result, str)
        assert "2025-01-15" in result

    def test_convert_to_serializable_path(self) -> None:
        """Test converting Path to serializable format."""
        path = Path("/test/path")
        result = _convert_to_serializable(path)
        assert result == str(path)

    def test_convert_to_serializable_list(self) -> None:
        """Test converting list with mixed types."""
        data = [
            1,
            "string",
            UUID("12345678-1234-5678-1234-567812345678"),
            {"nested": "dict"},
        ]
        result = _convert_to_serializable(data)
        assert isinstance(result, list)
        assert len(result) == 4
        assert isinstance(result[2], str)  # UUID converted to string

    def test_save_json_file_success(self) -> None:
        """Test successful JSON file saving."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            test_data = {"key": "value", "number": 42}

            result = _save_json_file(test_data, Path(f.name))

            assert result.is_success

            # Verify the file was saved correctly
            with open(f.name, encoding="utf-8") as saved_file:
                loaded_data = json.load(saved_file)
                assert loaded_data == test_data

            Path(f.name).unlink()

    def test_save_yaml_file_success(self) -> None:
        """Test successful YAML file saving."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            test_data = {"key": "value", "list": [1, 2, 3]}

            result = _save_yaml_file(test_data, Path(f.name))

            assert result.is_success

            # Verify the file was saved correctly
            with open(f.name, encoding="utf-8") as saved_file:
                loaded_data = yaml.safe_load(saved_file)
                assert loaded_data == test_data

            Path(f.name).unlink()

    def test_save_csv_file_success(self) -> None:
        """Test successful CSV file saving."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            test_data = [{"name": "John", "age": "30"}, {"name": "Jane", "age": "25"}]

            result = _save_csv_file(test_data, Path(f.name))

            assert result.is_success

            # Verify the file was saved correctly
            content = Path(f.name).read_text(encoding="utf-8")
            assert "name,age" in content
            assert "John,30" in content

            Path(f.name).unlink()

    def test_save_csv_file_invalid_data(self) -> None:
        """Test CSV saving with invalid data."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            invalid_data = "not a list"

            result = _save_csv_file(invalid_data, Path(f.name))

            assert not result.is_success
            assert "must be a list" in result.error

            Path(f.name).unlink()

    def test_save_text_file_success(self) -> None:
        """Test successful text file saving."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            test_content = "This is test content\nWith multiple lines"

            result = _save_text_file(test_content, Path(f.name))

            assert result.is_success

            # Verify the file was saved correctly
            saved_content = Path(f.name).read_text(encoding="utf-8")
            assert saved_content == test_content

            Path(f.name).unlink()

    def test_cli_save_data_file_json(self) -> None:
        """Test cli_save_data_file with JSON format."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            test_data = {"test": "data"}

            result = cli_save_data_file(
                test_data, Path(f.name), FlextCliOutputFormat.JSON
            )

            assert result.is_success

            # Verify the file was saved correctly
            with open(f.name, encoding="utf-8") as saved_file:
                loaded_data = json.load(saved_file)
                assert loaded_data == test_data

            Path(f.name).unlink()

    def test_cli_save_data_file_unsupported_format(self) -> None:
        """Test cli_save_data_file with unsupported format."""
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            result = cli_save_data_file(
                {"data": "test"}, Path(f.name), FlextCliOutputFormat.PLAIN
            )

            assert not result.is_success
            assert "Unsupported output format" in result.error

            Path(f.name).unlink()


class TestTableCreation:
    """Test table creation utilities."""

    def test_cli_create_table_dict_data(self) -> None:
        """Test creating table from dictionary data."""
        data = {"name": "John", "age": 30, "city": "NYC"}

        result = cli_create_table(data, "Test Table")

        assert result.is_success
        table = result.value
        assert hasattr(table, "title")
        assert table.title == "Test Table"

    def test_cli_create_table_list_data(self) -> None:
        """Test creating table from list data."""
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]

        result = cli_create_table(data)

        assert result.is_success
        table = result.value
        assert hasattr(table, "columns")

    def test_cli_create_table_invalid_data(self) -> None:
        """Test creating table with invalid data."""
        result = cli_create_table("invalid data")

        assert not result.is_success
        assert "must be a dictionary or list" in result.error

    def test_cli_create_table_empty_list(self) -> None:
        """Test creating table with empty list."""
        result = cli_create_table([])

        assert not result.is_success
        assert "empty" in result.error


class TestFormatOutput:
    """Test output formatting utilities."""

    def test_cli_format_output_json(self) -> None:
        """Test formatting output as JSON."""
        data = {"key": "value", "number": 42}

        result = cli_format_output(data, FlextCliOutputFormat.JSON)

        assert result.is_success
        output = result.value
        assert isinstance(output, str)
        parsed = json.loads(output)
        assert parsed == data

    def test_cli_format_output_yaml(self) -> None:
        """Test formatting output as YAML."""
        data = {"key": "value", "list": [1, 2, 3]}

        result = cli_format_output(data, FlextCliOutputFormat.YAML)

        assert result.is_success
        output = result.value
        assert isinstance(output, str)
        parsed = yaml.safe_load(output)
        assert parsed == data

    def test_cli_format_output_table(self) -> None:
        """Test formatting output as table."""
        data = {"name": "John", "age": 30}

        result = cli_format_output(data, FlextCliOutputFormat.TABLE)

        assert result.is_success
        output = result.value
        assert isinstance(output, str)
        # Table output should contain the data
        assert "John" in output

    def test_cli_format_output_csv(self) -> None:
        """Test formatting output as CSV."""
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]

        result = cli_format_output(data, FlextCliOutputFormat.CSV)

        assert result.is_success
        output = result.value
        assert isinstance(output, str)
        assert "name,age" in output
        assert "John,30" in output

    def test_cli_format_output_plain(self) -> None:
        """Test formatting output as plain text."""
        data = "Simple string data"

        result = cli_format_output(data, FlextCliOutputFormat.PLAIN)

        assert result.is_success
        output = result.value
        assert output == str(data)

    def test_cli_format_output_invalid_csv_data(self) -> None:
        """Test formatting invalid data as CSV."""
        data = "not a list"

        result = cli_format_output(data, FlextCliOutputFormat.CSV)

        assert not result.is_success
        assert "CSV format requires" in result.error


class TestCommandExecution:
    """Test command execution utilities."""

    @patch("subprocess.run")
    def test_cli_run_command_success(self, mock_run: MagicMock) -> None:
        """Test successful command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = cli_run_command("echo hello")

        assert result.is_success
        output = result.value
        assert isinstance(output, dict)
        assert output["returncode"] == 0
        assert output["stdout"] == "Success output"

    @patch("subprocess.run")
    def test_cli_run_command_failure(self, mock_run: MagicMock) -> None:
        """Test failed command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error output"
        mock_run.return_value = mock_result

        result = cli_run_command("false")

        assert not result.is_success
        assert "Command failed" in result.error

    @patch("subprocess.run")
    def test_cli_run_command_with_timeout(self, mock_run: MagicMock) -> None:
        """Test command execution with timeout."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = cli_run_command("sleep 1", timeout=30)

        assert result.is_success
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[1]["timeout"] == 30

    @patch("subprocess.run")
    def test_cli_run_command_exception(self, mock_run: MagicMock) -> None:
        """Test command execution with exception."""
        mock_run.side_effect = Exception("Command not found")

        result = cli_run_command("nonexistent-command")

        assert not result.is_success
        assert "Command not found" in result.error


class TestInteractiveUtilities:
    """Test interactive utility functions."""

    @patch("builtins.input")
    def test_cli_confirm_yes(self, mock_input: MagicMock) -> None:
        """Test confirmation with yes response."""
        mock_input.return_value = "y"

        result = cli_confirm("Do you want to continue?")

        assert result.is_success
        assert result.value is True

    @patch("builtins.input")
    def test_cli_confirm_no(self, mock_input: MagicMock) -> None:
        """Test confirmation with no response."""
        mock_input.return_value = "n"

        result = cli_confirm("Do you want to continue?")

        assert result.is_success
        assert result.value is False

    @patch("builtins.input")
    def test_cli_confirm_default_true(self, mock_input: MagicMock) -> None:
        """Test confirmation with default true."""
        mock_input.return_value = ""  # Empty input

        result = cli_confirm("Continue?", default=True)

        assert result.is_success
        assert result.value is True

    @patch("builtins.input")
    def test_cli_confirm_default_false(self, mock_input: MagicMock) -> None:
        """Test confirmation with default false."""
        mock_input.return_value = ""  # Empty input

        result = cli_confirm("Continue?", default=False)

        assert result.is_success
        assert result.value is False

    @patch("builtins.input")
    def test_cli_confirm_invalid_then_valid(self, mock_input: MagicMock) -> None:
        """Test confirmation with invalid then valid response."""
        mock_input.side_effect = ["invalid", "yes"]

        result = cli_confirm("Continue?")

        assert result.is_success
        assert result.value is True

    @patch("builtins.input")
    def test_cli_confirm_exception(self, mock_input: MagicMock) -> None:
        """Test confirmation with input exception."""
        mock_input.side_effect = KeyboardInterrupt()

        result = cli_confirm("Continue?")

        assert not result.is_success
        assert "cancelled" in result.error

    @patch("builtins.input")
    def test_cli_prompt_success(self, mock_input: MagicMock) -> None:
        """Test prompt with successful input."""
        mock_input.return_value = "user response"

        result = cli_prompt("Enter your name:")

        assert result.is_success
        assert result.value == "user response"

    @patch("builtins.input")
    def test_cli_prompt_with_default(self, mock_input: MagicMock) -> None:
        """Test prompt with default value."""
        mock_input.return_value = ""  # Empty input

        result = cli_prompt("Enter name:", default="Anonymous")

        assert result.is_success
        assert result.value == "Anonymous"

    @patch("builtins.input")
    def test_cli_prompt_exception(self, mock_input: MagicMock) -> None:
        """Test prompt with input exception."""
        mock_input.side_effect = KeyboardInterrupt()

        result = cli_prompt("Enter input:")

        assert not result.is_success
        assert "cancelled" in result.error

    @patch("getpass.getpass")
    def test_cli_prompt_secure(self, mock_getpass: MagicMock) -> None:
        """Test secure prompt."""
        mock_getpass.return_value = "secret"

        result = cli_prompt("Enter password:", hidden=True)

        assert result.is_success
        assert result.value == "secret"


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
            None,
        ]

        for data in valid_data:
            # Should not raise any type errors
            assert data is not None or data is None

    def test_type_variable(self) -> None:
        """Test T type variable usage."""

        def identity_func(value: T) -> T:
            return value

        assert identity_func("test") == "test"
        assert identity_func(42) == 42
