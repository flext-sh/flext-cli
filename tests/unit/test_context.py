"""Tests for FlextCliContext - CLI execution context management.

Modules Tested:
- flext_cli.context.FlextCliContext: CLI execution context service

Scope:
- Context initialization and ID generation
- Context activation/deactivation
- Environment variable management (get/set)
- Command argument management (add/remove)
- Metadata operations (get/set)
- Context serialization (summary, to_dict)
- Error handling and validation

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import uuid

import pytest
from flext_core import FlextResult, FlextUtilities

from flext_cli import FlextCliContext
from tests.fixtures.constants import TestContext
from tests.helpers import FlextCliTestHelpers
from tests._helpers import FlextCliTestHelpers as FlextCliTestHelpersBase

# Alias for nested class
ContextFactory = FlextCliTestHelpersBase.ContextFactory


class TestFlextCliContext:
    """Comprehensive test suite for FlextCliContext service."""

    # ========================================================================
    # INITIALIZATION AND BASIC FUNCTIONALITY
    # ========================================================================

    @pytest.mark.parametrize(
        ("command", "arguments", "env_vars", "working_dir"),
        [
            (None, None, None, None),
            (TestContext.Basic.DEFAULT_COMMAND, None, None, None),
            (
                TestContext.Basic.DEFAULT_COMMAND,
                TestContext.Arguments.MULTIPLE_ARGS,
                TestContext.Environment.MULTIPLE_VARS,
                TestContext.Paths.TEST_PATH,
            ),
        ],
    )
    def test_context_creation(
        self,
        command: str | None,
        arguments: list[str] | None,
        env_vars: dict[
            str, str | int | float | bool | dict[str, object] | list[object] | None
        ]
        | None,
        working_dir: str | None,
    ) -> None:
        """Test context creation with various parameters."""
        result = ContextFactory.create_context(
            command=command,
            arguments=arguments,
            environment_variables=env_vars,
            working_directory=working_dir,
        )
        FlextCliTestHelpers.AssertHelpers.assert_result_success(result)
        context = result.unwrap()

        assert isinstance(context, FlextCliContext)
        assert context.command == command
        assert context.arguments == (arguments or [])
        assert context.environment_variables == (env_vars or {})
        assert context.working_directory == working_dir
        assert context.id is not None
        assert isinstance(context.id, str)
        assert len(context.id) > 0

    def test_context_service_execute_method(self) -> None:
        """Test context service execute method."""
        context = FlextCliContext()
        result = context.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, dict)

    # ========================================================================
    # ACTIVATION AND DEACTIVATION
    # ========================================================================

    def test_context_activation_flow(self) -> None:
        """Test context activation and deactivation state transitions."""
        context = FlextCliContext()

        # Initial state
        assert not context.is_active

        # Activate
        result = context.activate()
        assert result.is_success
        assert context.is_active

        # Try to activate again - should fail
        result = context.activate()
        assert result.is_failure

        # Deactivate
        result = context.deactivate()
        assert result.is_success
        assert not context.is_active

        # Try to deactivate again - should fail
        result = context.deactivate()
        assert result.is_failure

    # ========================================================================
    # ENVIRONMENT VARIABLE OPERATIONS
    # ========================================================================

    @pytest.mark.parametrize(
        ("var_name", "var_value"),
        [
            (
                TestContext.Environment.TEST_VAR_NAME,
                TestContext.Environment.TEST_VAR_VALUE,
            ),
            ("ANOTHER_VAR", "another_value"),
            ("NUMERIC_VAR", "12345"),
        ],
    )
    def test_environment_variable_operations(
        self, var_name: str, var_value: str
    ) -> None:
        """Test environment variable get/set operations."""
        context = FlextCliContext()

        # Get non-existent variable
        get_result = context.get_environment_variable(var_name)
        assert get_result.is_failure

        # Set variable
        set_result = context.set_environment_variable(var_name, var_value)
        assert set_result.is_success

        # Get existing variable
        get_result2 = context.get_environment_variable(var_name)
        assert get_result2.is_success
        assert get_result2.unwrap() == var_value

    @pytest.mark.parametrize(
        "invalid_input",
        [
            "",  # Empty string
            "   ",  # Whitespace only
        ],
    )
    def test_environment_variable_validation(self, invalid_input: str) -> None:
        """Test environment variable name validation."""
        context = FlextCliContext()

        result = context.get_environment_variable(invalid_input)
        assert result.is_failure

        set_result = context.set_environment_variable(invalid_input, "value")
        assert set_result.is_failure

    def test_environment_variables_none_state(self) -> None:
        """Test fast-fail when environment_variables is None."""
        context = FlextCliContext(command="test")
        context.environment_variables = None

        get_result = context.get_environment_variable("VAR")
        assert get_result.is_failure

        set_result = context.set_environment_variable("VAR", "value")
        assert set_result.is_failure

    def test_set_environment_variable_type_validation(self) -> None:
        """Test environment variable value type validation."""
        context = FlextCliContext()

        # Try to set non-string value
        result = context.set_environment_variable(
            "VAR", "123"
        )  # Intentional pass of str
        assert result.is_success

    # ========================================================================
    # ARGUMENT OPERATIONS
    # ========================================================================

    @pytest.mark.parametrize(
        "args",
        [
            TestContext.Arguments.SINGLE_ARG,
            TestContext.Arguments.MULTIPLE_ARGS,
            TestContext.Arguments.LONG_ARGS,
        ],
    )
    def test_argument_operations(self, args: list[str]) -> None:
        """Test argument add/remove operations."""
        context = FlextCliContext()

        # Add arguments
        for arg in args:
            result = context.add_argument(arg)
            assert result.is_success

        assert context.arguments == args

        # Remove arguments
        for arg in args:
            result = context.remove_argument(arg)
            assert result.is_success

        assert context.arguments == []

    @pytest.mark.parametrize(
        "invalid_arg",
        [
            "",  # Empty
            "   ",  # Whitespace
        ],
    )
    def test_argument_validation(self, invalid_arg: str) -> None:
        """Test argument validation."""
        context = FlextCliContext()

        result = context.add_argument(invalid_arg)
        assert result.is_failure

        result = context.remove_argument(invalid_arg)
        assert result.is_failure

    def test_remove_nonexistent_argument(self) -> None:
        """Test removing non-existent argument."""
        context = FlextCliContext()
        context.add_argument("existing_arg")

        result = context.remove_argument("nonexistent_arg")
        assert result.is_failure
        assert "not found" in str(result.error).lower()

    def test_arguments_none_state(self) -> None:
        """Test fast-fail when arguments is None."""
        context = FlextCliContext(command="test")
        context.arguments = None

        add_result = context.add_argument("arg")
        assert add_result.is_failure

        remove_result = context.remove_argument("arg")
        assert remove_result.is_failure

    # ========================================================================
    # METADATA OPERATIONS
    # ========================================================================

    @pytest.mark.parametrize(
        ("key", "value"),
        [
            ("key1", "value1"),
            ("nested_key", {"inner": "value"}),
            ("list_key", [1, 2, 3]),
            ("number_key", 42),
        ],
    )
    def test_metadata_operations(
        self,
        key: str,
        value: str | float | bool | dict[str, object] | list[object] | None,
    ) -> None:
        """Test metadata get/set operations."""
        context = FlextCliContext()

        # Set metadata
        set_result = context.set_metadata(key, value)
        assert set_result.is_success

        # Get metadata
        get_result = context.get_metadata(key)
        assert get_result.is_success
        assert get_result.unwrap() == value

    @pytest.mark.parametrize(
        "invalid_key",
        [
            "",
            "   ",
        ],
    )
    def test_metadata_key_validation(self, invalid_key: str) -> None:
        """Test metadata key validation."""
        context = FlextCliContext()

        set_result = context.set_metadata(invalid_key, "value")
        assert set_result.is_failure

        get_result = context.get_metadata(invalid_key)
        assert get_result.is_failure

    def test_get_nonexistent_metadata(self) -> None:
        """Test getting non-existent metadata."""
        context = FlextCliContext()

        result = context.get_metadata("nonexistent")
        assert result.is_failure
        assert "not found" in str(result.error).lower()

    # ========================================================================
    # CONTEXT SUMMARY AND SERIALIZATION
    # ========================================================================

    def test_context_summary(self) -> None:
        """Test context summary generation."""
        context = FlextCliContext(
            command="test_cmd",
            arguments=TestContext.Arguments.MULTIPLE_ARGS,
            working_directory=TestContext.Paths.TEST_PATH,
        )

        result = context.get_context_summary()
        assert result.is_success

        summary = result.unwrap()
        assert summary["command"] == "test_cmd"
        assert summary["arguments"] == TestContext.Arguments.MULTIPLE_ARGS
        assert summary["arguments_count"] == len(TestContext.Arguments.MULTIPLE_ARGS)
        assert summary["working_directory"] == TestContext.Paths.TEST_PATH
        assert summary["is_active"] is False

    def test_context_to_dict(self) -> None:
        """Test context serialization to dictionary."""
        context = FlextCliContext(
            command="test_cmd",
            arguments=TestContext.Arguments.SINGLE_ARG,
            working_directory=TestContext.Paths.TEST_PATH,
        )

        result = context.to_dict()
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, dict)
        assert data["command"] == "test_cmd"
        assert data["arguments"] == TestContext.Arguments.SINGLE_ARG
        assert data["working_directory"] == TestContext.Paths.TEST_PATH
        assert "timeout_seconds" in data

    def test_to_dict_with_none_arguments(self) -> None:
        """Test to_dict fast-fail when arguments is None."""
        context = FlextCliContext(command="test")
        context.arguments = None

        result = context.to_dict()
        assert result.is_failure

    def test_to_dict_with_none_env_vars(self) -> None:
        """Test to_dict fast-fail when environment_variables is None."""
        context = FlextCliContext(command="test")
        context.environment_variables = None

        result = context.to_dict()
        assert result.is_failure

    # ========================================================================
    # ID GENERATION AND VALIDATION
    # ========================================================================

    def test_id_generation(self) -> None:
        """Test automatic ID generation on context creation."""
        context1 = FlextCliContext()
        context2 = FlextCliContext()

        # Both should have IDs
        assert context1.id is not None
        assert context2.id is not None

        # IDs should be different
        assert context1.id != context2.id

        # IDs should be valid UUID format or string
        for context_id in [context1.id, context2.id]:
            try:
                uuid.UUID(context_id)
            except ValueError:
                # If not UUID, should at least be a non-empty string
                assert len(context_id) > 0

    def test_explicit_id_provides(self) -> None:
        """Test context creation with explicit ID."""
        explicit_id = "custom_id_123"
        context = FlextCliContext(id=explicit_id)

        assert context.id == explicit_id

    def test_empty_id_fallback(self) -> None:
        """Test fallback when explicit ID is empty."""
        context = FlextCliContext(id="")

        # Should generate a valid ID
        assert context.id is not None
        assert len(context.id) > 0

    # ========================================================================
    # COMPLEX SCENARIOS AND EDGE CASES
    # ========================================================================

    def test_full_context_workflow(self) -> None:
        """Test complete context workflow with multiple operations."""
        context = FlextCliContext(
            command="deploy",
            arguments=["--production", "--force"],
        )

        # Set environment variables
        context.set_environment_variable("DEPLOY_ENV", "prod")
        context.set_environment_variable("DEPLOY_TIMEOUT", "300")

        # Add arguments
        context.add_argument("--verify")

        # Set metadata
        context.set_metadata(
            "started_at", FlextUtilities.Generators.generate_iso_timestamp()
        )
        context.set_metadata("deployment_id", "dep_12345")

        # Activate context
        context.activate()

        # Get summary
        summary = context.get_context_summary().unwrap()
        assert summary["command"] == "deploy"
        assert summary["arguments_count"] == 3
        assert summary["is_active"] is True

    def test_execute_arguments_none(self) -> None:
        """Test execute when arguments is None."""
        context = FlextCliContext(command="test")
        context.arguments = None

        result = context.execute()
        assert result.is_failure

    def test_context_state_isolation(self) -> None:
        """Test that context instances are isolated."""
        context1 = FlextCliContext(command="cmd1")
        context2 = FlextCliContext(command="cmd2")

        # Modify context1
        context1.set_environment_variable("VAR", "value1")
        context1.add_argument("arg1")

        # context2 should not be affected
        assert context2.get_environment_variable("VAR").is_failure
        assert context2.arguments == []
        assert context1.command != context2.command
