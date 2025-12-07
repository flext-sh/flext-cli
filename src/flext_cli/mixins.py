"""FLEXT CLI Mixins - Single unified class following FLEXT standards.

**MODULE**: FlextCliMixins - Single primary class for CLI mixins
**SCOPE**: Business rules validation, CLI command execution patterns with decorator composition

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import (
    FlextDecorators,
    FlextMixins,
    FlextResult,
    r,
    t,
)

from flext_cli.protocols import p
from flext_cli.utilities import u


class FlextCliMixins(FlextMixins):
    """Single unified CLI mixins class following FLEXT standards.

    Business Rules:
    ───────────────
    1. BusinessRulesMixin delegates to u.CliValidation (SRP)
    2. CliCommandMixin composes flext-core decorators for command execution
    3. Command execution MUST use railway pattern for error handling
    4. Context management MUST include correlation ID and operation logging
    5. Performance tracking MUST be enabled for all command executions
    6. Double-wrapped FlextResult MUST be unwrapped correctly
    7. Non-FlextResult returns MUST be wrapped in FlextResult
    8. All mixin methods MUST be static (no instance state)

    Architecture Implications:
    ───────────────────────────
    - BusinessRulesMixin is a delegating facade (backward compatibility)
    - CliCommandMixin composes decorators in correct order
    - Railway decorator ensures FlextResult return type
    - Performance tracking via track_performance decorator
    - Operation logging via log_operation decorator
    - Extends x for base mixin functionality

    Audit Implications:
    ───────────────────
    - Command executions MUST be logged with operation name and correlation ID
    - Performance metrics MUST be logged for monitoring
    - Business rule violations MUST be logged with context
    - Decorator composition MUST preserve error handling chain

    Contains all mixin subclasses for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.
    """

    # =========================================================================
    # CLI COMMAND MIXIN - Decorator composition for CLI commands
    # =========================================================================

    # =========================================================================
    # BUSINESS RULES MIXIN - Delegating facade to u.CliValidation
    # =========================================================================

    class BusinessRulesMixin:
        """Mixin providing common business rule validation patterns for CLI classes.

        NOTE: This is a delegating facade. The actual implementation has been
        consolidated into u.CliValidation to follow SRP principles.
        This class is maintained for backward compatibility with existing code.
        """

        @staticmethod
        def validate_command_execution_state(
            current_status: str,
            required_status: str,
            operation: str,
        ) -> r[bool]:
            """Validate command execution state for operations (delegates to utilities)."""
            return u.CliValidation.v_state(
                current_status,
                required=required_status,
                name=operation,
            )

        @staticmethod
        def validate_session_state(
            current_status: str,
            valid_states: list[str],
        ) -> r[bool]:
            """Validate session state (delegates to utilities)."""
            return u.CliValidation.v_session(current_status, valid=valid_states)

        @staticmethod
        def validate_pipeline_step(
            step: t.Json.JsonDict | None,
        ) -> r[bool]:
            """Validate pipeline step configuration (delegates to utilities)."""
            return u.CliValidation.v_step(step)

        @staticmethod
        def validate_configuration_consistency(
            config_data: t.Json.JsonDict | None,
            required_fields: list[str],
        ) -> r[bool]:
            """Validate configuration consistency (delegates to utilities)."""
            return u.CliValidation.v_config(config_data, fields=required_fields)

    class CliCommandMixin:
        """Mixin providing CLI command execution patterns with flext-core decorators.

        **PURPOSE**: Eliminate repetitive decorator application and context setup.

        Provides helper methods that compose flext-core decorators for common
        CLI command patterns. Reduces 18 lines of context setup per command to
        a single method call.
        """

        @staticmethod
        def execute_with_cli_context(
            operation: str,
            handler: p.Cli.CliCommandHandler,
            **context_data: t.GeneralValueType,
        ) -> r[t.GeneralValueType]:
            """Execute handler with automatic CLI context management.

            Composes flext-core decorators to provide complete context setup:
            - Correlation ID generation and management
            - Operation logging with structured context
            - Performance tracking
            - Railway pattern error handling

            Args:
                operation: Operation name (e.g., "migrate", "validate")
                handler: Handler function to execute with context
                **context_data: Additional context data for logging

            Returns:
                FlextResult from handler execution

            """
            # Compose decorators in correct order (outermost to innermost)
            # log_operation already handles correlation internally via track_perf=True
            # Access decorators as static methods
            railway_decorator = FlextDecorators.railway()
            track_perf_decorator = FlextDecorators.track_performance()
            log_op_decorator = FlextDecorators.log_operation(operation, track_perf=True)

            wrapped_handler = railway_decorator(
                track_perf_decorator(
                    log_op_decorator(handler),
                ),
            )

            # Execute with composed decorators
            # Railway decorator ensures handler_result is always r[GeneralValueType]
            handler_result = wrapped_handler(**context_data)

            # Type narrowing: railway decorator ensures r return
            # Handle both single and double-wrapped r cases
            # Check if handler_result is not FlextResult first (fallback case)
            if not isinstance(handler_result, FlextResult):
                # Fallback: wrap non-FlextResult returns (defensive coding)
                # This path is unreachable if decorators work correctly but kept for runtime safety
                # handler_result is not FlextResult at this point, convert to GeneralValueType
                converted_handler_result: t.GeneralValueType
                if isinstance(
                    handler_result,
                    (str, int, float, bool, type(None), dict, list),
                ):
                    converted_handler_result = handler_result
                else:
                    converted_handler_result = str(handler_result)
                return r[t.GeneralValueType].ok(converted_handler_result)

            # Check if it's a double-wrapped r[r[...]]
            if handler_result.is_success:
                inner_value = handler_result.unwrap()
                if isinstance(inner_value, FlextResult):
                    # Double-wrapped: unwrap inner FlextResult
                    # Type narrowing: inner_value is r[t.GeneralValueType] after isinstance check
                    return inner_value
                # Single-wrapped with value: extract value and wrap in new FlextResult
                # inner_value is not FlextResult at this point (after isinstance check)
                # inner_value is object from unwrap - convert to GeneralValueType
                converted_value: t.GeneralValueType
                if isinstance(
                    inner_value,
                    (str, int, float, bool, type(None), dict, list),
                ):
                    converted_value = inner_value
                else:
                    converted_value = str(inner_value)
                return r[t.GeneralValueType].ok(converted_value)
            # Failure case: unwrap and re-wrap to ensure correct type
            error_msg = handler_result.error or "Unknown error"
            return r[t.GeneralValueType].fail(error_msg)


x = FlextCliMixins

__all__ = ["FlextCliMixins", "x"]
