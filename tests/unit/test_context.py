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
from typing import TypeVar, cast

import pytest
from flext_core import FlextResult, FlextTypes, FlextUtilities
from flext_tests import FlextTestsUtilities

from flext_cli import FlextCliContext
from flext_cli.typings import FlextCliTypes

from .._helpers import FlextCliTestHelpers
from ..fixtures.constants import TestContext

T = TypeVar("T")


class TestFlextCliContext:
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
            env_vars: dict[str, object] | None = None,
            working_dir: str | None = None,
        ) -> FlextResult[FlextCliContext]:
            """Create FlextCliContext instance."""
            # Cast env_vars to JsonDict for type compatibility
            json_env_vars: FlextTypes.JsonDict | None = (
                cast("FlextTypes.JsonDict", env_vars) if env_vars is not None else None
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
                    "command": TestContext.Basic.DEFAULT_COMMAND,
                    "arguments": None,
                    "env_vars": None,
                    "working_dir": None,
                },
                {
                    "command": TestContext.Basic.DEFAULT_COMMAND,
                    "arguments": TestContext.Arguments.MULTIPLE_ARGS,
                    "env_vars": TestContext.Environment.MULTIPLE_VARS,
                    "working_dir": TestContext.Paths.TEST_PATH,
                },
            ]

        @staticmethod
        def get_env_var_cases() -> list[tuple[str, str]]:
            """Get parametrized test cases for environment variables."""
            return [
                (
                    TestContext.Environment.TEST_VAR_NAME,
                    TestContext.Environment.TEST_VAR_VALUE,
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
                TestContext.Arguments.SINGLE_ARG,
                TestContext.Arguments.MULTIPLE_ARGS,
                TestContext.Arguments.LONG_ARGS,
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

    class Assertions:
        """Helper methods for test assertions using flext-core helpers."""

        @staticmethod
        def assert_result_success(result: FlextResult[T]) -> None:
            """Assert result is successful using flext-core helper."""
            FlextTestsUtilities.TestUtilities.assert_result_success(result)

        @staticmethod
        def assert_result_failure(
            result: FlextResult[T], error_contains: str | None = None
        ) -> None:
            """Assert result is failure with optional error message check."""
            FlextTestsUtilities.TestUtilities.assert_result_failure(result)
            if error_contains:
                # Case-insensitive check for error message
                assert result.error is not None
                error_msg = str(result.error).lower()
                assert error_contains.lower() in error_msg, (
                    f"Error should contain '{error_contains}', got: {error_msg}"
                )

        @staticmethod
        def assert_context_properties(
            context: FlextCliContext,
            command: str | None = None,
            arguments: list[str] | None = None,
            env_vars: dict[str, object] | None = None,
            working_dir: str | None = None,
        ) -> None:
            """Assert context has expected properties."""
            if command is not None:
                assert context.command == command
            if arguments is not None:
                assert context.arguments == arguments
            if env_vars is not None:
                assert context.environment_variables == env_vars
            if working_dir is not None:
                assert context.working_directory == working_dir
            assert context.id is not None
            assert isinstance(context.id, str)
            assert len(context.id) > 0

    # =========================================================================
    # INITIALIZATION TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize("test_case", TestData.get_creation_cases())
    def test_context_creation(self, test_case: dict[str, object | None]) -> None:
        """Test context creation with parametrized cases."""
        # Cast test_case values to proper types
        command = cast("str | None", test_case.get("command"))
        arguments = cast("list[str] | None", test_case.get("arguments"))
        env_vars_raw = test_case.get("env_vars")
        env_vars = (
            cast("dict[str, object]", env_vars_raw)
            if env_vars_raw is not None
            else None
        )
        working_dir = cast("str | None", test_case.get("working_dir"))

        result = self.Fixtures.create_context(
            command=command,
            arguments=arguments,
            env_vars=env_vars,
            working_dir=working_dir,
        )
        self.Assertions.assert_result_success(result)
        context = result.unwrap()

        assert isinstance(context, FlextCliContext)
        self.Assertions.assert_context_properties(
            context,
            command=command,
            arguments=arguments or [],
            env_vars=env_vars or {},
            working_dir=working_dir,
        )

    def test_context_service_execute_method(self) -> None:
        """Test context service execute method."""
        context = FlextCliContext()
        result = context.execute()

        assert isinstance(result, FlextResult)
        self.Assertions.assert_result_success(result)
        assert isinstance(result.unwrap(), dict)

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
        self.Assertions.assert_result_success(result)
        assert context.is_active

        # Try to activate again - should fail
        result = context.activate()
        self.Assertions.assert_result_failure(result)

        # Deactivate
        result = context.deactivate()
        self.Assertions.assert_result_success(result)
        assert not context.is_active

        # Try to deactivate again - should fail
        result = context.deactivate()
        self.Assertions.assert_result_failure(result)

    # =========================================================================
    # ENVIRONMENT VARIABLE OPERATIONS TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize(("var_name", "var_value"), TestData.get_env_var_cases())
    def test_environment_variable_operations(
        self, var_name: str, var_value: str
    ) -> None:
        """Test environment variable get/set operations."""
        context = FlextCliContext()

        # Get non-existent variable
        get_result = context.get_environment_variable(var_name)
        self.Assertions.assert_result_failure(get_result)

        # Set variable
        set_result = context.set_environment_variable(var_name, var_value)
        self.Assertions.assert_result_success(set_result)

        # Get existing variable
        get_result2 = context.get_environment_variable(var_name)
        self.Assertions.assert_result_success(get_result2)
        assert get_result2.unwrap() == var_value

    @pytest.mark.parametrize("invalid_input", TestData.get_invalid_inputs())
    def test_environment_variable_validation(self, invalid_input: str) -> None:
        """Test environment variable name validation."""
        context = FlextCliContext()

        result = context.get_environment_variable(invalid_input)
        self.Assertions.assert_result_failure(result)

        set_result = context.set_environment_variable(invalid_input, "value")
        self.Assertions.assert_result_failure(set_result)

    def test_environment_variables_none_state(self) -> None:
        """Test fast-fail when environment_variables is None."""
        context = FlextCliContext(command="test")
        context.environment_variables = None

        get_result = context.get_environment_variable("VAR")
        self.Assertions.assert_result_failure(get_result)

        set_result = context.set_environment_variable("VAR", "value")
        self.Assertions.assert_result_failure(set_result)

    # =========================================================================
    # ARGUMENT OPERATIONS TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize("args", TestData.get_argument_cases())
    def test_argument_operations(self, args: list[str]) -> None:
        """Test argument add/remove operations."""
        context = FlextCliContext()

        # Add arguments
        for arg in args:
            result = context.add_argument(arg)
            self.Assertions.assert_result_success(result)

        assert context.arguments == args

        # Remove arguments
        for arg in args:
            result = context.remove_argument(arg)
            self.Assertions.assert_result_success(result)

        assert context.arguments == []

    @pytest.mark.parametrize("invalid_arg", TestData.get_invalid_inputs())
    def test_argument_validation(self, invalid_arg: str) -> None:
        """Test argument validation."""
        context = FlextCliContext()

        result = context.add_argument(invalid_arg)
        self.Assertions.assert_result_failure(result)

        result = context.remove_argument(invalid_arg)
        self.Assertions.assert_result_failure(result)

    def test_remove_nonexistent_argument(self) -> None:
        """Test removing non-existent argument."""
        context = FlextCliContext()
        context.add_argument("existing_arg")

        result = context.remove_argument("nonexistent_arg")
        self.Assertions.assert_result_failure(result, "not found")

    def test_arguments_none_state(self) -> None:
        """Test fast-fail when arguments is None."""
        context = FlextCliContext(command="test")
        context.arguments = None

        add_result = context.add_argument("arg")
        self.Assertions.assert_result_failure(add_result)

        remove_result = context.remove_argument("arg")
        self.Assertions.assert_result_failure(remove_result)

    # =========================================================================
    # METADATA OPERATIONS TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize(("key", "value"), TestData.get_metadata_cases())
    def test_metadata_operations(self, key: str, value: object) -> None:
        """Test metadata get/set operations."""
        context = FlextCliContext()

        # Set metadata - cast value to FlextCliTypes.CliJsonValue for type compatibility
        json_value = cast("FlextCliTypes.CliJsonValue", value)
        set_result = context.set_metadata(key, json_value)
        self.Assertions.assert_result_success(set_result)

        # Get metadata
        get_result = context.get_metadata(key)
        self.Assertions.assert_result_success(get_result)
        assert get_result.unwrap() == value

    @pytest.mark.parametrize("invalid_key", TestData.get_invalid_inputs())
    def test_metadata_key_validation(self, invalid_key: str) -> None:
        """Test metadata key validation."""
        context = FlextCliContext()

        set_result = context.set_metadata(invalid_key, "value")
        self.Assertions.assert_result_failure(set_result)

        get_result = context.get_metadata(invalid_key)
        self.Assertions.assert_result_failure(get_result)

    def test_get_nonexistent_metadata(self) -> None:
        """Test getting non-existent metadata."""
        context = FlextCliContext()

        result = context.get_metadata("nonexistent")
        self.Assertions.assert_result_failure(result, "not found")

    # =========================================================================
    # CONTEXT SUMMARY AND SERIALIZATION TESTS
    # =========================================================================

    def test_context_summary(self) -> None:
        """Test context summary generation."""
        context = FlextCliContext(
            command="test_cmd",
            arguments=TestContext.Arguments.MULTIPLE_ARGS,
            working_directory=TestContext.Paths.TEST_PATH,
        )

        result = context.get_context_summary()
        self.Assertions.assert_result_success(result)

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
        self.Assertions.assert_result_success(result)

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
        self.Assertions.assert_result_failure(result)

    def test_to_dict_with_none_env_vars(self) -> None:
        """Test to_dict fast-fail when environment_variables is None."""
        context = FlextCliContext(command="test")
        context.environment_variables = None

        result = context.to_dict()
        self.Assertions.assert_result_failure(result)

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
        self.Assertions.assert_result_failure(result)

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
