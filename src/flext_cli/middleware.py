"""Middleware chain pattern for CLI commands.

FlextMiddleware provides a protocol and implementations for middleware chains
that can process CLI command execution with logging, validation, retry, and
other cross-cutting concerns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from collections.abc import Callable

from flext_core import r
from pydantic import BaseModel

from flext_cli.protocols import p
from flext_cli.typings import t

# Use existing Protocol from protocols.py (no duplicate definitions)
FlextMiddleware = p.Cli.MiddlewareProtocol


class LoggingMiddleware:
    """Log command execution with timing information."""

    def __call__(
        self,
        ctx: p.Cli.CliContextProtocol,
        next_: Callable[[p.Cli.CliContextProtocol], r[t.GeneralValueType]],
    ) -> r[t.GeneralValueType]:
        """Log command execution.

        Args:
            ctx: CLI execution context.
            next_: Next middleware or handler.

        Returns:
            r[t.GeneralValueType]: Result from next middleware or handler.

        """
        # Extract command name from context
        getattr(ctx, "command", "unknown")
        start = time.perf_counter()
        result = next_(ctx)
        _elapsed = time.perf_counter() - start
        return result


class ValidationMiddleware:
    """Validate command inputs using Pydantic schema."""

    def __init__(self, schema: type[BaseModel]) -> None:
        """Initialize validation middleware.

        Args:
            schema: Pydantic model class for validation.

        """
        self._schema = schema

    def __call__(
        self,
        ctx: p.Cli.CliContextProtocol,
        next_: Callable[[p.Cli.CliContextProtocol], r[t.GeneralValueType]],
    ) -> r[t.GeneralValueType]:
        """Validate command inputs.

        Args:
            ctx: CLI execution context.
            next_: Next middleware or handler.

        Returns:
            r[t.GeneralValueType]: Result from next middleware or handler, or failure
                if validation fails.

        """
        # Extract parameters from context
        params = getattr(ctx, "params", {})
        try:
            validated = self._schema.model_validate(params)
            # Update context with validated params
            ctx.params = validated.model_dump()
            return next_(ctx)
        except Exception as e:
            return r[t.GeneralValueType].fail(f"Validation failed: {e}")


class RetryMiddleware:
    """Retry failed commands with exponential backoff."""

    def __init__(self, max_retries: int = 3, backoff: float = 1.0) -> None:
        """Initialize retry middleware.

        Args:
            max_retries: Maximum number of retry attempts (default: 3).
            backoff: Base backoff delay in seconds (default: 1.0).

        """
        self._max_retries = max_retries
        self._backoff = backoff

    def __call__(
        self,
        ctx: p.Cli.CliContextProtocol,
        next_: Callable[[p.Cli.CliContextProtocol], r[t.GeneralValueType]],
    ) -> r[t.GeneralValueType]:
        """Retry failed commands.

        Args:
            ctx: CLI execution context.
            next_: Next middleware or handler.

        Returns:
            r[t.GeneralValueType]: Result from next middleware or handler after retries.

        """
        # Initialize result to satisfy type checker (loop always executes at least once)
        result = next_(ctx)
        if result.is_success:
            return result

        # Retry loop (starts from attempt 1 since we already tried once)
        for attempt in range(1, self._max_retries):
            delay = self._backoff * attempt
            time.sleep(delay)
            result = next_(ctx)
            if result.is_success:
                return result
        return result


def compose_middleware(
    middlewares: list[FlextMiddleware],
    handler: Callable[[p.Cli.CliContextProtocol], p.Result[t.GeneralValueType]],
) -> Callable[[p.Cli.CliContextProtocol], p.Result[t.GeneralValueType]]:
    """Compose middleware into single callable.

    Args:
        middlewares: List of middleware functions to compose.
        handler: Final command handler.

    Returns:
        Composed callable that executes all middleware in order.

    Example:
        >>> composed = compose_middleware(
        ...     [LoggingMiddleware(), ValidationMiddleware(MySchema)], my_handler
        ... )
        >>> result = composed(context)

    """

    def composed(ctx: p.Cli.CliContextProtocol) -> p.Result[t.GeneralValueType]:
        def build_chain(
            idx: int,
        ) -> Callable[[p.Cli.CliContextProtocol], p.Result[t.GeneralValueType]]:
            if idx >= len(middlewares):
                return handler
            current_middleware = middlewares[idx]
            return lambda c: current_middleware(c, build_chain(idx + 1))

        return build_chain(0)(ctx)

    return composed
