"""Tests for FlextCli Advanced Helpers - Comprehensive Testing Suite.

This test suite validates all advanced helper classes and functions that provide
massive boilerplate reduction for CLI applications, ensuring 95%+ coverage and
robust functionality under various conditions.

Test Categories:
    - FlextCliHelper: Core helper functionality and validation
    - FlextCliDataProcessor: Data processing workflows
    - FlextCliFileManager: Advanced file operations
    - Factory functions: Helper instantiation
    - Batch operations: Multi-operation workflows
    - Edge cases and error conditions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Never
from unittest.mock import MagicMock, Mock, patch

import pytest
from flext_core import FlextResult

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
    """Test suite for FlextCliHelper core functionality."""

    def test_helper_initialization(self) -> None:
        """Test helper initialization with default and custom options."""
        # Default initialization
        helper = FlextCliHelper()
        assert helper.console is not None
        assert helper.quiet is False

        # Custom initialization
        helper_quiet = FlextCliHelper(quiet=True)
        assert helper_quiet.quiet is True

    def test_flext_cli_confirm(self) -> None:
        """Test confirmation functionality."""
        helper = FlextCliHelper(quiet=True)

        # Quiet mode returns default
        result = helper.flext_cli_confirm("Test confirmation", default=True)
        assert result.is_success
        assert result.value is True

        result = helper.flext_cli_confirm("Test confirmation", default=False)
        assert result.is_success
        assert result.value is False

    @patch("rich.prompt.Prompt.ask")
    def test_flext_cli_prompt(self, mock_ask: MagicMock) -> None:
        """Test prompt functionality."""
        helper = FlextCliHelper()

        # Normal prompt
        mock_ask.return_value = "test input"
        result = helper.flext_cli_prompt("Enter value:")
        assert result.is_success
        assert result.value == "test input"

        # Prompt with default
        mock_ask.return_value = ""
        result = helper.flext_cli_prompt("Enter value:", default="default_value")
        assert result.is_success
        assert result.value == "default_value"

        # Empty prompt without default should fail
        mock_ask.return_value = ""
        result = helper.flext_cli_prompt("Enter value:")
        assert not result.is_success

    def test_flext_cli_validate_email(self) -> None:
        """Test email validation functionality."""
        helper = FlextCliHelper()

        # Valid emails
        valid_emails = [
            "user@example.com",
            "test.email@domain.co.uk",
            "user+tag@example.org",
        ]

        for email in valid_emails:
            result = helper.flext_cli_validate_email(email)
            assert result.is_success, f"Email {email} should be valid"
            assert result.value == email

        # Invalid emails
        invalid_emails = [
            "",
            "   ",
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
        ]

        for email in invalid_emails:
            result = helper.flext_cli_validate_email(email)
            assert not result.is_success, f"Email {email} should be invalid"

    def test_flext_cli_validate_url(self) -> None:
        """Test URL validation functionality."""
        helper = FlextCliHelper()

        # Valid URLs
        valid_urls = [
            "https://example.com",
            f"http://{__import__('flext_core.constants').flext_core.constants.FlextConstants.Platform.DEFAULT_HOST}:{__import__('flext_core.constants').flext_core.constants.FlextConstants.Platform.FLEXT_API_PORT}",
            "ftp://files.example.com/path",
        ]

        for url in valid_urls:
            result = helper.flext_cli_validate_url(url)
            assert result.is_success, f"URL {url} should be valid"
            assert result.value == url

        # Invalid URLs
        invalid_urls = [
            "",
            "   ",
            "not-a-url",
            "://missing-scheme",
            "http://",
        ]

        for url in invalid_urls:
            result = helper.flext_cli_validate_url(url)
            assert not result.is_success, f"URL {url} should be invalid"

    def test_flext_cli_validate_path(self) -> None:
        """Test path validation functionality."""
        helper = FlextCliHelper()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.txt"
            test_file.write_text("test content")

            # Valid existing file
            result = helper.flext_cli_validate_path(
                str(test_file),
                must_exist=True,
                must_be_file=True,
            )
            assert result.is_success
            assert result.value == test_file

            # Valid existing directory
            result = helper.flext_cli_validate_path(
                str(temp_path),
                must_exist=True,
                must_be_dir=True,
            )
            assert result.is_success

            # Non-existent path with must_exist=True should fail
            result = helper.flext_cli_validate_path(
                str(temp_path / "nonexistent"),
                must_exist=True,
            )
            assert not result.is_success

            # Empty path should fail
            result = helper.flext_cli_validate_path("")
            assert not result.is_success

    def test_flext_cli_sanitize_filename(self) -> None:
        """Test filename sanitization functionality."""
        helper = FlextCliHelper()

        # Test normal filename
        result = helper.flext_cli_sanitize_filename("normal_file.txt")
        assert result.is_success
        assert result.value == "normal_file.txt"

        # Test filename with invalid characters
        result = helper.flext_cli_sanitize_filename('file<>:"/\\|?*.txt')
        assert result.is_success
        assert '<>:"/\\|?*' not in result.value

        # Test filename starting with dot
        result = helper.flext_cli_sanitize_filename(".hidden")
        assert result.is_success
        assert not result.value.startswith(".")

        # Test empty filename
        result = helper.flext_cli_sanitize_filename("")
        assert not result.is_success

    def test_flext_cli_create_table(self) -> None:
        """Test table creation functionality."""
        helper = FlextCliHelper()

        # Valid table data
        data = [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "London"},
        ]

        result = helper.flext_cli_create_table(data, title="Users")
        assert result.is_success

        # Empty data should fail
        result = helper.flext_cli_create_table([])
        assert not result.is_success

    @patch("flext_cli.core.helpers.asyncio.wait_for")
    @patch("flext_cli.core.helpers.asyncio.create_subprocess_exec")
    def test_flext_cli_execute_command(
        self,
        mock_create: MagicMock,
        mock_wait_for: MagicMock,
    ) -> None:
        """Test command execution functionality."""
        helper = FlextCliHelper()

        # Prepare fake process
        proc = Mock()
        proc.returncode = 0
        mock_create.return_value = proc
        mock_wait_for.return_value = (b"command output", b"")

        result = helper.flext_cli_execute_command("echo 'test'")
        assert result.is_success
        assert result.value["success"] is True
        assert result.value["stdout"] == "command output"

        # Failed command
        proc.returncode = 1
        mock_wait_for.return_value = (b"", b"command error")

        result = helper.flext_cli_execute_command("false")
        assert result.is_success  # FlextResult is success, but command failed
        assert result.value["success"] is False
        assert result.value["stderr"] == "command error"

        # Empty command should fail
        result = helper.flext_cli_execute_command("")
        assert not result.is_success

    def test_flext_cli_load_json_file(self) -> None:
        """Test JSON file loading functionality."""
        helper = FlextCliHelper()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8",
            mode="w",
            suffix=".json",
            delete=False,
        ) as f:
            test_data = {"key": "value", "number": 42}
            json.dump(test_data, f)
            temp_path = f.name

        try:
            # Load valid JSON
            result = helper.flext_cli_load_json_file(temp_path)
            assert result.is_success
            assert result.value == test_data

            # Load non-existent file
            result = helper.flext_cli_load_json_file("nonexistent.json")
            assert not result.is_success

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_flext_cli_save_json_file(self) -> None:
        """Test JSON file saving functionality."""
        helper = FlextCliHelper()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / "test.json"
            test_data = {"key": "value", "array": [1, 2, 3]}

            # Save JSON data
            result = helper.flext_cli_save_json_file(test_data, str(temp_file))
            assert result.is_success

            # Verify saved data
            assert temp_file.exists()
            with temp_file.open() as f:
                loaded_data = json.load(f)
            assert loaded_data == test_data

    def test_flext_cli_with_progress(self) -> None:
        """Test progress tracking functionality."""
        helper = FlextCliHelper()

        items = ["item1", "item2", "item3"]
        result = helper.flext_cli_with_progress(items, "Processing items")

        # Should return the same items
        assert result == items

    def test_flext_cli_print_status(self) -> None:
        """Test status printing functionality."""
        helper = FlextCliHelper()

        # Test different status types
        statuses = ["info", "success", "warning", "error"]
        for status in statuses:
            # Should not raise exceptions
            helper.flext_cli_print_status(f"Test {status} message", status=status)


class TestFlextCliDataProcessor:
    """Test suite for FlextCliDataProcessor workflows."""

    def test_processor_initialization(self) -> None:
        """Test data processor initialization."""
        processor = FlextCliDataProcessor()
        assert processor.helper is not None

        # Custom helper
        custom_helper = FlextCliHelper(quiet=True)
        processor = FlextCliDataProcessor(helper=custom_helper)
        assert processor.helper is custom_helper

    def test_flext_cli_process_workflow(self) -> None:
        """Test workflow processing functionality."""
        processor = FlextCliDataProcessor(helper=FlextCliHelper(quiet=True))

        # Define workflow steps
        def step1(data: str) -> FlextResult[str]:
            return FlextResult[None].ok(data + " -> step1")

        def step2(data: str) -> FlextResult[str]:
            return FlextResult[None].ok(data + " -> step2")

        steps = [
            ("Step 1", step1),
            ("Step 2", step2),
        ]

        # Process workflow
        result = processor.flext_cli_process_workflow(
            "initial",
            steps,
            show_progress=False,
        )
        assert result.is_success
        assert result.value == "initial -> step1 -> step2"

        # Test failing step
        def failing_step(data: str) -> FlextResult[str]:  # noqa: ARG001
            return FlextResult[None].fail("Step failed")

        steps_with_failure = [
            ("Step 1", step1),
            ("Failing Step", failing_step),
            ("Step 2", step2),  # Should not execute
        ]

        result = processor.flext_cli_process_workflow(
            "initial",
            steps_with_failure,
            show_progress=False,
        )
        assert not result.is_success
        assert "Step failed" in result.error

    def test_flext_cli_validate_and_transform(self) -> None:
        """Test validation and transformation functionality."""
        processor = FlextCliDataProcessor(helper=FlextCliHelper(quiet=True))

        # Test data
        data = {
            "email": "user@example.com",
            "url": "https://example.com",
            "name": "John Doe",
        }

        validators = {
            "email": "email",
            "url": "url",
            "name": "none",  # No validation
        }

        transformers = {"name": lambda x: x.upper()}

        # Process validation and transformation
        result = processor.flext_cli_validate_and_transform(
            data,
            validators,
            transformers,
        )
        assert result.is_success
        assert result.value["email"] == "user@example.com"
        assert result.value["url"] == "https://example.com"
        assert result.value["name"] == "JOHN DOE"

        # Test validation failure
        invalid_data = {"email": "invalid-email"}
        validators = {"email": "email"}

        result = processor.flext_cli_validate_and_transform(invalid_data, validators)
        assert not result.is_success

        # Test missing required field
        result = processor.flext_cli_validate_and_transform({}, {"required": "email"})
        assert not result.is_success


class TestFlextCliFileManager:
    """Test suite for FlextCliFileManager advanced file operations."""

    def test_file_manager_initialization(self) -> None:
        """Test file manager initialization."""
        manager = FlextCliFileManager()
        assert manager.helper is not None

        # Custom helper
        custom_helper = FlextCliHelper(quiet=True)
        manager = FlextCliFileManager(helper=custom_helper)
        assert manager.helper is custom_helper

    def test_flext_cli_backup_and_process(self) -> None:
        """Test backup and process functionality."""
        manager = FlextCliFileManager(helper=FlextCliHelper(quiet=True))

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("original content")

            # Define processor
            def processor(content: str) -> FlextResult[str]:
                return FlextResult[None].ok(content.replace("original", "processed"))

            # Process file
            result = manager.flext_cli_backup_and_process(
                str(test_file),
                processor,
                require_confirmation=False,
            )
            assert result.is_success

            # Check that file was processed
            assert test_file.read_text() == "processed content"

            # Check that backup exists
            backup_file = test_file.with_suffix(test_file.suffix + ".bak")
            assert backup_file.exists()
            assert backup_file.read_text() == "original content"

    def test_flext_cli_safe_write(self) -> None:
        """Test safe file writing functionality."""
        manager = FlextCliFileManager(helper=FlextCliHelper(quiet=True))

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "subdirectory" / "test.txt"
            content = "test content"

            # Write file with directory creation
            result = manager.flext_cli_safe_write(content, str(test_file))
            assert result.is_success
            assert test_file.exists()
            assert test_file.read_text() == content

            # Test backup functionality
            new_content = "updated content"
            result = manager.flext_cli_safe_write(
                new_content,
                str(test_file),
                backup=True,
            )
            assert result.is_success
            assert test_file.read_text() == new_content

            # Check backup was created
            backup_file = test_file.with_suffix(test_file.suffix + ".bak")
            assert backup_file.exists()
            assert backup_file.read_text() == content


class TestFactoryFunctions:
    """Test suite for factory functions."""

    def test_flext_cli_create_helper(self) -> None:
        """Test helper factory function."""
        # Default helper
        helper = flext_cli_create_helper()
        assert isinstance(helper, FlextCliHelper)
        assert not helper.quiet

        # Custom helper
        helper = flext_cli_create_helper(quiet=True)
        assert helper.quiet

    def test_flext_cli_create_data_processor(self) -> None:
        """Test data processor factory function."""
        # Default processor
        processor = flext_cli_create_data_processor()
        assert isinstance(processor, FlextCliDataProcessor)
        assert isinstance(processor.helper, FlextCliHelper)

        # Custom helper
        custom_helper = FlextCliHelper(quiet=True)
        processor = flext_cli_create_data_processor(helper=custom_helper)
        assert processor.helper is custom_helper

    def test_flext_cli_create_file_manager(self) -> None:
        """Test file manager factory function."""
        # Default manager
        manager = flext_cli_create_file_manager()
        assert isinstance(manager, FlextCliFileManager)
        assert isinstance(manager.helper, FlextCliHelper)

        # Custom helper
        custom_helper = FlextCliHelper(quiet=True)
        manager = flext_cli_create_file_manager(helper=custom_helper)
        assert manager.helper is custom_helper


class TestBatchOperations:
    """Test suite for batch operation utilities."""

    def test_flext_cli_batch_validate(self) -> None:
        """Test batch validation functionality."""
        # Valid inputs
        inputs = {
            "email": ("user@example.com", "email"),
            "url": ("https://example.com", "url"),
        }

        result = flext_cli_batch_validate(inputs)
        assert result.is_success
        assert "email" in result.value
        assert "url" in result.value

        # Invalid inputs
        invalid_inputs = {
            "email": ("invalid-email", "email"),
        }

        result = flext_cli_batch_validate(invalid_inputs)
        assert not result.is_success


class TestErrorConditions:
    """Test suite for error conditions and edge cases."""

    def test_helper_with_none_values(self) -> None:
        """Test helper methods with None and invalid values."""
        helper = FlextCliHelper()

        # None email
        result = helper.flext_cli_validate_email(None)
        assert not result.is_success

        # None URL
        result = helper.flext_cli_validate_url(None)
        assert not result.is_success

        # None path
        result = helper.flext_cli_validate_path(None)
        assert not result.is_success

    @patch("flext_cli.core.helpers.asyncio.wait_for")
    @patch("flext_cli.core.helpers.asyncio.create_subprocess_exec")
    def test_command_execution_timeout(
        self,
        mock_create: MagicMock,
        mock_wait_for: MagicMock,
    ) -> None:
        """Test command execution timeout handling."""
        helper = FlextCliHelper()

        # Mock process and make wait_for raise TimeoutError
        proc = Mock()
        proc.kill = Mock()
        proc.wait = Mock()
        mock_create.return_value = proc
        mock_wait_for.side_effect = TimeoutError()

        result = helper.flext_cli_execute_command("sleep 10", timeout=1)
        assert not result.is_success
        assert "timed out" in result.error

    def test_file_operations_with_permissions(self) -> None:
        """Test file operations with permission issues."""
        manager = FlextCliFileManager(helper=FlextCliHelper(quiet=True))

        # Try to process non-existent file
        result = manager.flext_cli_backup_and_process(
            "/nonexistent/file.txt",
            FlextResult[str].ok,
            require_confirmation=False,
        )
        assert not result.is_success

    def test_data_processor_with_exception(self) -> None:
        """Test data processor with exception in steps."""
        processor = FlextCliDataProcessor(helper=FlextCliHelper(quiet=True))

        def exception_step(data: str) -> Never:  # noqa: ARG001
            msg = "Simulated error"
            raise ValueError(msg)

        steps = [("Exception Step", exception_step)]

        result = processor.flext_cli_process_workflow(
            "data",
            steps,
            show_progress=False,
        )
        assert not result.is_success
        assert "Simulated error" in result.error


@pytest.mark.integration
class TestIntegrationScenarios:
    """Integration tests for real-world scenarios."""

    def test_complete_workflow(self) -> None:
        """Test complete workflow with all components."""
        # Initialize components
        helper = flext_cli_create_helper(quiet=True)
        processor = flext_cli_create_data_processor(helper=helper)
        flext_cli_create_file_manager(helper=helper)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data
            test_data = {"users": [{"name": "John", "email": "john@example.com"}]}

            # Save data
            data_file = Path(temp_dir) / "data.json"
            save_result = helper.flext_cli_save_json_file(test_data, str(data_file))
            assert save_result.is_success

            # Load and validate data
            load_result = helper.flext_cli_load_json_file(str(data_file))
            assert load_result.is_success

            # Validate user emails
            for user in load_result.value["users"]:
                email_result = helper.flext_cli_validate_email(user["email"])
                assert email_result.is_success

            # Process through workflow
            def validate_users(
                data: dict[str, list[dict[str, str]]],
            ) -> FlextResult[dict[str, list[dict[str, str]]]]:
                for user in data["users"]:
                    if "@" not in user["email"]:
                        return FlextResult[None].fail(f"Invalid email: {user['email']}")
                return FlextResult[None].ok(data)

            workflow_result = processor.flext_cli_process_workflow(
                load_result.value,
                [("Validate Users", validate_users)],
                show_progress=False,
            )
            assert workflow_result.is_success

    def test_error_recovery_workflow(self) -> None:
        """Test workflow error recovery and reporting."""
        processor = FlextCliDataProcessor(helper=FlextCliHelper(quiet=True))

        def step1(data: str) -> FlextResult[str]:
            return FlextResult[None].ok(data + " -> step1")

        def failing_step(data: str) -> FlextResult[str]:  # noqa: ARG001
            return FlextResult[None].fail("Step failed intentionally")

        def step3(data: str) -> FlextResult[str]:
            return FlextResult[None].ok(data + " -> step3")

        steps = [
            ("Step 1", step1),
            ("Failing Step", failing_step),
            ("Step 3", step3),
        ]

        result = processor.flext_cli_process_workflow(
            "initial",
            steps,
            show_progress=False,
        )

        # Should fail and provide detailed error message
        assert not result.is_success
        assert "Failing Step" in result.error
        assert "Step failed intentionally" in result.error
