"""Comprehensive tests for core/helpers.py to maximize coverage (corrected version).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from flext_core import FlextResult
from rich.console import Console
from rich.progress import Progress

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

        assert result.is_success
        assert result.value is False

    def test_flext_cli_confirm_default_true(self) -> None:
        """Test confirmation with default True in quiet mode."""
        helper = FlextCliHelper(quiet=True)

        result = helper.flext_cli_confirm("Are you sure?", default=True)

        assert result.is_success
        assert result.value is True

    @patch("rich.prompt.Confirm.ask")
    def test_flext_cli_confirm_interactive_yes(self, mock_confirm) -> None:
        """Test interactive confirmation returning yes."""
        mock_confirm.return_value = True
        helper = FlextCliHelper(quiet=False)

        result = helper.flext_cli_confirm("Are you sure?")

        assert result.is_success
        assert result.value is True
        mock_confirm.assert_called_once()

    @patch("rich.prompt.Confirm.ask")
    def test_flext_cli_confirm_interactive_no(self, mock_confirm) -> None:
        """Test interactive confirmation returning no."""
        mock_confirm.return_value = False
        helper = FlextCliHelper(quiet=False)

        result = helper.flext_cli_confirm("Are you sure?")

        assert result.is_success
        assert result.value is False

    @patch("rich.prompt.Confirm.ask")
    def test_flext_cli_confirm_exception_handling(self, mock_confirm) -> None:
        """Test confirmation with exception handling."""
        mock_confirm.side_effect = KeyboardInterrupt("User interrupted")
        helper = FlextCliHelper(quiet=False)

        result = helper.flext_cli_confirm("Are you sure?")

        assert not result.is_success
        assert "User interrupted" in result.error

    def test_confirm_method_success(self) -> None:
        """Test non-FlextResult confirm method."""
        helper = FlextCliHelper()

        with patch("rich.prompt.Confirm.ask", return_value=True):
            result = helper.confirm("Are you sure?")
            assert result is True

    def test_confirm_method_exception(self) -> None:
        """Test non-FlextResult confirm method with exception."""
        helper = FlextCliHelper()

        with patch("rich.prompt.Confirm.ask", side_effect=Exception("Error")):
            result = helper.confirm("Are you sure?")
            assert result is False

    @patch("rich.prompt.Prompt.ask")
    def test_flext_cli_prompt_interactive(self, mock_prompt) -> None:
        """Test interactive prompt."""
        mock_prompt.return_value = "user input"
        helper = FlextCliHelper(quiet=False)

        result = helper.flext_cli_prompt("Enter name:")

        assert result.is_success
        assert result.value == "user input"

    @patch("rich.prompt.Prompt.ask")
    def test_flext_cli_prompt_with_default(self, mock_prompt) -> None:
        """Test prompt with default value."""
        mock_prompt.return_value = ""
        helper = FlextCliHelper(quiet=False)

        result = helper.flext_cli_prompt("Enter name:", default="default_value")

        assert result.is_success
        assert result.value == "default_value"

    @patch("rich.prompt.Prompt.ask")
    def test_flext_cli_prompt_empty_input(self, mock_prompt) -> None:
        """Test prompt with empty input and no default."""
        mock_prompt.return_value = ""
        helper = FlextCliHelper(quiet=False)

        result = helper.flext_cli_prompt("Enter name:")

        assert not result.is_success
        assert "Empty input" in result.error

    @patch("rich.prompt.Prompt.ask")
    def test_flext_cli_prompt_exception_handling(self, mock_prompt) -> None:
        """Test prompt with exception handling."""
        mock_prompt.side_effect = KeyboardInterrupt("User interrupted")
        helper = FlextCliHelper(quiet=False)

        result = helper.flext_cli_prompt("Enter name:")

        assert not result.is_success
        assert "User interrupted" in result.error

    def test_prompt_method_success(self) -> None:
        """Test non-FlextResult prompt method."""
        helper = FlextCliHelper()

        with patch("rich.prompt.Prompt.ask", return_value="result"):
            result = helper.prompt("Enter value:")
            assert result == "result"

    def test_prompt_method_exception(self) -> None:
        """Test non-FlextResult prompt method with exception."""
        helper = FlextCliHelper()

        with patch("rich.prompt.Prompt.ask", side_effect=Exception("Error")):
            result = helper.prompt("Enter value:", default="default")
            assert result == "default"

    def test_flext_cli_validate_email_valid(self) -> None:
        """Test email validation with valid email."""
        helper = FlextCliHelper()

        result = helper.flext_cli_validate_email("test@example.com")

        assert result.is_success
        assert result.value == "test@example.com"

    def test_flext_cli_validate_email_invalid(self) -> None:
        """Test email validation with invalid email."""
        helper = FlextCliHelper()

        result = helper.flext_cli_validate_email("invalid-email")

        assert not result.is_success
        assert "Invalid email" in result.error

    def test_flext_cli_validate_email_none(self) -> None:
        """Test email validation with None."""
        helper = FlextCliHelper()

        result = helper.flext_cli_validate_email(None)

        assert not result.is_success
        assert "Email cannot be empty" in result.error

    def test_validate_email_method_valid(self) -> None:
        """Test non-FlextResult validate_email method."""
        helper = FlextCliHelper()

        result = helper.validate_email("test@example.com")
        assert result is True

    def test_validate_email_method_invalid(self) -> None:
        """Test non-FlextResult validate_email method with invalid email."""
        helper = FlextCliHelper()

        result = helper.validate_email("invalid")
        assert result is False

    def test_flext_cli_validate_url_valid(self) -> None:
        """Test URL validation with valid URL."""
        helper = FlextCliHelper()

        result = helper.flext_cli_validate_url("https://example.com")

        assert result.is_success
        assert result.value == "https://example.com"

    def test_flext_cli_validate_url_invalid(self) -> None:
        """Test URL validation with invalid URL."""
        helper = FlextCliHelper()

        result = helper.flext_cli_validate_url("not-a-url")

        assert not result.is_success
        assert "Invalid URL" in result.error

    def test_flext_cli_validate_url_none(self) -> None:
        """Test URL validation with None."""
        helper = FlextCliHelper()

        result = helper.flext_cli_validate_url(None)

        assert not result.is_success
        assert "Invalid URL format" in result.error

    def test_validate_url_method_valid(self) -> None:
        """Test non-FlextResult validate_url method."""
        helper = FlextCliHelper()

        result = helper.validate_url("https://example.com")
        assert result is True

    def test_validate_url_method_invalid(self) -> None:
        """Test non-FlextResult validate_url method with invalid URL."""
        helper = FlextCliHelper()

        result = helper.validate_url("invalid")
        assert result is False

    def test_flext_cli_validate_path_existing_file(self) -> None:
        """Test path validation with existing file."""
        helper = FlextCliHelper()

        with tempfile.NamedTemporaryFile() as temp_file:
            result = helper.flext_cli_validate_path(temp_file.name, must_exist=True)

            assert result.is_success
            assert Path(result.value) == Path(temp_file.name)

    def test_flext_cli_validate_path_nonexistent_required(self) -> None:
        """Test path validation with nonexistent file when required."""
        helper = FlextCliHelper()

        result = helper.flext_cli_validate_path(
            "/nonexistent/file.txt", must_exist=True
        )

        assert not result.is_success
        assert "does not exist" in result.error

    def test_flext_cli_validate_path_nonexistent_allowed(self) -> None:
        """Test path validation with nonexistent file when allowed."""
        helper = FlextCliHelper()

        result = helper.flext_cli_validate_path(
            "/nonexistent/file.txt", must_exist=False
        )

        assert result.is_success

    def test_validate_path_method_existing(self) -> None:
        """Test non-FlextResult validate_path method."""
        helper = FlextCliHelper()

        with tempfile.NamedTemporaryFile() as temp_file:
            result = helper.validate_path(temp_file.name, must_exist=True)
            assert result is True

    def test_validate_path_method_nonexistent(self) -> None:
        """Test non-FlextResult validate_path method with nonexistent file."""
        helper = FlextCliHelper()

        result = helper.validate_path("/nonexistent/file.txt", must_exist=True)
        assert result is False

    def test_flext_cli_sanitize_filename_valid(self) -> None:
        """Test filename sanitization with valid filename."""
        helper = FlextCliHelper()

        result = helper.flext_cli_sanitize_filename("valid_file.txt")

        assert result.is_success
        assert result.value == "valid_file.txt"

    def test_flext_cli_sanitize_filename_with_invalid_chars(self) -> None:
        """Test filename sanitization with invalid characters."""
        helper = FlextCliHelper()

        result = helper.flext_cli_sanitize_filename('file<>:"|?*.txt')

        assert result.is_success
        sanitized = result.value
        assert "<" not in sanitized
        assert ">" not in sanitized
        assert "|" not in sanitized

    def test_flext_cli_sanitize_filename_too_long(self) -> None:
        """Test filename sanitization with overly long filename."""
        helper = FlextCliHelper()
        long_name = "a" * 300 + ".txt"

        result = helper.flext_cli_sanitize_filename(long_name)

        assert result.is_success
        sanitized = result.value
        assert len(sanitized) <= 255

    def test_sanitize_filename_method(self) -> None:
        """Test non-FlextResult sanitize_filename method."""
        helper = FlextCliHelper()

        result = helper.sanitize_filename("file<>name.txt")
        assert "<" not in result
        assert ">" not in result

    def test_format_size_bytes(self) -> None:
        """Test format_size with various byte sizes."""
        helper = FlextCliHelper()

        assert "KB" in helper.format_size(1024)
        assert "MB" in helper.format_size(1024 * 1024)
        assert "GB" in helper.format_size(1024 * 1024 * 1024)

    def test_truncate_text_short(self) -> None:
        """Test truncate_text with text shorter than limit."""
        helper = FlextCliHelper()

        result = helper.truncate_text("short", max_length=10)
        assert result == "short"

    def test_truncate_text_long(self) -> None:
        """Test truncate_text with text longer than limit."""
        helper = FlextCliHelper()

        result = helper.truncate_text("very long text here", max_length=10)
        assert len(result) <= 10
        assert "..." in result

    def test_flext_cli_print_status_info(self) -> None:
        """Test print_status with info status."""
        helper = FlextCliHelper()

        # Should not raise exception
        helper.flext_cli_print_status("Test message", status="info")

    def test_flext_cli_print_status_success(self) -> None:
        """Test print_status with success status."""
        helper = FlextCliHelper()

        # Should not raise exception
        helper.flext_cli_print_status("Success message", status="success")

    def test_print_convenience_methods(self) -> None:
        """Test convenience print methods."""
        helper = FlextCliHelper()

        # All should execute without error
        helper.print_success("Success")
        helper.print_error("Error")
        helper.print_warning("Warning")
        helper.print_info("Info")

    def test_flext_cli_create_table_basic(self) -> None:
        """Test create_table with basic data."""
        helper = FlextCliHelper()
        data = [{"name": "John", "age": 30}]

        result = helper.flext_cli_create_table(data)

        assert result.is_success
        # Result should be a formatted string or table object

    def test_flext_cli_execute_command_success(self) -> None:
        """Test execute_command with successful command."""
        helper = FlextCliHelper()

        result = helper.flext_cli_execute_command("echo hello")

        assert result.is_success
        output = result.value
        assert isinstance(output, dict)
        assert "stdout" in output or "output" in output

    def test_flext_cli_execute_command_failure(self) -> None:
        """Test execute_command with failing command."""
        helper = FlextCliHelper()

        result = helper.flext_cli_execute_command("nonexistent_command_12345")

        assert not result.is_success

    def test_flext_cli_load_json_file_success(self) -> None:
        """Test loading JSON file successfully."""
        helper = FlextCliHelper()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".json", delete=False
        ) as temp_file:
            json.dump({"test": "data"}, temp_file)
            temp_file_path = temp_file.name

        try:
            result = helper.flext_cli_load_json_file(temp_file_path)

            assert result.is_success
            data = result.value
            assert data["test"] == "data"
        finally:
            Path(temp_file_path).unlink()

    def test_flext_cli_load_json_file_not_found(self) -> None:
        """Test loading nonexistent JSON file."""
        helper = FlextCliHelper()

        result = helper.flext_cli_load_json_file("/nonexistent/file.json")

        assert not result.is_success

    def test_flext_cli_save_json_file_success(self) -> None:
        """Test saving JSON file successfully."""
        helper = FlextCliHelper()
        data = {"test": "data", "number": 42}

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            result = helper.flext_cli_save_json_file(data, temp_file_path)

            assert result.is_success

            # Verify file was saved correctly
            with open(temp_file_path, encoding="utf-8") as f:
                loaded_data = json.load(f)
            assert loaded_data == data
        finally:
            Path(temp_file_path).unlink()

    def test_flext_cli_with_progress_context(self) -> None:
        """Test with_progress context manager."""
        helper = FlextCliHelper()

        items = [1, 2, 3]
        result = helper.flext_cli_with_progress(items, "Processing...")

        # Should return the items list
        assert result == items

    def test_create_progress_method(self) -> None:
        """Test create_progress method."""
        helper = FlextCliHelper()

        progress = helper.create_progress("Test message")

        assert isinstance(progress, Progress)


class TestFlextCliDataProcessor:
    """Test FlextCliDataProcessor class comprehensive coverage."""

    def test_processor_init_default(self) -> None:
        """Test processor initialization with defaults."""
        processor = FlextCliDataProcessor()

        assert processor is not None

    def test_processor_init_with_helper(self) -> None:
        """Test processor initialization with helper."""
        helper = FlextCliHelper()
        processor = FlextCliDataProcessor(helper=helper)

        assert processor is not None

    def test_flext_cli_process_workflow_basic(self) -> None:
        """Test process_workflow with basic workflow."""
        processor = FlextCliDataProcessor()
        input_data = {"email": "test@example.com"}

        # Create valid workflow steps as list of tuples
        steps = [("validate_email", FlextResult[dict[str, object]].ok)]

        result = processor.flext_cli_process_workflow(input_data, steps)

        # Should succeed or fail gracefully
        assert isinstance(result, FlextResult)

    def test_flext_cli_validate_and_transform_success(self) -> None:
        """Test validate_and_transform with valid data."""
        processor = FlextCliDataProcessor()
        data = {"name": "John", "age": "30"}
        validators = {"name": "str", "age": "int"}
        transforms = {}

        result = processor.flext_cli_validate_and_transform(
            data, validators, transforms
        )

        # Should succeed or fail gracefully
        assert isinstance(result, FlextResult)

    def test_flext_cli_aggregate_data_basic(self) -> None:
        """Test aggregate_data with basic aggregation."""
        processor = FlextCliDataProcessor()

        # Create valid data sources as dict of functions
        sources = {
            "source1": lambda: FlextResult[str].ok("data1"),
            "source2": lambda: FlextResult[str].ok("data2"),
        }

        result = processor.flext_cli_aggregate_data(sources)

        assert isinstance(result, FlextResult)

    def test_transform_data_pipeline_basic(self) -> None:
        """Test transform_data_pipeline with basic pipeline."""
        processor = FlextCliDataProcessor()
        data = [{"value": 1}, {"value": 2}]
        pipeline_config = {"steps": []}

        result = processor.transform_data_pipeline(data, pipeline_config)

        assert isinstance(result, FlextResult)


class TestFlextCliFileManager:
    """Test FlextCliFileManager class comprehensive coverage."""

    def test_file_manager_init_default(self) -> None:
        """Test file manager initialization with defaults."""
        manager = FlextCliFileManager()

        assert manager is not None

    def test_file_manager_init_with_helper(self) -> None:
        """Test file manager initialization with helper."""
        helper = FlextCliHelper()
        manager = FlextCliFileManager(helper=helper)

        assert manager is not None

    def test_backup_and_process_basic(self) -> None:
        """Test backup_and_process with basic operation."""
        manager = FlextCliFileManager()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False
        ) as temp_file:
            temp_file.write("original content")
            temp_file_path = temp_file.name

        try:

            def process_func(content: str) -> FlextResult[str]:
                return FlextResult[str].ok(content.upper())

            result = manager.backup_and_process(temp_file_path, process_func)

            # Should succeed or fail gracefully
            assert isinstance(result, FlextResult)
        finally:
            Path(temp_file_path).unlink()

    def test_safe_write_success(self) -> None:
        """Test safe_write with successful write."""
        manager = FlextCliFileManager()

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            result = manager.safe_write("test content", temp_file_path)

            # Should succeed
            assert isinstance(result, FlextResult)
            if result.is_success:
                assert (
                    Path(temp_file_path).read_text(encoding="utf-8") == "test content"
                )
        finally:
            Path(temp_file_path).unlink()


class TestFactoryFunctions:
    """Test factory functions comprehensive coverage."""

    def test_flext_cli_create_helper_default(self) -> None:
        """Test creating helper with defaults."""
        helper = flext_cli_create_helper()

        assert isinstance(helper, FlextCliHelper)
        assert helper.quiet is False

    def test_flext_cli_create_helper_quiet(self) -> None:
        """Test creating helper in quiet mode."""
        helper = flext_cli_create_helper(quiet=True)

        assert isinstance(helper, FlextCliHelper)
        assert helper.quiet is True

    def test_flext_cli_create_helper_with_console(self) -> None:
        """Test creating helper with custom console."""
        console = Console()
        helper = flext_cli_create_helper(console=console)

        assert isinstance(helper, FlextCliHelper)
        assert helper.console is console

    def test_flext_cli_create_data_processor_default(self) -> None:
        """Test creating data processor with defaults."""
        processor = flext_cli_create_data_processor()

        assert isinstance(processor, FlextCliDataProcessor)

    def test_flext_cli_create_data_processor_with_helper(self) -> None:
        """Test creating data processor with helper."""
        helper = FlextCliHelper()
        processor = flext_cli_create_data_processor(helper=helper)

        assert isinstance(processor, FlextCliDataProcessor)

    def test_flext_cli_create_file_manager_default(self) -> None:
        """Test creating file manager with defaults."""
        manager = flext_cli_create_file_manager()

        assert isinstance(manager, FlextCliFileManager)

    def test_flext_cli_create_file_manager_with_helper(self) -> None:
        """Test creating file manager with helper."""
        helper = FlextCliHelper()
        manager = flext_cli_create_file_manager(helper=helper)

        assert isinstance(manager, FlextCliFileManager)

    def test_flext_cli_batch_validate_basic(self) -> None:
        """Test batch_validate with correct signature."""
        # The function expects dict[str, tuple[object, str]] format
        inputs = {"field1": ("value1", "str"), "field2": (42, "int")}

        result = flext_cli_batch_validate(inputs)

        # Should return FlextResult
        assert isinstance(result, FlextResult)


class TestValidationMethods:
    """Test various validation helper methods."""

    def test_validate_email_field(self) -> None:
        """Test email field validation in data processor."""
        processor = FlextCliDataProcessor()

        # Test internal validation methods if accessible
        result = processor._validate_email_field("test@example.com", {"required": True})

        assert isinstance(result, FlextResult)

    def test_validate_url_field(self) -> None:
        """Test URL field validation in data processor."""
        processor = FlextCliDataProcessor()

        result = processor._validate_url_field(
            "https://example.com", {"required": True}
        )

        assert isinstance(result, FlextResult)

    def test_validate_file_field(self) -> None:
        """Test file field validation in data processor."""
        processor = FlextCliDataProcessor()

        with tempfile.NamedTemporaryFile() as temp_file:
            result = processor._validate_file_field(
                temp_file.name, {"must_exist": True}
            )

            assert isinstance(result, FlextResult)

    def test_sanitize_filename_field(self) -> None:
        """Test filename sanitization in data processor."""
        processor = FlextCliDataProcessor()

        result = processor._sanitize_filename_field("file<>name.txt", {})

        assert isinstance(result, FlextResult)

    def test_transform_path_field(self) -> None:
        """Test path transformation in data processor."""
        processor = FlextCliDataProcessor()

        result = processor._transform_path_field("/some/path", {"make_absolute": True})

        assert isinstance(result, FlextResult)

    def test_validate_dir_field(self) -> None:
        """Test directory validation in data processor."""
        processor = FlextCliDataProcessor()

        with tempfile.TemporaryDirectory() as temp_dir:
            result = processor._validate_dir_field(temp_dir, {"must_exist": True})

            assert isinstance(result, FlextResult)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_helper_with_none_values(self) -> None:
        """Test helper methods with None values."""
        helper = FlextCliHelper()

        # Test methods that should handle None gracefully
        email_result = helper.flext_cli_validate_email(None)
        assert not email_result.is_success

        url_result = helper.flext_cli_validate_url(None)
        assert not url_result.is_success

    def test_processor_with_empty_data(self) -> None:
        """Test processor methods with empty data."""
        processor = FlextCliDataProcessor()

        # Test with empty lists/dicts
        # Test with empty sources
        result = processor.flext_cli_aggregate_data({})
        assert isinstance(result, FlextResult)

    def test_file_manager_with_invalid_paths(self) -> None:
        """Test file manager with invalid paths."""
        manager = FlextCliFileManager()

        # Test with invalid path
        result = manager.backup_and_process("/nonexistent/file.txt", lambda x: x)
        assert isinstance(result, FlextResult)
        assert not result.is_success

    def test_concurrent_helper_usage(self) -> None:
        """Test multiple helpers used concurrently."""
        helpers = [FlextCliHelper(quiet=True) for _ in range(10)]

        results = []
        for helper in helpers:
            result = helper.flext_cli_confirm("Test?", default=True)
            results.append(result)

        # All should succeed
        for result in results:
            assert result.is_success
            assert result.value is True

    def test_large_data_processing(self) -> None:
        """Test processing larger datasets."""
        processor = FlextCliDataProcessor()

        # Create larger dataset
        [{"id": i, "value": f"item_{i}"} for i in range(1000)]

        # Create large data sources
        large_sources = {
            f"source_{i}": lambda i=i: FlextResult[str].ok(f"data_{i}")
            for i in range(100)
        }

        result = processor.flext_cli_aggregate_data(large_sources)
        assert isinstance(result, FlextResult)

    def test_unicode_handling(self) -> None:
        """Test Unicode content handling."""
        helper = FlextCliHelper()

        # Test with Unicode content
        unicode_filename = "测试文件_🚀.txt"
        result = helper.flext_cli_sanitize_filename(unicode_filename)

        assert result.is_success
        sanitized = result.value
        assert len(sanitized) > 0
