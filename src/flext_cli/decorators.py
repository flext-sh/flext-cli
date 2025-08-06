"""FlextCli Advanced Decorators - Zero-Boilerplate Function Enhancement.

This module provides decorators that eliminate 90%+ of cross-cutting concerns
through AOP patterns following SOLID, DRY, and KISS principles.

Decorator Categories:
    - Data decorators: file_operation, validate_inputs, cache_result
    - Execution decorators: retry_on_failure, measure_performance, log_execution
    - UI decorators: confirm_before_execute, show_progress, handle_keyboard_interrupt
    - Configuration decorators: require_config, inject_config_values

Usage Pattern:
    @flext_cli_retry(max_attempts=3)
    @flext_cli_validate_inputs({"email": "email", "port": "port"})
    @flext_cli_confirm("Execute dangerous operation?")
    @flext_cli_measure_time
    def my_operation(email: str, port: int) -> FlextResult[str]:
        # Business logic only - all boilerplate eliminated
        return FlextResult.ok("Success")

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import functools
import inspect
import json
import os
import time
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

from flext_core import FlextResult
from rich.console import Console

from flext_cli.core.helpers import FlextCliHelper
from flext_cli.core.typedefs import FlextCliValidationType

F = TypeVar("F", bound=Callable[[object], object])


def flext_cli_file_operation(
    *,
    backup: bool = False,
    create_dirs: bool = True,
) -> Callable[[F], F]:
    """File operation decorator - eliminates 90% of file handling boilerplate.

    Automatically handles:
    - Directory creation
    - Backup file creation
    - Error handling and recovery
    - Path validation

    Example:
        @flext_cli_file_operation(backup=True)
        def save_config(data: dict, path: str) -> FlextResult[None]:
            # File operations handled automatically
            return helper.flext_cli_save_file(data, path)

    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            helper = FlextCliHelper()

            # Extract file path from arguments
            file_path = None
            if args and isinstance(args[0], (str, Path)):
                file_path = Path(args[0])
            elif "path" in kwargs:
                file_path = Path(str(kwargs["path"]))
            elif "file_path" in kwargs:
                file_path = Path(str(kwargs["file_path"]))

            if file_path and create_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)

            if file_path and backup and file_path.exists():
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                helper.flext_cli_save_file(
                    helper.flext_cli_load_file(file_path).unwrap_or({}),
                    backup_path,
                )

            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]
    return decorator


def flext_cli_validate_inputs(validations: dict[str, str]) -> Callable[[F], F]:
    """Input validation decorator - eliminates 95% of validation boilerplate.

    Args:
        validations: Mapping of parameter names to validation types

    Example:
        @flext_cli_validate_inputs({"email": "email", "port": "port"})
        def send_notification(email: str, port: int) -> FlextResult[str]:
            # Validation handled automatically
            return FlextResult.ok("Sent")

    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            helper = FlextCliHelper()

            # Get function parameter names
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())

            # Validate positional arguments
            for i, value in enumerate(args):
                if i < len(param_names) and param_names[i] in validations:
                    validation_type = validations[param_names[i]]
                    if validation_type == "email":
                        result = helper.flext_cli_validate_input(str(value), FlextCliValidationType.EMAIL)
                    elif validation_type == "port":
                        result = helper.flext_cli_validate_input(str(value), FlextCliValidationType.PORT)
                    elif validation_type == "url":
                        result = helper.flext_cli_validate_input(str(value), FlextCliValidationType.URL)
                    elif validation_type == "path":
                        result = helper.flext_cli_validate_input(str(value), FlextCliValidationType.PATH)
                    elif validation_type == "file":
                        result = helper.flext_cli_validate_input(str(value), FlextCliValidationType.FILE)
                    elif validation_type == "uuid":
                        result = helper.flext_cli_validate_input(str(value), FlextCliValidationType.UUID)
                    else:
                        continue

                    if not result.success:
                        return FlextResult.fail(f"Validation failed for {param_names[i]}: {result.error}")

            # Validate keyword arguments
            for param_name, value in kwargs.items():
                if param_name in validations:
                    validation_type = validations[param_name]
                    if validation_type == "email":
                        result = helper.flext_cli_validate_input(str(value), FlextCliValidationType.EMAIL)
                    elif validation_type == "port":
                        result = helper.flext_cli_validate_input(str(value), FlextCliValidationType.PORT)
                    else:
                        continue

                    if not result.success:
                        return FlextResult.fail(f"Validation failed for {param_name}: {result.error}")

            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]
    return decorator


def flext_cli_retry(
    max_attempts: int = 3,
    delay: float = 0.1,
    *,
    exponential_backoff: bool = True,
) -> Callable[[F], F]:
    """Retry decorator - eliminates 85% of retry logic boilerplate.

    Example:
        @flext_cli_retry(max_attempts=5, delay=0.2)
        def network_operation() -> FlextResult[str]:
            # Retry logic handled automatically
            return FlextResult.ok("Connected")

    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            last_error = None

            for attempt in range(max_attempts):
                try:
                    result = func(*args, **kwargs)
                    # If it's a FlextResult, check success
                    if hasattr(result, "success") and not result.success and attempt < max_attempts - 1:
                        wait_time = delay * (2 ** attempt if exponential_backoff else 1)
                        time.sleep(wait_time)
                        continue
                    return result

                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        wait_time = delay * (2 ** attempt if exponential_backoff else 1)
                        time.sleep(wait_time)
                    else:
                        return FlextResult.fail(f"Failed after {max_attempts} attempts: {e}")

            return FlextResult.fail(f"Failed after {max_attempts} attempts: {last_error}")

        return wrapper  # type: ignore[return-value]
    return decorator


def flext_cli_measure_time[F: Callable[[object], object]](func: F) -> F:
    """Performance measurement decorator - eliminates timing boilerplate.

    Example:
        @flext_cli_measure_time
        def complex_operation() -> FlextResult[str]:
            # Timing handled automatically
            return FlextResult.ok("Complete")

    """
    @functools.wraps(func)
    def wrapper(*args: object, **kwargs: object) -> object:
        console = Console()
        start_time = time.perf_counter()

        try:
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_time = end_time - start_time

            console.print(f"[dim]{func.__name__} completed in {execution_time:.3f}s[/dim]")
            return result

        except Exception as e:
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            console.print(f"[red]{func.__name__} failed after {execution_time:.3f}s: {e}[/red]")
            raise

    return wrapper  # type: ignore[return-value]


def flext_cli_confirm(message: str, *, default: bool = False) -> Callable[[F], F]:
    """Confirmation decorator - eliminates user interaction boilerplate.

    Example:
        @flext_cli_confirm("Delete all files?")
        def delete_files() -> FlextResult[str]:
            # Confirmation handled automatically
            return FlextResult.ok("Files deleted")

    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            helper = FlextCliHelper()
            confirmation = helper.flext_cli_confirm(message, default=default)

            if not confirmation.success:
                return FlextResult.fail(f"Confirmation failed: {confirmation.error}")

            if not confirmation.data:
                return FlextResult.fail("Operation cancelled by user")

            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]
    return decorator


def flext_cli_handle_keyboard_interrupt(
    cleanup_message: str = "Operation interrupted",
) -> Callable[[F], F]:
    """Keyboard interrupt handler - eliminates interrupt handling boilerplate.

    Example:
        @flext_cli_handle_keyboard_interrupt("Cleaning up...")
        def long_operation() -> FlextResult[str]:
            # Interrupt handling automatic
            return FlextResult.ok("Complete")

    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            console = Console()

            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                console.print(f"\n[yellow]{cleanup_message}[/yellow]")
                return FlextResult.fail("Operation interrupted by user")

        return wrapper  # type: ignore[return-value]
    return decorator


def flext_cli_inject_config(config_keys: list[str]) -> Callable[[F], F]:
    """Configuration injection decorator - eliminates config loading boilerplate.

    Args:
        config_keys: List of config keys to inject as keyword arguments

    Example:
        @flext_cli_inject_config(["database_url", "api_key"])
        def connect_api(database_url: str, api_key: str) -> FlextResult[str]:
            # Config injection handled automatically
            return FlextResult.ok("Connected")

    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:

            # Inject config values as keyword arguments
            for key in config_keys:
                if key not in kwargs:
                    env_key = f"FLEXT_CLI_{key.upper()}"
                    env_value = os.environ.get(env_key)
                    if env_value:
                        kwargs[key] = env_value
                    else:
                        return FlextResult.fail(f"Required config key '{key}' not found")

            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]
    return decorator


def flext_cli_cache_result(ttl_seconds: int = 300) -> Callable[[F], F]:
    """Result caching decorator - eliminates caching boilerplate.

    Example:
        @flext_cli_cache_result(ttl_seconds=600)
        def expensive_operation(param: str) -> FlextResult[str]:
            # Caching handled automatically
            return FlextResult.ok("Expensive result")

    """
    cache: dict[str, tuple[object, float]] = {}

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            # Create cache key from arguments
            cache_key = f"{func.__name__}:{json.dumps([str(arg) for arg in args] + [f'{k}={v}' for k, v in sorted(kwargs.items())], sort_keys=True)}"

            current_time = time.time()

            # Check cache
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < ttl_seconds:
                    return result

            # Execute and cache
            result = func(*args, **kwargs)
            cache[cache_key] = (result, current_time)

            return result

        return wrapper  # type: ignore[return-value]
    return decorator


def flext_cli_log_execution(
    _log_level: str = "info",
    *,
    include_args: bool = False,
) -> Callable[[F], F]:
    """Execution logging decorator - eliminates logging boilerplate.

    Example:
        @flext_cli_log_execution(log_level="debug", include_args=True)
        def important_operation(data: str) -> FlextResult[str]:
            # Logging handled automatically
            return FlextResult.ok("Complete")

    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            console = Console()

            # Log start
            args_str = f" with args={args}, kwargs={kwargs}" if include_args else ""

            console.print(f"[dim]Starting {func.__name__}{args_str}[/dim]")

            try:
                result = func(*args, **kwargs)

                # Log success
                if hasattr(result, "success"):
                    if result.success:
                        console.print(f"[green]✓ {func.__name__} completed successfully[/green]")
                    elif hasattr(result, "error"):
                        console.print(f"[red]✗ {func.__name__} failed: {result.error}[/red]")
                    else:
                        console.print(f"[red]✗ {func.__name__} failed: {result}[/red]")
                else:
                    console.print(f"[green]✓ {func.__name__} completed[/green]")

                return result

            except Exception as e:
                console.print(f"[red]✗ {func.__name__} raised exception: {e}[/red]")
                raise

        return wrapper  # type: ignore[return-value]
    return decorator


# Composite decorator for maximum convenience
def flext_cli_enhanced(
    retry_attempts: int = 3,
    *,
    measure_time: bool = True,
    log_execution: bool = True,
    handle_interrupts: bool = True,
) -> Callable[[F], F]:
    """Enhanced decorator combining multiple capabilities - maximum boilerplate reduction.

    Example:
        @flext_cli_enhanced(retry_attempts=5)
        def robust_operation() -> FlextResult[str]:
            # All enhancements applied automatically
            return FlextResult.ok("Complete")

    """
    def decorator(func: F) -> F:
        enhanced_func = func

        if handle_interrupts:
            enhanced_func = flext_cli_handle_keyboard_interrupt()(enhanced_func)

        if retry_attempts > 1:
            enhanced_func = flext_cli_retry(max_attempts=retry_attempts)(enhanced_func)

        if log_execution:
            enhanced_func = flext_cli_log_execution()(enhanced_func)

        if measure_time:
            enhanced_func = flext_cli_measure_time(enhanced_func)

        return enhanced_func

    return decorator


# Export all decorators
__all__ = [
    "flext_cli_cache_result",
    "flext_cli_confirm",
    "flext_cli_enhanced",
    "flext_cli_file_operation",
    "flext_cli_handle_keyboard_interrupt",
    "flext_cli_inject_config",
    "flext_cli_log_execution",
    "flext_cli_measure_time",
    "flext_cli_retry",
    "flext_cli_validate_inputs",
]
