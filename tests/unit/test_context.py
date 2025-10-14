"""Tests for FlextCliContext - CLI execution context management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import cast

from flext_core import FlextCore

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
        assert hasattr(context, "container")  # Property from FlextCore.Service
        assert hasattr(context, "command")  # Direct attribute access
        assert hasattr(context, "arguments")  # Direct attribute access

    def test_context_service_execute_method(self) -> None:
        """Test context service execute method."""
        context = FlextCliContext()
        result = context.execute()

        assert isinstance(result, FlextCore.Result)
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
