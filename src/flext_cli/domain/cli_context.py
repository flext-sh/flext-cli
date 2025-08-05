"""FLEXT CLI Domain Context - CLI Context Value Objects and State Management.

This module provides context value objects for FLEXT CLI operations, managing
state, configuration, and execution context throughout command lifecycle.
Uses flext-core DomainValueObject patterns for immutable context management.

Context Classes:
    - CLIContext: Main CLI context with configuration and console
    - CLIExecutionContext: Command execution tracking and metadata

Architecture:
    - DomainValueObject base for immutable context objects
    - Rich console integration for enhanced output
    - Domain validation with FlextResult error handling
    - Type-safe context management with Pydantic
    - Centralized state management for CLI operations

Current Implementation Status:
    ✅ CLIContext with configuration and console management
    ✅ CLIExecutionContext for command tracking
    ✅ DomainValueObject integration with domain validation
    ✅ Rich console integration for output management
    ✅ Debug, info, success, warning, error output methods
    ⚠️ Basic implementation (TODO: Sprint 2 - enhance context features)

TODO (docs/TODO.md):
    Sprint 2: Add correlation ID tracking across commands
    Sprint 3: Add user session management and persistence
    Sprint 5: Add command history and audit logging
    Sprint 7: Add performance metrics and monitoring context
    Sprint 8: Add interactive mode context and state

Features:
    - Immutable context objects with validation
    - Rich console integration for beautiful output
    - Debug mode and quiet mode support
    - Command execution tracking and metadata
    - Type-safe context passing between commands

Usage Examples:
    Basic CLI context:
    >>> context = CLIContext(
    ...     config=cli_config, settings=cli_settings, console=Console()
    ... )
    >>> context.print_success("Operation completed")

    Execution context:
    >>> exec_context = CLIExecutionContext(
    ...     command_name="auth login", user_id="user123", session_id="session456"
    ... )

Integration:
    - Used by all CLI commands for consistent context
    - Integrates with dependency injection container
    - Provides foundation for command lifecycle management
    - Supports debugging and monitoring patterns

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from flext_core import (
    FlextDomainValueObject as DomainValueObject,
    FlextResult,
)
from pydantic import ConfigDict, Field

if TYPE_CHECKING:
    from flext_cli.config import CLIConfig

from rich.console import (
    Console,  # noqa: TC002 - needed for runtime Pydantic model_rebuild
)


class CLIContext(DomainValueObject):
    """Main CLI context value object for state and configuration management.

    Immutable context object that carries configuration, settings, and console
    throughout command execution. Provides convenience methods for different
    types of output and integrates with Rich console for enhanced UX.

    Features:
        - Immutable value object with validation
        - Rich console integration for beautiful output
        - Debug, quiet, and verbose mode support
        - Convenient output methods (debug, info, success, warning, error)
        - Type-safe configuration and settings access

    Design Pattern:
        Uses Value Object pattern from DDD with DomainValueObject base for
        immutable state management and validation. Ensures consistency
        across command executions.

    Usage:
        >>> context = CLIContext(
        ...     config=cli_config, settings=cli_settings, console=Console()
        ... )
        >>> context.print_success("Command completed successfully")
        >>> if context.is_debug:
        ...     context.print_debug("Debug information")
    """

    config: CLIConfig = Field(..., description="CLI configuration")
    console: Console = Field(..., description="Rich console instance")

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Allow Console type

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate domain business rules for CLI context.

        Returns:
            FlextResult indicating success or failure with validation errors.

        """
        # No specific domain rules to validate for CLI context
        return FlextResult.ok(None)

    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled.

        Returns:
            True if debug/verbose mode is enabled.

        """
        return self.config.debug or self.config.verbose

    @property
    def is_quiet(self) -> bool:
        """Check if quiet mode is enabled.

        Returns:
            True if quiet mode is enabled.

        """
        return self.config.quiet

    @property
    def is_verbose(self) -> bool:
        """Check if verbose mode is enabled.

        Returns:
            True if verbose mode is enabled.

        """
        return self.config.verbose

    def print_debug(self, message: str) -> None:
        """Print debug message if debug mode is enabled.

        Args:
            message: Debug message to print.

        """
        if self.is_debug:
            self.console.print(f"[dim][DEBUG][/dim] {message}")

    def print_info(self, message: str) -> None:
        """Print info message if not in quiet mode.

        Args:
            message: Info message to print.

        """
        if not self.is_quiet:
            self.console.print(f"[blue][INFO][/blue] {message}")

    def print_success(self, message: str) -> None:
        """Print success message.

        Args:
            message: Success message to print.

        """
        self.console.print(f"[green][SUCCESS][/green] {message}")

    def print_warning(self, message: str) -> None:
        """Print warning message.

        Args:
            message: Warning message to print.

        """
        self.console.print(f"[yellow][WARNING][/yellow] {message}")

    def print_error(self, message: str) -> None:
        """Print error message.

        Args:
            message: Error message to print.

        """
        self.console.print(f"[red][ERROR][/red] {message}")

    def print_verbose(self, message: str) -> None:
        """Print verbose message if verbose mode is enabled.

        Args:
            message: Verbose message to print.

        """
        if self.is_verbose:
            self.console.print(f"[dim][VERBOSE][/dim] {message}")


class CLIExecutionContext(DomainValueObject):
    """CLI execution context for tracking command execution state and metadata.

    Immutable value object that tracks command execution lifecycle, user context,
    and session information. Used for audit logging, performance monitoring,
    and command history tracking across CLI operations.

    Features:
        - Command execution tracking and metadata
        - User and session identification
        - Timestamp tracking for performance analysis
        - Additional context data for command-specific information
        - Domain validation for execution context integrity

    Use Cases:
        - Command audit logging and history
        - Performance monitoring and analysis
        - User session tracking
        - Error tracking and debugging
        - Command lifecycle management

    TODO (Sprint 5):
        - Add execution duration tracking
        - Add command result and exit code tracking
        - Add parent/child command relationships
        - Add correlation ID for distributed tracing

    Usage:
        >>> exec_context = CLIExecutionContext(
        ...     command_name="auth login",
        ...     user_id="user123",
        ...     session_id="session456",
        ...     started_at="2025-01-01T12:00:00Z",
        ... )
        >>> # Track command execution metadata
    """

    command_name: str = Field(..., description="Name of the command being executed")
    user_id: str | None = Field(
        default=None,
        description="User ID executing the command",
    )
    session_id: str | None = Field(
        default=None,
        description="Session ID for command execution",
    )
    started_at: str | None = Field(
        default=None,
        description="Execution start timestamp",
    )
    context_data: dict[str, object] = Field(
        default_factory=dict,
        description="Additional context data",
    )

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate domain business rules for CLI execution context.

        Returns:
            FlextResult indicating success or failure with validation errors.

        """
        if not self.command_name or not self.command_name.strip():
            return FlextResult.fail("Command name cannot be empty")

        return FlextResult.ok(None)


# Models use forward references - no runtime imports needed for types

# Rebuild Pydantic models to resolve forward references
with contextlib.suppress(Exception):
    # Import dependencies for runtime model building
    from flext_cli.config import CLIConfig

    # Rebuild all models in dependency order
    CLIConfig.model_rebuild()
    CLIContext.model_rebuild()
    CLIExecutionContext.model_rebuild()
