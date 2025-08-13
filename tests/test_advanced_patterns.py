"""Tests for FlextCli Advanced Boilerplate Reduction Patterns.

This module provides comprehensive tests for the most advanced FlextCli patterns
that achieve 85%+ boilerplate reduction through zero-configuration decorators,
advanced mixins, and data processing utilities.

Test Coverage:
    - FlextCliAdvancedMixin with complex workflow methods
    - Zero-configuration decorators (flext_cli_zero_config, flext_cli_auto_retry, flext_cli_with_progress)
    - FlextCliDataProcessor with workflow processing
    - FlextCliFileManager with batch operations
    - Advanced batch processing and data aggregation
    - Integration patterns showing real-world usage

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from flext_core import FlextResult
from rich.console import Console

from flext_cli.core.helpers import FlextCliDataProcessor, FlextCliFileManager
from flext_cli.core.mixins import (
    FlextCliAdvancedMixin,
    flext_cli_auto_retry,
    flext_cli_with_progress,
    flext_cli_zero_config,
)


class TestFlextCliAdvancedMixin:
    """Test suite for FlextCliAdvancedMixin complex workflows."""

    class TestAdvancedClass(FlextCliAdvancedMixin):
        """Test class using FlextCliAdvancedMixin."""

        def __init__(self):
            super().__init__()

    def setup_method(self) -> None:
        """Setup test environment."""
        self.test_instance = self.TestAdvancedClass()
        self.console_mock = MagicMock(spec=Console)
        self.console_mock.get_time = MagicMock(return_value=0.0)
        self.test_instance._flext_cli_console = self.console_mock

    def test_flext_cli_execute_with_full_validation_success(self) -> None:
        """Test full validation workflow with success."""
        inputs = {
            "email": ("user@example.com", "email"),
            "url": ("https://api.flext.sh", "url"),
        }

        def mock_operation() -> FlextResult[str]:
            return FlextResult.ok("Operation completed successfully")

        # Mock confirmation to return success
        with patch.object(
            self.test_instance,
            "flext_cli_require_confirmation",
        ) as mock_confirm:
            mock_confirm.return_value = FlextResult.ok(True)

            result = self.test_instance.flext_cli_execute_with_full_validation(
                inputs,
                mock_operation,
                operation_name="test operation",
            )

        assert result.success
        assert result.data == "Operation completed successfully"

        # Should have printed validation success
        print_calls = self.console_mock.print.call_args_list
        success_messages = [call for call in print_calls if "✓" in str(call)]
        assert len(success_messages) >= 2  # Validation + operation success

    def test_flext_cli_execute_with_full_validation_invalid_input(self) -> None:
        """Test full validation workflow with invalid input."""
        inputs = {
            "email": ("invalid-email", "email"),
            "url": ("https://api.flext.sh", "url"),
        }

        def mock_operation() -> FlextResult[str]:
            return FlextResult.ok("Should not execute")

        result = self.test_instance.flext_cli_execute_with_full_validation(
            inputs,
            mock_operation,
            operation_name="test operation",
        )

        assert not result.success
        assert "Validation failed" in result.error

    def test_flext_cli_execute_with_full_validation_dangerous_operation(self) -> None:
        """Test full validation with dangerous operation styling."""
        inputs = {"email": ("user@example.com", "email")}

        # Mock confirmation to return success
        with patch.object(
            self.test_instance,
            "flext_cli_require_confirmation",
        ) as mock_confirm:
            mock_confirm.return_value = FlextResult.ok(True)

            def mock_operation() -> FlextResult[str]:
                return FlextResult.ok("Dangerous operation completed")

            result = self.test_instance.flext_cli_execute_with_full_validation(
                inputs,
                mock_operation,
                operation_name="delete all data",
                dangerous=True,
            )

        assert result.success
        # Should have called confirmation with dangerous=True
        mock_confirm.assert_called_once_with("delete all data", dangerous=True)

    def test_flext_cli_process_data_workflow_success(self) -> None:
        """Test data processing workflow with multiple steps."""
        workflow_steps = [
            ("validate", lambda data: FlextResult.ok(f"validated_{data}")),
            ("clean", lambda data: FlextResult.ok(f"cleaned_{data}")),
            ("transform", lambda data: FlextResult.ok(f"transformed_{data}")),
        ]

        result = self.test_instance.flext_cli_process_data_workflow(
            "raw_data",
            workflow_steps,
        )

        assert result.success
        assert result.data == "transformed_cleaned_validated_raw_data"

        # Should have printed step progress
        info_calls = [
            call
            for call in self.console_mock.print.call_args_list
            if "Processing step:" in str(call)
        ]
        assert len(info_calls) == 3

    def test_flext_cli_process_data_workflow_step_failure(self) -> None:
        """Test data processing workflow with step failure."""
        workflow_steps = [
            ("validate", lambda data: FlextResult.ok(f"validated_{data}")),
            ("fail_step", lambda data: FlextResult.fail("Processing step failed")),
            ("transform", lambda data: FlextResult.ok("should_not_execute")),
        ]

        result = self.test_instance.flext_cli_process_data_workflow(
            "raw_data",
            workflow_steps,
        )

        assert not result.success
        assert "Step 'fail_step' failed: Processing step failed" in result.error

    def test_flext_cli_process_data_workflow_step_exception(self) -> None:
        """Test data processing workflow with step exception."""

        def failing_step(data: Any) -> FlextResult[str]:
            msg = "Step raised exception"
            raise ValueError(msg)

        workflow_steps = [
            ("validate", lambda data: FlextResult.ok(f"validated_{data}")),
            ("failing_step", failing_step),
        ]

        result = self.test_instance.flext_cli_process_data_workflow(
            "raw_data",
            workflow_steps,
        )

        assert not result.success
        assert (
            "Step 'failing_step' raised exception: Step raised exception"
            in result.error
        )

    def test_flext_cli_handle_file_operations_success(self, tmp_path: Path) -> None:
        """Test file operations handling with success."""
        # Create test files
        test_file1 = tmp_path / "file1.txt"
        test_file2 = tmp_path / "file2.txt"
        test_file1.write_text("content1")
        test_file2.write_text("content2")

        def mock_backup(file_path: str) -> FlextResult[str]:
            return FlextResult.ok(f"Backed up {file_path}")

        def mock_process(file_path: str) -> FlextResult[str]:
            return FlextResult.ok(f"Processed {file_path}")

        file_operations = [
            ("backup", str(test_file1), mock_backup),
            ("process", str(test_file1), mock_process),
            ("backup", str(test_file2), mock_backup),
            ("process", str(test_file2), mock_process),
        ]

        # Mock confirmation
        with patch.object(
            self.test_instance,
            "flext_cli_require_confirmation",
        ) as mock_confirm:
            mock_confirm.return_value = FlextResult.ok(True)

            result = self.test_instance.flext_cli_handle_file_operations(
                file_operations,
            )

        assert result.success
        assert len(result.data) == 4
        assert f"backup_{test_file1}" in result.data
        assert f"process_{test_file1}" in result.data

    def test_flext_cli_handle_file_operations_validation_failure(
        self,
        tmp_path: Path,
    ) -> None:
        """Test file operations with file validation failure."""
        nonexistent_file = tmp_path / "nonexistent.txt"

        def mock_operation(file_path: str) -> FlextResult[str]:
            return FlextResult.ok("Should not execute")

        file_operations = [
            ("process", str(nonexistent_file), mock_operation),
        ]

        result = self.test_instance.flext_cli_handle_file_operations(file_operations)

        assert not result.success
        # Should fail validation before operations


class TestZeroConfigurationDecorators:
    """Test suite for zero-configuration decorators."""

    def test_flext_cli_zero_config_success(self) -> None:
        """Test zero-config decorator with successful execution."""
        with patch("flext_cli.core.mixins.FlextCliHelper") as mock_helper_class:
            mock_helper = mock_helper_class.return_value
            mock_helper.flext_cli_confirm.return_value = FlextResult.ok(True)
            mock_helper.console.print = MagicMock()

            @flext_cli_zero_config("test operation")
            def test_function() -> FlextResult[str]:
                return FlextResult.ok("Operation completed")

            result = test_function()

            assert result.success
            assert result.data == "Operation completed"

    def test_flext_cli_zero_config_with_validation(self) -> None:
        """Test zero-config decorator with input validation."""
        with patch("flext_cli.core.mixins.FlextCliHelper") as mock_helper_class:
            mock_helper = mock_helper_class.return_value
            mock_helper.flext_cli_confirm.return_value = FlextResult.ok(True)
            mock_helper.console.print = MagicMock()

            @flext_cli_zero_config("process user", validate_inputs={"email": "email"})
            def test_function(email: str) -> FlextResult[str]:
                return FlextResult.ok(f"Processed {email}")

            result = test_function(email="user@example.com")

            assert result.success
            assert result.data == "Processed user@example.com"

    def test_flext_cli_zero_config_validation_failure(self) -> None:
        """Test zero-config decorator with validation failure."""

        @flext_cli_zero_config("process user", validate_inputs={"email": "email"})
        def test_function(email: str) -> FlextResult[str]:
            return FlextResult.ok("Should not execute")

        result = test_function(email="invalid-email")

        assert not result.success

    def test_flext_cli_zero_config_dangerous_operation(self) -> None:
        """Test zero-config decorator with dangerous operation."""
        with patch("flext_cli.core.mixins.FlextCliHelper") as mock_helper_class:
            mock_helper = mock_helper_class.return_value
            mock_helper.flext_cli_confirm.return_value = FlextResult.ok(True)

            @flext_cli_zero_config("delete data", dangerous=True)
            def test_function() -> FlextResult[str]:
                return FlextResult.ok("Data deleted")

            result = test_function()

            assert result.success
            assert result.data == "Data deleted"
            # Should have prompted with dangerous styling
            mock_helper.flext_cli_confirm.assert_called_once()
            call_args = mock_helper.flext_cli_confirm.call_args[0][0]
            assert "[bold red]" in call_args

    def test_flext_cli_zero_config_user_cancellation(self) -> None:
        """Test zero-config decorator with user cancellation."""
        with patch("flext_cli.core.mixins.FlextCliHelper") as mock_helper_class:
            mock_helper = mock_helper_class.return_value
            mock_helper.flext_cli_confirm.return_value = FlextResult.ok(False)

            @flext_cli_zero_config("test operation")
            def test_function() -> FlextResult[str]:
                return FlextResult.ok("Should not execute")

            result = test_function()

            assert result.success
            assert result.data == "Operation cancelled by user"

    def test_flext_cli_zero_config_exception_handling(self) -> None:
        """Test zero-config decorator exception handling."""

        @flext_cli_zero_config("test operation", confirm=False)
        def test_function() -> FlextResult[str]:
            msg = "Something went wrong"
            raise ValueError(msg)

        result = test_function()

        assert not result.success
        assert "Test operation raised exception" in result.error
        assert "Something went wrong" in result.error

    def test_flext_cli_auto_retry_success_first_attempt(self) -> None:
        """Test auto-retry decorator with success on first attempt."""
        call_count = 0

        @flext_cli_auto_retry(max_attempts=3, delay=0.1)
        def test_function() -> FlextResult[str]:
            nonlocal call_count
            call_count += 1
            return FlextResult.ok("Success")

        result = test_function()

        assert result.success
        assert result.data == "Success"
        assert call_count == 1

    def test_flext_cli_auto_retry_success_after_retries(self) -> None:
        """Test auto-retry decorator with success after retries."""
        call_count = 0

        @flext_cli_auto_retry(max_attempts=3, delay=0.1)
        def test_function() -> FlextResult[str]:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return FlextResult.fail(f"Attempt {call_count} failed")
            return FlextResult.ok("Success on third attempt")

        result = test_function()

        assert result.success
        assert result.data == "Success on third attempt"
        assert call_count == 3

    def test_flext_cli_auto_retry_all_attempts_fail(self) -> None:
        """Test auto-retry decorator with all attempts failing."""
        call_count = 0

        @flext_cli_auto_retry(max_attempts=3, delay=0.1)
        def test_function() -> FlextResult[str]:
            nonlocal call_count
            call_count += 1
            return FlextResult.fail(f"Attempt {call_count} failed")

        result = test_function()

        assert not result.success
        assert "Operation failed after 3 attempts" in result.error
        assert call_count == 3

    def test_flext_cli_auto_retry_with_exceptions(self) -> None:
        """Test auto-retry decorator with exceptions."""
        call_count = 0

        @flext_cli_auto_retry(max_attempts=2, delay=0.1)
        def test_function() -> FlextResult[str]:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                msg = "Connection failed"
                raise ConnectionError(msg)
            return FlextResult.ok("Connected")

        result = test_function()

        assert result.success
        assert result.data == "Connected"
        assert call_count == 2

    def test_flext_cli_with_progress_success(self) -> None:
        """Test progress decorator with successful execution."""

        @flext_cli_with_progress("Processing data...")
        def test_function() -> FlextResult[str]:
            time.sleep(0.1)  # Simulate work
            return FlextResult.ok("Data processed")

        result = test_function()

        assert result.success
        assert result.data == "Data processed"

    def test_flext_cli_with_progress_failure(self) -> None:
        """Test progress decorator with operation failure."""

        @flext_cli_with_progress("Processing data...")
        def test_function() -> FlextResult[str]:
            return FlextResult.fail("Processing failed")

        result = test_function()

        assert not result.success
        assert result.error == "Processing failed"

    def test_flext_cli_with_progress_exception(self) -> None:
        """Test progress decorator with exception."""

        @flext_cli_with_progress("Processing data...")
        def test_function() -> FlextResult[str]:
            msg = "Unexpected error"
            raise RuntimeError(msg)

        result = test_function()

        assert not result.success
        assert "Operation failed: Unexpected error" in result.error


class TestFlextCliDataProcessor:
    """Test suite for FlextCliDataProcessor advanced features."""

    def setup_method(self) -> None:
        """Setup test environment."""
        self.processor = FlextCliDataProcessor()

    def test_flext_cli_process_workflow_complete(self) -> None:
        """Test complete workflow processing."""
        data = {"items": [1, 2, 3, 4, 5]}

        workflow_steps = [
            ("validate", self._validate_data),
            ("process", self._process_items),
            ("summarize", self._summarize_results),
        ]

        result = self.processor.flext_cli_process_workflow(
            data,
            workflow_steps,
            show_progress=False,
        )

        assert result.success
        assert "summary" in result.data
        assert result.data["summary"]["total_processed"] == 5

    def test_flext_cli_validate_and_transform_complex(self) -> None:
        """Test complex validation and transformation."""
        data = {
            "user_email": "user@example.com",
            "api_endpoint": "https://api.flext.sh/v1",
            "config_file": __file__,  # Use current test file
            "count": "10",
        }

        validators = {
            "user_email": "email",
            "api_endpoint": "url",
            "config_file": "file",
        }

        transformers = {
            "count": int,
            "user_email": lambda x: x.lower(),
        }

        result = self.processor.flext_cli_validate_and_transform(
            data,
            validators,
            transformers,
        )

        assert result.success
        assert result.data["user_email"] == "user@example.com"
        assert result.data["api_endpoint"] == "https://api.flext.sh/v1"
        assert isinstance(result.data["config_file"], Path)
        assert result.data["count"] == 10

    def _validate_data(self, data: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Mock validation step."""
        if "items" not in data:
            return FlextResult.fail("Missing items field")
        return FlextResult.ok(data)

    def _process_items(self, data: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Mock processing step."""
        processed_items = [item * 2 for item in data["items"]]
        return FlextResult.ok({**data, "processed_items": processed_items})

    def _summarize_results(self, data: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Mock summarization step."""
        summary = {
            "total_original": len(data["items"]),
            "total_processed": len(data["processed_items"]),
            "sum_processed": sum(data["processed_items"]),
        }
        return FlextResult.ok({**data, "summary": summary})


class TestFlextCliFileManager:
    """Test suite for FlextCliFileManager advanced operations."""

    def setup_method(self) -> None:
        """Setup test environment."""
        self.file_manager = FlextCliFileManager()

    def test_flext_cli_backup_and_process_success(self, tmp_path: Path) -> None:
        """Test backup and process file with success."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("original content")

        def process_content(content: str) -> FlextResult[str]:
            return FlextResult.ok(content.upper())

        # Mock confirmation
        with patch.object(
            self.file_manager.helper,
            "flext_cli_confirm",
        ) as mock_confirm:
            mock_confirm.return_value = FlextResult.ok(True)

            result = self.file_manager.flext_cli_backup_and_process(
                str(test_file),
                process_content,
                require_confirmation=True,
            )

        assert result.success
        assert result.data["status"] == "completed"
        assert result.data["original_file"] == str(test_file)

        # Verify backup was created
        backup_file = Path(result.data["backup_file"])
        assert backup_file.exists()
        assert backup_file.read_text(encoding="utf-8") == "original content"

        # Verify file was processed
        assert test_file.read_text() == "ORIGINAL CONTENT"

    def test_flext_cli_backup_and_process_processor_failure(
        self,
        tmp_path: Path,
    ) -> None:
        """Test backup and process with processor failure and recovery."""
        test_file = tmp_path / "test.txt"
        original_content = "original content"
        test_file.write_text(original_content)

        def failing_processor(content: str) -> FlextResult[str]:
            return FlextResult.fail("Processing failed")

        # Mock confirmation
        with patch.object(
            self.file_manager.helper,
            "flext_cli_confirm",
        ) as mock_confirm:
            mock_confirm.return_value = FlextResult.ok(True)

            result = self.file_manager.flext_cli_backup_and_process(
                str(test_file),
                failing_processor,
                require_confirmation=True,
            )

        assert not result.success
        assert "Processing failed" in result.error

        # Verify file was restored from backup
        assert test_file.read_text() == original_content

    def test_flext_cli_safe_write_with_backup(self, tmp_path: Path) -> None:
        """Test safe write with backup creation."""
        test_file = tmp_path / "test.txt"
        original_content = "original content"
        new_content = "new content"

        test_file.write_text(original_content)

        result = self.file_manager.flext_cli_safe_write(
            new_content,
            str(test_file),
            backup=True,
        )

        assert result.success
        assert result.data == str(test_file)

        # Verify new content
        assert test_file.read_text() == new_content

        # Verify backup exists
        backup_file = test_file.with_suffix(test_file.suffix + ".bak")
        assert backup_file.exists()
        assert backup_file.read_text() == original_content

    def test_flext_cli_safe_write_create_directories(self, tmp_path: Path) -> None:
        """Test safe write with directory creation."""
        nested_file = tmp_path / "level1" / "level2" / "test.txt"
        content = "nested file content"

        result = self.file_manager.flext_cli_safe_write(
            content,
            str(nested_file),
            create_dirs=True,
        )

        assert result.success
        assert nested_file.exists()
        assert nested_file.read_text() == content


class TestAdvancedIntegrationPatterns:
    """Test suite for advanced integration patterns."""

    def test_combined_decorators_workflow(self) -> None:
        """Test combining multiple decorators for maximum boilerplate reduction."""

        @flext_cli_auto_retry(max_attempts=2, delay=0.1)
        @flext_cli_with_progress("Processing critical data...")
        @flext_cli_zero_config(
            "critical operation",
            dangerous=True,
            validate_inputs={"email": "email"},
        )
        def critical_operation(email: str) -> FlextResult[str]:
            return FlextResult.ok(f"Critical operation completed for {email}")

        # Mock confirmation
        with patch("flext_cli.core.mixins.FlextCliHelper") as mock_helper_class:
            mock_helper = mock_helper_class.return_value
            mock_helper.flext_cli_confirm.return_value = FlextResult.ok(True)

            result = critical_operation(email="REDACTED_LDAP_BIND_PASSWORD@example.com")

        assert result.success
        assert "REDACTED_LDAP_BIND_PASSWORD@example.com" in result.data

    def test_mixin_and_decorator_integration(self) -> None:
        """Test integration of advanced mixin with decorators."""

        class AdvancedProcessor(FlextCliAdvancedMixin):
            @flext_cli_zero_config(
                "process user batch",
                validate_inputs={"count": "int"},
            )
            def process_user_batch(
                self,
                users: list[str],
                count: int,
            ) -> FlextResult[dict]:
                workflow_steps = [
                    (
                        "validate_users",
                        lambda data: self._validate_users(data["users"]),
                    ),
                    ("process_batch", lambda data: self._process_batch(data, count)),
                    ("generate_report", self._generate_report),
                ]

                return self.flext_cli_process_data_workflow(
                    {"users": users},
                    workflow_steps,
                )

            def _validate_users(self, users: list[str]) -> FlextResult[dict[str, Any]]:
                if not users:
                    return FlextResult.fail("No users provided")
                return FlextResult.ok({"users": users, "validated": True})

            def _process_batch(
                self,
                data: dict[str, Any],
                count: int,
            ) -> FlextResult[dict[str, Any]]:
                processed = data["users"][:count]  # Limit by count
                return FlextResult.ok({**data, "processed": processed})

            def _generate_report(
                self,
                data: dict[str, Any],
            ) -> FlextResult[dict[str, Any]]:
                report = {
                    "total_users": len(data["users"]),
                    "processed_users": len(data["processed"]),
                    "success": True,
                }
                return FlextResult.ok({**data, "report": report})

        processor = AdvancedProcessor()

        # Mock confirmation for zero-config decorator
        with patch("flext_cli.core.mixins.FlextCliHelper") as mock_helper_class:
            mock_helper = mock_helper_class.return_value
            mock_helper.flext_cli_confirm.return_value = FlextResult.ok(True)

            result = processor.process_user_batch(
                ["user1@example.com", "user2@example.com", "user3@example.com"],
                count=2,
            )

        assert result.success
        assert result.data["report"]["total_users"] == 3
        assert result.data["report"]["processed_users"] == 2


if __name__ == "__main__":
    pytest.main([__file__])
