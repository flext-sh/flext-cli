"""FLEXT CLI Decorators - Class-only decorator utilities (no free helpers)."""

from __future__ import annotations

import asyncio
import functools
import time
from collections.abc import Awaitable, Callable, Mapping
from pathlib import Path
from typing import ParamSpec, TypeVar, cast

from flext_core import FlextDecorators, FlextLogger, FlextResult, FlextTypes
from rich.console import Console

from flext_cli.constants import FlextCliConstants

# Type variables for generic decorators
P = ParamSpec("P")
T = TypeVar("T")


class FlextCliDecorators(FlextDecorators):
    """CLI-specific decorators extending flext-core FlextDecorators.

    All decorators are exposed as class methods to avoid module-level helpers.
    """

    @staticmethod
    def handle_service_result(
        func: Callable[P, T],
    ) -> Callable[P, T | None] | Callable[P, Awaitable[T | None]]:
        """Decorator for handling FlextResult values - extracts success data or returns None on failure."""
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def _async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
                try:
                    result = await func(*args, **kwargs)

                    # Process FlextResult
                    if isinstance(result, FlextResult):
                        if result.success:
                            # Type-safe extraction of value from FlextResult
                            return cast("T", result.unwrap())
                        # For failures, log error and return None
                        logger = FlextLogger(__name__)
                        logger.error(f"Async FlextResult error: {result.error}")
                        return None

                    # Pass through non-FlextResult values with type safety
                    return cast("T", result)

                except Exception:
                    # Handle exceptions by logging error and re-raising
                    logger = FlextLogger(__name__)
                    logger.exception("Exception in async decorated function")
                    raise  # Re-raise the exception for proper error handling

            return _async_wrapper

        @functools.wraps(func)
        def _sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
            try:
                result = func(*args, **kwargs)

                # Process FlextResult
                if isinstance(result, FlextResult):
                    if result.success:
                        # Type-safe extraction of value from FlextResult
                        return cast("T", result.unwrap())
                    # For failures, log error and return None
                    logger = FlextLogger(__name__)
                    logger.error(f"FlextResult error: {result.error}")
                    return None

                # Pass through non-FlextResult values with type safety
                return result

            except Exception:
                # Handle exceptions by logging error and re-raising
                logger = FlextLogger(__name__)
                logger.exception("Exception in decorated function")
                raise  # Re-raise the exception for proper error handling

        return _sync_wrapper

    @staticmethod
    def async_command(func: Callable[P, T]) -> Callable[P, T]:
        """Convert async function to sync by running with asyncio.run when safe."""
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            def _wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                try:
                    # Check if we're in an event loop already
                    asyncio.get_running_loop()
                    # If we get here, there's a running loop, cannot use asyncio.run
                    # Return error instead of coroutine
                    error_msg = "Cannot run async command within existing event loop"
                    raise RuntimeError(error_msg)
                except RuntimeError:
                    # No event loop running, safe to use asyncio.run
                    return cast("T", asyncio.run(func(*args, **kwargs)))

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
                try:
                    console = Console()
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
                        console = Console()
                        console.print(f"⏱  Execution time: {elapsed:.2f}s", style="dim")

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
                logger = FlextLogger(__name__)

                candidate = (
                    kwargs.get("config")
                    or kwargs.get("cfg")
                    or kwargs.get("settings")
                    or kwargs.get("mock_config")
                    or (args[0] if args else None)
                )

                if candidate is None:
                    logger.warning("Configuration not available for validation.")
                    return None

                def _get(c: object, k: str) -> object | None:
                    if isinstance(c, Mapping):
                        return c.get(k)
                    return getattr(c, k, None)

                for key in required_keys:
                    if _get(candidate, key) is None:
                        logger.error(f"Missing required configuration: {key}")
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
                logger = FlextLogger(__name__)
                logger.info(f"Starting: {message}")
                result = func(*args, **kwargs)
                logger.info(f"Completed: {message}")
                return result

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
    def retry(max_attempts: int = 3) -> Callable[[T], T]:  # Match superclass signature
        """Create retry decorator with exponential backoff."""

        def decorator(func: T) -> T:
            if not callable(func):
                return func

            @functools.wraps(func)
            def _wrapped(*args: object, **kwargs: object) -> T:
                last_exception: Exception | None = None

                for attempt in range(max_attempts):
                    try:
                        return cast("T", func(*args, **kwargs))
                    except Exception as e:
                        last_exception = e
                        if attempt < max_attempts - 1:  # Don't sleep on last attempt
                            sleep_time = 0.5 * (2**attempt)  # Exponential backoff
                            time.sleep(sleep_time)
                        continue

                # Re-raise the last exception if all attempts failed
                if last_exception is not None:
                    raise last_exception
                error_msg = "Retry failed without exception"
                raise RuntimeError(error_msg)

            return cast("T", _wrapped)

        return decorator


# Backward compatibility - expose static methods as module functions
handle_service_result = FlextCliDecorators.handle_service_result
flext_cli_require_confirmation = FlextCliDecorators.require_confirmation


__all__ = [
    "FlextCliDecorators",
    "flext_cli_require_confirmation",
    "handle_service_result",
]
