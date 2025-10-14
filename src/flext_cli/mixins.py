"""FLEXT CLI Mixins - Single unified class following FLEXT standards.

Common validation and factory patterns for CLI operations.
Single FlextCliMixins class with nested mixin subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from urllib.parse import urlparse

from flext_core import FlextCore

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import FlextCliTypes


class FlextCliMixins(FlextCore.Mixins):
    """Single unified CLI mixins class following FLEXT standards.

    Contains all mixin subclasses for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.
    """

    # =========================================================================
    # VALIDATION MIXIN - Common validation utilities
    # =========================================================================

    class ValidationMixin:
        """Mixin providing common validation utilities for CLI classes.

        Contains reusable validation methods to eliminate duplication
        across CLI config and models classes.
        """

        @staticmethod
        def validate_not_empty(
            field_name: str, field_value: str | float | None
        ) -> FlextCore.Result[None]:
            """Validate that a field is not empty or whitespace.

            Args:
                field_name: Name of the field for error messages
                field_value: Value to validate (string, number, or boolean)

            Returns:
                FlextCore.Result[None]: Success or failure result

            """
            # Handle non-string types
            if not isinstance(field_value, str):
                if not field_value:  # Falsy values (0, False, None, empty collections)
                    return FlextCore.Result[None].fail(f"{field_name} cannot be empty")
                return FlextCore.Result[None].ok(None)

            # Handle string types
            if not field_value or not field_value.strip():
                return FlextCore.Result[None].fail(f"{field_name} cannot be empty")
            return FlextCore.Result[None].ok(None)

        @staticmethod
        def validate_url(field_name: str, url_value: str) -> FlextCore.Result[None]:
            """Validate that a URL field has proper format - delegates to FlextCliUtilities.

            Args:
                field_name: Name of the field for error messages
                url_value: URL string to validate

            Returns:
                FlextCore.Result[None]: Success or failure result

            """
            # Validate emptiness first
            if not url_value or not url_value.strip():
                return FlextCore.Result[None].fail(f"{field_name} cannot be empty")

            # Simple URL validation

            try:
                parsed = urlparse(url_value)
                if not parsed.scheme or not parsed.netloc:
                    return FlextCore.Result[None].fail(
                        f"{field_name} is not a valid URL"
                    )
            except Exception as e:
                return FlextCore.Result[None].fail(
                    f"{field_name} validation failed: {e}"
                )

            return FlextCore.Result[None].ok(None)

        @staticmethod
        def validate_enum_value(
            field_name: str, field_value: str, valid_values: FlextCore.Types.StringList
        ) -> FlextCore.Result[None]:
            """Validate that a field value is in the allowed list.

            Args:
                field_name: Name of the field for error messages
                field_value: Value to validate
                valid_values: List of valid values

            Returns:
                FlextCore.Result[None]: Success or failure result

            """
            if field_value not in valid_values:
                return FlextCore.Result[None].fail(
                    f"Invalid {field_name}. Valid values: {valid_values}"
                )
            return FlextCore.Result[None].ok(None)

        @staticmethod
        def validate_positive_number(
            field_name: str, field_value: int
        ) -> FlextCore.Result[None]:
            """Validate that a number field is positive.

            Args:
                field_name: Name of the field for error messages
                field_value: Number to validate

            Returns:
                FlextCore.Result[None]: Success or failure result

            """
            if field_value <= 0:
                return FlextCore.Result[None].fail(f"{field_name} must be positive")
            return FlextCore.Result[None].ok(None)

        @staticmethod
        def validate_non_negative_number(
            field_name: str, field_value: int
        ) -> FlextCore.Result[None]:
            """Validate that a number field is non-negative.

            Args:
                field_name: Name of the field for error messages
                field_value: Number to validate

            Returns:
                FlextCore.Result[None]: Success or failure result

            """
            if field_value < 0:
                return FlextCore.Result[None].fail(f"{field_name} cannot be negative")
            return FlextCore.Result[None].ok(None)

        @staticmethod
        def validate_output_format(format_value: str) -> FlextCore.Result[None]:
            """Validate output format against allowed values.

            Args:
                format_value: Output format to validate

            Returns:
                FlextCore.Result[None]: Success or failure result

            """
            return FlextCliMixins.ValidationMixin.validate_enum_value(
                "output format", format_value, FlextCliConstants.OUTPUT_FORMATS_LIST
            )

        @staticmethod
        def validate_log_level(log_level_value: str) -> FlextCore.Result[None]:
            """Validate log level against allowed values.

            Args:
                log_level_value: Log level to validate

            Returns:
                FlextCore.Result[None]: Success or failure result

            """
            return FlextCliMixins.ValidationMixin.validate_enum_value(
                "log level", log_level_value, FlextCliConstants.LOG_LEVELS_LIST
            )

        @staticmethod
        def validate_status(status_value: str) -> FlextCore.Result[None]:
            """Validate command status against allowed values.

            Args:
                status_value: Status to validate

            Returns:
                FlextCore.Result[None]: Success or failure result

            """
            return FlextCliMixins.ValidationMixin.validate_enum_value(
                "status", status_value, FlextCliConstants.COMMAND_STATUSES_LIST
            )

    # =========================================================================
    # FACTORY MIXIN - Common factory patterns
    # =========================================================================

    # Removed - use FlextCore.Result[T].ok() and FlextCore.Result[T].fail() directly

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
        ) -> FlextCore.Result[None]:
            """Validate command execution state for operations.

            Args:
                current_status: Current command status
                required_status: Required status for the operation
                operation: Name of the operation being performed

            Returns:
                FlextCore.Result[None]: Validation result

            """
            if current_status != required_status:
                return FlextCore.Result[None].fail(
                    f"Cannot {operation}: command is in '{current_status}' state, requires '{required_status}'"
                )
            return FlextCore.Result[None].ok(None)

        @staticmethod
        def validate_session_state(
            current_status: str, valid_states: FlextCore.Types.StringList
        ) -> FlextCore.Result[None]:
            """Validate session state.

            Args:
                current_status: Current session status
                valid_states: List of valid session states

            Returns:
                FlextCore.Result[None]: Validation result

            """
            if current_status not in valid_states:
                return FlextCore.Result[None].fail(
                    f"Invalid session status '{current_status}'. Valid states: {valid_states}"
                )
            return FlextCore.Result[None].ok(None)

        @staticmethod
        def validate_pipeline_step(
            step: FlextCliTypes.Data.CliDataDict | None,
        ) -> FlextCore.Result[None]:
            """Validate pipeline step configuration.

            Args:
                step: Pipeline step dictionary to validate

            Returns:
                FlextCore.Result[None]: Validation result

            """
            if not step:
                return FlextCore.Result[None].fail(
                    "Pipeline step must be a non-empty dictionary"
                )

            if "name" not in step:
                return FlextCore.Result[None].fail(
                    "Pipeline step must have a 'name' field"
                )

            if not step["name"] or not str(step["name"]).strip():
                return FlextCore.Result[None].fail("Pipeline step name cannot be empty")

            return FlextCore.Result[None].ok(None)

        @staticmethod
        def validate_configuration_consistency(
            config_data: FlextCliTypes.Data.CliDataDict | None,
            required_fields: FlextCore.Types.StringList,
        ) -> FlextCore.Result[None]:
            """Validate configuration consistency.

            Args:
                config_data: Configuration data to validate
                required_fields: List of required field names

            Returns:
                FlextCore.Result[None]: Validation result

            """
            missing_fields = [
                field
                for field in required_fields
                if config_data and field not in config_data
            ]
            if missing_fields:
                return FlextCore.Result[None].fail(
                    f"Missing required configuration fields: {missing_fields}"
                )

            return FlextCore.Result[None].ok(None)


__all__ = [
    "FlextCliMixins",
]
