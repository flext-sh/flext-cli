"""FLEXT CLI Context Tests - Comprehensive test coverage for FlextCliContext.

Tests all context functionality with real implementations and comprehensive coverage.
"""

from __future__ import annotations

import json

import pytest

from flext_cli.context import FlextCliContext
from flext_core import FlextResult
from flext_tests import FlextTestsUtilities


class TestFlextCliContext:
    """Comprehensive tests for FlextCliContext functionality."""

    @pytest.fixture
    def context(self) -> FlextCliContext:
        """Create FlextCliContext instance for testing."""
        return FlextCliContext()

    @pytest.fixture
    def test_utilities(self) -> FlextTestsUtilities:
        """Provide FlextTestsUtilities for test support."""
        return FlextTestsUtilities()

    def test_context_initialization(self, context: FlextCliContext) -> None:
        """Test context initialization and basic properties."""
        assert isinstance(context, FlextCliContext)
        assert hasattr(context, "_timeout_seconds")
        assert hasattr(context, "_config")

    def test_context_execute(self, context: FlextCliContext) -> None:
        """Test context execute method."""
        result = context.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), dict)

    def test_context_execute_operation(self, context: FlextCliContext) -> None:
        """Test context execute method (now sync, delegates to execute)."""
        result = context.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_context_timeout_seconds(self, context: FlextCliContext) -> None:
        """Test context timeout seconds property."""
        timeout = context.timeout_seconds
        assert isinstance(timeout, int)
        assert timeout > 0

    def test_context_set_timeout(self, context: FlextCliContext) -> None:
        """Test context timeout setting."""
        # Test with different timeout values
        test_timeouts = [10, 30, 60, 120]

        for timeout in test_timeouts:
            context.timeout_seconds = timeout
            assert context.timeout_seconds == timeout

    def test_context_to_dict(self, context: FlextCliContext) -> None:
        """Test context to_dict functionality."""
        data = context.to_dict()

        assert isinstance(data, dict)
        assert "timeout_seconds" in data
        assert isinstance(data["timeout_seconds"], int)

    def test_context_to_dict_json(self, context: FlextCliContext) -> None:
        """Test context to_dict JSON functionality."""
        data = context.to_dict()
        json_data = json.dumps(data)

        assert isinstance(json_data, str)
        assert "timeout_seconds" in json_data

    def test_context_validation(self, context: FlextCliContext) -> None:
        """Test context validation functionality."""
        # Test valid timeout values
        valid_timeouts = [1, 30, 60, 300]

        for timeout in valid_timeouts:
            context.timeout_seconds = timeout
            # Should not raise any exceptions
            _ = context.timeout_seconds

    def test_context_real_functionality(self, context: FlextCliContext) -> None:
        """Test context real functionality with comprehensive scenarios."""
        # Test basic execution
        result = context.execute()
        assert result.is_success

        # Test with different configurations
        context.timeout_seconds = 15
        result = context.execute()
        assert result.is_success

        # Test serialization
        data = context.to_dict()
        assert "timeout_seconds" in data
        assert data["timeout_seconds"] == 15

    def test_context_integration_workflow(self, context: FlextCliContext) -> None:
        """Test context integration workflow."""
        # 1. Initialize context
        assert isinstance(context, FlextCliContext)

        # 2. Configure timeout
        context.timeout_seconds = 45

        # 3. Execute context operations
        result = context.execute()
        assert result.is_success

        # 4. Verify configuration persistence
        assert context.timeout_seconds == 45

        # 5. Test serialization
        data = context.to_dict()
        assert data["timeout_seconds"] == 45

    def test_context_edge_cases(self, context: FlextCliContext) -> None:
        """Test context edge cases and error handling."""
        # Test with minimum timeout
        context.timeout_seconds = 1
        assert context.timeout_seconds == 1

        # Test with large timeout
        context.timeout_seconds = 3600
        assert context.timeout_seconds == 3600

        # Test to_dict with edge values
        data = context.to_dict()
        assert data["timeout_seconds"] == 3600

    # ========================================================================
    # Property and method tests for FlextCliContext
    # ========================================================================

    def test_context_command_property(self, context: FlextCliContext) -> None:
        """Test command property."""
        command = context.command
        # Can be None or str
        assert command is None or isinstance(command, str)

    def test_context_arguments_property(self, context: FlextCliContext) -> None:
        """Test arguments property."""
        arguments = context.arguments
        assert isinstance(arguments, list)

    def test_context_environment_variables_property(
        self, context: FlextCliContext
    ) -> None:
        """Test environment_variables property."""
        env_vars = context.environment_variables
        assert isinstance(env_vars, dict)

    def test_context_working_directory_property(self, context: FlextCliContext) -> None:
        """Test working_directory property."""
        working_dir = context.working_directory
        # Can be None or str
        assert working_dir is None or isinstance(working_dir, str)

    def test_context_is_active_property(self, context: FlextCliContext) -> None:
        """Test is_active property."""
        is_active = context.is_active
        assert isinstance(is_active, bool)

    def test_context_activate_method(self, context: FlextCliContext) -> None:
        """Test activate method."""
        result = context.activate()
        assert result.is_success

    def test_context_deactivate_method(self, context: FlextCliContext) -> None:
        """Test deactivate method."""
        # Activate first, then deactivate
        context.activate()
        result = context.deactivate()
        assert result.is_success

    def test_context_get_environment_variable(self, context: FlextCliContext) -> None:
        """Test get_environment_variable method."""
        # Set an environment variable first
        context.set_environment_variable("TEST_VAR", "test_value")

        # Get the variable
        result = context.get_environment_variable("TEST_VAR")
        assert result.is_success
        assert result.unwrap() == "test_value"

    def test_context_get_environment_variable_not_found(
        self, context: FlextCliContext
    ) -> None:
        """Test get_environment_variable with non-existent variable."""
        result = context.get_environment_variable("NON_EXISTENT_VAR")
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None and "not found" in result.error.lower()

    def test_context_set_environment_variable(self, context: FlextCliContext) -> None:
        """Test set_environment_variable method."""
        result = context.set_environment_variable("NEW_VAR", "new_value")
        assert result.is_success

        # Verify it was set
        get_result = context.get_environment_variable("NEW_VAR")
        assert get_result.is_success
        assert get_result.unwrap() == "new_value"

    def test_context_add_argument(self, context: FlextCliContext) -> None:
        """Test add_argument method."""
        result = context.add_argument("--test-arg")
        assert result.is_success

        # Verify it was added
        arguments = context.arguments
        assert "--test-arg" in arguments

    def test_context_remove_argument(self, context: FlextCliContext) -> None:
        """Test remove_argument method."""
        # Add an argument first
        context.add_argument("--remove-me")

        # Remove it
        result = context.remove_argument("--remove-me")
        assert result.is_success

        # Verify it was removed
        arguments = context.arguments
        assert "--remove-me" not in arguments

    def test_context_remove_argument_not_found(self, context: FlextCliContext) -> None:
        """Test remove_argument with non-existent argument."""
        result = context.remove_argument("non_existent_arg")
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None and "not found" in result.error.lower()

    def test_context_set_metadata(self, context: FlextCliContext) -> None:
        """Test set_metadata method."""
        result = context.set_metadata("test_key", "test_value")
        assert result.is_success

    def test_context_get_metadata(self, context: FlextCliContext) -> None:
        """Test get_metadata method."""
        # Set metadata first
        context.set_metadata("meta_key", "meta_value")

        # Get it back
        result = context.get_metadata("meta_key")
        assert result.is_success
        assert result.unwrap() == "meta_value"

    def test_context_get_metadata_not_found(self, context: FlextCliContext) -> None:
        """Test get_metadata with non-existent key."""
        result = context.get_metadata("non_existent_key")
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None and "not found" in result.error.lower()

    def test_context_get_context_summary(self, context: FlextCliContext) -> None:
        """Test get_context_summary method."""
        result = context.get_context_summary()
        assert result.is_success
        summary = result.unwrap()
        assert isinstance(summary, dict)
        assert "command" in summary
        assert "arguments" in summary or "arguments_count" in summary

    def test_context_print_error(self, context: FlextCliContext) -> None:
        """Test print_error method."""
        # Should not raise exception
        context.print_error("Test error message")

    def test_context_print_info(self, context: FlextCliContext) -> None:
        """Test print_info method."""
        # Should not raise exception
        context.print_info("Test info message")

    def test_context_print_success(self, context: FlextCliContext) -> None:
        """Test print_success method."""
        # Should not raise exception
        context.print_success("Test success message")

    def test_context_print_warning(self, context: FlextCliContext) -> None:
        """Test print_warning method."""
        # Should not raise exception
        context.print_warning("Test warning message")
