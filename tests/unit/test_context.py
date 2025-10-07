"""Tests for FlextCliContext - CLI execution context management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_core import FlextResult

from flext_cli.context import FlextCliContext
from flext_cli.models import FlextCliModels


class TestFlextCliContext:
    """Test suite for FlextCliContext service."""

    @pytest.fixture
    def context_service(self) -> FlextCliContext:
        """Fixture providing FlextCliContext instance."""
        return FlextCliContext()

    # ========================================================================
    # INITIALIZATION AND BASIC FUNCTIONALITY
    # ========================================================================

    def test_context_service_initialization(
        self, context_service: FlextCliContext
    ) -> None:
        """Test context service initialization."""
        assert context_service is not None
        assert hasattr(context_service, "logger")
        assert hasattr(context_service, "container")  # Property from FlextService
        assert hasattr(context_service, "_model_class")

    def test_context_service_execute_method(
        self, context_service: FlextCliContext
    ) -> None:
        """Test context service execute method."""
        result = context_service.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, dict)

    # ========================================================================
    # CREATE CONTEXT
    # ========================================================================

    def test_create_context_minimal(self, context_service: FlextCliContext) -> None:
        """Test creating context with minimal parameters."""
        result = context_service.create_context()

        assert isinstance(result, FlextResult)
        assert result.is_success

        context = result.unwrap()
        assert isinstance(context, FlextCliModels.CliContext)

    def test_create_context_with_command(
        self, context_service: FlextCliContext
    ) -> None:
        """Test creating context with command."""
        result = context_service.create_context(command="test_command")

        assert isinstance(result, FlextResult)
        assert result.is_success

        context = result.unwrap()
        assert context.command == "test_command"

    def test_create_context_with_arguments(
        self, context_service: FlextCliContext
    ) -> None:
        """Test creating context with arguments."""
        result = context_service.create_context(
            command="test", arguments=["arg1", "arg2"]
        )

        assert isinstance(result, FlextResult)
        assert result.is_success

        context = result.unwrap()
        assert context.arguments == ["arg1", "arg2"]

    def test_create_context_with_environment(
        self, context_service: FlextCliContext
    ) -> None:
        """Test creating context with environment variables."""
        env = {"KEY": "value", "DEBUG": "true"}
        result = context_service.create_context(environment_variables=env)

        assert isinstance(result, FlextResult)
        assert result.is_success

        context = result.unwrap()
        assert context.environment_variables == env

    # ========================================================================
    # VALIDATE CONTEXT
    # ========================================================================

    def test_validate_context_success(self, context_service: FlextCliContext) -> None:
        """Test validating a valid context."""
        create_result = context_service.create_context(command="test")
        assert create_result.is_success

        context = create_result.unwrap()
        validate_result = context_service.validate_context(context)

        assert isinstance(validate_result, FlextResult)
        assert validate_result.is_success

    # ========================================================================
    # CREATE CONTEXT FROM MODEL
    # ========================================================================

    def test_create_context_from_model(self, context_service: FlextCliContext) -> None:
        """Test creating context from model data."""
        # Create a proper Pydantic model instance (use CliContext as the model)
        model_instance = FlextCliModels.CliContext(
            command="test",
            arguments=["arg1"],
            environment_variables={},
            working_directory=None,
        )

        result = context_service.create_context_from_model(
            model_instance, command="test"
        )

        assert isinstance(result, FlextResult)
        assert result.is_success

        context = result.unwrap()
        assert isinstance(context, FlextCliModels.CliContext)

    # ========================================================================
    # ATTACH AND EXTRACT MODEL
    # ========================================================================

    def test_attach_and_extract_model(self, context_service: FlextCliContext) -> None:
        """Test attaching and extracting model from context."""
        # Create a context
        create_result = context_service.create_context(command="test")
        assert create_result.is_success
        context = create_result.unwrap()

        # Create a model instance to attach
        model_instance = FlextCliModels.CliContext(
            command="test_model",
            arguments=["arg1"],
            environment_variables={},
            working_directory=None,
        )

        # Attach model to context
        attach_result = context_service.attach_model_to_context(context, model_instance)
        assert isinstance(attach_result, FlextResult)
        assert attach_result.is_success

        # Extract model from context
        extract_result = context_service.extract_model_from_context(
            context, FlextCliModels.CliContext
        )
        assert isinstance(extract_result, FlextResult)
        assert extract_result.is_success

    # ========================================================================
    # GET MODEL METADATA
    # ========================================================================

    def test_get_model_metadata(self, context_service: FlextCliContext) -> None:
        """Test getting model metadata."""
        # First create a context
        create_result = context_service.create_context(command="test")
        assert create_result.is_success
        context = create_result.unwrap()

        # Then get metadata from it
        result = context_service.get_model_metadata(context)

        assert isinstance(result, FlextResult)
        assert result.is_success

        metadata = result.unwrap()
        assert isinstance(metadata, dict)
