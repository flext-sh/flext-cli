"""FLEXT CLI Mixins - Single unified class following FLEXT standards.

Common validation and factory patterns for CLI operations.
Single FlextCliMixins class with nested mixin subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import cast

from flext_core import (
    FlextDecorators,
    FlextMixins,
    FlextResult,
    FlextTypes,
    FlextUtilities,
)

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import FlextCliTypes


class FlextCliMixins(FlextMixins):
    """Single unified CLI mixins class following FLEXT standards.

    Contains all mixin subclasses for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.
    """

    # =========================================================================
    # VALIDATION MIXIN - REMOVED
    # All validation logic moved to Pydantic v2 field constraints
    # =========================================================================

    # =========================================================================
    # FACTORY MIXIN - Common factory patterns
    # =========================================================================

    # Removed - use FlextResult[T].ok() and FlextResult[T].fail() directly

    # =========================================================================
    # BUSINESS RULES MIXIN - Common business rule validation patterns
    # =========================================================================

    class BusinessRulesMixin:
        """Mixin providing common business rule validation patterns for CLI classes.

        Contains reusable business rule validation methods.
        """

        @staticmethod
        def validate_command_execution_state(
            current_status: str, required_status: str, operation: str
        ) -> FlextResult[bool]:
            """Validate command execution state for operations.

            Args:
                current_status: Current command status
                required_status: Required status for the operation
                operation: Name of the operation being performed

            Returns:
                FlextResult[bool]: True if validation passed, failure on error

            """
            if current_status != required_status:
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.COMMAND_STATE_INVALID.format(
                        operation=operation,
                        current_status=current_status,
                        required_status=required_status,
                    )
                )
            return FlextResult[bool].ok(True)

        @staticmethod
        def validate_session_state(
            current_status: str, valid_states: list[str]
        ) -> FlextResult[bool]:
            """Validate session state.

            Args:
                current_status: Current session status
                valid_states: List of valid session states

            Returns:
                FlextResult[bool]: True if validation passed, failure on error

            """
            if current_status not in valid_states:
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.SESSION_STATUS_INVALID.format(
                        current_status=current_status, valid_states=valid_states
                    )
                )
            return FlextResult[bool].ok(True)

        @staticmethod
        def validate_pipeline_step(
            step: FlextCliTypes.Data.CliDataDict | None,
        ) -> FlextResult[bool]:
            """Validate pipeline step configuration.

            Args:
                step: Pipeline step dictionary to validate

            Returns:
                FlextResult[bool]: True if validation passed, failure on error

            """
            # Fast-fail if step is None - no fallback
            if step is None:
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.PIPELINE_STEP_EMPTY
                )

            if FlextCliConstants.MixinsFieldNames.PIPELINE_STEP_NAME not in step:
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.PIPELINE_STEP_NO_NAME
                )

            step_name = step[FlextCliConstants.MixinsFieldNames.PIPELINE_STEP_NAME]
            # Fast-fail validation - no fallback
            if not step_name:
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.PIPELINE_STEP_NAME_EMPTY
                )
            step_name_str = str(step_name)
            # Use FlextUtilities.Validation for step name validation
            try:
                FlextUtilities.Validation.validate_required_string(
                    step_name_str, "Pipeline step name"
                )
            except ValueError:
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.PIPELINE_STEP_NAME_EMPTY
                )

            return FlextResult[bool].ok(True)

        @staticmethod
        def validate_configuration_consistency(
            config_data: FlextCliTypes.Data.CliDataDict | None,
            required_fields: list[str],
        ) -> FlextResult[bool]:
            """Validate configuration consistency.

            Args:
                config_data: Configuration data to validate
                required_fields: List of required field names

            Returns:
                FlextResult[bool]: True if validation passed, failure on error

            """
            # Fast-fail if config_data is None - no fallback
            if config_data is None:
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.CONFIG_MISSING_FIELDS.format(
                        missing_fields=required_fields
                    )
                )
            missing_fields = [
                field for field in required_fields if field not in config_data
            ]
            if missing_fields:
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.CONFIG_MISSING_FIELDS.format(
                        missing_fields=missing_fields
                    )
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

        **ELIMINATES**:
        - Manual correlation_id generation (2 lines)
        - FlextContext setup calls (4 lines)
        - Scoped context manager boilerplate (8 lines)
        - Manual context cleanup (4 lines)
        Total: 18 lines per command

        **USAGE**:
            ```python
            from flext_cli import FlextCliMixins
            from flext_core import FlextDecorators, FlextResult


            class MyCli(FlextCliMixins.CliCommandMixin):
                def execute_command(self, operation: str) -> FlextResult[bool]:
                    # Use mixin method for automatic decorator composition
                    return self.execute_with_cli_context(
                        operation="migrate",
                        handler=self._do_migration,
                        input_dir="data",
                        output_dir="out",
                    )

                def _do_migration(self, **kwargs) -> FlextResult[bool]:
                    # Just implement logic - context already set up!
                    return FlextResult[bool].ok(True)
            ```
        """

        @staticmethod
        def execute_with_cli_context(
            operation: str,
            handler: FlextCliTypes.Callable.HandlerFunction,
            **context_data: FlextTypes.JsonValue,
        ) -> FlextResult[FlextTypes.JsonValue]:
            """Execute handler with automatic CLI context management.

            Composes flext-core decorators to provide complete context setup:
            - Correlation ID generation and management
            - Operation logging with structured context
            - Performance tracking
            - Railway pattern error handling

            **ELIMINATES**:
            - Manual correlation_id = FlextContext.Correlation.generate_correlation_id()
            - Manual FlextContext.Correlation.set_correlation_id(correlation_id)
            - Manual FlextContext.Request.set_operation_name(operation)
            - Manual with FlextLogger.scoped_context(...)
            - Manual context cleanup

            Args:
                operation: Operation name (e.g., "migrate", "validate")
                handler: Handler function to execute with context
                **context_data: Additional context data for logging

            Returns:
                FlextResult from handler execution

            Example:
                ```python
                class client-aOudMigrationCli(FlextCliMixins.CliCommandMixin):
                    def _execute_migrate(
                        self, args: list[str]
                    ) -> FlextResult[FlextTypes.JsonValue]:
                        # Single line replaces 18 lines of boilerplate!
                        return self.execute_with_cli_context(
                            operation="migrate",
                            handler=self._run_migration_service,
                            input_dir=args[0],
                            output_dir=args[1],
                        )

                    def _run_migration_service(
                        self, **kwargs
                    ) -> FlextResult[FlextTypes.JsonValue]:
                        # Context auto-managed - just implement logic
                        service = client-aOudMigrationService(**kwargs)
                        return service.execute()
                ```

            **DECORATOR COMPOSITION** (applied in correct order):
            ```
            @FlextDecorators.railway          # Outermost - converts exceptions
            @FlextDecorators.track_performance # Track execution time
            @FlextDecorators.log_operation     # Log with context
            @FlextDecorators.with_correlation  # Correlation ID management
            ```

            """
            # Compose decorators in correct order (outermost to innermost)
            # Railway must be outermost to catch all exceptions
            wrapped_handler = FlextDecorators.railway()(
                FlextDecorators.track_performance()(
                    FlextDecorators.log_operation(operation)(
                        FlextDecorators.with_correlation()(handler)
                    )
                )
            )

            # Execute with composed decorators
            # Handler returns FlextResult[FlextTypes.JsonValue]
            # context_data is already correctly typed
            # The railway decorator ensures the handler result is wrapped in FlextResult
            # If handler already returns FlextResult, railway returns it as-is (no double wrapping)
            handler_result = wrapped_handler(**context_data)
            # Type cast: railway decorator may wrap or return as-is, but we know it's FlextResult[JsonValue]
            result: FlextResult[FlextTypes.JsonValue] = cast(
                "FlextResult[FlextTypes.JsonValue]", handler_result
            )
            return result


__all__ = [
    "FlextCliMixins",
]
