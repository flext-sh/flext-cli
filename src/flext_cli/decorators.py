"""FLEXT CLI Decorators - Class-only decorator utilities (no free helpers)."""

from __future__ import annotations

import asyncio
import functools
import time
from collections.abc import Awaitable, Callable, Mapping
from pathlib import Path
from typing import overload

from flext_cli.constants import FlextCliConstants
from flext_core import FlextLogger, FlextResult, P, T


class FlextCliDecorators:
    """CLI-specific decorator utilities."""

    @staticmethod
    def cli_measure_time(func: Callable[P, T]) -> Callable[P, T]:
        """Decorator to measure and log execution time of CLI commands.

        Args:
            func: Function to wrap with timing measurement

        Returns:
            Wrapped function that logs execution time

        """

        @functools.wraps(func)
        def _wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            start_time = time.time()
            logger = FlextLogger(__name__)

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(
                    f"Command '{func.__name__}' executed in {execution_time:.3f}s",
                )
                return result
            except Exception:
                execution_time = time.time() - start_time
                logger.exception(
                    f"Command '{func.__name__}' failed after {execution_time:.3f}s",
                )
                raise

        return _wrapper

    @staticmethod
    @overload
    def handle_service_result(
        func: Callable[P, FlextResult[T]],
    ) -> Callable[P, T | None]: ...

    @staticmethod
    @overload
    def handle_service_result(
        func: Callable[P, Awaitable[FlextResult[T]]],
    ) -> Callable[P, Awaitable[T | None]]: ...

    @staticmethod
    def handle_service_result(
        func: Callable[P, FlextResult[T]] | Callable[P, Awaitable[FlextResult[T]]],
    ) -> Callable[P, T | None] | Callable[P, Awaitable[T | None]]:
        """Decorator for handling FlextResult values - extracts success data or returns None on failure."""
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def _async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
                try:
                    result = await func(*args, **kwargs)

                    # Process FlextResult - func should return FlextResult[T]
                    if isinstance(result, FlextResult):
                        if result.success:
                            # Type-safe extraction of value from FlextResult
                            unwrapped_value: T = result.unwrap()
                            return unwrapped_value
                        # For failures, log error and return None
                        logger = FlextLogger(__name__)
                        logger.error(f"Async FlextResult error: {result.error}")
                        return None

                    # This shouldn't happen if func returns FlextResult[T]
                    logger = FlextLogger(__name__)
                    logger.warning(f"Expected FlextResult, got {type(result)}")
                    return None

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

                # Process FlextResult - func should return FlextResult[T]
                if isinstance(result, FlextResult):
                    if result.success:
                        # Type-safe extraction of value from FlextResult
                        unwrapped_value: T = result.unwrap()
                        return unwrapped_value
                    # For failures, log error and return None
                    logger = FlextLogger(__name__)
                    logger.error(f"FlextResult error: {result.error}")
                    return None

                # This shouldn't happen if func returns FlextResult[T]
                logger = FlextLogger(__name__)
                logger.warning(f"Expected FlextResult, got {type(result)}")
                return None

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
                    error_msg = "Cannot run async command within existing event loop"
                    raise RuntimeError(error_msg)
                except RuntimeError as e:
                    # Check if this is the "no running loop" error or our custom error
                    if "Cannot run async command" in str(e):
                        raise
                    # No event loop running, safe to use asyncio.run
                    result: T = asyncio.run(func(*args, **kwargs))
                    return result

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
                    answer = input(f"{message} (y/N): ").strip().lower()
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
                        logger = FlextLogger(__name__)
                        logger.info(f"⏱  Execution time: {elapsed:.2f}s")

            return _wrapped

        return _decorator

    @staticmethod
    def validate_config(
        required_keys: list[str],
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
                        result = c.get(k)
                        return result if result is not None else None
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
        _validators: list[str],
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
    def cli_retry(max_attempts: int = 3) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """Create CLI-specific retry decorator with exponential backoff."""

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            @functools.wraps(func)
            def _wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
                last_exception: Exception | None = None

                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
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

            return _wrapped

        return decorator

    # CLI-specific retry alias to avoid override conflict

    # Override the stub retry method from flext-core with proper implementation
    @staticmethod
    def retry(
        max_attempts: int = 3,
        *,
        exceptions: tuple[type[BaseException], ...] = (Exception,),
        initial_backoff: float = 0.5,
        backoff_multiplier: float = 2.0,
        logger_name: str | None = None,
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """Retry decorator with actual retry functionality (overrides flext-core stub)."""

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            @functools.wraps(func)
            def _wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
                last_exception: BaseException | None = None
                logger = FlextLogger(logger_name or func.__name__)

                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts - 1:  # Don't sleep on last attempt
                            sleep_time = initial_backoff * (backoff_multiplier**attempt)
                            logger.debug(
                                f"Retry attempt {attempt + 1}/{max_attempts} failed: {e}, sleeping {sleep_time}s",
                            )
                            time.sleep(sleep_time)
                        continue

                # Re-raise the last exception if all attempts failed
                if last_exception is not None:
                    logger.error(f"All {max_attempts} retry attempts failed")
                    raise last_exception
                error_msg = "Retry failed without exception"
                raise RuntimeError(error_msg)

            return _wrapped

        return decorator


__all__ = [
    "FlextCliDecorators",
]
