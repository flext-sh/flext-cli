"""FlextCli Decorators - Advanced boilerplate reduction decorators.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import functools
import time
from typing import TYPE_CHECKING, Any, TypeVar

from flext_core import FlextResult, get_logger

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")
logger = get_logger(__name__)


def flext_cli_result_wrapper(error_prefix: str = "Operation failed") -> Callable:
    """Decorator to automatically wrap function results in FlextResult."""
    def decorator(func: Callable[..., T]) -> Callable[..., FlextResult[T]]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> FlextResult[T]:
            try:
                result = func(*args, **kwargs)
                return FlextResult(success=True, data=result, error=None)
            except Exception as e:
                error_msg = f"{error_prefix}: {e}"
                logger.exception(f"Function {func.__name__} failed")
                return FlextResult(success=False, data=None, error=error_msg)
        return wrapper
    return decorator


def flext_cli_validate_input(validator: Callable[[Any], bool], error_msg: str = "Invalid input") -> Callable:
    """Decorator to validate function inputs."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Validate first positional argument if exists
            if args and not validator(args[0]):
                raise ValueError(error_msg)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def flext_cli_retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Callable:
    """Decorator for automatic retry with exponential backoff."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.exception(f"All {max_attempts} attempts failed for {func.__name__}")

            # Re-raise the last exception if all attempts failed
            if last_exception:
                raise last_exception

            msg = f"Function {func.__name__} failed after {max_attempts} attempts"
            raise RuntimeError(msg)
        return wrapper
    return decorator


def flext_cli_cache_result(ttl_seconds: int = 300) -> Callable:
    """Decorator for simple result caching with TTL."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache: dict[str, tuple[T, float]] = {}

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            current_time = time.time()

            # Check if cached result exists and is still valid
            if cache_key in cache:
                cached_result, timestamp = cache[cache_key]
                if current_time - timestamp < ttl_seconds:
                    return cached_result
                # Remove expired entry
                del cache[cache_key]

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            return result

        # Add cache management methods
        wrapper.clear_cache = lambda: cache.clear()  # type: ignore[attr-defined]
        wrapper.cache_info = lambda: {  # type: ignore[attr-defined]
            "cache_size": len(cache),
            "ttl_seconds": ttl_seconds,
        }

        return wrapper
    return decorator


def flext_cli_timing(log_result: bool = True) -> Callable:
    """Decorator to measure and log function execution time."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                execution_time = time.perf_counter() - start_time

                if log_result:
                    logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")

                # Store timing info as function attribute
                wrapper.last_execution_time = execution_time  # type: ignore[attr-defined]

                return result
            except Exception as e:
                execution_time = time.perf_counter() - start_time
                logger.exception(f"{func.__name__} failed after {execution_time:.4f} seconds: {e}")
                raise

        return wrapper
    return decorator


def flext_cli_deprecation_warning(
    message: str,
    replacement: str | None = None,
    removal_version: str | None = None,
) -> Callable:
    """Decorator to mark functions as deprecated with warnings."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            import warnings

            warning_msg = f"{func.__name__} is deprecated. {message}"
            if replacement:
                warning_msg += f" Use {replacement} instead."
            if removal_version:
                warning_msg += f" Will be removed in version {removal_version}."

            warnings.warn(
                warning_msg,
                DeprecationWarning,
                stacklevel=2,
            )

            return func(*args, **kwargs)
        return wrapper
    return decorator


def flext_cli_data_validator(
    required_keys: list[str] | None = None,
    optional_keys: list[str] | None = None,
    min_items: int | None = None,
    max_items: int | None = None,
) -> Callable:
    """Decorator to validate data structures."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Validate first argument if it's data
            if args:
                data = args[0]

                # Validate list constraints
                if isinstance(data, list):
                    if min_items is not None and len(data) < min_items:
                        msg = f"Data must have at least {min_items} items"
                        raise ValueError(msg)
                    if max_items is not None and len(data) > max_items:
                        msg = f"Data must have at most {max_items} items"
                        raise ValueError(msg)

                    # Validate dict items in list
                    if required_keys and data:
                        for item in data:
                            if isinstance(item, dict):
                                missing_keys = set(required_keys) - set(item.keys())
                                if missing_keys:
                                    msg = f"Missing required keys: {missing_keys}"
                                    raise ValueError(msg)

                # Validate dict constraints
                elif isinstance(data, dict):
                    if required_keys:
                        missing_keys = set(required_keys) - set(data.keys())
                        if missing_keys:
                            msg = f"Missing required keys: {missing_keys}"
                            raise ValueError(msg)

                    if optional_keys:
                        allowed_keys = set(required_keys or []) | set(optional_keys)
                        extra_keys = set(data.keys()) - allowed_keys
                        if extra_keys:
                            msg = f"Unexpected keys: {extra_keys}"
                            raise ValueError(msg)

            return func(*args, **kwargs)
        return wrapper
    return decorator


def flext_cli_pipeline_step(step_name: str, log_progress: bool = True) -> Callable:
    """Decorator to mark functions as pipeline steps."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            if log_progress:
                logger.info(f"Starting pipeline step: {step_name}")

            try:
                result = func(*args, **kwargs)
                if log_progress:
                    logger.info(f"Completed pipeline step: {step_name}")
                return result
            except Exception as e:
                logger.exception(f"Pipeline step '{step_name}' failed: {e}")
                raise

        # Store step metadata
        wrapper.step_name = step_name  # type: ignore[attr-defined]
        wrapper.is_pipeline_step = True  # type: ignore[attr-defined]

        return wrapper
    return decorator


def flext_cli_auto_export(
    formats: list[str],
    base_path: str = "./exports",
    auto_timestamp: bool = True,
) -> Callable:
    """Decorator to automatically export function results."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            result = func(*args, **kwargs)

            # Only export if result looks like data
            if isinstance(result, (list, dict)):
                try:
                    from flext_cli.core.data_exporter import FlextCliDataExporter

                    exporter = FlextCliDataExporter()

                    if auto_timestamp:
                        import datetime
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        export_path = f"{base_path}/{func.__name__}_{timestamp}"
                    else:
                        export_path = f"{base_path}/{func.__name__}"

                    export_result = exporter.export_multiple_formats(result, export_path, formats)

                    if export_result.success:
                        logger.info(f"Auto-exported results from {func.__name__} to {formats}")
                    else:
                        logger.warning(f"Auto-export failed for {func.__name__}: {export_result.error}")

                except Exception as e:
                    logger.warning(f"Auto-export error for {func.__name__}: {e}")

            return result
        return wrapper
    return decorator


# Convenience decorator factories
def flext_cli_quick_retry(attempts: int = 3) -> Callable:
    """Quick retry decorator with sensible defaults."""
    return flext_cli_retry(max_attempts=attempts, delay=0.5, backoff=1.5)


def flext_cli_quick_cache(minutes: int = 5) -> Callable:
    """Quick cache decorator with minute-based TTL."""
    return flext_cli_cache_result(ttl_seconds=minutes * 60)


def flext_cli_quick_timing() -> Callable:
    """Quick timing decorator with logging."""
    return flext_cli_timing(log_result=True)


# Export all decorators
__all__ = [
    "flext_cli_auto_export",
    "flext_cli_cache_result",
    "flext_cli_data_validator",
    "flext_cli_deprecation_warning",
    "flext_cli_pipeline_step",
    "flext_cli_quick_cache",
    # Quick convenience decorators
    "flext_cli_quick_retry",
    "flext_cli_quick_timing",
    "flext_cli_result_wrapper",
    "flext_cli_retry",
    "flext_cli_timing",
    "flext_cli_validate_input",
]
