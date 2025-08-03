"""FLEXT CLI Core Decorators - Cross-Cutting Concerns and CLI Patterns.

This module provides essential decorators for FLEXT CLI operations including
async/sync integration, error handling, performance monitoring, authentication,
and other cross-cutting concerns that apply across CLI commands.

Decorator Categories:
    - Execution: async_command for async/sync integration
    - Error Handling: retry, with error recovery and logging
    - Performance: measure_time for operation timing
    - Security: require_auth for authentication enforcement
    - UX: with_spinner for long-running operations, confirm_action for safety
    - Validation: validate_config for configuration checks

Architecture:
    - SOLID principles with Open/Closed principle for extensibility
    - Functional implementation for production reliability
    - Integration with Rich console for enhanced UX
    - FlextResult integration for error handling patterns

Current Implementation Status:
    ✅ Basic decorators implemented (async_command, measure_time, etc.)
    ✅ Rich console integration for UX enhancements
    ✅ Error handling and retry logic
    ⚠️ Basic implementation (TODO: Sprint 2 - enhance with metrics)
    ❌ Advanced authentication integration not implemented (TODO: Sprint 2)

TODO (docs/TODO.md):
    Sprint 2: Add correlation ID tracking to all decorators
    Sprint 2: Enhance authentication integration with FLEXT services
    Sprint 3: Add comprehensive validation decorators
    Sprint 7: Add performance metrics collection and monitoring
    Sprint 8: Add interactive confirmation and progress decorators

Usage Patterns:
    @async_command: Convert async functions for CLI command use
    @measure_time: Track operation performance
    @require_auth: Enforce authentication for sensitive operations
    @retry: Add resilience with exponential backoff
    @with_spinner: Enhance UX for long operations

Integration:
    - Used by all CLI commands for consistent behavior
    - Integrates with authentication and authorization systems
    - Supports monitoring and observability patterns
    - Provides consistent error handling across commands

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

from rich.console import Console


def async_command(f: object) -> object:
    """Run async functions in sync context (SOLID: Open/Closed Principle)."""
    if not callable(f):
        return f

    def wrapper(*args: object, **kwargs: object) -> object:
        try:
            result = f(*args, **kwargs)
            if asyncio.iscoroutine(result):
                return asyncio.run(result)
            return result
        except (RuntimeError, OSError, TypeError, AttributeError):
            # Log the exception if needed
            return None

    # Copy function metadata manually to avoid functools.wraps typing issues
    wrapper.__name__ = getattr(f, "__name__", "wrapped_function")
    wrapper.__doc__ = getattr(f, "__doc__", wrapper.__doc__)
    wrapper.__module__ = getattr(f, "__module__", __name__)

    return wrapper


def confirm_action(
    message: str = "Are you sure?",
    *,
    default: bool = False,
) -> object:
    """Add confirmation prompt before executing function."""

    def decorator(f: object) -> object:
        if not callable(f):
            return f

        def wrapper(*args: object, **kwargs: object) -> object:
            console = Console()
            prompt = f"{message} [{'Y/n' if default else 'y/N'}]: "
            response = console.input(prompt).lower()
            should_continue = default if not response else response.startswith("y")

            if should_continue:
                return f(*args, **kwargs)
            console.print("Operation cancelled.", style="yellow")
            return None

        # Copy function metadata manually
        wrapper.__name__ = getattr(f, "__name__", "wrapped_function")
        wrapper.__doc__ = getattr(f, "__doc__", wrapper.__doc__)
        wrapper.__module__ = getattr(f, "__module__", __name__)

        return wrapper

    return decorator


def require_auth(*, token_file: str | None = None) -> object:
    """Require authentication before executing function."""

    def decorator(f: object) -> object:
        if not callable(f):
            return f

        def wrapper(*args: object, **kwargs: object) -> object:
            path = token_file or "~/.flext/auth_token"
            token_path = Path(path).expanduser()

            if not token_path.exists():
                console = Console()
                console.print(
                    f"Authentication required. Token file not found: {token_path}",
                    style="red",
                )
                console.print("Please run 'flext auth login' first.", style="yellow")
                return None

            try:
                with token_path.open() as file_handle:
                    token = file_handle.read().strip()
                if not token:
                    console = Console()
                    console.print("Token file is empty", style="red")
                    return None
            except (OSError, ValueError) as e:
                console = Console()
                console.print(f"Invalid token file: {e}", style="red")
                return None

            # Add token to kwargs for the function if needed
            return f(*args, **kwargs)

        # Copy function metadata manually
        wrapper.__name__ = getattr(f, "__name__", "wrapped_function")
        wrapper.__doc__ = getattr(f, "__doc__", wrapper.__doc__)
        wrapper.__module__ = getattr(f, "__module__", __name__)

        return wrapper

    return decorator


def measure_time(*, show_in_output: bool = True) -> object:
    """Measure and optionally display execution time."""

    def decorator(f: object) -> object:
        if not callable(f):
            return f

        def wrapper(*args: object, **kwargs: object) -> object:
            start_time = time.time()
            try:
                return f(*args, **kwargs)
            finally:
                end_time = time.time()
                duration = end_time - start_time

                if show_in_output:
                    console = Console()
                    console.print(
                        f"⏱  Execution time: {duration:.2f}s",
                        style="dim",
                    )

        # Copy function metadata manually
        wrapper.__name__ = getattr(f, "__name__", "wrapped_function")
        wrapper.__doc__ = getattr(f, "__doc__", wrapper.__doc__)
        wrapper.__module__ = getattr(f, "__module__", __name__)

        return wrapper

    return decorator


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> object:
    """Retry function calls with exponential backoff."""

    def decorator(f: object) -> object:
        if not callable(f):
            return f

        def wrapper(*args: object, **kwargs: object) -> object:
            console = Console()
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return f(*args, **kwargs)
                except (RuntimeError, ValueError, TypeError) as e:
                    if attempt == max_attempts - 1:
                        console.print(
                            f"Failed after {max_attempts} attempts: {e}",
                            style="red",
                        )
                        raise

                    console.print(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in "
                        f"{current_delay:.1f}s...",
                        style="yellow",
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff

            return None  # Should never reach here

        # Copy function metadata manually
        wrapper.__name__ = getattr(f, "__name__", "wrapped_function")
        wrapper.__doc__ = getattr(f, "__doc__", wrapper.__doc__)
        wrapper.__module__ = getattr(f, "__module__", __name__)

        return wrapper

    return decorator


def validate_config(required_keys: list[str]) -> object:
    """Validate required configuration keys before execution."""

    def decorator(f: object) -> object:
        if not callable(f):
            return f

        def wrapper(*args: object, **kwargs: object) -> object:
            # Try to get config from context or kwargs
            config = kwargs.get("config") if isinstance(kwargs, dict) else None

            if not config and args and hasattr(args[0], "config"):
                # Try to get from args (assuming first arg might be context with config)
                config = getattr(args[0], "config", None)

            if not config:
                console = Console()
                console.print(
                    "Configuration not available for validation.",
                    style="red",
                )
                return None

            # Validate required keys
            missing_keys = [
                key
                for key in required_keys
                if not hasattr(config, key) or getattr(config, key) is None
            ]

            if missing_keys:
                console = Console()
                console.print(
                    f"Missing required configuration: {', '.join(missing_keys)}",
                    style="red",
                )
                return None

            return f(*args, **kwargs)

        return wrapper

    return decorator


def with_spinner(message: str = "Processing...") -> object:
    """Show a spinner during function execution."""

    def decorator(f: object) -> object:
        if not callable(f):
            return f

        def wrapper(*args: object, **kwargs: object) -> object:
            console = Console()
            with console.status(message, spinner="dots"):
                return f(*args, **kwargs)

        return wrapper

    return decorator
