"""FLEXT CLI Mixins - Single unified class following FLEXT standards.

**MODULE**: FlextCliMixins - Single primary class for CLI mixins
**SCOPE**: Business rules validation, CLI command execution patterns with decorator composition

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextDecorators, FlextMixins, r

from flext_cli import p, t
from flext_cli.typings import FlextCliTypes


class FlextCliMixins(FlextMixins):
    """Single unified CLI mixins class following FLEXT standards.

    Business Rules:
    ───────────────
    1. CliCommandMixin composes flext-core decorators for command execution
    2. CliCommandMixin composes flext-core decorators for command execution
    3. Command execution MUST use railway pattern for error handling
    4. Context management MUST include correlation ID and operation logging
    5. Performance tracking MUST be enabled for all command executions
    6. Double-wrapped r MUST be unwrapped correctly
    7. Non-r returns MUST be wrapped in r
    8. All mixin methods MUST be static (no instance state)

    Architecture Implications:
    ───────────────────────────
    - CliCommandMixin composes decorators in correct order
    - CliCommandMixin composes decorators in correct order
    - Railway decorator ensures r return type
    - Performance tracking via track_performance decorator
    - Operation logging via log_operation decorator
    - Extends x for base mixin functionality

    Audit Implications:
    ───────────────────
    - Command executions MUST be logged with operation name and correlation ID
    - Performance metrics MUST be logged for monitoring
    - Decorator composition MUST preserve error handling chain
    - Decorator composition MUST preserve error handling chain

    Contains all mixin subclasses for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.
    """

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
            **context_data: t.Scalar,
        ) -> r[FlextCliTypes.Cli.JsonValue]:
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
                r from handler execution

            """
            log_op_decorator = FlextDecorators.log_operation(operation, track_perf=True)
            wrapped_handler = log_op_decorator(handler)
            raw_result = wrapped_handler(**context_data)
            if isinstance(raw_result, r):
                return raw_result
            return r.ok(raw_result)


x = FlextCliMixins
__all__ = ["FlextCliMixins", "x"]
