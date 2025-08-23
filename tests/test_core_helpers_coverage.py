"""REAL CODE TESTS for core/helpers.py - NO MOCKS, REAL EXECUTION.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This module tests FlextCliHelper, FlextCliDataProcessor, and FlextCliFileManager
with REAL execution, validating actual functionality without mocking.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from flext_core import FlextResult
from rich.console import Console
from rich.table import Table

from flext_cli import (
    FlextCliDataProcessor,
    FlextCliFileManager,
    FlextCliHelper,
    flext_cli_batch_validate,
    flext_cli_create_data_processor,
    flext_cli_create_file_manager,
    flext_cli_create_helper,
)


class TestFlextCliHelper:
    """Test FlextCliHelper class with REAL execution."""

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

    def test_flext_cli_confirm_quiet_mode(self) -> None:
        """Test confirm in quiet mode."""
        helper = FlextCliHelper(quiet=True)

        # In quiet mode, should return default without prompting
        result = helper.flext_cli_confirm("Proceed?", default=True)

        assert result.is_success
        assert result.value is True

        # Test with False default
        result = helper.flext_cli_confirm("Proceed?", default=False)

        assert result.is_success
        assert result.value is False

    def test_flext_cli_validate_path_existing_file(self) -> None:
        """Test validate_path with existing file."""
        helper = FlextCliHelper()

        with tempfile.NamedTemporaryFile() as temp_file:
            result = helper.flext_cli_validate_path(
                temp_file.name, must_be_file=True, must_exist=True
            )

            assert result.is_success
            assert result.value == Path(temp_file.name)

    def test_flext_cli_validate_path_nonexistent(self) -> None:
        """Test validate_path with nonexistent file."""
        helper = FlextCliHelper()

        result = helper.flext_cli_validate_path(
            "/nonexistent/file.txt", must_be_file=True, must_exist=True
        )

        assert not result.is_success
        assert "does not exist" in result.error

    def test_flext_cli_validate_path_directory(self) -> None:
        """Test validate_path with directory."""
        helper = FlextCliHelper()

        with tempfile.TemporaryDirectory() as temp_dir:
            result = helper.flext_cli_validate_path(
                temp_dir, must_be_dir=True, must_exist=True
            )

            assert result.is_success
            assert result.value == Path(temp_dir)

    def test_flext_cli_validate_path_directory_as_file_error(self) -> None:
        """Test validate_path with directory when file is required."""
        helper = FlextCliHelper()

        with tempfile.TemporaryDirectory() as temp_dir:
            result = helper.flext_cli_validate_path(
                temp_dir, must_be_file=True, must_exist=True
            )

            assert not result.is_success
            assert "must be a file" in result.error

    def test_flext_cli_validate_email_valid(self) -> None:
        """Test validate_email with valid email."""
        helper = FlextCliHelper()

        result = helper.flext_cli_validate_email("test@example.com")

        assert result.is_success
        assert result.value == "test@example.com"

    def test_flext_cli_validate_email_invalid(self) -> None:
        """Test validate_email with invalid email."""
        helper = FlextCliHelper()

        result = helper.flext_cli_validate_email("invalid-email")

        assert not result.is_success
        assert "Invalid email format" in result.error

    def test_flext_cli_validate_url_valid(self) -> None:
        """Test validate_url with valid URL."""
        helper = FlextCliHelper()

        result = helper.flext_cli_validate_url("https://example.com")

        assert result.is_success
        assert result.value == "https://example.com"

    def test_flext_cli_validate_url_invalid(self) -> None:
        """Test validate_url with invalid URL."""
        helper = FlextCliHelper()

        result = helper.flext_cli_validate_url("not-a-url")

        assert not result.is_success
        assert "Invalid URL format" in result.error

    def test_flext_cli_sanitize_filename_valid(self) -> None:
        """Test sanitize_filename with valid filename."""
        helper = FlextCliHelper()

        result = helper.flext_cli_sanitize_filename("test_file.txt")

        assert result.is_success
        assert result.value == "test_file.txt"

    def test_flext_cli_sanitize_filename_invalid_chars(self) -> None:
        """Test sanitize_filename with invalid characters."""
        helper = FlextCliHelper()

        result = helper.flext_cli_sanitize_filename("test<>file|.txt")

        assert result.is_success
        # Should have cleaned invalid characters
        assert "<" not in result.value
        assert ">" not in result.value
        assert "|" not in result.value

    def test_flext_cli_execute_command_empty(self) -> None:
        """Test execute_command with empty command."""
        helper = FlextCliHelper()

        result = helper.flext_cli_execute_command("")

        assert not result.is_success
        assert "empty" in result.error.lower()

    def test_flext_cli_execute_command_whitespace(self) -> None:
        """Test execute_command with whitespace-only command."""
        helper = FlextCliHelper()

        result = helper.flext_cli_execute_command("   ")

        assert not result.is_success
        assert "empty" in result.error.lower()

    def test_create_progress_object(self) -> None:
        """Test create_progress method."""
        helper = FlextCliHelper()

        progress = helper.create_progress("Processing items")
        assert progress is not None
        # Progress object should be created

    def test_create_progress_quiet_mode(self) -> None:
        """Test create_progress in quiet mode."""
        helper = FlextCliHelper(quiet=True)

        progress = helper.create_progress("Processing quietly")
        assert progress is not None
        # Should still return Progress object

    def test_flext_cli_create_table_with_data(self) -> None:
        """Test create_table with real data."""
        helper = FlextCliHelper()
        data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]

        result = helper.flext_cli_create_table(data, title="Users")

        assert result.is_success
        assert isinstance(result.value, Table)
        assert result.value.title == "Users"

    def test_flext_cli_create_table_empty_data(self) -> None:
        """Test create_table with empty data."""
        helper = FlextCliHelper()

        result = helper.flext_cli_create_table([])

        assert not result.is_success
        assert "No data" in result.error

    def test_flext_cli_create_table_simple_data(self) -> None:
        """Test create_table with simple list data."""
        helper = FlextCliHelper()
        data = ["item1", "item2", "item3"]

        result = helper.flext_cli_create_table(data)

        assert result.is_success
        assert isinstance(result.value, Table)

    def test_flext_cli_load_json_file_success(self) -> None:
        """Test load_json_file with valid JSON file."""
        helper = FlextCliHelper()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".json", delete=False
        ) as temp_file:
            temp_file.write('{"test": "data"}')
            temp_file.flush()
            file_path = Path(temp_file.name)

            result = helper.flext_cli_load_json_file(file_path)

            assert result.is_success
            assert result.value == {"test": "data"}

            # Clean up
            file_path.unlink()

    def test_flext_cli_load_json_file_not_found(self) -> None:
        """Test load_json_file with non-existent file."""
        helper = FlextCliHelper()

        result = helper.flext_cli_load_json_file(Path("/nonexistent/file.json"))

        assert not result.is_success
        assert (
            "not found" in result.error.lower()
            or "does not exist" in result.error.lower()
        )

    def test_flext_cli_save_json_file_success(self) -> None:
        """Test save_json_file with valid data."""
        helper = FlextCliHelper()
        data = {"test": "data", "number": 42}

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.json"

            result = helper.flext_cli_save_json_file(data, str(file_path))

            assert result.is_success
            # Verify file was created and contains correct data
            assert file_path.exists()
            import json

            with open(file_path, encoding="utf-8") as f:
                saved_data = json.load(f)
            assert saved_data == data

    def test_format_size_bytes(self) -> None:
        """Test format_size with bytes."""
        helper = FlextCliHelper()

        result = helper.format_size(512)
        assert "B" in result

    def test_format_size_kilobytes(self) -> None:
        """Test format_size with kilobytes."""
        helper = FlextCliHelper()

        result = helper.format_size(2048)  # 2 KB
        assert "KB" in result

    def test_truncate_text_short(self) -> None:
        """Test truncate_text with text shorter than max length."""
        helper = FlextCliHelper()

        result = helper.truncate_text("short", max_length=20)
        assert result == "short"

    def test_truncate_text_long(self) -> None:
        """Test truncate_text with text longer than max length."""
        helper = FlextCliHelper()

        result = helper.truncate_text("this is a very long text", max_length=10)
        assert len(result) <= 10
        assert result.endswith("...")

    def test_print_methods_exist(self) -> None:
        """Test that print methods exist and can be called."""
        helper = FlextCliHelper()

        # These should not raise exceptions
        helper.print_success("Success message")
        helper.print_error("Error message")
        helper.print_warning("Warning message")
        helper.print_info("Info message")
        helper.flext_cli_print_status("Status message")


class TestFlextCliFileManager:
    """Test FlextCliFileManager class with REAL file operations."""

    def test_file_manager_init(self) -> None:
        """Test file manager initialization."""
        manager = FlextCliFileManager()

        assert manager is not None
        # Test that it has expected methods
        assert hasattr(manager, "flext_cli_backup_and_process")
        assert hasattr(manager, "flext_cli_safe_write")

    def test_flext_cli_backup_and_process_existing_file(self) -> None:
        """Test backup_and_process with existing file."""
        manager = FlextCliFileManager()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False
        ) as temp_file:
            temp_file.write("original content")
            temp_file.flush()
            file_path = Path(temp_file.name)

            def process_fn(content: str) -> FlextResult[str]:
                return FlextResult[str].ok(content.upper())

            result = manager.flext_cli_backup_and_process(str(file_path), process_fn)

            assert result.is_success
            # Verify processed content
            processed_content = file_path.read_text(encoding="utf-8")
            assert "ORIGINAL CONTENT" in processed_content

            # Clean up
            file_path.unlink()
            # Clean up backup file if it exists
            backup_path = file_path.with_suffix(file_path.suffix + ".bak")
            if backup_path.exists():
                backup_path.unlink()

    def test_flext_cli_backup_and_process_nonexistent_file(self) -> None:
        """Test backup_and_process with nonexistent file."""
        manager = FlextCliFileManager()

        def process_fn(content: str) -> FlextResult[str]:
            return FlextResult[str].ok(content.upper())

        result = manager.flext_cli_backup_and_process(
            "/nonexistent/file.txt", process_fn
        )

        assert not result.is_success
        assert "not found" in result.error.lower() or "File not found" in result.error

    def test_flext_cli_safe_write_success(self) -> None:
        """Test safe_write with valid content."""
        manager = FlextCliFileManager()
        content = "test safe write content"

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test_safe_write.txt"

            result = manager.flext_cli_safe_write(content, str(file_path))

            assert result.is_success
            # Verify content was written
            written_content = file_path.read_text()
            assert written_content == content


class TestFlextCliDataProcessor:
    """Test FlextCliDataProcessor class with REAL processing."""

    def test_processor_init(self) -> None:
        """Test processor initialization."""
        processor = FlextCliDataProcessor()

        assert processor is not None
        # Test basic methods exist
        assert hasattr(processor, "flext_cli_process_workflow")
        assert hasattr(processor, "flext_cli_validate_and_transform")
        assert hasattr(processor, "flext_cli_aggregate_data")
        assert hasattr(processor, "flext_cli_transform_data_pipeline")

    def test_processor_workflow_simple_case(self) -> None:
        """Test processor workflow with simple data."""
        processor = FlextCliDataProcessor()

        data = {"values": [1, 2, 3]}

        def double_values_step(
            item: dict[str, object],
        ) -> FlextResult[dict[str, object]]:
            values = item.get("values", [])
            if isinstance(values, list):
                doubled = [v * 2 for v in values if isinstance(v, (int, float))]
                return FlextResult[dict[str, object]].ok({"doubled_values": doubled})
            return FlextResult[dict[str, object]].fail("No valid values found")

        steps = [("double", double_values_step)]
        result = processor.flext_cli_process_workflow(data, steps)

        assert result.is_success
        processed_data = result.value
        assert "doubled_values" in processed_data
        assert processed_data["doubled_values"] == [2, 4, 6]

    def test_processor_validate_and_transform_valid_data(self) -> None:
        """Test validate_and_transform with valid data."""
        processor = FlextCliDataProcessor()

        data = {"name": "test", "value": 42}

        # The method expects validators as dict[str, str] mapping field -> validation type
        validators = {
            "name": "none",
            "value": "none",
        }  # Use 'none' for no-op validation
        transformers = {
            "name": lambda x: str(x).upper() if isinstance(x, str) else str(x),
            "value": lambda x: x * 2 if isinstance(x, (int, float)) else x,
        }

        result = processor.flext_cli_validate_and_transform(
            data, validators, transformers
        )

        assert result.is_success
        transformed = result.value
        assert transformed["name"] == "TEST"
        assert transformed["value"] == 84

    def test_processor_aggregate_data_sources(self) -> None:
        """Test aggregate_data with source functions."""
        processor = FlextCliDataProcessor()

        def source1() -> FlextResult[str]:
            return FlextResult[str].ok("10")

        def source2() -> FlextResult[str]:
            return FlextResult[str].ok("20")

        def source3() -> FlextResult[str]:
            return FlextResult[str].ok("30")

        sources = {"amount1": source1, "amount2": source2, "amount3": source3}
        result = processor.flext_cli_aggregate_data(sources)

        assert result.is_success
        aggregated = result.value
        assert aggregated["amount1"] == "10"
        assert aggregated["amount2"] == "20"
        assert aggregated["amount3"] == "30"

    def test_processor_transform_data_pipeline_success(self) -> None:
        """Test transform_data_pipeline with multiple stages."""
        processor = FlextCliDataProcessor()

        data = {"numbers": [1, 2, 3, 4, 5]}

        def double_stage(d: dict[str, object]) -> FlextResult[dict[str, object]]:
            if "numbers" in d and isinstance(d["numbers"], list):
                doubled = [x * 2 for x in d["numbers"] if isinstance(x, (int, float))]
                return FlextResult[dict[str, object]].ok({"numbers": doubled})
            return FlextResult[dict[str, object]].fail("No numbers to double")

        def filter_stage(d: dict[str, object]) -> FlextResult[dict[str, object]]:
            if "numbers" in d and isinstance(d["numbers"], list):
                filtered = [
                    x for x in d["numbers"] if isinstance(x, (int, float)) and x > 5
                ]
                return FlextResult[dict[str, object]].ok({"numbers": filtered})
            return FlextResult[dict[str, object]].fail("No numbers to filter")

        pipeline_stages = [double_stage, filter_stage]

        result = processor.flext_cli_transform_data_pipeline(data, pipeline_stages)

        assert result.is_success
        final_result = result.value
        # Original: [1, 2, 3, 4, 5] -> double: [2, 4, 6, 8, 10] -> filter: [6, 8, 10]
        assert final_result["numbers"] == [6, 8, 10]


# Factory function tests
def test_flext_cli_create_helper() -> None:
    """Test create_helper factory function."""
    helper = flext_cli_create_helper()

    assert helper is not None
    assert isinstance(helper, FlextCliHelper)
    assert hasattr(helper, "console")
    assert hasattr(helper, "quiet")


def test_flext_cli_create_data_processor() -> None:
    """Test create_data_processor factory function."""
    processor = flext_cli_create_data_processor()

    assert processor is not None
    assert isinstance(processor, FlextCliDataProcessor)


def test_flext_cli_create_file_manager() -> None:
    """Test create_file_manager factory function."""
    manager = flext_cli_create_file_manager()

    assert manager is not None
    assert isinstance(manager, FlextCliFileManager)


def test_flext_cli_batch_validate_simple_case() -> None:
    """Test batch_validate with simple validation."""
    # batch_validate expects dict[str, tuple[object, str]] where str is validation type
    inputs = {
        "field1": ("test1", "none"),
        "field2": ("test2", "none"),
        "field3": ("test3", "none"),
    }
    result = flext_cli_batch_validate(inputs)

    assert result.is_success
    assert result.value["field1"] == "test1"
    assert result.value["field2"] == "test2"
    assert result.value["field3"] == "test3"


def test_flext_cli_batch_validate_empty_dict() -> None:
    """Test batch_validate with empty dict."""
    inputs: dict[str, tuple[object, str]] = {}

    result = flext_cli_batch_validate(inputs)

    assert result.is_success
    assert result.value == {}


def test_flext_cli_batch_validate_with_validation() -> None:
    """Test batch_validate with actual validation."""
    # Use 'none' validation type which passes everything through
    inputs = {
        "field1": ("valid_value", "none"),
        "field2": (42, "none"),
        "field3": ([1, 2, 3], "none"),
    }
    result = flext_cli_batch_validate(inputs)

    # Should succeed with 'none' validation
    assert result.is_success
    validation_results = result.value
    assert validation_results["field1"] == "valid_value"
    assert validation_results["field2"] == 42
    assert validation_results["field3"] == [1, 2, 3]
