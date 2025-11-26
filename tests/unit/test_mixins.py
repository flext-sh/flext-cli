"""FLEXT CLI Mixins Tests - Comprehensive Mixins Validation Testing.

Tests for FlextCliMixins covering business rules validation (command/session state,
pipeline steps, configuration consistency), CLI command mixin execution, and edge cases
with 100% coverage.

Modules tested: flext_cli.mixins.FlextCliMixins (BusinessRulesMixin, CliCommandMixin)
Scope: All validation methods, CLI context execution, error handling, edge cases

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TypeVar

import pytest
from flext_core import FlextResult, FlextTypes

from flext_cli import FlextCliMixins

from ..fixtures.constants import TestMixins

T = TypeVar("T")


class TestFlextCliMixins:
    """Comprehensive test suite for FlextCliMixins validation and composition.

    Single class with nested helper classes and methods organized by functionality.
    Uses factories, constants, dynamic tests, and helpers to reduce code while
    maintaining and expanding coverage.
    """

    # =========================================================================
    # NESTED: Assertion Helpers
    # =========================================================================

    class Assertions:
        """Helper methods for test assertions."""

        @staticmethod
        def assert_result_success(result: FlextResult[T]) -> None:
            """Assert result is successful."""
            assert result.is_success, f"Expected success, got: {result.error}"

        @staticmethod
        def assert_result_failure(
            result: FlextResult[T],
            error_contains: str | None = None
        ) -> None:
            """Assert result is failure."""
            assert result.is_failure, f"Expected failure, got: {result}"
            if error_contains:
                error_msg = str(result.error).lower() if result.error else ""
                assert error_contains.lower() in error_msg

    # =========================================================================
    # BUSINESS RULES - COMMAND EXECUTION STATE VALIDATION TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize(
        ("current_status", "required_status", "operation"),
        [
            (
                TestMixins.BusinessRules.CommandStates.RUNNING,
                TestMixins.BusinessRules.CommandStates.RUNNING,
                "test",
            ),
            (
                TestMixins.BusinessRules.CommandStates.COMPLETED,
                TestMixins.BusinessRules.CommandStates.COMPLETED,
                "deploy",
            ),
            (
                TestMixins.BusinessRules.CommandStates.PAUSED,
                TestMixins.BusinessRules.CommandStates.PAUSED,
                "pause_op",
            ),
        ],
    )
    def test_command_execution_state_valid(
        self, current_status: str, required_status: str, operation: str
    ) -> None:
        """Test command execution state validation with valid states."""
        result = FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
            current_status=current_status,
            required_status=required_status,
            operation=operation,
        )
        self.Assertions.assert_result_success(result)

    @pytest.mark.parametrize(
        ("current_status", "required_status", "operation"),
        [
            (
                TestMixins.BusinessRules.CommandStates.STOPPED,
                TestMixins.BusinessRules.CommandStates.RUNNING,
                "migrate",
            ),
            (
                TestMixins.BusinessRules.CommandStates.FAILED,
                TestMixins.BusinessRules.CommandStates.RUNNING,
                "sync",
            ),
            (
                TestMixins.BusinessRules.CommandStates.PAUSED,
                TestMixins.BusinessRules.CommandStates.COMPLETED,
                "finalize",
            ),
        ],
    )
    def test_command_execution_state_invalid(
        self, current_status: str, required_status: str, operation: str
    ) -> None:
        """Test command execution state validation with invalid states."""
        result = FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
            current_status=current_status,
            required_status=required_status,
            operation=operation,
        )
        self.Assertions.assert_result_failure(result, operation)

    # =========================================================================
    # BUSINESS RULES - SESSION STATE VALIDATION TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize(
        ("current_status", "valid_states"),
        [
            (
                TestMixins.BusinessRules.SessionStates.ACTIVE,
                [
                    TestMixins.BusinessRules.SessionStates.ACTIVE,
                    TestMixins.BusinessRules.SessionStates.IDLE,
                ],
            ),
            (
                TestMixins.BusinessRules.SessionStates.IDLE,
                [
                    TestMixins.BusinessRules.SessionStates.ACTIVE,
                    TestMixins.BusinessRules.SessionStates.IDLE,
                ],
            ),
            (
                TestMixins.BusinessRules.SessionStates.ACTIVE,
                [TestMixins.BusinessRules.SessionStates.ACTIVE],
            ),
        ],
    )
    def test_session_state_valid(
        self, current_status: str, valid_states: list[str]
    ) -> None:
        """Test session state validation with valid states."""
        result = FlextCliMixins.BusinessRulesMixin.validate_session_state(
            current_status=current_status,
            valid_states=valid_states,
        )
        self.Assertions.assert_result_success(result)

    @pytest.mark.parametrize(
        ("current_status", "valid_states"),
        [
            (
                TestMixins.BusinessRules.SessionStates.ERROR,
                [
                    TestMixins.BusinessRules.SessionStates.ACTIVE,
                    TestMixins.BusinessRules.SessionStates.IDLE,
                ],
            ),
            (
                TestMixins.BusinessRules.SessionStates.CLOSED,
                [TestMixins.BusinessRules.SessionStates.ACTIVE],
            ),
        ],
    )
    def test_session_state_invalid(
        self, current_status: str, valid_states: list[str]
    ) -> None:
        """Test session state validation with invalid states."""
        result = FlextCliMixins.BusinessRulesMixin.validate_session_state(
            current_status=current_status,
            valid_states=valid_states,
        )
        self.Assertions.assert_result_failure(result, current_status)

    # =========================================================================
    # BUSINESS RULES - PIPELINE STEP VALIDATION TESTS (Parametrized)
    # =========================================================================

    def test_pipeline_step_valid(self) -> None:
        """Test pipeline step validation with valid step."""
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(
            TestMixins.BusinessRules.PipelineSteps.VALID_STEP
        )
        self.Assertions.assert_result_success(result)

    @pytest.mark.parametrize(
        "step",
        [
            None,
            {},
        ],
    )
    def test_pipeline_step_empty(
        self,
        step: dict[
            str, str | int | float | bool | dict[str, object] | list[object] | None
        ]
        | None,
    ) -> None:
        """Test pipeline step validation with empty/None step."""
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
        self.Assertions.assert_result_failure(result)
        # Check for appropriate error message based on step type
        if step is None:
            # None should return "non-empty" message
            assert "non-empty" in str(result.error).lower()
        else:
            # Empty dict should return "name" message (no name field)
            assert "name" in str(result.error).lower()

    @pytest.mark.parametrize(
        "step",
        [
            TestMixins.BusinessRules.PipelineSteps.STEP_NO_NAME,
            TestMixins.BusinessRules.PipelineSteps.STEP_EMPTY_NAME,
            TestMixins.BusinessRules.PipelineSteps.STEP_WHITESPACE_NAME,
        ],
    )
    def test_pipeline_step_invalid_name(
        self,
        step: dict[
            str, str | int | float | bool | dict[str, object] | list[object] | None
        ],
    ) -> None:
        """Test pipeline step validation with invalid name."""
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
        self.Assertions.assert_result_failure(result, "name")

    # =========================================================================
    # BUSINESS RULES - CONFIGURATION CONSISTENCY VALIDATION TESTS
    # =========================================================================

    def test_configuration_consistency_valid(self) -> None:
        """Test configuration consistency validation with valid config."""
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            TestMixins.BusinessRules.ConfigData.VALID_CONFIG,
            TestMixins.BusinessRules.ConfigData.REQUIRED_FIELDS_COMPLETE,
        )
        self.Assertions.assert_result_success(result)

    def test_configuration_consistency_missing_fields(self) -> None:
        """Test configuration consistency with missing required fields."""
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            TestMixins.BusinessRules.ConfigData.INCOMPLETE_CONFIG,
            TestMixins.BusinessRules.ConfigData.REQUIRED_FIELDS_INCOMPLETE,
        )
        self.Assertions.assert_result_failure(result, "field2")

    def test_configuration_consistency_none_config(self) -> None:
        """Test configuration consistency with None config."""
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            None,
            TestMixins.BusinessRules.ConfigData.REQUIRED_FIELDS_COMPLETE,
        )
        self.Assertions.assert_result_failure(result)

    # =========================================================================
    # CLI COMMAND MIXIN - EXECUTE WITH CONTEXT TESTS
    # =========================================================================

    def test_execute_with_cli_context_success(self) -> None:
        """Test CLI context execution with successful handler."""

        def success_handler(
            **kwargs: FlextTypes.JsonValue,
        ) -> FlextResult[FlextTypes.JsonValue]:
            return FlextResult[FlextTypes.JsonValue].ok({
                TestMixins.CliCommand.SUCCESS_RESULT_KEY: TestMixins.CliCommand.SUCCESS_RESULT_VALUE,
                **kwargs,
            })

        result = FlextCliMixins.CliCommandMixin.execute_with_cli_context(
            operation=TestMixins.CliCommand.OPERATION_NAME,
            handler=success_handler,
            **{
                TestMixins.CliCommand.TEST_PARAM_KEY: TestMixins.CliCommand.TEST_PARAM_VALUE
            },
        )

        self.Assertions.assert_result_success(result)
        data = result.unwrap()
        assert isinstance(data, dict)
        assert (
            data.get(TestMixins.CliCommand.SUCCESS_RESULT_KEY)
            == TestMixins.CliCommand.SUCCESS_RESULT_VALUE
        )
        assert (
            data.get(TestMixins.CliCommand.TEST_PARAM_KEY)
            == TestMixins.CliCommand.TEST_PARAM_VALUE
        )

    def test_execute_with_cli_context_failure(self) -> None:
        """Test CLI context execution with failing handler."""

        def failure_handler(
            **kwargs: FlextTypes.JsonValue,
        ) -> FlextResult[FlextTypes.JsonValue]:
            return FlextResult[FlextTypes.JsonValue].fail(
                TestMixins.CliCommand.TEST_ERROR_MSG
            )

        result = FlextCliMixins.CliCommandMixin.execute_with_cli_context(
            operation=TestMixins.CliCommand.OPERATION_NAME,
            handler=failure_handler,
        )

        self.Assertions.assert_result_failure(
            result, TestMixins.CliCommand.TEST_ERROR_MSG
        )

    @pytest.mark.parametrize(
        "extra_params",
        [
            {},
            {"param1": "value1"},
            {"param1": "value1", "param2": "value2"},
        ],
    )
    def test_execute_with_cli_context_various_params(
        self, extra_params: dict[str, str]
    ) -> None:
        """Test CLI context execution with various parameter combinations."""

        def params_handler(
            **kwargs: FlextTypes.JsonValue,
        ) -> FlextResult[FlextTypes.JsonValue]:
            return FlextResult[FlextTypes.JsonValue].ok(dict(kwargs))

        result = FlextCliMixins.CliCommandMixin.execute_with_cli_context(
            operation=TestMixins.CliCommand.OPERATION_NAME,
            handler=params_handler,
            **extra_params,
        )

        self.Assertions.assert_result_success(result)
        data = result.unwrap()
        assert isinstance(data, dict)
        for key, value in extra_params.items():
            assert data.get(key) == value
