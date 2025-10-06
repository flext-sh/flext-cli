"""FLEXT CLI Exceptions - Single unified class following FLEXT standards.

Provides CLI-specific exception handling using flext-core patterns.
Single FlextCliExceptions class with nested exception subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_core import FlextExceptions

from flext_cli.constants import FlextCliConstants


class FlextCliExceptions(FlextExceptions):
    """Single unified CLI exceptions class following FLEXT standards.

    Contains all exception subclasses for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.

    ARCHITECTURAL COMPLIANCE:
    - Inherits from FlextExceptions to avoid duplication
    - Uses centralized exception patterns from FlextExceptions
    - Implements CLI-specific extensions while reusing core functionality
    """

    class BaseError(FlextExceptions.BaseError):
        """Base CLI exception extending FlextExceptions.BaseError.

        Simple exception class for CLI error scenarios with error categorization
        and contextual information support using standard helper methods.
        """

        # Add context attribute for CLI-specific usage
        context: dict[str, object]

        @override
        def __init__(
            self,
            message: str,
            *,
            error_code: str | int = FlextCliConstants.ErrorCodes.CLI_ERROR,
            **kwargs: object,
        ) -> None:
            """Initialize CLI exception with message, error code, and context using helpers.

            Args:
                message: Error message
                error_code: CLI error code (string or int)
                **kwargs: Additional context (context, correlation_id)

            """
            # Convert int error codes to string for consistency
            if isinstance(error_code, int):
                error_code = str(error_code)

            # Default empty error_code to CLI_ERROR constant
            if not error_code:
                error_code = FlextCliConstants.ErrorCodes.CLI_ERROR

            # Extract common parameters using helper
            base_context, correlation_id, remaining = self._extract_common_kwargs(
                kwargs
            )

            # Build context merging base and remaining kwargs
            context = self._build_context(base_context, remaining)

            # Initialize context attribute before calling parent
            self.context = context or {}

            # Call parent with complete error information
            super().__init__(
                message,
                error_code=error_code,
                correlation_id=correlation_id,
                metadata=context,
            )

        @override
        def __str__(self) -> str:
            """Return string representation of the exception."""
            context_str = ""
            if self.context:
                context_items = [f"{k}={v}" for k, v in self.context.items()]
                context_str = f" ({', '.join(context_items)})"

            return f"[{self.error_code}] {self.message}{context_str}"

        @override
        def __repr__(self) -> str:
            """Return detailed representation for debugging."""
            return (
                f"FlextCliExceptions.BaseError("
                f"message='{self.message}', "
                f"error_code='{self.error_code}', "
                f"context={self.context})"
            )

        def get_context_value(self, key: str, default: object = None) -> object:
            """Get context value by key with optional default."""
            return self.context.get(key, default)

        def is_error_code(self, error_code: str) -> bool:
            """Check if exception matches specific error code."""
            return str(self.error_code) == error_code

        def _extract_common_kwargs(
            self, kwargs: dict[str, object]
        ) -> tuple[dict[str, object], str | None, dict[str, object]]:
            """Extract common kwargs for exception initialization.

            If context is provided as a dict, use it as base context.
            If context is provided as a non-dict value, treat it as a regular kwarg.
            """
            context = kwargs.get("context")
            base_context: dict[str, object] = {}
            remaining: dict[str, object] = {}

            # If context is a dict, use it as base context
            if isinstance(context, dict):
                base_context = context
                # Remaining excludes both context and correlation_id
                remaining = {
                    k: v
                    for k, v in kwargs.items()
                    if k not in {"context", "correlation_id"}
                }
            else:
                # If context is not a dict, treat all kwargs (including context) as remaining
                remaining = {k: v for k, v in kwargs.items() if k != "correlation_id"}

            correlation_id = kwargs.get("correlation_id")
            if correlation_id is not None and not isinstance(correlation_id, str):
                correlation_id = str(correlation_id)

            return base_context, correlation_id, remaining

        def _build_context(
            self,
            base_context: dict[str, object],
            remaining: dict[str, object] | None = None,
        ) -> dict[str, object]:
            """Build complete context dictionary merging base and remaining kwargs."""
            result = base_context.copy()
            if remaining:
                result.update(remaining)
            return result

    class CliValidationError(BaseError):
        """CLI validation error exception."""

        @override
        def __init__(self, message: str, **kwargs: object) -> None:
            """Initialize validation error with message and context using helpers.

            Args:
                message: Error message
                **kwargs: Additional context (context, correlation_id, plus any extra kwargs)

            """
            # Extract common parameters using helper
            base_context, correlation_id, remaining = self._extract_common_kwargs(
                kwargs
            )

            # Build context merging base and remaining kwargs
            context = self._build_context(base_context, remaining)

            # Call parent with complete error information
            super().__init__(
                message,
                error_code=FlextCliConstants.ErrorCodes.VALIDATION_ERROR,
                context=context,
                correlation_id=correlation_id,
            )

    class CliConfigurationError(BaseError):
        """CLI configuration error exception."""

        @override
        def __init__(self, message: str, **kwargs: object) -> None:
            """Initialize configuration error with message and context using helpers.

            Args:
                message: Error message
                **kwargs: Additional context (context, correlation_id)

            """
            # Extract common parameters using helper
            base_context, correlation_id, remaining = self._extract_common_kwargs(
                kwargs
            )

            # Build context
            context = self._build_context(base_context, remaining)

            # Call parent with complete error information
            super().__init__(
                message,
                error_code=FlextCliConstants.ErrorCodes.CONFIGURATION_ERROR,
                context=context,
                correlation_id=correlation_id,
            )

    class CliConnectionError(BaseError):
        """CLI connection error exception."""

        @override
        def __init__(self, message: str, **kwargs: object) -> None:
            """Initialize connection error with message and context using helpers.

            Args:
                message: Error message
                **kwargs: Additional context (context, correlation_id)

            """
            # Extract common parameters using helper
            base_context, correlation_id, remaining = self._extract_common_kwargs(
                kwargs
            )

            # Build context
            context = self._build_context(base_context, remaining)

            # Call parent with complete error information
            super().__init__(
                message,
                error_code=FlextCliConstants.ErrorCodes.CONNECTION_ERROR,
                context=context,
                correlation_id=correlation_id,
            )

    class CliAuthenticationError(BaseError):
        """CLI authentication error exception."""

        @override
        def __init__(self, message: str, **kwargs: object) -> None:
            """Initialize authentication error with message and context using helpers.

            Args:
                message: Error message
                **kwargs: Additional context (context, correlation_id)

            """
            # Extract common parameters using helper
            base_context, correlation_id, remaining = self._extract_common_kwargs(
                kwargs
            )

            # Build context
            context = self._build_context(base_context, remaining)

            # Call parent with complete error information
            super().__init__(
                message,
                error_code=FlextCliConstants.ErrorCodes.AUTHENTICATION_ERROR,
                context=context,
                correlation_id=correlation_id,
            )

    class CliCommandError(BaseError):
        """CLI command error exception."""

        @override
        def __init__(self, message: str, **kwargs: object) -> None:
            """Initialize command error with message and context using helpers.

            Args:
                message: Error message
                **kwargs: Additional context (context, correlation_id)

            """
            # Extract common parameters using helper
            base_context, correlation_id, remaining = self._extract_common_kwargs(
                kwargs
            )

            # Build context
            context = self._build_context(base_context, remaining)

            # Call parent with complete error information
            super().__init__(
                message,
                error_code=FlextCliConstants.ErrorCodes.COMMAND_ERROR,
                context=context,
                correlation_id=correlation_id,
            )

    class CliTimeoutError(BaseError):
        """CLI timeout error exception."""

        @override
        def __init__(self, message: str, **kwargs: object) -> None:
            """Initialize timeout error with message and context using helpers.

            Args:
                message: Error message
                **kwargs: Additional context (context, correlation_id)

            """
            # Extract common parameters using helper
            base_context, correlation_id, remaining = self._extract_common_kwargs(
                kwargs
            )

            # Build context
            context = self._build_context(base_context, remaining)

            # Call parent with complete error information
            super().__init__(
                message,
                error_code=FlextCliConstants.ErrorCodes.TIMEOUT_ERROR,
                context=context,
                correlation_id=correlation_id,
            )

    class CliFormatError(BaseError):
        """CLI format error exception."""

        @override
        def __init__(self, message: str, **kwargs: object) -> None:
            """Initialize format error with message and context using helpers.

            Args:
                message: Error message
                **kwargs: Additional context (context, correlation_id)

            """
            # Extract common parameters using helper
            base_context, correlation_id, remaining = self._extract_common_kwargs(
                kwargs
            )

            # Build context
            context = self._build_context(base_context, remaining)

            # Call parent with complete error information
            super().__init__(
                message,
                error_code=FlextCliConstants.ErrorCodes.FORMAT_ERROR,
                context=context,
                correlation_id=correlation_id,
            )


__all__ = [
    "FlextCliExceptions",
]
