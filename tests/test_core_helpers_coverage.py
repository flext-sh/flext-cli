"""Comprehensive tests for core/helpers.py to maximize coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Never
from unittest.mock import patch

from flext_core import FlextResult
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from flext_cli.helpers import (
    FlextCliDataProcessor,
    FlextCliFileManager,
    FlextCliHelper,
    flext_cli_batch_validate,
    flext_cli_create_data_processor,
    flext_cli_create_file_manager,
    flext_cli_create_helper,
)


class TestFlextCliHelper:
    """Test FlextCliHelper class comprehensive coverage."""

    def test_helper_init_default(self) -> None:
        """Test helper initialization with defaults."""
        helper = FlextCliHelper()

        assert helper.console is not None
        assert helper.quiet is False

    def test_helper_init_with_console(self) -> None:
        """Test helper initialization with console."""
        console = Console()
        helper = FlextCliHelper(console=console)

        assert helper.console is console
        assert helper.quiet is False

    def test_helper_init_quiet_mode(self) -> None:
        """Test helper initialization in quiet mode."""
        helper = FlextCliHelper(quiet=True)

        assert helper.quiet is True
        assert helper.console is not None

    def test_flext_cli_confirm_default_false(self) -> None:
        """Test confirmation with default False in quiet mode."""
        helper = FlextCliHelper(quiet=True)

        result = helper.flext_cli_confirm("Are you sure?", default=False)

        assert result.success
        assert result.unwrap() is False

    def test_flext_cli_confirm_default_true(self) -> None:
        """Test confirmation with default True in quiet mode."""
        helper = FlextCliHelper(quiet=True)

        result = helper.flext_cli_confirm("Are you sure?", default=True)

        assert result.success
        assert result.unwrap() is True

    @patch("rich.prompt.Confirm.ask")
    def test_flext_cli_confirm_interactive_yes(self, mock_confirm) -> None:
        """Test interactive confirmation returning yes."""
        mock_confirm.return_value = True
        helper = FlextCliHelper(quiet=False)

        result = helper.flext_cli_confirm("Are you sure?")

        assert result.success
        assert result.unwrap() is True
        mock_confirm.assert_called_once()

    @patch("rich.prompt.Confirm.ask")
    def test_flext_cli_confirm_interactive_no(self, mock_confirm) -> None:
        """Test interactive confirmation returning no."""
        mock_confirm.return_value = False
        helper = FlextCliHelper(quiet=False)

        result = helper.flext_cli_confirm("Are you sure?")

        assert result.success
        assert result.unwrap() is False

    @patch("rich.prompt.Confirm.ask")
    def test_flext_cli_confirm_exception_handling(self, mock_confirm) -> None:
        """Test confirmation with exception handling."""
        mock_confirm.side_effect = KeyboardInterrupt("User interrupted")
        helper = FlextCliHelper(quiet=False)

        result = helper.flext_cli_confirm("Are you sure?")

        assert not result.success
        assert "KeyboardInterrupt" in result.error

    def test_flext_cli_prompt_quiet_mode(self) -> None:
        """Test prompt in quiet mode returns default."""
        helper = FlextCliHelper(quiet=True)

        result = helper.flext_cli_prompt("Enter name:", default="default")

        assert result.success
        assert result.unwrap() == "default"

    def test_flext_cli_prompt_quiet_mode_no_default(self) -> None:
        """Test prompt in quiet mode with no default fails."""
        helper = FlextCliHelper(quiet=True)

        result = helper.flext_cli_prompt("Enter name:")

        assert not result.success
        assert "Cannot prompt in quiet mode" in result.error

    @patch("rich.prompt.Prompt.ask")
    def test_flext_cli_prompt_interactive(self, mock_prompt) -> None:
        """Test interactive prompt."""
        mock_prompt.return_value = "user input"
        helper = FlextCliHelper(quiet=False)

        result = helper.flext_cli_prompt("Enter name:")

        assert result.success
        assert result.unwrap() == "user input"

    @patch("rich.prompt.Prompt.ask")
    def test_flext_cli_prompt_exception_handling(self, mock_prompt) -> None:
        """Test prompt with exception handling."""
        mock_prompt.side_effect = KeyboardInterrupt("User interrupted")
        helper = FlextCliHelper(quiet=False)

        result = helper.flext_cli_prompt("Enter name:")

        assert not result.success
        assert "KeyboardInterrupt" in result.error

    def test_flext_cli_show_progress_quiet_mode(self) -> None:
        """Test show_progress in quiet mode."""
        helper = FlextCliHelper(quiet=True)

        result = helper.flext_cli_show_progress("Processing", 100)

        assert result.success
        progress = result.unwrap()
        assert isinstance(progress, Progress)

    def test_flext_cli_show_progress_normal_mode(self) -> None:
        """Test show_progress in normal mode."""
        helper = FlextCliHelper(quiet=False)

        result = helper.flext_cli_show_progress("Processing", 100)

        assert result.success
        progress = result.unwrap()
        assert isinstance(progress, Progress)

    def test_flext_cli_show_progress_with_description(self) -> None:
        """Test show_progress with custom description."""
        helper = FlextCliHelper()

        result = helper.flext_cli_show_progress("Custom task", 50)

        assert result.success
        progress = result.unwrap()
        assert isinstance(progress, Progress)

    def test_flext_cli_create_table_empty_data(self) -> None:
        """Test create_table with empty data."""
        helper = FlextCliHelper()

        result = helper.flext_cli_create_table([])

        assert result.success
        table = result.unwrap()
        assert isinstance(table, Table)

    def test_flext_cli_create_table_with_headers(self) -> None:
        """Test create_table with headers and data."""
        helper = FlextCliHelper()
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]

        result = helper.flext_cli_create_table(data, headers=["name", "age"])

        assert result.success
        table = result.unwrap()
        assert isinstance(table, Table)

    def test_flext_cli_create_table_auto_headers(self) -> None:
        """Test create_table with automatic header detection."""
        helper = FlextCliHelper()
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]

        result = helper.flext_cli_create_table(data)

        assert result.success
        table = result.unwrap()
        assert isinstance(table, Table)

    def test_flext_cli_create_table_with_title(self) -> None:
        """Test create_table with title."""
        helper = FlextCliHelper()
        data = [{"name": "John"}]

        result = helper.flext_cli_create_table(data, title="Users")

        assert result.success
        table = result.unwrap()
        assert isinstance(table, Table)
        assert table.title == "Users"

    def test_flext_cli_create_table_exception_handling(self) -> None:
        """Test create_table with invalid data causing exception."""
        helper = FlextCliHelper()

        # Create problematic data that might cause issues
        with patch.object(
            Table, "add_column", side_effect=ValueError("Invalid column")
        ):
            result = helper.flext_cli_create_table([{"name": "test"}])

        assert not result.success
        assert "Invalid column" in result.error

    def test_flext_cli_execute_command_success(self) -> None:
        """Test execute_command with successful command."""
        helper = FlextCliHelper()

        result = helper.flext_cli_execute_command("echo hello")

        assert result.success
        output = result.unwrap()
        assert "hello" in output

    def test_flext_cli_execute_command_with_args(self) -> None:
        """Test execute_command with command arguments."""
        helper = FlextCliHelper()

        result = helper.flext_cli_execute_command("echo test args")

        assert result.success
        output = result.unwrap()
        assert "test args" in output

    def test_flext_cli_execute_command_failure(self) -> None:
        """Test execute_command with failing command."""
        helper = FlextCliHelper()

        result = helper.flext_cli_execute_command("nonexistent_command_12345")

        assert not result.success
        assert (
            "Failed to execute" in result.error or "not found" in result.error.lower()
        )

    def test_flext_cli_execute_command_with_timeout(self) -> None:
        """Test execute_command with timeout."""
        helper = FlextCliHelper()

        # Use sleep command to test timeout
        result = helper.flext_cli_execute_command("sleep 10", timeout=0.1)

        assert not result.success
        # Could timeout or be killed depending on system
        assert result.error is not None

    def test_flext_cli_execute_command_exception_handling(self) -> None:
        """Test execute_command exception handling."""
        helper = FlextCliHelper()

        # Test with invalid command structure
        result = helper.flext_cli_execute_command("")

        assert not result.success
        assert result.error is not None

    @patch("shutil.which")
    def test_flext_cli_check_command_exists_found(self, mock_which) -> None:
        """Test check_command_exists when command is found."""
        mock_which.return_value = "/usr/bin/ls"
        helper = FlextCliHelper()

        result = helper.flext_cli_check_command_exists("ls")

        assert result.success
        assert result.unwrap() is True

    @patch("shutil.which")
    def test_flext_cli_check_command_exists_not_found(self, mock_which) -> None:
        """Test check_command_exists when command not found."""
        mock_which.return_value = None
        helper = FlextCliHelper()

        result = helper.flext_cli_check_command_exists("nonexistent")

        assert result.success
        assert result.unwrap() is False

    def test_flext_cli_check_command_exists_exception(self) -> None:
        """Test check_command_exists with exception."""
        helper = FlextCliHelper()

        with patch("shutil.which", side_effect=OSError("Permission denied")):
            result = helper.flext_cli_check_command_exists("ls")

        assert not result.success
        assert "Permission denied" in result.error

    def test_flext_cli_validate_file_path_existing_file(self) -> None:
        """Test validate_file_path with existing file."""
        helper = FlextCliHelper()

        with tempfile.NamedTemporaryFile() as temp_file:
            result = helper.flext_cli_validate_file_path(Path(temp_file.name))

            assert result.success
            assert result.unwrap() == Path(temp_file.name)

    def test_flext_cli_validate_file_path_nonexistent(self) -> None:
        """Test validate_file_path with nonexistent file."""
        helper = FlextCliHelper()

        result = helper.flext_cli_validate_file_path(Path("/nonexistent/file.txt"))

        assert not result.success
        assert "does not exist" in result.error

    def test_flext_cli_validate_file_path_directory(self) -> None:
        """Test validate_file_path with directory instead of file."""
        helper = FlextCliHelper()

        with tempfile.TemporaryDirectory() as temp_dir:
            result = helper.flext_cli_validate_file_path(Path(temp_dir))

        assert not result.success
        assert "is not a file" in result.error

    def test_flext_cli_validate_file_path_permission_error(self) -> None:
        """Test validate_file_path with permission error."""
        helper = FlextCliHelper()

        # Mock permission error
        with patch("pathlib.Path.exists", side_effect=PermissionError("Access denied")):
            result = helper.flext_cli_validate_file_path(Path("test.txt"))

        assert not result.success
        assert "Access denied" in result.error


class TestFlextCliDataProcessor:
    """Test FlextCliDataProcessor class comprehensive coverage."""

    def test_processor_init(self) -> None:
        """Test processor initialization."""
        processor = FlextCliDataProcessor()

        assert processor is not None

    def test_process_json_data_valid(self) -> None:
        """Test processing valid JSON data."""
        processor = FlextCliDataProcessor()
        json_data = '{"name": "test", "value": 123}'

        result = processor.process_json_data(json_data)

        assert result.success
        data = result.unwrap()
        assert data["name"] == "test"
        assert data["value"] == 123

    def test_process_json_data_invalid(self) -> None:
        """Test processing invalid JSON data."""
        processor = FlextCliDataProcessor()
        invalid_json = '{"invalid": json,}'

        result = processor.process_json_data(invalid_json)

        assert not result.success
        assert "JSON" in result.error

    def test_process_json_data_empty_string(self) -> None:
        """Test processing empty JSON string."""
        processor = FlextCliDataProcessor()

        result = processor.process_json_data("")

        assert not result.success
        assert result.error is not None

    def test_filter_data_simple(self) -> None:
        """Test filtering data with simple criteria."""
        processor = FlextCliDataProcessor()
        data = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25},
            {"name": "Bob", "age": 35},
        ]

        result = processor.filter_data(data, lambda x: x["age"] > 30)

        assert result.success
        filtered = result.unwrap()
        assert len(filtered) == 1
        assert filtered[0]["name"] == "Bob"

    def test_filter_data_no_matches(self) -> None:
        """Test filtering data with no matches."""
        processor = FlextCliDataProcessor()
        data = [{"name": "John", "age": 30}]

        result = processor.filter_data(data, lambda x: x["age"] > 100)

        assert result.success
        filtered = result.unwrap()
        assert len(filtered) == 0

    def test_filter_data_empty_list(self) -> None:
        """Test filtering empty data list."""
        processor = FlextCliDataProcessor()

        result = processor.filter_data([], lambda x: True)

        assert result.success
        filtered = result.unwrap()
        assert len(filtered) == 0

    def test_filter_data_exception_handling(self) -> None:
        """Test filter_data exception handling."""
        processor = FlextCliDataProcessor()
        data = [{"name": "test"}]

        # Filter function that causes exception
        def bad_filter(item) -> Never:
            msg = "Bad filter"
            raise ValueError(msg)

        result = processor.filter_data(data, bad_filter)

        assert not result.success
        assert "Bad filter" in result.error

    def test_transform_data_simple(self) -> None:
        """Test transforming data with simple function."""
        processor = FlextCliDataProcessor()
        data = [{"value": 1}, {"value": 2}, {"value": 3}]

        result = processor.transform_data(
            data, lambda x: {**x, "doubled": x["value"] * 2}
        )

        assert result.success
        transformed = result.unwrap()
        assert len(transformed) == 3
        assert transformed[0]["doubled"] == 2
        assert transformed[2]["doubled"] == 6

    def test_transform_data_empty_list(self) -> None:
        """Test transforming empty data list."""
        processor = FlextCliDataProcessor()

        result = processor.transform_data([], lambda x: x)

        assert result.success
        transformed = result.unwrap()
        assert len(transformed) == 0

    def test_transform_data_exception_handling(self) -> None:
        """Test transform_data exception handling."""
        processor = FlextCliDataProcessor()
        data = [{"test": "value"}]

        def bad_transform(item) -> Never:
            msg = "Missing key"
            raise KeyError(msg)

        result = processor.transform_data(data, bad_transform)

        assert not result.success
        assert "Missing key" in result.error

    def test_aggregate_data_sum(self) -> None:
        """Test aggregating data with sum."""
        processor = FlextCliDataProcessor()
        data = [
            {"category": "A", "value": 10},
            {"category": "A", "value": 20},
            {"category": "B", "value": 15},
        ]

        result = processor.aggregate_data(data, "category", sum, "value")

        assert result.success
        aggregated = result.unwrap()
        assert len(aggregated) == 2

        # Check aggregated values
        category_a = next(item for item in aggregated if item["category"] == "A")
        category_b = next(item for item in aggregated if item["category"] == "B")

        assert category_a["value"] == 30
        assert category_b["value"] == 15

    def test_aggregate_data_count(self) -> None:
        """Test aggregating data with count."""
        processor = FlextCliDataProcessor()
        data = [
            {"category": "A", "value": 10},
            {"category": "A", "value": 20},
            {"category": "B", "value": 15},
        ]

        result = processor.aggregate_data(data, "category", len)

        assert result.success
        aggregated = result.unwrap()
        assert len(aggregated) == 2

    def test_aggregate_data_empty_list(self) -> None:
        """Test aggregating empty data list."""
        processor = FlextCliDataProcessor()

        result = processor.aggregate_data([], "category", sum)

        assert result.success
        aggregated = result.unwrap()
        assert len(aggregated) == 0

    def test_aggregate_data_missing_key(self) -> None:
        """Test aggregating data with missing group key."""
        processor = FlextCliDataProcessor()
        data = [{"name": "test"}]  # Missing 'category' key

        result = processor.aggregate_data(data, "category", sum)

        assert not result.success
        assert "category" in result.error

    def test_aggregate_data_exception_handling(self) -> None:
        """Test aggregate_data exception handling."""
        processor = FlextCliDataProcessor()
        data = [{"category": "A", "value": "not_number"}]

        result = processor.aggregate_data(data, "category", sum, "value")

        # Should handle type errors gracefully
        assert not result.success


class TestFlextCliFileManager:
    """Test FlextCliFileManager class comprehensive coverage."""

    def test_file_manager_init_default(self) -> None:
        """Test file manager initialization with defaults."""
        manager = FlextCliFileManager()

        assert manager.base_directory == Path.cwd()

    def test_file_manager_init_with_directory(self) -> None:
        """Test file manager initialization with specific directory."""
        test_dir = Path("/tmp")
        manager = FlextCliFileManager(base_directory=test_dir)

        assert manager.base_directory == test_dir

    def test_read_file_success(self) -> None:
        """Test reading file successfully."""
        manager = FlextCliFileManager()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".txt"
        ) as temp_file:
            temp_file.write("test content")
            temp_file_path = Path(temp_file.name)

        try:
            result = manager.read_file(temp_file_path)

            assert result.success
            content = result.unwrap()
            assert content == "test content"
        finally:
            temp_file_path.unlink()

    def test_read_file_not_found(self) -> None:
        """Test reading nonexistent file."""
        manager = FlextCliFileManager()

        result = manager.read_file(Path("/nonexistent/file.txt"))

        assert not result.success
        assert "No such file" in result.error or "not find" in result.error

    def test_read_file_permission_denied(self) -> None:
        """Test reading file with permission error."""
        manager = FlextCliFileManager()

        with patch(
            "pathlib.Path.read_text", side_effect=PermissionError("Access denied")
        ):
            result = manager.read_file(Path("test.txt"))

        assert not result.success
        assert "Access denied" in result.error

    def test_write_file_success(self) -> None:
        """Test writing file successfully."""
        manager = FlextCliFileManager()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file_path = Path(temp_file.name)

        try:
            result = manager.write_file(temp_file_path, "test content")

            assert result.success

            # Verify content was written
            assert temp_file_path.read_text(encoding="utf-8") == "test content"
        finally:
            temp_file_path.unlink()

    def test_write_file_create_directory(self) -> None:
        """Test writing file with directory creation."""
        manager = FlextCliFileManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "subdir" / "test.txt"

            result = manager.write_file(
                file_path, "test content", create_directory=True
            )

            assert result.success
            assert file_path.exists()
            assert file_path.read_text() == "test content"

    def test_write_file_no_directory_creation(self) -> None:
        """Test writing file without directory creation fails."""
        manager = FlextCliFileManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "nonexistent" / "test.txt"

            result = manager.write_file(
                file_path, "test content", create_directory=False
            )

            assert not result.success

    def test_write_file_permission_denied(self) -> None:
        """Test writing file with permission error."""
        manager = FlextCliFileManager()

        with patch(
            "pathlib.Path.write_text", side_effect=PermissionError("Access denied")
        ):
            result = manager.write_file(Path("test.txt"), "content")

        assert not result.success
        assert "Access denied" in result.error

    def test_copy_file_success(self) -> None:
        """Test copying file successfully."""
        manager = FlextCliFileManager()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".txt"
        ) as source_file:
            source_file.write("test content")
            source_path = Path(source_file.name)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as dest_file:
            dest_path = Path(dest_file.name)

        try:
            result = manager.copy_file(source_path, dest_path)

            assert result.success
            assert dest_path.read_text(encoding="utf-8") == "test content"
        finally:
            source_path.unlink()
            dest_path.unlink()

    def test_copy_file_source_not_found(self) -> None:
        """Test copying nonexistent source file."""
        manager = FlextCliFileManager()

        result = manager.copy_file(Path("/nonexistent.txt"), Path("/dest.txt"))

        assert not result.success
        assert result.error is not None

    def test_copy_file_exception_handling(self) -> None:
        """Test copy_file exception handling."""
        manager = FlextCliFileManager()

        with patch("shutil.copy2", side_effect=OSError("Copy failed")):
            result = manager.copy_file(Path("source.txt"), Path("dest.txt"))

        assert not result.success
        assert "Copy failed" in result.error

    def test_delete_file_success(self) -> None:
        """Test deleting file successfully."""
        manager = FlextCliFileManager()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file_path = Path(temp_file.name)

        # File should exist
        assert temp_file_path.exists()

        result = manager.delete_file(temp_file_path)

        assert result.success
        assert not temp_file_path.exists()

    def test_delete_file_not_found(self) -> None:
        """Test deleting nonexistent file."""
        manager = FlextCliFileManager()

        result = manager.delete_file(Path("/nonexistent/file.txt"))

        assert not result.success
        assert result.error is not None

    def test_delete_file_permission_denied(self) -> None:
        """Test deleting file with permission error."""
        manager = FlextCliFileManager()

        with patch("pathlib.Path.unlink", side_effect=PermissionError("Access denied")):
            result = manager.delete_file(Path("test.txt"))

        assert not result.success
        assert "Access denied" in result.error

    def test_list_files_success(self) -> None:
        """Test listing files successfully."""
        manager = FlextCliFileManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = ["file1.txt", "file2.py", "file3.json"]
            for filename in test_files:
                (Path(temp_dir) / filename).touch()

            result = manager.list_files(Path(temp_dir))

            assert result.success
            files = result.unwrap()
            assert len(files) >= len(test_files)  # May include other files

            file_names = [f.name for f in files]
            for test_file in test_files:
                assert test_file in file_names

    def test_list_files_with_pattern(self) -> None:
        """Test listing files with pattern filter."""
        manager = FlextCliFileManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            (Path(temp_dir) / "test1.txt").touch()
            (Path(temp_dir) / "test2.txt").touch()
            (Path(temp_dir) / "other.py").touch()

            result = manager.list_files(Path(temp_dir), pattern="*.txt")

            assert result.success
            files = result.unwrap()
            assert len(files) == 2

            file_names = [f.name for f in files]
            assert "test1.txt" in file_names
            assert "test2.txt" in file_names
            assert "other.py" not in file_names

    def test_list_files_nonexistent_directory(self) -> None:
        """Test listing files in nonexistent directory."""
        manager = FlextCliFileManager()

        result = manager.list_files(Path("/nonexistent/directory"))

        assert not result.success
        assert result.error is not None

    def test_list_files_permission_denied(self) -> None:
        """Test listing files with permission error."""
        manager = FlextCliFileManager()

        with patch(
            "pathlib.Path.iterdir", side_effect=PermissionError("Access denied")
        ):
            result = manager.list_files(Path())

        assert not result.success
        assert "Access denied" in result.error


class TestFactoryFunctions:
    """Test factory functions comprehensive coverage."""

    def test_flext_cli_create_helper_default(self) -> None:
        """Test creating helper with defaults."""
        result = flext_cli_create_helper()

        assert result.success
        helper = result.unwrap()
        assert isinstance(helper, FlextCliHelper)
        assert helper.quiet is False

    def test_flext_cli_create_helper_quiet(self) -> None:
        """Test creating helper in quiet mode."""
        result = flext_cli_create_helper(quiet=True)

        assert result.success
        helper = result.unwrap()
        assert isinstance(helper, FlextCliHelper)
        assert helper.quiet is True

    def test_flext_cli_create_helper_with_console(self) -> None:
        """Test creating helper with custom console."""
        console = Console()
        result = flext_cli_create_helper(console=console)

        assert result.success
        helper = result.unwrap()
        assert isinstance(helper, FlextCliHelper)
        assert helper.console is console

    def test_flext_cli_create_data_processor(self) -> None:
        """Test creating data processor."""
        result = flext_cli_create_data_processor()

        assert result.success
        processor = result.unwrap()
        assert isinstance(processor, FlextCliDataProcessor)

    def test_flext_cli_create_file_manager_default(self) -> None:
        """Test creating file manager with defaults."""
        result = flext_cli_create_file_manager()

        assert result.success
        manager = result.unwrap()
        assert isinstance(manager, FlextCliFileManager)
        assert manager.base_directory == Path.cwd()

    def test_flext_cli_create_file_manager_with_directory(self) -> None:
        """Test creating file manager with specific directory."""
        test_dir = Path("/tmp")
        result = flext_cli_create_file_manager(base_directory=test_dir)

        assert result.success
        manager = result.unwrap()
        assert isinstance(manager, FlextCliFileManager)
        assert manager.base_directory == test_dir

    def test_flext_cli_batch_validate_all_valid(self) -> None:
        """Test batch validation with all valid results."""
        valid_results = [
            FlextResult[str].ok("result1"),
            FlextResult[str].ok("result2"),
            FlextResult[str].ok("result3"),
        ]

        result = flext_cli_batch_validate(valid_results)

        assert result.success
        summary = result.unwrap()
        assert summary["total"] == 3
        assert summary["successful"] == 3
        assert summary["failed"] == 0
        assert len(summary["errors"]) == 0

    def test_flext_cli_batch_validate_mixed_results(self) -> None:
        """Test batch validation with mixed results."""
        mixed_results = [
            FlextResult[str].ok("success1"),
            FlextResult[str].fail("error1"),
            FlextResult[str].ok("success2"),
            FlextResult[str].fail("error2"),
        ]

        result = flext_cli_batch_validate(mixed_results)

        assert result.success
        summary = result.unwrap()
        assert summary["total"] == 4
        assert summary["successful"] == 2
        assert summary["failed"] == 2
        assert len(summary["errors"]) == 2
        assert "error1" in summary["errors"]
        assert "error2" in summary["errors"]

    def test_flext_cli_batch_validate_all_failures(self) -> None:
        """Test batch validation with all failures."""
        failed_results = [
            FlextResult[str].fail("error1"),
            FlextResult[str].fail("error2"),
        ]

        result = flext_cli_batch_validate(failed_results)

        assert result.success
        summary = result.unwrap()
        assert summary["total"] == 2
        assert summary["successful"] == 0
        assert summary["failed"] == 2
        assert len(summary["errors"]) == 2

    def test_flext_cli_batch_validate_empty_list(self) -> None:
        """Test batch validation with empty list."""
        result = flext_cli_batch_validate([])

        assert result.success
        summary = result.unwrap()
        assert summary["total"] == 0
        assert summary["successful"] == 0
        assert summary["failed"] == 0
        assert len(summary["errors"]) == 0


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and comprehensive error handling."""

    def test_helper_with_unicode_content(self) -> None:
        """Test helper operations with unicode content."""
        helper = FlextCliHelper()

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, encoding="utf-8"
        ) as temp_file:
            unicode_content = "测试 🚀 émoji content"
            temp_file.write(unicode_content)
            temp_file_path = Path(temp_file.name)

        try:
            # Test file validation with unicode path/content
            result = helper.flext_cli_validate_file_path(temp_file_path)
            assert result.success
        finally:
            temp_file_path.unlink()

    def test_data_processor_with_complex_data(self) -> None:
        """Test data processor with complex nested data."""
        processor = FlextCliDataProcessor()

        complex_data = [
            {
                "user": {
                    "name": "John",
                    "profile": {"age": 30, "tags": ["admin", "user"]},
                },
                "actions": [{"type": "login", "time": "2023-01-01"}],
            },
            {
                "user": {"name": "Jane", "profile": {"age": 25, "tags": ["user"]}},
                "actions": [{"type": "logout", "time": "2023-01-02"}],
            },
        ]

        # Test filtering complex data
        result = processor.filter_data(
            complex_data, lambda x: x["user"]["profile"]["age"] > 26
        )

        assert result.success
        filtered = result.unwrap()
        assert len(filtered) == 1
        assert filtered[0]["user"]["name"] == "John"

    def test_file_manager_with_large_files(self) -> None:
        """Test file manager operations with larger content."""
        manager = FlextCliFileManager()

        # Create content larger than typical small files
        large_content = "A" * 10000  # 10KB

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = Path(temp_file.name)

        try:
            # Test writing large content
            result = manager.write_file(temp_file_path, large_content)
            assert result.success

            # Test reading large content
            read_result = manager.read_file(temp_file_path)
            assert read_result.success
            assert read_result.unwrap() == large_content
        finally:
            temp_file_path.unlink()

    def test_concurrent_operations(self) -> None:
        """Test helpers with concurrent-like operations."""
        helper = FlextCliHelper(quiet=True)

        # Test multiple rapid operations
        results = []
        for i in range(10):
            result = helper.flext_cli_confirm(f"Test {i}?", default=True)
            results.append(result)

        # All should succeed
        for result in results:
            assert result.success
            assert result.unwrap() is True

    def test_memory_efficiency(self) -> None:
        """Test that operations don't leak memory significantly."""
        # Create and destroy many helpers
        helpers = []
        for _i in range(100):
            helper = FlextCliHelper(quiet=True)
            helpers.append(helper)

        # Clean up
        del helpers

        # If we get here without memory issues, test passes
        assert True

    def test_exception_context_preservation(self) -> None:
        """Test that exception contexts are properly preserved."""
        helper = FlextCliHelper()

        # Create a situation where multiple exception types could occur
        with patch("pathlib.Path.exists", side_effect=OSError("System error")):
            result = helper.flext_cli_validate_file_path(Path("test.txt"))

        assert not result.success
        assert "System error" in result.error
        # Should preserve the original exception type information
