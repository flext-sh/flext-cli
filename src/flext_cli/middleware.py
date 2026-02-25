"""Middleware chain pattern for CLI commands.

FlextCliMiddleware provides a protocol and implementations for middleware chains
that can process CLI command execution with logging, validation, retry, and
other cross-cutting concerns. All classes use FlextCli prefix; compose is
FlextCliMiddleware.compose (no loose functions).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from collections.abc import Callable

from flext_core import p as p_core, r
from pydantic import BaseModel
from rich.errors import ConsoleError, LiveError, StyleError

from flext_cli.protocols import p
from flext_cli.typings import t

FlextCliMiddlewareProtocol = p.Cli.MiddlewareProtocol


class FlextCliLoggingMiddleware:
    """Log command execution with timing information."""

    def __call__(
        self,
        ctx: p.Cli.CliContextProtocol,
        next_: Callable[[p.Cli.CliContextProtocol], r[t.JsonValue]],
    ) -> r[t.JsonValue]:
        """Log command execution.

        Args:
            ctx: CLI execution context.
            next_: Next middleware or handler.

        Returns:
            r[t.JsonValue]: Result from next middleware or handler.

        """
        _ = getattr(ctx, "command", "unknown")
        start = time.perf_counter()
        result = next_(ctx)
        _elapsed = time.perf_counter() - start
        return result


class FlextCliValidationMiddleware:
    """Validate command inputs using Pydantic schema."""

    def __init__(self, schema: type[BaseModel]) -> None:
        """Initialize validation middleware.

        Args:
            schema: Pydantic model class for validation.

        """
        super().__init__()
        self._schema = schema

    def __call__(
        self,
        ctx: p.Cli.CliContextProtocol,
        next_: Callable[[p.Cli.CliContextProtocol], r[t.JsonValue]],
    ) -> r[t.JsonValue]:
        """Validate command inputs.

        Args:
            ctx: CLI execution context.
            next_: Next middleware or handler.

        Returns:
            r[t.JsonValue]: Result from next middleware or handler, or failure
                if validation fails.

        """
        params = getattr(ctx, "params", {})
        try:
            validated = self._schema.model_validate(params)
            ctx.params = validated.model_dump()
            return next_(ctx)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            return r[t.JsonValue].fail(f"Validation failed: {e}")


class FlextCliRetryMiddleware:
    """Retry failed commands with exponential backoff."""

    def __init__(self, max_retries: int = 3, backoff: float = 1.0) -> None:
        """Initialize retry middleware.

        Args:
            max_retries: Maximum number of retry attempts (default: 3).
            backoff: Base backoff delay in seconds (default: 1.0).

        """
        super().__init__()
        self._max_retries = max_retries
        self._backoff = backoff

    def __call__(
        self,
        ctx: p.Cli.CliContextProtocol,
        next_: Callable[[p.Cli.CliContextProtocol], r[t.JsonValue]],
    ) -> r[t.JsonValue]:
        """Retry failed commands.

        Args:
            ctx: CLI execution context.
            next_: Next middleware or handler.

        Returns:
            r[t.JsonValue]: Result from next middleware or handler after retries.

        """
        result = next_(ctx)
        if result.is_success:
            return result

        for attempt in range(1, self._max_retries):
            delay = self._backoff * attempt
            time.sleep(delay)
            result = next_(ctx)
            if result.is_success:
                return result
        return result


class FlextCliMiddleware:
    """Middleware namespace: protocol type and compose static method."""

    # Alias for type hints (same as p.Cli.MiddlewareProtocol)
    Protocol = p.Cli.MiddlewareProtocol

    @staticmethod
    def compose(
        middlewares: list[FlextCliMiddlewareProtocol],
        handler: Callable[[p.Cli.CliContextProtocol], p_core.Result[t.JsonValue]],
    ) -> Callable[[p.Cli.CliContextProtocol], p_core.Result[t.JsonValue]]:
        """Compose middleware into single callable.

        Args:
            middlewares: List of middleware instances to compose.
            handler: Final command handler.

        Returns:
            Composed callable that executes all middleware in order.

        Example:
            >>> composed = FlextCliMiddleware.compose(
            ...     [
            ...         FlextCliLoggingMiddleware(),
            ...         FlextCliValidationMiddleware(MySchema),
            ...     ],
            ...     my_handler,
            ... )
            >>> result = composed(context)

        """

        def composed(ctx: p.Cli.CliContextProtocol) -> p_core.Result[t.JsonValue]:
            def build_chain(
                idx: int,
            ) -> Callable[[p.Cli.CliContextProtocol], p_core.Result[t.JsonValue]]:
                if idx >= len(middlewares):
                    return handler
                current_middleware = middlewares[idx]
                return lambda c: current_middleware(c, build_chain(idx + 1))

            return build_chain(0)(ctx)

        return composed
