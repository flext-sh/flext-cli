"""FLEXT CLI Core Base Classes - Foundation for CLI Operations.

This module provides core base classes and utilities that form the foundation
for all FLEXT CLI operations. Includes context management, error handling
decorators, and common patterns used throughout the CLI framework.

Core Components:
    - CLIContext: Value object for CLI execution context and configuration
    - handle_service_result: Decorator for FlextResult error handling
    - CLI utilities and helper functions

Architecture:
    - FlextValueObject base for immutable CLI context
    - Railway-oriented programming with FlextResult patterns
    - Rich console integration for beautiful terminal output
    - Domain validation with business rule enforcement

Integration:
    - Used by all CLI commands for context management
    - Integrates with flext-core patterns and utilities
    - Provides consistent error handling across CLI operations
    - Supports Rich console for enhanced terminal experience

Current Implementation:
    ✅ CLIContext value object with validation
    ✅ handle_service_result decorator for error handling
    ✅ Rich console integration
    ⚠️ Basic implementation (can be enhanced in Sprint 2)

TODO (docs/TODO.md):
    Sprint 2: Add correlation ID tracking for operations
    Sprint 3: Enhance context with additional metadata
    Sprint 7: Add performance metrics and monitoring
    Sprint 8: Add interactive mode context support

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import get_logger
from flext_core.decorators import FlextDecorators
from flext_core.result import FlextResult
from flext_core.value_objects import FlextValueObject
from pydantic import Field
from rich.console import Console

# Simplified type handling for MyPy compatibility


class CLIContext(FlextValueObject):
    """CLI Context Value Object - Immutable execution context for CLI operations.

    Represents the execution context for CLI commands including configuration,
    output preferences, and operational flags. Follows flext-core value object
    patterns with immutability and validation.

    Context Fields:
        profile: Configuration profile name (dev, staging, prod)
        output_format: Output format (table, json, yaml, csv)
        debug: Enable debug mode with verbose logging
        quiet: Suppress non-error output for scripting
        verbose: Enable verbose output with additional details
        no_color: Disable colored output for terminals that don't support it

    Business Rules:
        - Profile names must be non-empty strings
        - Output format must be one of supported formats
        - Debug and quiet modes are mutually exclusive
        - All context values are immutable after creation

    Usage:
        >>> context = CLIContext(
        ...     profile="dev",
        ...     output_format="json",
        ...     debug=True
        ... )
        >>> assert context.profile == "dev"
        >>> assert context.debug is True

    Integration:
        - Used by all CLI commands for execution context
        - Passed through Click context object
        - Supports Rich console configuration
        - Integrates with configuration management

    TODO (Sprint 2):
        - Add correlation ID for request tracking
        - Add user identity and authorization context
        - Add workspace and project context
        - Add performance metrics context
    """

    profile: str = Field(default="default", description="Active profile")
    output_format: str = Field(default="table", description="Output format")
    debug: bool = Field(default=False, description="Debug mode enabled")
    quiet: bool = Field(default=False, description="Quiet mode enabled")
    verbose: bool = Field(default=False, description="Verbose mode enabled")
    no_color: bool = Field(default=False, description="No color output")

    def model_post_init(self, __context: object, /) -> None:
        """Post-initialization validation hook."""
        super().model_post_init(__context)
        result = self.validate_domain_rules()
        if not result.is_success:
            raise ValueError(result.error)

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain business rules for CLI context.

        Returns:
            FlextResult indicating success or failure with validation errors.

        """
        # Profile cannot be empty
        if not self.profile or not self.profile.strip():
            return FlextResult.fail("Profile cannot be empty")

        # Output format must be valid
        valid_formats = {"table", "json", "yaml", "csv", "plain"}
        if self.output_format not in valid_formats:
            return FlextResult.fail(f"Output format must be one of: {valid_formats}")

        # Cannot have both quiet and verbose modes
        if self.quiet and self.verbose:
            return FlextResult.fail("Cannot have both quiet and verbose modes enabled")

        return FlextResult.ok(None)


def _handle_flext_result(result: object) -> object:
    """Handle FlextResult response.

    Args:
        result: The result to handle

    Returns:
        Processed result or None for errors

    """
    if isinstance(result, FlextResult):
        if result.is_success:
            return result.data
        console = Console()
        console.print(f"[red]Error: {result.error}[/red]")
        return None
    return result


def _handle_exception(e: Exception) -> None:
    """Handle exceptions with proper logging and console output.

    Args:
        e: The exception to handle

    """
    console = Console()
    console.print(f"[red]Error: {e}[/red]")
    logger = get_logger(__name__)
    logger.error("Unhandled exception in CLI command")


# Use FlextDecorators from flext-core for proper type safety
handle_service_result = FlextDecorators.safe_result
