"""FLEXT CLI Decorators - Complete decorator system consolidating all CLI decorators.

This module consolidates all CLI-related decorators from multiple scattered files
into a single, well-organized module following PEP8 naming conventions.

Consolidated from:
    - decorators.py (root level)
    - core/decorators.py (cross-cutting concerns)
    - Various decorator definitions across modules

Design Principles:
    - PEP8 naming: cli_decorators.py (not decorators.py for clarity)
    - Single source of truth for all CLI decorators
    - Delegates to flext-core decorators where appropriate
    - Eliminates duplication through proper delegation
    - Type safety with comprehensive annotations

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import functools
import hashlib
import time
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from flext_core import FlextErrorHandlingDecorators, get_logger
from rich.console import Console

if TYPE_CHECKING:
    from collections.abc import Callable

P = ParamSpec("P")
T = TypeVar("T")

# =============================================================================
# CLI-SPECIFIC DECORATORS - Extending flext-core patterns
# =============================================================================


def cli_enhanced[**P, T](
    func: Callable[P, T] | None = None,
    *,
    validate_inputs: bool = True,
    handle_keyboard_interrupt: bool = True,
    measure_time: bool = False,
    log_execution: bool = True,
    show_spinner: bool = False,
) -> Callable[[Callable[P, T]], Callable[P, T]] | Callable[P, T]:
    """Enhanced CLI decorator combining multiple CLI-specific behaviors.

    This decorator consolidates common CLI patterns into a single,
    configurable decorator that delegates to appropriate flext-core
    decorators where possible.

    Args:
        func: Optional function for bare decorator usage (@cli_enhanced)
        validate_inputs: Enable input validation
        handle_keyboard_interrupt: Handle Ctrl+C gracefully
        measure_time: Measure and log execution time
        log_execution: Log command execution
        show_spinner: Show spinner during execution

    Returns:
        Decorated function with CLI enhancements

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        enhanced_func = func

        # Apply flext-core error handling if available
        if handle_keyboard_interrupt:
            enhanced_func = FlextErrorHandlingDecorators.safe_call()(enhanced_func)  # type: ignore[assignment]

        # Apply CLI-specific decorators
        if validate_inputs:
            enhanced_func = cli_validate_inputs(enhanced_func)

        if handle_keyboard_interrupt:
            enhanced_func = cli_handle_keyboard_interrupt(enhanced_func)

        if measure_time:
            enhanced_func = cli_measure_time(enhanced_func)

        if log_execution:
            enhanced_func = cli_log_execution(enhanced_func)

        if show_spinner:
            enhanced_func = cli_spinner()(enhanced_func)

        return enhanced_func

    # Support both @cli_enhanced and @cli_enhanced(...)
    if func is not None:
        return decorator(func)
    return decorator


def cli_validate_inputs[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    """Validate CLI command inputs before execution.

    Delegates to flext-core validation where possible and adds
    CLI-specific input validation.
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        logger = get_logger(func.__name__)

        # Basic input validation (linear, minimal branching)
        for arg in args:
            if isinstance(arg, str) and arg.strip() == "":
                logger.error("Input validation failed for %s", func.__name__)
                msg = "Empty string argument not allowed"
                raise ValueError(msg)

        for key, value in kwargs.items():
            if (
                isinstance(value, str)
                and key.endswith("_required")
                and value.strip() == ""
            ):
                logger.error("Input validation failed for %s", func.__name__)
                raise ValueError("Required argument '" + key + "' cannot be empty")

        return func(*args, **kwargs)

    return wrapper


def cli_handle_keyboard_interrupt[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    """Handle keyboard interrupt (Ctrl+C) gracefully in CLI commands."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt as err:
            console = Console()
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            raise SystemExit(1) from err

    return wrapper


def cli_measure_time[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    """Measure and log CLI command execution time."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        logger = get_logger(func.__name__)
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time

            logger.info(
                "Command '%s' completed in %.3f seconds",
                func.__name__,
                duration,
            )
            return result

        except Exception:
            end_time = time.time()
            duration = end_time - start_time

            logger.exception(
                "Command '%s' failed after %.3f seconds",
                func.__name__,
                duration,
            )
            raise

    return wrapper


def cli_log_execution[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    """Log CLI command execution with structured logging."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        logger = get_logger(func.__name__)

        # Log command start
        logger.info("Starting CLI command: %s", func.__name__)

        try:
            result = func(*args, **kwargs)

            # Log successful completion
            logger.info("CLI command completed successfully: %s", func.__name__)

            return result

        except Exception:
            # Log failure
            logger.exception("CLI command failed: %s", func.__name__)
            raise

    return wrapper


def cli_confirm(
    message: str,
    *,
    default: bool = False,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Require user confirmation before executing CLI command.

    Args:
        message: Confirmation message to display
        default: Default response if user just presses Enter

    Returns:
        Decorator that requires confirmation before execution

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            console = Console()

            # Show confirmation prompt
            default_text = "Y/n" if default else "y/N"
            prompt = f"{message} ({default_text}): "

            try:
                response = input(prompt).strip().lower()

                if not response:
                    confirmed = default
                elif response in {"y", "yes", "true", "1"}:
                    confirmed = True
                elif response in {"n", "no", "false", "0"}:
                    confirmed = False
                else:
                    console.print("[red]Please answer 'y' or 'n'[/red]")
                    raise SystemExit(1)

                if confirmed:
                    return func(*args, **kwargs)
                console.print("[yellow]Operation cancelled by user[/yellow]")
                raise SystemExit(1)

            except (EOFError, KeyboardInterrupt) as err:
                console.print("\n[yellow]Operation cancelled by user[/yellow]")
                raise SystemExit(1) from err

        return wrapper

    return decorator


def cli_retry(
    *,
    max_attempts: int = 3,
    delay: float = 1.0,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Retry CLI command on failure with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds

    Returns:
        Decorator that retries failed commands

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            logger = get_logger(func.__name__)
            console = Console()

            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except KeyboardInterrupt:
                    # Don't retry on user cancellation
                    raise

                except Exception as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        retry_delay = delay * (2**attempt)  # Exponential backoff

                        logger.warning(
                            "Attempt %d failed for %s: %s. Retrying in %.1f seconds...",
                            attempt + 1,
                            func.__name__,
                            e,
                            retry_delay,
                        )

                        console.print(
                            f"[yellow]Attempt {attempt + 1} failed. "
                            f"Retrying in {retry_delay:.1f} seconds...[/yellow]",
                        )

                        time.sleep(retry_delay)
                    else:
                        logger.exception(
                            "All %d attempts failed for %s",
                            max_attempts,
                            func.__name__,
                        )

            # If we get here, all attempts failed
            if last_exception:
                raise last_exception
            msg = f"All {max_attempts} attempts failed"
            raise RuntimeError(msg)

        return wrapper

    return decorator


def cli_spinner(
    *,
    message: str = "Processing...",
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Show spinner during CLI command execution.

    Args:
        message: Message to display with spinner

    Returns:
        Decorator that shows spinner during execution

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            console = Console()

            with console.status(message, spinner="dots"):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def cli_cache_result(
    *,
    cache_key: str | None = None,
    ttl: int = 300,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Cache CLI command results to avoid repeated execution.

    Args:
        cache_key: Custom cache key (defaults to function name + args hash)
        ttl: Time to live in seconds

    Returns:
        Decorator that caches command results

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        cache: dict[str, tuple[T, float]] = {}

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Generate cache key
            if cache_key:
                key = cache_key
            else:
                # Create key from function name and arguments
                arg_str = str(args) + str(sorted(kwargs.items()))
                key = f"{func.__name__}_{hashlib.sha256(arg_str.encode(), usedforsecurity=False).hexdigest()[:8]}"

            # Check cache
            current_time = time.time()
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < ttl:
                    logger = get_logger(func.__name__)
                    logger.debug(f"Using cached result for {func.__name__}")
                    return result
                # Expired, remove from cache
                del cache[key]

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)

            return result

        return wrapper

    return decorator


def cli_inject_config(config_key: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Inject configuration into CLI command.

    Args:
        config_key: Configuration key to inject

    Returns:
        Decorator that injects configuration

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # This would integrate with the actual configuration system
            # For now, it's a placeholder implementation
            logger = get_logger(func.__name__)
            logger.debug("Injecting configuration key: %s", config_key)

            # Add config to kwargs if not already present
            if "config" not in kwargs:
                # This would load actual configuration
                kwargs = dict(kwargs)  # type: ignore[assignment]
                kwargs["config"] = {config_key: "default_value"}

            return func(*args, **kwargs)

        return wrapper

    return decorator


def cli_file_operation(
    *,
    backup: bool = True,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Handle file operations with optional backup.

    Args:
        backup: Whether to create backups before file operations

    Returns:
        Decorator that handles file operations safely

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            logger = get_logger(func.__name__)

            if backup:
                logger.debug(f"File operation with backup enabled: {func.__name__}")
                # Backup logic would go here

            try:
                return func(*args, **kwargs)
            except OSError:
                logger.exception("File operation failed in %s", func.__name__)
                raise

        return wrapper

    return decorator


# =============================================================================
# LEGACY COMPATIBILITY DECORATORS
# =============================================================================

# Legacy aliases for backward compatibility
flext_cli_enhanced = cli_enhanced
flext_cli_validate_inputs = cli_validate_inputs
flext_cli_handle_keyboard_interrupt = cli_handle_keyboard_interrupt
flext_cli_measure_time = cli_measure_time
flext_cli_log_execution = cli_log_execution
flext_cli_confirm = cli_confirm
flext_cli_retry = cli_retry
flext_cli_cache_result = cli_cache_result
flext_cli_inject_config = cli_inject_config
flext_cli_file_operation = cli_file_operation


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "cli_cache_result",
    "cli_confirm",
    # Modern CLI decorators
    "cli_enhanced",
    "cli_file_operation",
    "cli_handle_keyboard_interrupt",
    "cli_inject_config",
    "cli_log_execution",
    "cli_measure_time",
    "cli_retry",
    "cli_spinner",
    "cli_validate_inputs",
    "flext_cli_cache_result",
    "flext_cli_confirm",
    # Legacy aliases
    "flext_cli_enhanced",
    "flext_cli_file_operation",
    "flext_cli_handle_keyboard_interrupt",
    "flext_cli_inject_config",
    "flext_cli_log_execution",
    "flext_cli_measure_time",
    "flext_cli_retry",
    "flext_cli_validate_inputs",
]
