"""FLEXT CLI Decorators - Class-only decorator utilities (no free helpers)."""

from __future__ import annotations

import asyncio
import functools
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import ParamSpec, TypeVar

from flext_core import FlextDecorators, FlextResult, FlextTypes
from rich.console import Console

from flext_cli.constants import FlextCliConstants

P = ParamSpec("P")
T = TypeVar("T")


class FlextCliDecorators(FlextDecorators):
    """CLI-specific decorators extending flext-core FlextDecorators.

    All decorators are exposed as class methods to avoid module-level helpers.
    """

    @staticmethod
    def handle_service_result(func: Callable[..., object]) -> Callable[..., object]:
        """Decorator for handling FlextResult values - extracts success data or returns None on failure."""

        @functools.wraps(func)
        def _wrapper(*args: object, **kwargs: object) -> object:
            # For async functions, return a coroutine that handles FlextResult
            if asyncio.iscoroutinefunction(func):

                async def async_handler() -> object:
                    # Call the async function and await the result
                    coro = func(*args, **kwargs)
                    if asyncio.iscoroutine(coro):
                        result = await coro
                    else:
                        result = coro

                    # Process FlextResult
                    if isinstance(result, FlextResult):
                        if result.is_success:
                            return result.value
                        # For failures, print error and return None
                        console = Console()
                        console.print(f"[red]Error: {result.error}[/red]")
                        return None

                    # Pass through non-FlextResult values
                    return result

                return async_handler()

            # Handle sync functions normally
            result = func(*args, **kwargs)

            # Process FlextResult
            if isinstance(result, FlextResult):
                if result.is_success:
                    return result.value
                # For failures, print error and return None
                console = Console()
                console.print(f"[red]Error: {result.error}[/red]")
                return None

            # Pass through non-FlextResult values
            return result

        return _wrapper

    @staticmethod
    def async_command(func: Callable[..., object]) -> Callable[..., object]:
        """Convert async function to sync by running with asyncio.run when safe."""
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            def _wrapper(*args: object, **kwargs: object) -> object:
                try:
                    # Check if we're in an event loop already
                    asyncio.get_running_loop()
                    # If we get here, there's a running loop, so return the coroutine
                    return func(*args, **kwargs)
                except RuntimeError:
                    # No event loop running, safe to use asyncio.run
                    return asyncio.run(func(*args, **kwargs))

            return _wrapper
        return func

    @staticmethod
    def confirm_action(
        message: str,
    ) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
        """Create confirmation decorator for user actions."""
        def _decorator(func: Callable[P, T]) -> Callable[P, T | None]:
            @functools.wraps(func)
            def _wrapped(*args: P.args, **kwargs: P.kwargs) -> T | None:
                console = Console()
                try:
                    answer = console.input(f"{message} (y/N): ").strip().lower()
                    if answer in {"y", "yes"}:
                        return func(*args, **kwargs)
                    return None
                except (EOFError, KeyboardInterrupt, OSError, ValueError):
                    return None

            return _wrapped

        return _decorator

    @staticmethod
    def require_auth(
        token_file: str | None = None,
    ) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
        """Create authentication requirement decorator."""
        def _decorator(func: Callable[P, T]) -> Callable[P, T | None]:
            @functools.wraps(func)
            def _wrapped(*args: P.args, **kwargs: P.kwargs) -> T | None:
                try:
                    path = (
                        Path(token_file)
                        if token_file
                        else Path.home()
                        / FlextCliConstants.FLEXT_DIR_NAME
                        / FlextCliConstants.AUTH_DIR_NAME
                        / FlextCliConstants.TOKEN_FILE_NAME
                    )
                    if not path.exists():
                        return None
                    content = path.read_text(encoding="utf-8").strip()
                    if not content:
                        return None
                    return func(*args, **kwargs)
                except (OSError, UnicodeDecodeError, ValueError):
                    return None

            return _wrapped

        return _decorator

    @staticmethod
    def measure_time(
        *,
        show_in_output: bool = False,
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """Create execution time measurement decorator."""
        def _decorator(func: Callable[P, T]) -> Callable[P, T]:
            @functools.wraps(func)
            def _wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
                start = time.time()
                try:
                    return func(*args, **kwargs)
                finally:
                    elapsed = time.time() - start
                    if show_in_output:
                        Console().print(
                            f"⏱  Execution time: {elapsed:.2f}s",
                            style="dim",
                        )

            return _wrapped

        return _decorator

    @staticmethod
    def validate_config(
        required_keys: FlextTypes.Core.StringList,
    ) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
        """Create configuration validation decorator."""
        def _decorator(func: Callable[P, T]) -> Callable[P, T | None]:
            @functools.wraps(func)
            def _wrapped(*args: P.args, **kwargs: P.kwargs) -> T | None:
                console = Console()

                candidate = (
                    kwargs.get("config")
                    or kwargs.get("cfg")
                    or kwargs.get("settings")
                    or kwargs.get("mock_config")
                    or (args[0] if args else None)
                )

                if candidate is None:
                    console.print(
                        "Configuration not available for validation.",
                        style="red",
                    )
                    return None

                def _get(c: object, k: str) -> object | None:
                    if isinstance(c, Mapping):
                        return c.get(k)
                    return getattr(c, k, None)

                for key in required_keys:
                    if _get(candidate, key) is None:
                        console.print(
                            f"Missing required configuration: {key}",
                            style="red",
                        )
                        return None

                return func(*args, **kwargs)

            return _wrapped

        return _decorator

    @staticmethod
    def with_spinner(
        message: str = "Processing...",
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """Create spinner decorator for long operations."""
        def _decorator(func: Callable[P, T]) -> Callable[P, T]:
            @functools.wraps(func)
            def _wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
                console = Console()
                with console.status(message, spinner="dots"):
                    return func(*args, **kwargs)

            return _wrapped

        return _decorator

    @staticmethod
    def flext_cli_auto_validate(
        _validators: FlextTypes.Core.StringList,
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """Create automatic validation decorator."""
        def _decorator(func: Callable[P, T]) -> Callable[P, T]:
            return functools.wraps(func)(func)

        return _decorator

    @staticmethod
    def require_confirmation(
        _action: str,
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """Compatibility no-op confirmation decorator (non-interactive)."""

        def _decorator(func: Callable[P, T]) -> Callable[P, T]:
            return functools.wraps(func)(func)

        return _decorator

    @staticmethod
    def retry(
        *,
        max_attempts: int = 3,
        delay: float = 0.1,
        exceptions: tuple[type[Exception], ...] = (Exception,),
    ) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
        """Retry decorator for handling transient failures.

        Args:
            max_attempts: Maximum number of attempts (default: 3)
            delay: Delay between attempts in seconds (default: 0.1)
            exceptions: Tuple of exceptions to catch and retry (default: Exception)

        Returns:
            Decorated function with retry logic

        """

        def _decorator(func: Callable[P, T]) -> Callable[P, T | None]:
            @functools.wraps(func)
            def _wrapped(*args: P.args, **kwargs: P.kwargs) -> T | None:
                last_exception = None

                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts - 1:  # Not last attempt
                            time.sleep(delay)
                            continue
                        break

                # All attempts failed
                console = Console()
                console.print(
                    f"[red]Retry failed after {max_attempts} attempts: {last_exception}[/red]",
                )
                return None

            return _wrapped

        return _decorator


# Backward compatibility - expose static methods as module functions
handle_service_result = FlextCliDecorators.handle_service_result
flext_cli_require_confirmation = FlextCliDecorators.require_confirmation


__all__ = [
    "FlextCliDecorators",
    "flext_cli_require_confirmation",
    "handle_service_result",
]
