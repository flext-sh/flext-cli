"""FLEXT CLI Mixins - Single unified class following FLEXT standards.

**MODULE**: FlextCliMixins - Single primary class for CLI mixins
**SCOPE**: Business rules validation, CLI command execution patterns with decorator composition

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import (
    FlextMixins,
    FlextResult,
    FlextRuntime,
    FlextUtilities,
)
from flext_core.decorators import FlextDecorators

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import CliJsonValue, FlextCliTypes


class FlextCliMixins(FlextMixins):
    """Single unified CLI mixins class following FLEXT standards.

    Contains all mixin subclasses for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.
    """

    # =========================================================================
    # BUSINESS RULES MIXIN - Common business rule validation patterns
    # =========================================================================

    class BusinessRulesMixin:
        """Mixin providing common business rule validation patterns for CLI classes.

        Contains reusable business rule validation methods.
        """

        @staticmethod
        def validate_command_execution_state(
            current_status: str,
            required_status: str,
            operation: str,
        ) -> FlextResult[bool]:
            """Validate command execution state for operations."""
            if current_status != required_status:
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.COMMAND_STATE_INVALID.format(
                        operation=operation,
                        current_status=current_status,
                        required_status=required_status,
                    ),
                )
            return FlextResult[bool].ok(True)

        @staticmethod
        def validate_session_state(
            current_status: str,
            valid_states: list[str],
        ) -> FlextResult[bool]:
            """Validate session state."""
            if current_status not in valid_states:
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.SESSION_STATUS_INVALID.format(
                        current_status=current_status,
                        valid_states=valid_states,
                    ),
                )
            return FlextResult[bool].ok(True)

        @staticmethod
        def validate_pipeline_step(
            step: FlextCliTypes.Data.CliDataDict | None,
        ) -> FlextResult[bool]:
            """Validate pipeline step configuration."""
            if step is None:
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.PIPELINE_STEP_EMPTY,
                )

            if FlextCliConstants.MixinsFieldNames.PIPELINE_STEP_NAME not in step:
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.PIPELINE_STEP_NO_NAME,
                )

            step_name = step[FlextCliConstants.MixinsFieldNames.PIPELINE_STEP_NAME]
            if not step_name:
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.PIPELINE_STEP_NAME_EMPTY,
                )

            step_name_str = str(step_name)
            try:
                FlextUtilities.Validation.validate_required_string(
                    step_name_str,
                    "Pipeline step name",
                )
            except ValueError:
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.PIPELINE_STEP_NAME_EMPTY,
                )

            return FlextResult[bool].ok(True)

        @staticmethod
        def validate_configuration_consistency(
            config_data: FlextCliTypes.Data.CliDataDict | None,
            required_fields: list[str],
        ) -> FlextResult[bool]:
            """Validate configuration consistency."""
            if config_data is None:
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.CONFIG_MISSING_FIELDS.format(
                        missing_fields=required_fields,
                    ),
                )

            missing_fields = [
                field for field in required_fields if field not in config_data
            ]
            if missing_fields:
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.CONFIG_MISSING_FIELDS.format(
                        missing_fields=missing_fields,
                    ),
                )

            return FlextResult[bool].ok(True)

    # =========================================================================
    # CLI COMMAND MIXIN - Decorator composition for CLI commands
    # =========================================================================

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
            handler: FlextCliTypes.Callable.HandlerFunction,
            **context_data: CliJsonValue,
        ) -> FlextResult[CliJsonValue]:
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
            wrapped_handler = FlextDecorators.railway()(
                FlextDecorators.track_performance()(
                    FlextDecorators.log_operation(operation)(
                        FlextDecorators.with_correlation()(handler),
                    ),
                ),
            )

            # Execute with composed decorators
            handler_result = wrapped_handler(**context_data)

            # Type narrowing: railway decorator ensures FlextResult return
            # Handle both single and double-wrapped FlextResult cases
            if isinstance(handler_result, FlextResult):
                # Check if it's a double-wrapped FlextResult[FlextResult[...]]
                if handler_result.is_success:
                    inner_value = handler_result.unwrap()
                    if isinstance(inner_value, FlextResult):
                        # Double-wrapped: unwrap inner FlextResult
                        # Type narrowing: inner_value is FlextResult[CliJsonValue]
                        return inner_value
                    # Single-wrapped with value: extract value and wrap in new FlextResult
                    # inner_value is CliJsonValue
                    return FlextResult[CliJsonValue].ok(inner_value)
                # Failure case: unwrap and re-wrap to ensure correct type
                error_msg = handler_result.error or "Unknown error"
                return FlextResult[CliJsonValue].fail(error_msg)

            # If not FlextResult, wrap it (railway should have done this, but defensive)
            # This should not happen if decorators work correctly
            if FlextRuntime.is_dict_like(handler_result):
                return FlextResult[CliJsonValue].ok(handler_result)
            if FlextRuntime.is_list_like(handler_result):
                return FlextResult[CliJsonValue].ok(handler_result)
            if isinstance(handler_result, (str, int, float, bool, type(None))):
                return FlextResult[CliJsonValue].ok(handler_result)

            # Fallback: wrap any other type
            return FlextResult[CliJsonValue].ok(handler_result)


__all__ = ["FlextCliMixins"]
