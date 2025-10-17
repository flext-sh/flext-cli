"""Tests for FlextCliContext - CLI execution context management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import cast

from flext_core import FlextResult

from flext_cli.context import FlextCliContext


class TestFlextCliContext:
    """Test suite for FlextCliContext service."""

    # ========================================================================
    # INITIALIZATION AND BASIC FUNCTIONALITY
    # ========================================================================

    def test_context_service_initialization(self) -> None:
        """Test context service initialization."""
        context = FlextCliContext()
        assert context is not None
        assert hasattr(context, "logger")
        assert hasattr(context, "container")  # Property from FlextService
        assert hasattr(context, "command")  # Direct attribute access
        assert hasattr(context, "arguments")  # Direct attribute access

    def test_context_service_execute_method(self) -> None:
        """Test context service execute method."""
        context = FlextCliContext()
        result = context.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, dict)

    # ========================================================================
    # CREATE CONTEXT
    # ========================================================================

    def test_create_context_minimal(self) -> None:
        """Test creating context with minimal parameters."""
        context = FlextCliContext()

        assert isinstance(context, FlextCliContext)
        assert context.command is None
        assert context.arguments == []
        assert context.is_active is False

    def test_create_context_with_command(self) -> None:
        """Test creating context with command."""
        context = FlextCliContext(command="test_command")

        assert isinstance(context, FlextCliContext)
        assert context.command == "test_command"

    def test_create_context_with_arguments(self) -> None:
        """Test creating context with arguments."""
        context = FlextCliContext(command="test", arguments=["arg1", "arg2"])

        assert isinstance(context, FlextCliContext)
        assert context.command == "test"
        assert context.arguments == ["arg1", "arg2"]

    def test_create_context_with_environment(self) -> None:
        """Test creating context with environment variables."""
        env = cast("dict[str, object]", {"KEY": "value", "DEBUG": "true"})
        context = FlextCliContext(environment_variables=env)

        assert isinstance(context, FlextCliContext)
        assert context.environment_variables == env

    def test_validate_context_success(self) -> None:
        """Test that a valid context can be created."""
        context = FlextCliContext(command="test")

        assert isinstance(context, FlextCliContext)
        assert context.command == "test"
        # Validation is automatic via Pydantic in the constructor

    # ========================================================================
    # CONTEXT OPERATIONS
    # ========================================================================

    def test_context_activate_deactivate(self) -> None:
        """Test context activation and deactivation."""
        context = FlextCliContext()

        # Initially not active
        assert not context.is_active

        # Activate
        result = context.activate()
        assert result.is_success
        assert context.is_active

        # Try to activate again - should fail
        result = context.activate()
        assert not result.is_success

        # Deactivate
        result = context.deactivate()
        assert result.is_success
        assert not context.is_active

        # Try to deactivate again - should fail
        result = context.deactivate()
        assert not result.is_success

    def test_context_environment_variables(self) -> None:
        """Test environment variable operations."""
        context = FlextCliContext()

        # Initially empty
        result = context.get_environment_variable("TEST_KEY")
        assert not result.is_success

        # Set a variable
        result = context.set_environment_variable("TEST_KEY", "test_value")
        assert result.is_success

        # Get the variable
        result = context.get_environment_variable("TEST_KEY")
        assert result.is_success
        assert result.unwrap() == "test_value"

    def test_context_arguments(self) -> None:
        """Test argument operations."""
        context = FlextCliContext()

        # Initially empty
        assert context.arguments == []

        # Add arguments
        result = context.add_argument("arg1")
        assert result.is_success
        assert context.arguments == ["arg1"]

        result = context.add_argument("arg2")
        assert result.is_success
        assert context.arguments == ["arg1", "arg2"]

        # Remove argument
        result = context.remove_argument("arg1")
        assert result.is_success
        assert context.arguments == ["arg2"]

        # Try to remove non-existent argument
        result = context.remove_argument("nonexistent")
        assert not result.is_success

    def test_context_metadata(self) -> None:
        """Test metadata operations."""
        context = FlextCliContext()

        # Set metadata
        result = context.set_metadata("key1", "value1")
        assert result.is_success

        result = context.set_metadata("key2", {"nested": "data"})
        assert result.is_success

        # Get metadata
        result = context.get_metadata("key1")
        assert result.is_success
        assert result.unwrap() == "value1"

        result = context.get_metadata("key2")
        assert result.is_success
        assert result.unwrap() == {"nested": "data"}

        # Get non-existent metadata
        result = context.get_metadata("nonexistent")
        assert not result.is_success

    def test_context_summary(self) -> None:
        """Test context summary generation."""
        context = FlextCliContext(
            command="test_cmd", arguments=["arg1", "arg2"], working_directory="/tmp"
        )

        result = context.get_context_summary()
        assert result.is_success

        summary = result.unwrap()
        assert summary["command"] == "test_cmd"
        assert summary["arguments"] == ["arg1", "arg2"]
        assert summary["arguments_count"] == 2
        assert summary["working_directory"] == "/tmp"
        assert not summary["is_active"]

    def test_context_to_dict(self) -> None:
        """Test context serialization to dict."""
        context = FlextCliContext(
            command="test_cmd", arguments=["arg1"], working_directory="/tmp"
        )

        result = context.to_dict()
        assert isinstance(result, dict)
        assert result["command"] == "test_cmd"
        assert result["arguments"] == ["arg1"]
        assert result["working_directory"] == "/tmp"
        assert "timeout_seconds" in result

    # ========================================================================
    # ERROR HANDLING AND EDGE CASES
    # ========================================================================

    def test_get_environment_variable_invalid_name(self) -> None:
        """Test get_environment_variable with invalid name (line 124)."""
        context = FlextCliContext()

        # Test with empty string
        result = context.get_environment_variable("")
        assert result.is_failure
        assert "must be a non-empty string" in str(result.error).lower()

        # Test with None - this will cause type error but should be handled
        try:
            result = context.get_environment_variable(None)  # type: ignore
            assert result.is_failure
        except TypeError:
            pass  # Expected for None input

        # Test with non-string - this will cause type error but should be handled
        try:
            result = context.get_environment_variable(123)  # type: ignore
            assert result.is_failure
        except TypeError:
            pass  # Expected for non-string input

    def test_set_environment_variable_invalid_inputs(self) -> None:
        """Test set_environment_variable with invalid inputs (lines 147, 152)."""
        context = FlextCliContext()

        # Test with empty name
        result = context.set_environment_variable("", "value")
        assert result.is_failure
        assert "must be a non-empty string" in str(result.error).lower()

        # Test with None name
        try:
            result = context.set_environment_variable(None, "value")  # type: ignore
            assert result.is_failure
        except TypeError:
            pass  # Expected for None input

        # Test with non-string name
        try:
            result = context.set_environment_variable(123, "value")  # type: ignore
            assert result.is_failure
        except TypeError:
            pass  # Expected for non-string input

        # Test with non-string value
        result = context.set_environment_variable("TEST", 123)  # type: ignore
        assert result.is_failure
        assert "must be a string" in str(result.error).lower()

        # Test with None value
        result = context.set_environment_variable("TEST", None)  # type: ignore
        assert result.is_failure
        assert "must be a string" in str(result.error).lower()

    def test_add_argument_invalid_input(self) -> None:
        """Test add_argument with invalid input (line 169)."""
        context = FlextCliContext()

        # Test with empty string
        result = context.add_argument("")
        assert result.is_failure
        assert "must be a non-empty string" in str(result.error).lower()

        # Test with None
        try:
            result = context.add_argument(None)  # type: ignore
            assert result.is_failure
        except TypeError:
            pass  # Expected for None input

        # Test with non-string
        try:
            result = context.add_argument(123)  # type: ignore
            assert result.is_failure
        except TypeError:
            pass  # Expected for non-string input

    def test_remove_argument_invalid_input(self) -> None:
        """Test remove_argument with invalid input (line 186)."""
        context = FlextCliContext()

        # Test with empty string
        result = context.remove_argument("")
        assert result.is_failure
        assert "must be a non-empty string" in str(result.error).lower()

        # Test with None
        try:
            result = context.remove_argument(None)  # type: ignore
            assert result.is_failure
        except TypeError:
            pass  # Expected for None input

        # Test with non-string
        try:
            result = context.remove_argument(123)  # type: ignore
            assert result.is_failure
        except TypeError:
            pass  # Expected for non-string input

    def test_set_metadata_invalid_key(self) -> None:
        """Test set_metadata with invalid key (line 209)."""
        context = FlextCliContext()

        # Test with empty string
        result = context.set_metadata("", "value")
        assert result.is_failure
        assert "must be a non-empty string" in str(result.error).lower()

        # Test with None
        try:
            result = context.set_metadata(None, "value")  # type: ignore
            assert result.is_failure
        except TypeError:
            pass  # Expected for None input

        # Test with non-string
        try:
            result = context.set_metadata(123, "value")  # type: ignore
            assert result.is_failure
        except TypeError:
            pass  # Expected for non-string input

    def test_get_metadata_invalid_key(self) -> None:
        """Test get_metadata with invalid key (line 226)."""
        context = FlextCliContext()

        # Test with empty string
        result = context.get_metadata("")
        assert result.is_failure
        assert "must be a non-empty string" in str(result.error).lower()

        # Test with None
        try:
            result = context.get_metadata(None)  # type: ignore
            assert result.is_failure
        except TypeError:
            pass  # Expected for None input

        # Test with non-string
        try:
            result = context.get_metadata(123)  # type: ignore
            assert result.is_failure
        except TypeError:
            pass  # Expected for non-string input

    def test_activate_exception_handling(self, monkeypatch) -> None:
        """Test activate method exception handling (lines 97-98)."""
        context = FlextCliContext()

        # Mock is_active property to raise exception when accessed
        def mock_is_active_get(self):
            raise RuntimeError("Mock exception")

        monkeypatch.setattr(type(context), 'is_active', property(mock_is_active_get))

        result = context.activate()
        assert result.is_failure
        assert "activation failed" in str(result.error).lower()

    def test_deactivate_exception_handling(self, monkeypatch) -> None:
        """Test deactivate method exception handling (lines 114-115)."""
        context = FlextCliContext()
        context.is_active = True  # Set as active first

        # Mock is_active property to raise exception when accessed
        def mock_is_active_get(self):
            raise RuntimeError("Mock exception")

        monkeypatch.setattr(type(context), 'is_active', property(mock_is_active_get))

        result = context.deactivate()
        assert result.is_failure
        assert "deactivation failed" in str(result.error).lower()

    def test_get_environment_variable_exception_handling(self, monkeypatch) -> None:
        """Test get_environment_variable exception handling (lines 137-138)."""
        context = FlextCliContext()

        # Mock environment_variables to raise exception when accessed
        def mock_getitem(self, key):
            raise RuntimeError("Mock exception")

        monkeypatch.setattr(type(context.environment_variables), '__getitem__', mock_getitem)

        # Set up environment variable so we get past the 'not in' check
        context.environment_variables = {"TEST": "value"}

        result = context.get_environment_variable("TEST")
        assert result.is_failure
        assert "retrieval failed" in str(result.error).lower()

    def test_set_environment_variable_exception_handling(self, monkeypatch) -> None:
        """Test set_environment_variable exception handling (lines 159-160)."""
        context = FlextCliContext()

        # Mock environment_variables __setitem__ to raise exception
        def mock_setitem(self, key, value):
            raise RuntimeError("Mock exception")

        monkeypatch.setattr(type(context.environment_variables), '__setitem__', mock_setitem)

        result = context.set_environment_variable("TEST", "value")
        assert result.is_failure
        assert "setting failed" in str(result.error).lower()

    def test_add_argument_exception_handling(self, monkeypatch) -> None:
        """Test add_argument exception handling (lines 176-177)."""
        context = FlextCliContext()

        # Mock arguments append to raise exception
        def mock_append(self, item):
            raise RuntimeError("Mock exception")

        monkeypatch.setattr(type(context.arguments), 'append', mock_append)

        result = context.add_argument("test_arg")
        assert result.is_failure
        assert "addition failed" in str(result.error).lower()

    def test_remove_argument_exception_handling(self, monkeypatch) -> None:
        """Test remove_argument exception handling (lines 199-200)."""
        context = FlextCliContext()
        context.arguments = ["test_arg"]

        # Mock arguments remove to raise exception
        def mock_remove(self, item):
            raise RuntimeError("Mock exception")

        monkeypatch.setattr(type(context.arguments), 'remove', mock_remove)

        result = context.remove_argument("test_arg")
        assert result.is_failure
        assert "removal failed" in str(result.error).lower()

    def test_set_metadata_exception_handling(self, monkeypatch) -> None:
        """Test set_metadata exception handling (lines 216-217)."""
        context = FlextCliContext()

        # Mock context_metadata __setitem__ to raise exception
        def mock_setitem(self, key, value):
            raise RuntimeError("Mock exception")

        monkeypatch.setattr(type(context.context_metadata), '__setitem__', mock_setitem)

        result = context.set_metadata("test_key", "test_value")
        assert result.is_failure
        assert "setting failed" in str(result.error).lower()

    def test_get_metadata_exception_handling(self, monkeypatch) -> None:
        """Test get_metadata exception handling (lines 238-239)."""
        context = FlextCliContext()

        # Mock context_metadata to raise exception when accessed
        def mock_getitem(self, key):
            raise RuntimeError("Mock exception")

        monkeypatch.setattr(type(context.context_metadata), '__getitem__', mock_getitem)

        # Set up metadata so we get past the 'not in' check
        context.context_metadata = {"test_key": "test_value"}

        result = context.get_metadata("test_key")
        assert result.is_failure
        assert "retrieval failed" in str(result.error).lower()

    def test_get_context_summary_exception_handling(self) -> None:
        """Test get_context_summary exception handling (lines 272-273)."""
        # Create a custom context class that raises exception when accessing attributes
        class FailingContext(FlextCliContext):
            @property
            def id(self) -> str:  # type: ignore
                raise RuntimeError("Mock exception accessing id")

        context = FailingContext()
        result = context.get_context_summary()
        assert result.is_failure
        assert "summary generation failed" in str(result.error).lower()

    def test_execute_exception_handling(self) -> None:
        """Test execute method exception handling (lines 291-292)."""
        # Create a custom context class that raises exception when accessing arguments
        class FailingContext(FlextCliContext):
            @property
            def arguments(self):  # type: ignore
                raise RuntimeError("Mock exception accessing arguments")

        context = FailingContext()
        result = context.execute()
        assert result.is_failure
        assert "execution failed" in str(result.error).lower()
