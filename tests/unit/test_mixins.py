"""FLEXT CLI Mixins Tests - Comprehensive Mixins Validation Testing.

Tests for FlextCliMixins covering business rules validation (command/session state,
pipeline steps, configuration consistency), CLI command mixin execution, and edge cases
with 100% coverage.

Modules tested: flext_cli.mixins.FlextCliMixins (BusinessRulesMixin, m.CommandMixin)
Scope: All validation methods, CLI context execution, error handling, edge cases

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TypeVar, cast

import pytest
from flext_core import t
from flext_tests import tm

from flext_cli import FlextCliMixins, p, r

T = TypeVar("T")


class TestsCliMixins:
    """Comprehensive test suite for FlextCliMixins validation and composition.

    Single class with nested helper classes and methods organized by functionality.
    Uses factories, constants, dynamic tests, and helpers to reduce code while
    maintaining and expanding coverage.
    """

    # =========================================================================
    # NESTED: Assertion Helpers
    # =========================================================================

    # Assertions removed - use FlextTestsMatchers directly

    # =========================================================================
    # BUSINESS RULES - COMMAND EXECUTION STATE VALIDATION TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize(
        ("current_status", "required_status", "operation"),
        [
            (
                "running",
                "running",
                "test",
            ),
            (
                "completed",
                "completed",
                "deploy",
            ),
            (
                "paused",
                "paused",
                "pause_op",
            ),
        ],
    )
    def test_command_execution_state_valid(
        self,
        current_status: str,
        required_status: str,
        operation: str,
    ) -> None:
        """Test command execution state validation with valid states."""
        result = FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
            current_status=current_status,
            required_status=required_status,
            operation=operation,
        )
        tm.ok(result)

    @pytest.mark.parametrize(
        ("current_status", "required_status", "operation"),
        [
            (
                "stopped",
                "running",
                "migrate",
            ),
            (
                "failed",
                "running",
                "sync",
            ),
            (
                "paused",
                "completed",
                "finalize",
            ),
        ],
    )
    def test_command_execution_state_invalid(
        self,
        current_status: str,
        required_status: str,
        operation: str,
    ) -> None:
        """Test command execution state validation with invalid states."""
        result = FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
            current_status=current_status,
            required_status=required_status,
            operation=operation,
        )
        tm.fail(result, has=operation)

    # =========================================================================
    # BUSINESS RULES - SESSION STATE VALIDATION TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize(
        ("current_status", "valid_states"),
        [
            (
                "active",
                [
                    "active",
                    "idle",
                ],
            ),
            (
                "idle",
                [
                    "active",
                    "idle",
                ],
            ),
            (
                "active",
                ["active"],
            ),
        ],
    )
    def test_session_state_valid(
        self,
        current_status: str,
        valid_states: list[str],
    ) -> None:
        """Test session state validation with valid states."""
        result = FlextCliMixins.BusinessRulesMixin.validate_session_state(
            current_status=current_status,
            valid_states=valid_states,
        )
        tm.ok(result)

    @pytest.mark.parametrize(
        ("current_status", "valid_states"),
        [
            (
                "error",
                [
                    "active",
                    "idle",
                ],
            ),
            (
                "closed",
                ["active"],
            ),
        ],
    )
    def test_session_state_invalid(
        self,
        current_status: str,
        valid_states: list[str],
    ) -> None:
        """Test session state validation with invalid states."""
        result = FlextCliMixins.BusinessRulesMixin.validate_session_state(
            current_status=current_status,
            valid_states=valid_states,
        )
        tm.fail(result, has=current_status)

    # =========================================================================
    # BUSINESS RULES - PIPELINE STEP VALIDATION TESTS (Parametrized)
    # =========================================================================

    def test_pipeline_step_valid(self) -> None:
        """Test pipeline step validation with valid step."""
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(
            cast(
                "t.Json.JsonDict | None",
                "valid_step",
            ),
        )
        tm.ok(result)

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
            str,
            str | int | float | bool | dict[str, object] | list[object] | None,
        ]
        | None,
    ) -> None:
        """Test pipeline step validation with empty/None step."""
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(
            cast("t.Json.JsonDict | None", step),
        )
        tm.fail(result)
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
            "",
            "   ",
        ],
    )
    def test_pipeline_step_invalid_name(
        self,
        step: dict[
            str,
            str | int | float | bool | dict[str, object] | list[object] | None,
        ],
    ) -> None:
        """Test pipeline step validation with invalid name."""
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(
            cast("t.Json.JsonDict | None", step),
        )
        tm.fail(result, has="name")

    # =========================================================================
    # BUSINESS RULES - CONFIGURATION CONSISTENCY VALIDATION TESTS
    # =========================================================================

    def test_configuration_consistency_valid(self) -> None:
        """Test configuration consistency validation with valid config."""
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            cast(
                "t.Json.JsonDict | None",
                {"debug": True, "timeout": 30},
            ),
            ["debug", "timeout"],
        )
        tm.ok(result)

    def test_configuration_consistency_missing_fields(self) -> None:
        """Test configuration consistency with missing required fields."""
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            cast(
                "t.Json.JsonDict | None",
                {"debug": True},
            ),
            ["debug", "timeout"],
        )
        tm.fail(result, has="field2")

    def test_configuration_consistency_none_config(self) -> None:
        """Test configuration consistency with None config."""
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            None,
            ["debug", "timeout"],
        )
        tm.fail(result)

    # =========================================================================
    # CLI COMMAND MIXIN - EXECUTE WITH CONTEXT TESTS
    # =========================================================================

    def test_execute_with_cli_context_success(self) -> None:
        """Test CLI context execution with successful handler."""
        # Test constants for command execution
        success_result_key = "success"
        success_result_value = "completed"
        operation_name = "test_operation"
        test_param_key = "test_param"
        test_param_value = "test_value"

        def success_handler(
            **kwargs: t.JsonValue,
        ) -> r[t.JsonValue]:
            return r[t.JsonValue].ok({
                success_result_key: success_result_value,
                **kwargs,
            })

        result = FlextCliMixins.CliCommandMixin.execute_with_cli_context(
            operation=operation_name,
            handler=cast("p.Cli.CliCommandHandler", success_handler),
            **{test_param_key: test_param_value},
        )

        tm.ok(result)
        data = result.unwrap()
        assert isinstance(data, dict)
        assert data.get(success_result_key) == success_result_value
        assert data.get(test_param_key) == test_param_value

    def test_execute_with_cli_context_failure(self) -> None:
        """Test CLI context execution with failing handler."""
        operation_name = "test_operation"
        test_error_msg = "Test error message"

        def failure_handler(
            **kwargs: t.JsonValue,
        ) -> r[t.JsonValue]:
            return r[t.JsonValue].fail(test_error_msg)

        result = FlextCliMixins.CliCommandMixin.execute_with_cli_context(
            operation=operation_name,
            handler=cast("p.Cli.CliCommandHandler", failure_handler),
        )

        tm.fail(result, has=test_error_msg)

    @pytest.mark.parametrize(
        "extra_params",
        [
            {},
            {"param1": "value1"},
            {"param1": "value1", "param2": "value2"},
        ],
    )
    def test_execute_with_cli_context_various_params(
        self,
        extra_params: dict[str, str],
    ) -> None:
        """Test CLI context execution with various parameter combinations."""

        def params_handler(
            **kwargs: t.JsonValue,
        ) -> r[t.JsonValue]:
            return r[t.JsonValue].ok(dict(kwargs))

        operation_name = "test_operation"
        result = FlextCliMixins.CliCommandMixin.execute_with_cli_context(
            operation=operation_name,
            handler=cast("p.Cli.CliCommandHandler", params_handler),
            **extra_params,
        )

        tm.ok(result)
        data = result.unwrap()
        assert isinstance(data, dict)
        for key, value in extra_params.items():
            assert data.get(key) == value
