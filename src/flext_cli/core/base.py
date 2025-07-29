"""Base classes and utilities for FLEXT CLI framework.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import inspect

from flext_core import get_logger
from flext_core.result import FlextResult
from flext_core.value_objects import FlextValueObject
from pydantic import Field
from rich.console import Console

# Simplified type handling for MyPy compatibility


class CLIContext(FlextValueObject):
    """CLI context for command execution using flext-core patterns."""

    profile: str = Field(default="default", description="Active profile")
    output_format: str = Field(default="table", description="Output format")
    debug: bool = Field(default=False, description="Debug mode enabled")
    quiet: bool = Field(default=False, description="Quiet mode enabled")
    verbose: bool = Field(default=False, description="Verbose mode enabled")
    no_color: bool = Field(default=False, description="No color output")

    def model_post_init(self, __context: object, /) -> None:
        """Post-initialization validation hook."""
        super().model_post_init(__context)
        self.validate_domain_rules()

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


def handle_service_result(func: object) -> object:
    """Handle FlextResult and render them appropriately.

    Args:
        func: Function to decorate

    Returns:
        Decorated function

    """
    if not callable(func):
        return func

    def sync_wrapper(*args: object, **kwargs: object) -> object:
        try:
            result = func(*args, **kwargs)
            return _handle_flext_result(result)
        except (RuntimeError, ValueError, TypeError) as e:
            _handle_exception(e)
            raise

    async def async_wrapper(*args: object, **kwargs: object) -> object:
        try:
            result = await func(*args, **kwargs)
            return _handle_flext_result(result)
        except (RuntimeError, ValueError, TypeError) as e:
            _handle_exception(e)
            raise

    # Return appropriate wrapper based on function type
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
