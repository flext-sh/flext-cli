"""FLEXT CLI Core Package - Centralized CLI Utilities and Patterns.

This package provides standardized CLI components, patterns, and utilities for
use across all FLEXT ecosystem projects. Implements core CLI functionality
including decorators, helpers, formatters, types, and base classes for
consistent CLI development.

Core Components:
    - Base classes: CLIContext and service result handling
    - Decorators: Cross-cutting concerns (auth, timing, retry, validation)
    - Helpers: CLI utilities and interactive functions
    - Formatters: Output formatting with Rich integration
    - Types: Custom Click parameter types and validation
    - Integration: flext-core utilities and patterns

Architecture:
    - Clean Architecture patterns with Clear layer separation
    - Domain-Driven Design (DDD) integration
    - SOLID principles with Open/Closed for extensibility
    - Dependency injection support and service patterns
    - Type safety with comprehensive MyPy coverage

Current Implementation Status:
    ✅ Complete core utility implementations
    ✅ Rich integration for enhanced UX
    ✅ flext-core integration and compatibility
    ✅ Comprehensive decorator patterns
    ✅ Type-safe parameter validation
    ✅ Output formatting with multiple formats
    ⚠️ Basic implementation (TODO: Sprint 2 - enhance features)

Package Exports:
    Base Classes:
        - CLIContext: Main CLI context for state management
        - handle_service_result: Service result handling utility

    Decorators:
        - async_command: Async/sync integration
        - confirm_action: Interactive confirmation prompts
        - measure_time: Performance timing
        - require_auth: Authentication enforcement
        - retry: Resilience with exponential backoff
        - validate_config: Configuration validation
        - with_spinner: Progress indication

    Helpers:
        - CLIHelper: General CLI utilities and interactive helpers

    Integration:
        - FlextUtilities: flext-core utility integration
        - CLI types: Type compatibility across ecosystem

Usage Examples:
    Using decorators:
    >>> @require_auth()
    >>> @measure_time()
    >>> def sensitive_operation():
    ...     # Authenticated and timed operation

    Using CLI helper:
    >>> helper = CLIHelper()
    >>> if helper.confirm("Delete data?"):
    ...     # Perform destructive operation

    Using context:
    >>> context = CLIContext(config=config, settings=settings, console=console)
    >>> context.print_success("Operation completed")

Integration:
    - Used by all FLEXT CLI commands for consistency
    - Provides foundation for ecosystem CLI development
    - Integrates with flext-core patterns and utilities
    - Supports Clean Architecture and DDD patterns

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core.utilities import FlextUtilities

from flext_cli.core.base import (
    CLIContext,
    handle_service_result,
)
from flext_cli.core.decorators import (
    async_command,
    confirm_action,
    measure_time,
    require_auth,
    retry,
    validate_config,
    with_spinner,
)
from flext_cli.core.helpers import CLIHelper, FlextCliHelper
from flext_cli.types import (
    FlextCliCommand,
    FlextCliConfig,
    FlextCliContext,
    FlextCliPlugin,
    FlextCliSession,
)

# Services will be imported when needed to avoid circular imports

# This will be resolved when the core.py file is imported

__all__: list[str] = [
    "CLIContext",
    "CLIHelper",
    "FlextCliCommand",
    "FlextCliConfig",
    "FlextCliContext",
    "FlextCliHelper",
    "FlextCliPlugin",
    "FlextCliSession",
    "FlextUtilities",
    "async_command",
    "confirm_action",
    "handle_service_result",
    "measure_time",
    "require_auth",
    "retry",
    "validate_config",
    "with_spinner",
]

__version__ = "0.9.0"
