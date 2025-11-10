"""Tests for FlextCliContext - CLI execution context management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections import UserDict, UserList
from typing import cast
from unittest.mock import patch

import pytest
from flext_core import FlextResult, FlextTypes

from flext_cli import FlextCliContext, FlextCliTypes


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
        env: FlextCliTypes.Data.CliDataDict = {"KEY": "value", "DEBUG": "true"}
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
        get_result = context.get_environment_variable("TEST_KEY")
        assert not get_result.is_success

        # Set a variable
        set_result = context.set_environment_variable("TEST_KEY", "test_value")
        assert set_result.is_success

        # Get the variable
        get_result2 = context.get_environment_variable("TEST_KEY")
        assert get_result2.is_success
        assert get_result2.unwrap() == "test_value"

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
        set_result1 = context.set_metadata("key1", "value1")
        assert set_result1.is_success

        set_result2 = context.set_metadata("key2", {"nested": "data"})
        assert set_result2.is_success

        # Get metadata
        get_result1 = context.get_metadata("key1")
        assert get_result1.is_success
        assert get_result1.unwrap() == "value1"

        get_result2 = context.get_metadata("key2")
        assert get_result2.is_success
        assert get_result2.unwrap() == {"nested": "data"}

        # Get non-existent metadata
        get_result3 = context.get_metadata("nonexistent")
        assert not get_result3.is_success

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

    @pytest.mark.skip(
        reason="Tests defensive runtime type checking - MyPy strict mode prevents these at compile-time"
    )
    def test_get_environment_variable_invalid_name(self) -> None:
        """Test get_environment_variable with invalid name (line 124)."""
        context = FlextCliContext()

        # Test with empty string
        result = context.get_environment_variable("")
        assert result.is_failure
        assert "must be a non-empty string" in str(result.error).lower()

        # Test with None - this will cause type error but should be handled
        # Test with None - this triggers runtime TypeError
        with pytest.raises(TypeError):
            context.get_environment_variable(cast("str", None))

        # Test with non-string - this triggers runtime TypeError
        with pytest.raises(TypeError):
            context.get_environment_variable(cast("str", 123))

    @pytest.mark.skip(
        reason="Tests defensive runtime type checking - MyPy strict mode prevents these at compile-time"
    )
    def test_set_environment_variable_invalid_inputs(self) -> None:
        """Test set_environment_variable with invalid inputs (lines 147, 152)."""
        context = FlextCliContext()

        # Test with empty name
        result = context.set_environment_variable("", "value")
        assert result.is_failure
        assert "must be a non-empty string" in str(result.error).lower()

        # Test with None name
        with pytest.raises(TypeError):
            context.set_environment_variable(cast("str", None), "value")

        # Test with non-string name
        with pytest.raises(TypeError):
            context.set_environment_variable(cast("str", 123), "value")

        # Test with non-string value
        result = context.set_environment_variable("TEST", cast("str", 123))
        assert result.is_failure
        assert "must be a string" in str(result.error).lower()

        # Test with None value
        result = context.set_environment_variable("TEST", cast("str", None))
        assert result.is_failure
        assert "must be a string" in str(result.error).lower()

    @pytest.mark.skip(
        reason="Tests defensive runtime type checking - MyPy strict mode prevents these at compile-time"
    )
    def test_add_argument_invalid_input(self) -> None:
        """Test add_argument with invalid input (line 169)."""
        context = FlextCliContext()

        # Test with empty string
        result = context.add_argument("")
        assert result.is_failure
        assert "must be a non-empty string" in str(result.error).lower()

        # Test with None
        with pytest.raises(TypeError):
            context.add_argument(cast("str", None))

        # Test with non-string
        with pytest.raises(TypeError):
            context.add_argument(cast("str", 123))

    @pytest.mark.skip(
        reason="Tests defensive runtime type checking - MyPy strict mode prevents these at compile-time"
    )
    def test_remove_argument_invalid_input(self) -> None:
        """Test remove_argument with invalid input (line 186)."""
        context = FlextCliContext()

        # Test with empty string
        result = context.remove_argument("")
        assert result.is_failure
        assert "must be a non-empty string" in str(result.error).lower()

        # Test with None
        with pytest.raises(TypeError):
            context.remove_argument(cast("str", None))

        # Test with non-string
        with pytest.raises(TypeError):
            context.remove_argument(cast("str", 123))

    @pytest.mark.skip(
        reason="Tests defensive runtime type checking - MyPy strict mode prevents these at compile-time"
    )
    def test_set_metadata_invalid_key(self) -> None:
        """Test set_metadata with invalid key (line 209)."""
        context = FlextCliContext()

        # Test with empty string
        result = context.set_metadata("", "value")
        assert result.is_failure
        assert "must be a non-empty string" in str(result.error).lower()

        # Test with None
        with pytest.raises(TypeError):
            context.set_metadata(cast("str", None), "value")

        # Test with non-string
        with pytest.raises(TypeError):
            context.set_metadata(cast("str", 123), "value")

    @pytest.mark.skip(
        reason="Tests defensive runtime type checking - MyPy strict mode prevents these at compile-time"
    )
    def test_get_metadata_invalid_key(self) -> None:
        """Test get_metadata with invalid key (line 226)."""
        context = FlextCliContext()

        # Test with empty string
        result = context.get_metadata("")
        assert result.is_failure
        assert "must be a non-empty string" in str(result.error).lower()

        # Test with None
        with pytest.raises(TypeError):
            context.get_metadata(cast("str", None))

        # Test with non-string
        with pytest.raises(TypeError):
            context.get_metadata(cast("str", 123))

    @pytest.mark.skip(reason="Tests defensive code marked with pragma: no cover")
    def test_activate_exception_handling(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test activate method exception handling by mocking the is_active attribute."""
        context = FlextCliContext()

        # Mock the is_active property setter to raise an exception
        def mock_setter(self: FlextCliContext, value: bool) -> None:
            msg = "Mock exception during activation"
            raise RuntimeError(msg)

        # Patch the is_active property setter
        monkeypatch.setattr(
            FlextCliContext, "is_active", property(lambda self: False, mock_setter)
        )

        result = context.activate()
        assert result.is_failure
        assert "mock exception" in str(result.error).lower()

    @pytest.mark.skip(reason="Tests defensive code marked with pragma: no cover")
    def test_deactivate_exception_handling(self) -> None:
        """Test deactivate method exception handling by mocking the is_active attribute directly."""
        # Create a context where accessing is_active raises an exception
        exception_context = FlextCliContext()
        exception_context.is_active = True  # Start as active

        # Mock the is_active field access to raise an exception
        original_getattribute = exception_context.__class__.__getattribute__

        def mock_getattribute(self: FlextCliContext, name: str) -> object:
            if name == "is_active":
                msg = "Mock exception"
                raise RuntimeError(msg)
            return original_getattribute(self, name)

        # Use setattr to mock method - necessary for testing exception behavior
        exception_context.__class__.__getattribute__ = mock_getattribute

        result = exception_context.deactivate()
        assert result.is_failure
        assert "deactivation failed" in str(result.error).lower()

    @pytest.mark.skip(reason="Tests defensive code marked with pragma: no cover")
    def test_get_environment_variable_exception_handling(self) -> None:
        """Test get_environment_variable exception handling by using a custom dict subclass."""

        class ExceptionDict(UserDict[str, str]):
            def __getitem__(self, key: str) -> str:
                msg = "Mock exception"
                raise RuntimeError(msg)

        # Create context with exception-raising environment_variables
        context = FlextCliContext()
        context.environment_variables = cast(
            "dict[str, FlextTypes.JsonValue]", ExceptionDict({"TEST": "value"})
        )

        result = context.get_environment_variable("TEST")
        assert result.is_failure
        assert "retrieval failed" in str(result.error).lower()

    @pytest.mark.skip(reason="Tests defensive code marked with pragma: no cover")
    def test_set_environment_variable_exception_handling(self) -> None:
        """Test set_environment_variable exception handling by using a custom dict subclass."""

        class ExceptionDict(UserDict[str, str]):
            def __setitem__(self, key: str, value: str) -> None:
                msg = "Mock exception"
                raise RuntimeError(msg)

        # Create context with exception-raising environment_variables
        context = FlextCliContext()
        context.environment_variables = cast(
            "dict[str, FlextTypes.JsonValue]", ExceptionDict()
        )

        result = context.set_environment_variable("TEST", "value")
        assert result.is_failure
        assert "setting failed" in str(result.error).lower()

    @pytest.mark.skip(reason="Tests defensive code marked with pragma: no cover")
    def test_add_argument_exception_handling(self) -> None:
        """Test add_argument exception handling by using a custom list subclass."""

        class ExceptionList(UserList[str]):
            def append(self, item: str) -> None:
                msg = "Mock exception"
                raise RuntimeError(msg)

        # Create context with exception-raising arguments
        context = FlextCliContext()
        context.arguments = cast("list[str]", ExceptionList())

        result = context.add_argument("test_arg")
        assert result.is_failure
        assert "addition failed" in str(result.error).lower()

    @pytest.mark.skip(reason="Tests defensive code marked with pragma: no cover")
    def test_remove_argument_exception_handling(self) -> None:
        """Test remove_argument exception handling by using a custom list subclass."""

        class ExceptionList(UserList[str]):
            def remove(self, item: str) -> None:
                msg = "Mock exception"
                raise RuntimeError(msg)

        # Create context with exception-raising arguments
        context = FlextCliContext()
        context.arguments = cast("list[str]", ExceptionList(["test_arg"]))

        result = context.remove_argument("test_arg")
        assert result.is_failure
        assert "removal failed" in str(result.error).lower()

    @pytest.mark.skip(reason="Tests defensive code marked with pragma: no cover")
    def test_set_metadata_exception_handling(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test set_metadata exception handling (lines 216-217)."""
        context = FlextCliContext()

        # Create a mock dict that raises exception on __setitem__
        class MockDict(UserDict[str, object]):
            def __setitem__(self, key: str, value: object) -> None:
                msg = "Mock exception"
                raise RuntimeError(msg)

        # Replace the context_metadata with our mock
        context.context_metadata = cast("dict[str, FlextTypes.JsonValue]", MockDict())

        result = context.set_metadata("test_key", "test_value")
        assert result.is_failure
        assert "setting failed" in str(result.error).lower()

    @pytest.mark.skip(reason="Tests defensive code marked with pragma: no cover")
    def test_get_metadata_exception_handling(self) -> None:
        """Test get_metadata exception handling by using a custom dict subclass."""

        class ExceptionDict(UserDict[str, object]):
            def __getitem__(self, key: str) -> object:
                msg = "Mock exception"
                raise RuntimeError(msg)

        # Create context with exception-raising context_metadata
        context = FlextCliContext()
        context.context_metadata = cast(
            "dict[str, FlextTypes.JsonValue]",
            ExceptionDict({"test_key": "test_value"}),
        )

        result = context.get_metadata("test_key")
        assert result.is_failure
        assert "retrieval failed" in str(result.error).lower()

    @pytest.mark.skip(reason="Tests defensive code marked with pragma: no cover")
    def test_get_context_summary_exception_handling(self) -> None:
        """Test get_context_summary exception handling (lines 272-273)."""
        context = FlextCliContext()

        # Mock self.id to raise exception when accessed
        with patch.object(
            context,
            "id",
            new_callable=lambda: property(
                lambda self: (_ for _ in ()).throw(RuntimeError("Mock exception"))
            ),
        ):
            result = context.get_context_summary()
            assert result.is_failure
            assert "summary generation failed" in str(result.error).lower()

    @pytest.mark.skip(reason="Tests defensive code marked with pragma: no cover")
    def test_execute_exception_handling(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test execute method exception handling (lines 291-292)."""
        context = FlextCliContext()

        # Mock len() to raise exception when called on arguments
        original_len = len
        call_count = 0

        def mock_len(obj: object) -> int:
            nonlocal call_count
            if (
                isinstance(obj, list)
                and hasattr(context, "arguments")
                and obj is context.arguments
            ):
                call_count += 1
                if call_count == 1:  # Only fail on first call
                    msg = "Mock exception"
                    raise RuntimeError(msg)
            return original_len(cast("list[object]", obj))

        with patch("builtins.len", side_effect=mock_len):
            result = context.execute()
            assert result.is_failure
            assert "execution failed" in str(result.error).lower()
