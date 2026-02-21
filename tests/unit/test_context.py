"""FLEXT CLI Context Tests - Comprehensive Context Management Testing.

Tests for FlextCliContext covering initialization, activation/deactivation,
environment variables, arguments, metadata, serialization, and edge cases
with 100% coverage.

Modules tested: flext_cli.context.FlextCliContext
Scope: All context operations, state management, validation, serialization

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import uuid
from typing import TypeVar

import pytest
from flext_cli import t
from flext_tests import tm

from flext_cli import FlextCliContext, FlextCliModels as m, r, u

from ..helpers import FlextCliTestHelpers

# from ..fixtures.constants import TestContext  # Fixtures removed - use conftest.py and flext_tests

T = TypeVar("T")


class TestsCliContext:
    """Comprehensive test suite for FlextCliContext service.

    Single class with nested helper classes and methods organized by functionality.
    Uses factories, constants, dynamic tests, and helpers to reduce code while
    maintaining and expanding coverage.
    """

    # =========================================================================
    # NESTED: Fixtures Factory
    # =========================================================================

    class Fixtures:
        """Factory for creating context instances for testing."""

        @staticmethod
        def create_context(
            command: str | None = None,
            arguments: list[str] | None = None,
            env_vars: dict[str, t.GeneralValueType] | None = None,
            working_dir: str | None = None,
        ) -> r[FlextCliContext]:
            """Create FlextCliContext instance."""
            # Use FlextTestsUtilities.GenericHelpers.to_json_dict for JSON conversion
            json_env_vars: dict[str, t.GeneralValueType] | None = None
            if env_vars:
                env_vars_converted = env_vars
                transform_result = u.transform(env_vars_converted, to_json=True)
                json_env_vars = (
                    transform_result.value
                    if transform_result.is_success
                    else env_vars_converted
                )
            return FlextCliTestHelpers.ContextFactory.create_context(
                command=command,
                arguments=arguments,
                environment_variables=json_env_vars,
                working_directory=working_dir,
            )

    # =========================================================================
    # NESTED: Test Data Factory
    # =========================================================================

    class TestData:
        """Factory for creating test data scenarios."""

        @staticmethod
        def get_creation_cases() -> list[dict[str, object | None]]:
            """Get parametrized test cases for context creation."""
            return [
                {
                    "command": None,
                    "arguments": None,
                    "env_vars": None,
                    "working_dir": None,
                },
                {
                    "command": "test_command",
                    "arguments": None,
                    "env_vars": None,
                    "working_dir": None,
                },
                {
                    "command": "test_command",
                    "arguments": ["arg1", "arg2", "arg3"],
                    "env_vars": {"VAR1": "value1", "VAR2": "value2"},
                    "working_dir": "/tmp/test",
                },
            ]

        @staticmethod
        def get_env_var_cases() -> list[tuple[str, str]]:
            """Get parametrized test cases for environment variables."""
            return [
                (
                    "TEST_VAR",
                    "test_value",
                ),
                ("ANOTHER_VAR", "another_value"),
                ("NUMERIC_VAR", "12345"),
            ]

        @staticmethod
        def get_invalid_inputs() -> list[str]:
            """Get invalid input values for validation tests."""
            return [
                "",
                "   ",
            ]

        @staticmethod
        def get_argument_cases() -> list[list[str]]:
            """Get parametrized test cases for arguments."""
            return [
                ["arg1"],
                ["arg1", "arg2", "arg3"],
                ["arg1", "arg2", "arg3", "arg4", "arg5"],
            ]

        @staticmethod
        def get_metadata_cases() -> list[tuple[str, object]]:
            """Get parametrized test cases for metadata."""
            return [
                ("key1", "value1"),
                ("nested_key", {"inner": "value"}),
                ("list_key", [1, 2, 3]),
                ("number_key", 42),
            ]

    # =========================================================================
    # NESTED: Assertion Helpers
    # =========================================================================

    # Assertions removed - use FlextTestsMatchers directly
    # Domain-specific assertions are inline in test methods

    # =========================================================================
    # INITIALIZATION TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize(
        "test_case",
        [
            {
                "command": None,
                "arguments": None,
                "env_vars": None,
                "working_dir": None,
            },
            {
                "command": "test_command",
                "arguments": None,
                "env_vars": None,
                "working_dir": None,
            },
            {
                "command": "test_command",
                "arguments": ["arg1", "arg2", "arg3"],
                "env_vars": {"VAR1": "value1", "VAR2": "value2"},
                "working_dir": "/tmp/test",
            },
        ],
    )
    def test_context_creation(self, test_case: dict[str, object | None]) -> None:
        """Test context creation with parametrized cases."""
        # Extract test_case values with type narrowing
        command_raw = test_case.get("command")
        command: str | None = command_raw if isinstance(command_raw, str) else None
        arguments_raw = test_case.get("arguments")
        arguments: list[str] | None = (
            arguments_raw if isinstance(arguments_raw, list) else None
        )
        env_vars_raw = test_case.get("env_vars")
        env_vars: dict[str, t.GeneralValueType] | None = (
            env_vars_raw if isinstance(env_vars_raw, dict) else None
        )
        working_dir_raw = test_case.get("working_dir")
        working_dir: str | None = (
            working_dir_raw if isinstance(working_dir_raw, str) else None
        )

        result = self.Fixtures.create_context(
            command=command,
            arguments=arguments,
            env_vars=env_vars,
            working_dir=working_dir,
        )
        tm.ok(result)
        context = result.value

        assert isinstance(context, FlextCliContext)
        # Validate context properties
        if command is not None:
            assert context.command == command
        if arguments is not None:
            assert context.arguments == arguments or []
        if env_vars is not None:
            assert context.environment_variables == env_vars or {}
        if working_dir is not None:
            assert context.working_directory == working_dir
        assert context.id is not None
        assert isinstance(context.id, str)
        assert len(context.id) > 0

    def test_context_service_execute_method(self) -> None:
        """Test context service execute method."""
        context = FlextCliContext()
        result = context.execute()

        assert isinstance(result, r)
        tm.ok(result)
        assert isinstance(result.value, m.Cli.ContextExecutionResult)

    # =========================================================================
    # ACTIVATION AND DEACTIVATION TESTS
    # =========================================================================

    def test_context_activation_flow(self) -> None:
        """Test context activation and deactivation state transitions."""
        context = FlextCliContext()

        # Initial state
        assert not context.is_active

        # Activate
        result = context.activate()
        tm.ok(result)
        assert context.is_active

        # Try to activate again - should fail
        if context.is_active:
            result = context.activate()
            tm.fail(result)

        # Deactivate
        result = context.deactivate()
        tm.ok(result)
        assert not context.is_active

        # Try to deactivate again - should fail
        result = context.deactivate()
        tm.fail(result)

    # =========================================================================
    # ENVIRONMENT VARIABLE OPERATIONS TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize(
        ("var_name", "var_value"),
        [
            ("TEST_VAR", "test_value"),
            ("ANOTHER_VAR", "another_value"),
            ("NUMERIC_VAR", "12345"),
        ],
    )
    def test_environment_variable_operations(
        self,
        var_name: str,
        var_value: str,
    ) -> None:
        """Test environment variable get/set operations."""
        context = FlextCliContext()

        # Get non-existent variable
        get_result = context.get_environment_variable(var_name)
        tm.fail(get_result)

        # Set variable
        set_result = context.set_environment_variable(var_name, var_value)
        tm.ok(set_result)

        # Get existing variable
        get_result2 = context.get_environment_variable(var_name)
        tm.ok(get_result2)
        assert get_result2.value == var_value

    @pytest.mark.parametrize("invalid_input", ["", "   "])
    def test_environment_variable_validation(self, invalid_input: str) -> None:
        """Test environment variable name validation."""
        context = FlextCliContext()

        result = context.get_environment_variable(invalid_input)
        tm.fail(result)

        set_result = context.set_environment_variable(invalid_input, "value")
        tm.fail(set_result)

    def test_environment_variables_none_state(self) -> None:
        """Test fast-fail when environment_variables is None."""
        context = FlextCliContext(command="test")
        # Use model_copy() to create a modified copy (frozen model pattern)
        context_with_none = context.model_copy(update={"environment_variables": None})

        get_result = context_with_none.get_environment_variable("VAR")
        tm.fail(get_result)

        set_result = context_with_none.set_environment_variable("VAR", "value")
        tm.fail(set_result)

    # =========================================================================
    # ARGUMENT OPERATIONS TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize(
        "args",
        [
            ["arg1"],
            ["arg1", "arg2", "arg3"],
            ["arg1", "arg2", "arg3", "arg4", "arg5"],
        ],
    )
    def test_argument_operations(self, args: list[str]) -> None:
        """Test argument add/remove operations."""
        context = FlextCliContext()

        # Add arguments
        for arg in args:
            result = context.add_argument(arg)
            tm.ok(result)

        assert context.arguments == args

        # Remove arguments
        for arg in args:
            result = context.remove_argument(arg)
            tm.ok(result)

        assert context.arguments == []

    @pytest.mark.parametrize("invalid_arg", ["", "   "])
    def test_argument_validation(self, invalid_arg: str) -> None:
        """Test argument validation."""
        context = FlextCliContext()

        result = context.add_argument(invalid_arg)
        tm.fail(result)

        result = context.remove_argument(invalid_arg)
        tm.fail(result)

    def test_remove_nonexistent_argument(self) -> None:
        """Test removing non-existent argument."""
        context = FlextCliContext()
        context.add_argument("existing_arg")

        result = context.remove_argument("nonexistent_arg")
        tm.fail(result, has="not found")

    def test_arguments_none_state(self) -> None:
        """Test fast-fail when arguments is None."""
        # Create context with None arguments using model_copy
        context = FlextCliContext(command="test")
        # Use model_copy to create a new instance with arguments=None for testing
        # This is the correct way to modify frozen Pydantic models
        context = context.model_copy(update={"arguments": None})

        add_result = context.add_argument("arg")
        tm.fail(add_result)

        remove_result = context.remove_argument("arg")
        tm.fail(remove_result)

    # =========================================================================
    # METADATA OPERATIONS TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize(("key", "value"), TestData.get_metadata_cases())
    def test_metadata_operations(self, key: str, value: object) -> None:
        """Test metadata get/set operations."""
        context = FlextCliContext()

        # Use t.GeneralValueType directly - set_metadata accepts t.GeneralValueType
        # Dict is already compatible with GeneralValueType via Mapping[str, GeneralValueType]
        json_value: t.GeneralValueType = value
        set_result = context.set_metadata(key, json_value)
        tm.ok(set_result)

        # Get metadata
        get_result = context.get_metadata(key)
        tm.ok(get_result)
        assert get_result.value == value

    @pytest.mark.parametrize("invalid_key", ["", "   "])
    def test_metadata_key_validation(self, invalid_key: str) -> None:
        """Test metadata key validation."""
        context = FlextCliContext()

        set_result = context.set_metadata(invalid_key, "value")
        tm.fail(set_result)

        get_result = context.get_metadata(invalid_key)
        tm.fail(get_result)

    def test_get_nonexistent_metadata(self) -> None:
        """Test getting non-existent metadata."""
        context = FlextCliContext()

        result = context.get_metadata("nonexistent")
        tm.fail(result, has="not found")

    # =========================================================================
    # CONTEXT SUMMARY AND SERIALIZATION TESTS
    # =========================================================================

    def test_context_summary(self) -> None:
        """Test context summary generation."""
        context = FlextCliContext(
            command="test_cmd",
            arguments=["arg1", "arg2", "arg3"],
            working_directory="/tmp/test",
        )

        result = context.get_context_summary()
        tm.ok(result)

        summary = result.value
        assert summary["command"] == "test_cmd"
        assert summary["arguments"] == ["arg1", "arg2", "arg3"]
        assert summary["arguments_count"] == len(["arg1", "arg2", "arg3"])
        assert summary["working_directory"] == "/tmp/test"
        assert summary["is_active"] is False

    def test_context_to_dict(self) -> None:
        """Test context serialization to dictionary."""
        context = FlextCliContext(
            command="test_cmd",
            arguments=["arg1"],
            working_directory="/tmp/test",
        )

        result = context.to_dict()
        tm.ok(result)

        data = result.value
        assert isinstance(data, dict)
        assert data["command"] == "test_cmd"
        assert data["arguments"] == ["arg1"]
        assert data["working_directory"] == "/tmp/test"
        assert "timeout_seconds" in data

    def test_to_dict_with_none_arguments(self) -> None:
        """Test to_dict fast-fail when arguments is None."""
        context = FlextCliContext(command="test")
        # Use model_copy() to create a modified copy (frozen model pattern)
        context_with_none = context.model_copy(update={"arguments": None})

        result = context_with_none.to_dict()
        tm.fail(result)

    def test_to_dict_with_none_env_vars(self) -> None:
        """Test to_dict fast-fail when environment_variables is None."""
        context = FlextCliContext(command="test")
        # Use model_copy() to create a modified copy (frozen model pattern)
        context_with_none = context.model_copy(update={"environment_variables": None})

        result = context_with_none.to_dict()
        tm.fail(result)

    # =========================================================================
    # ID GENERATION AND VALIDATION TESTS
    # =========================================================================

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

    # =========================================================================
    # COMPLEX SCENARIOS AND EDGE CASES TESTS
    # =========================================================================

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
        context.set_metadata("started_at", u.generate("timestamp"))
        context.set_metadata("deployment_id", "dep_12345")

        # Activate context
        context.activate()

        # Get summary
        summary = context.get_context_summary().value
        assert summary["command"] == "deploy"
        assert summary["arguments_count"] == 3
        assert summary["is_active"] is True

    def test_execute_arguments_none(self) -> None:
        """Test execute when arguments is None."""
        context = FlextCliContext(command="test")
        # Use model_copy() to create a modified copy (frozen model pattern)
        context_with_none = context.model_copy(update={"arguments": None})

        result = context_with_none.execute()
        tm.fail(result)

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
