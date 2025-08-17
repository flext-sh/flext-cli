"""Tests for FlextCli Mixins and Decorators.

This module provides comprehensive tests for FlextCli mixin classes that
provide boilerplate reduction patterns and decorator functionality.

Test Coverage:
    - FlextCli validation, interactive, progress, and result mixins
    - Decorator functions for automatic validation and error handling
    - Batch operation utilities and progress tracking
    - Error handling and edge cases

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from flext_core import FlextResult
from rich.console import Console
from rich.progress import Progress

from flext_cli import (
    FlextCliConfigMixin,
    FlextCliInteractiveMixin,
    FlextCliMixin,
    FlextCliProgressMixin,
    FlextCliResultMixin,
    FlextCliValidationMixin,
    flext_cli_auto_validate,
    flext_cli_handle_exceptions,
    flext_cli_require_confirmation,
)


class TestFlextCliValidationMixin:
    """Test suite for FlextCliValidationMixin."""

    class TestClass(FlextCliValidationMixin):
      """Test class using validation mixin."""

      def __init__(self) -> None:
          super().__init__()

    def setup_method(self) -> None:
      """Setup test environment."""
      self.test_instance = self.TestClass()

    def test_flext_cli_validate_inputs_success(self) -> None:
      """Test successful input validation."""
      inputs = {
          "email": ("user@example.com", "email"),
          "url": ("https://api.flext.sh", "url"),
      }

      result = self.test_instance.flext_cli_validate_inputs(inputs)

      assert result.success
      assert "email" in result.data
      assert "url" in result.data
      assert result.data["email"] == "user@example.com"

    def test_flext_cli_validate_inputs_failure(self) -> None:
      """Test input validation with failure."""
      inputs = {
          "email": ("invalid-email", "email"),
          "url": ("https://api.flext.sh", "url"),
      }

      result = self.test_instance.flext_cli_validate_inputs(inputs)

      assert not result.success
      assert "Validation failed for email" in result.error

    def test_flext_cli_validate_inputs_unknown_type(self) -> None:
      """Test input validation with unknown type."""
      inputs = {
          "test": ("value", "unknown_type"),
      }

      result = self.test_instance.flext_cli_validate_inputs(inputs)

      assert not result.success
      assert "Unknown validation type" in result.error

    def test_flext_cli_validate_inputs_file_path(self, tmp_path: Path) -> None:
      """Test file path validation in inputs."""
      test_file = tmp_path / "test.txt"
      test_file.write_text("content")

      inputs = {
          "config_file": (str(test_file), "file"),
      }

      result = self.test_instance.flext_cli_validate_inputs(inputs)

      assert result.success
      assert isinstance(result.data["config_file"], Path)

    def test_flext_cli_require_confirmation_success(self) -> None:
      """Test successful confirmation requirement."""
      with patch.object(self.test_instance, "_helper") as mock_helper:
          mock_helper.flext_cli_confirm.return_value = FlextResult.ok(True)

          result = self.test_instance.flext_cli_require_confirmation("test operation")

          assert result.success
          assert result.data is True

    def test_flext_cli_require_confirmation_denied(self) -> None:
      """Test denied confirmation requirement."""
      with patch.object(self.test_instance, "_helper") as mock_helper:
          mock_helper.flext_cli_confirm.return_value = FlextResult.ok(False)

          result = self.test_instance.flext_cli_require_confirmation("test operation")

          assert not result.success
          assert "Operation cancelled by user" in result.error

    def test_flext_cli_require_confirmation_dangerous(self) -> None:
      """Test dangerous operation confirmation."""
      with patch.object(self.test_instance, "_helper") as mock_helper:
          mock_helper.flext_cli_confirm.return_value = FlextResult.ok(True)

          result = self.test_instance.flext_cli_require_confirmation(
              "delete data",
              dangerous=True,
          )

          assert result.success
          # Verify dangerous styling was applied
          mock_helper.flext_cli_confirm.assert_called_once()
          call_args = mock_helper.flext_cli_confirm.call_args[0]
          assert "[bold red]" in call_args[0]


class TestFlextCliInteractiveMixin:
    """Test suite for FlextCliInteractiveMixin."""

    class TestClass(FlextCliInteractiveMixin):
      """Test class using interactive mixin."""

      def __init__(self) -> None:
          super().__init__()

    def setup_method(self) -> None:
      """Setup test environment."""
      self.test_instance = self.TestClass()
      self.console_mock = MagicMock(spec=Console)
      self.test_instance._flext_cli_console = self.console_mock

    def test_console_property_lazy_loading(self) -> None:
      """Test lazy loading of console property."""
      test_instance = self.TestClass()
      # Console should be created on first access
      console = test_instance.console
      assert isinstance(console, Console)
      # Same instance should be returned on subsequent calls
      assert test_instance.console is console

    def test_flext_cli_print_success(self) -> None:
      """Test success message printing."""
      self.test_instance.flext_cli_print_success("Operation completed")

      self.console_mock.print.assert_called_once()
      args = self.console_mock.print.call_args[0]
      assert "✓" in args[0]
      assert "Operation completed" in args[0]

    def test_flext_cli_print_error(self) -> None:
      """Test error message printing."""
      self.test_instance.flext_cli_print_error("Operation failed")

      self.console_mock.print.assert_called_once()
      args = self.console_mock.print.call_args[0]
      assert "✗" in args[0]
      assert "Operation failed" in args[0]

    def test_flext_cli_print_warning(self) -> None:
      """Test warning message printing."""
      self.test_instance.flext_cli_print_warning("Be careful")

      self.console_mock.print.assert_called_once()
      args = self.console_mock.print.call_args[0]
      assert "⚠" in args[0]
      assert "Be careful" in args[0]

    def test_flext_cli_print_info(self) -> None:
      """Test info message printing."""
      self.test_instance.flext_cli_print_info("Information")

      self.console_mock.print.assert_called_once()
      args = self.console_mock.print.call_args[0]
      assert "i" in args[0]
      assert "Information" in args[0]

    def test_flext_cli_print_result_success(self) -> None:
      """Test printing successful FlextResult."""
      result = FlextResult.ok("Success data")

      self.test_instance.flext_cli_print_result(result)

      self.console_mock.print.assert_called_once()
      args = self.console_mock.print.call_args[0]
      assert "✓" in args[0]
      assert "Success data" in args[0]

    def test_flext_cli_print_result_failure(self) -> None:
      """Test printing failed FlextResult."""
      result = FlextResult.fail("Error message")

      self.test_instance.flext_cli_print_result(result)

      self.console_mock.print.assert_called_once()
      args = self.console_mock.print.call_args[0]
      assert "✗" in args[0]
      assert "Error message" in args[0]

    @patch("flext_cli.core.helpers.FlextCliHelper")
    def test_flext_cli_confirm_operation_success(
      self,
      mock_helper_class: MagicMock,
    ) -> None:
      """Test successful operation confirmation."""
      mock_helper = mock_helper_class.return_value
      mock_helper.flext_cli_confirm.return_value = FlextResult.ok(True)

      result = self.test_instance.flext_cli_confirm_operation("test operation")

      assert result is True

    @patch("flext_cli.core.helpers.FlextCliHelper")
    def test_flext_cli_confirm_operation_denied(
      self,
      mock_helper_class: MagicMock,
    ) -> None:
      """Test denied operation confirmation."""
      mock_helper = mock_helper_class.return_value
      mock_helper.flext_cli_confirm.return_value = FlextResult.ok(False)

      result = self.test_instance.flext_cli_confirm_operation("test operation")

      assert result is False

    @patch("flext_cli.core.helpers.FlextCliHelper")
    def test_flext_cli_confirm_operation_error(
      self,
      mock_helper_class: MagicMock,
    ) -> None:
      """Test operation confirmation with error."""
      mock_helper = mock_helper_class.return_value
      mock_helper.flext_cli_confirm.return_value = FlextResult.fail(
          "Confirmation failed",
      )

      result = self.test_instance.flext_cli_confirm_operation("test operation")

      assert result is False
      # Should print error message
      self.console_mock.print.assert_called()


class TestFlextCliProgressMixin:
    """Test suite for FlextCliProgressMixin."""

    class TestClass(FlextCliProgressMixin):
      """Test class using progress mixin."""

      def __init__(self) -> None:
          super().__init__()

    def setup_method(self) -> None:
      """Setup test environment."""
      self.test_instance = self.TestClass()
      self.console_mock = MagicMock(spec=Console)
      self.test_instance._flext_cli_console = self.console_mock

    @patch("flext_cli.core.mixins.track")
    def test_flext_cli_track_progress(self, mock_track: MagicMock) -> None:
      """Test progress tracking for iterables."""
      test_items = [1, 2, 3, 4, 5]
      mock_track.return_value = test_items

      result = self.test_instance.flext_cli_track_progress(
          test_items,
          "Processing items",
      )

      assert result == test_items
      mock_track.assert_called_once_with(
          test_items,
          description="Processing items",
          console=self.console_mock,
      )

    def test_flext_cli_with_progress(self) -> None:
      """Test progress context manager creation."""
      progress = self.test_instance.flext_cli_with_progress(100, "Test progress")

      # Should return a Progress object

      assert isinstance(progress, Progress)


class TestFlextCliResultMixin:
    """Test suite for FlextCliResultMixin."""

    class TestClass(FlextCliResultMixin):
      """Test class using result mixin."""

      def __init__(self) -> None:
          super().__init__()

    def setup_method(self) -> None:
      """Setup test environment."""
      self.test_instance = self.TestClass()

    def test_flext_cli_chain_results_success(self) -> None:
      """Test successful result chaining."""
      operations = [
          lambda: FlextResult.ok("result1"),
          lambda: FlextResult.ok("result2"),
          lambda: FlextResult.ok("result3"),
      ]

      result = self.test_instance.flext_cli_chain_results(*operations)

      assert result.success
      assert result.data == ["result1", "result2", "result3"]

    def test_flext_cli_chain_results_failure(self) -> None:
      """Test result chaining with failure."""
      operations = [
          lambda: FlextResult.ok("result1"),
          lambda: FlextResult.fail("operation failed"),
          lambda: FlextResult.ok("result3"),  # Should not execute
      ]

      result = self.test_instance.flext_cli_chain_results(*operations)

      assert not result.success
      assert "operation failed" in result.error

    def test_flext_cli_chain_results_exception(self) -> None:
      """Test result chaining with exception."""

      def failing_operation() -> FlextResult[str]:
          msg = "Operation exception"
          raise ValueError(msg)

      operations = [
          lambda: FlextResult.ok("result1"),
          failing_operation,
      ]

      result = self.test_instance.flext_cli_chain_results(*operations)

      assert not result.success
      assert "Operation failed" in result.error
      assert "Operation exception" in result.error

    def test_flext_cli_handle_result_success_with_action(self) -> None:
      """Test result handling with success action."""
      success_action = MagicMock()
      result = FlextResult.ok("success_data")

      data = self.test_instance.flext_cli_handle_result(
          result,
          success_action=success_action,
      )

      assert data == "success_data"
      success_action.assert_called_once_with("success_data")

    def test_flext_cli_handle_result_failure_with_action(self) -> None:
      """Test result handling with error action."""
      error_action = MagicMock()
      result = FlextResult.fail("error_message")

      data = self.test_instance.flext_cli_handle_result(
          result,
          error_action=error_action,
      )

      assert data is None
      error_action.assert_called_once_with("error_message")

    def test_flext_cli_handle_result_no_actions(self) -> None:
      """Test result handling without actions."""
      success_result = FlextResult.ok("success_data")
      failure_result = FlextResult.fail("error_message")

      success_data = self.test_instance.flext_cli_handle_result(success_result)
      failure_data = self.test_instance.flext_cli_handle_result(failure_result)

      assert success_data == "success_data"
      assert failure_data is None


class TestFlextCliConfigMixin:
    """Test suite for FlextCliConfigMixin."""

    class TestClass(FlextCliConfigMixin):
      """Test class using config mixin."""

      def __init__(self) -> None:
          super().__init__()

    def setup_method(self) -> None:
      """Setup test environment."""
      self.test_instance = self.TestClass()

    @patch("flext_cli.config_hierarchical.create_default_hierarchy")
    def test_flext_cli_load_config_success(
      self,
      mock_create_hierarchy: MagicMock,
    ) -> None:
      """Test successful config loading."""
      mock_config = {"profile": "test", "debug": True}
      mock_create_hierarchy.return_value = FlextResult.ok(mock_config)

      result = self.test_instance.flext_cli_load_config()

      assert result.success
      assert result.data == mock_config
      assert self.test_instance.config == mock_config

    @patch("flext_cli.config_hierarchical.create_default_hierarchy")
    def test_flext_cli_load_config_with_path(
      self,
      mock_create_hierarchy: MagicMock,
    ) -> None:
      """Test config loading with specific path."""
      config_path = "/path/to/config.yml"
      mock_config = {"profile": "custom"}
      mock_create_hierarchy.return_value = FlextResult.ok(mock_config)

      result = self.test_instance.flext_cli_load_config(config_path)

      assert result.success
      mock_create_hierarchy.assert_called_once_with(config_path=config_path)

    @patch("flext_cli.config_hierarchical.create_default_hierarchy")
    def test_flext_cli_load_config_failure(
      self,
      mock_create_hierarchy: MagicMock,
    ) -> None:
      """Test config loading failure."""
      mock_create_hierarchy.return_value = FlextResult.fail("Config not found")

      result = self.test_instance.flext_cli_load_config()

      assert not result.success
      assert "Config loading failed" in result.error


class TestFlextCliMixin:
    """Test suite for combined FlextCliMixin."""

    class TestClass(FlextCliMixin):
      """Test class using combined mixin."""

      def __init__(self) -> None:
          super().__init__()

    def setup_method(self) -> None:
      """Setup test environment."""
      self.test_instance = self.TestClass()

    def test_combined_mixin_functionality(self) -> None:
      """Test that combined mixin has all expected methods."""
      # Should have methods from all mixins
      assert hasattr(self.test_instance, "flext_cli_validate_inputs")
      assert hasattr(self.test_instance, "flext_cli_print_success")
      assert hasattr(self.test_instance, "flext_cli_track_progress")
      assert hasattr(self.test_instance, "flext_cli_chain_results")
      assert hasattr(self.test_instance, "flext_cli_load_config")


class TestFlextCliDecorators:
    """Test suite for FlextCli decorators."""

    def test_flext_cli_auto_validate_success(self) -> None:
      """Test auto validation decorator with valid inputs."""

      @flext_cli_auto_validate(email="email", url="url")
      def test_function(email: str, url: str) -> FlextResult[str]:
          return FlextResult.ok(f"Processing {email} and {url}")

      result = test_function(email="user@example.com", url="https://api.flext.sh")

      assert result.success
      assert "user@example.com" in result.data
      assert "https://api.flext.sh" in result.data

    def test_flext_cli_auto_validate_failure(self) -> None:
      """Test auto validation decorator with invalid inputs."""

      @flext_cli_auto_validate(email="email")
      def test_function(email: str) -> FlextResult[str]:  # noqa: ARG001
          return FlextResult.ok("Success")

      result = test_function(email="invalid-email")

      assert not result.success
      assert "Validation failed for email" in result.error

    def test_flext_cli_handle_exceptions_success(self) -> None:
      """Test exception handling decorator with successful execution."""

      @flext_cli_handle_exceptions("Test operation failed")
      def test_function() -> FlextResult[str]:
          return FlextResult.ok("Success")

      result = test_function()

      assert result.success
      assert result.data == "Success"

    def test_flext_cli_handle_exceptions_with_exception(self) -> None:
      """Test exception handling decorator with raised exception."""

      @flext_cli_handle_exceptions("Test operation failed")
      def test_function() -> FlextResult[str]:
          msg = "Something went wrong"
          raise ValueError(msg)

      result = test_function()

      assert not result.success
      assert "Test operation failed" in result.error
      assert "Something went wrong" in result.error

    def test_flext_cli_handle_exceptions_non_flextresult(self) -> None:
      """Test exception handling decorator with non-FlextResult return."""

      @flext_cli_handle_exceptions("Test operation failed")
      def test_function() -> str:
          return "Plain string result"

      result = test_function()

      assert result.success
      assert result.data == "Plain string result"

    @patch("flext_cli.core.helpers.FlextCliHelper")
    def test_flext_cli_require_confirmation_confirmed(
      self,
      mock_helper_class: MagicMock,
    ) -> None:
      """Test confirmation decorator with user confirmation."""
      mock_helper = mock_helper_class.return_value
      mock_helper.flext_cli_confirm.return_value = FlextResult.ok(True)

      @flext_cli_require_confirmation("Delete data")
      def test_function() -> FlextResult[str]:
          return FlextResult.ok("Data deleted")

      result = test_function()

      assert result.success
      assert result.data == "Data deleted"

    @patch("flext_cli.core.helpers.FlextCliHelper")
    def test_flext_cli_require_confirmation_denied(
      self,
      mock_helper_class: MagicMock,
    ) -> None:
      """Test confirmation decorator with user denial."""
      mock_helper = mock_helper_class.return_value
      mock_helper.flext_cli_confirm.return_value = FlextResult.ok(False)

      @flext_cli_require_confirmation("Delete data")
      def test_function() -> FlextResult[str]:
          return FlextResult.ok("Data deleted")

      result = test_function()

      assert result.success
      assert "Operation cancelled by user" in result.data


if __name__ == "__main__":
    pytest.main([__file__])
