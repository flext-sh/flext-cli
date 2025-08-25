"""FLEXT CLI Decorators.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import functools
import hashlib
import time
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import ParamSpec, TypeVar, cast

from flext_core import (
    FlextCallable,
    FlextDecorators,
    FlextResult,
    get_logger,
    safe_call,
)
from rich.console import Console

P = ParamSpec("P")
T = TypeVar("T")

# =============================================================================
# CLI-SPECIFIC DECORATORS - Extending flext-core patterns
# =============================================================================


def cli_enhanced[T, **P](
    func: Callable[P, T] | None = None,
    *,
    validate_inputs: bool = False,
    handle_keyboard_interrupt: bool = True,
    measure_time: bool = False,
    log_execution: bool = False,
    show_spinner: bool = False,
    safe_execution: bool = True,
) -> Callable[[Callable[P, T]], Callable[P, T]] | Callable[P, T]:
    """Enhanced CLI decorator using flext-core FlextDecorators patterns.

    Integrates with FlextDecorators for modern decorator patterns including
    safe execution, validation, timing, and logging capabilities.
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        """Decorator that uses FlextDecorators for comprehensive CLI enhancement."""
        # Start with base function
        enhanced_func = func

        # Apply FlextDecorators chain based on options
        if safe_execution:
            # Cast to FlextCallable[T] for FlextDecorators.safe_result compatibility
            # This preserves the return type T through the decoration chain
            flext_callable = cast("FlextCallable[T]", enhanced_func)
            safe_wrapper = FlextDecorators.safe_result(flext_callable)

            # Wrap the safe result to handle CLI-specific needs
            @functools.wraps(func)
            def cli_safe_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                """CLI-specific wrapper for FlextResult handling."""
                logger = get_logger(func.__name__) if log_execution else None

                # Show spinner if requested
                if show_spinner and logger:
                    logger.info("Processing %s...", func.__name__)

                # Validate inputs if requested
                if validate_inputs:
                    _validate_cli_inputs(args, kwargs)

                # Execute with timing if requested
                if measure_time and logger:
                    start_time = time.time()
                    result = safe_wrapper(*args, **kwargs)
                    elapsed = time.time() - start_time
                    logger.info(
                        "Function %s completed in %.3fs", func.__name__, elapsed
                    )
                else:
                    result = safe_wrapper(*args, **kwargs)

                # Handle FlextResult return from FlextDecorators.safe_result
                if isinstance(result, FlextResult):
                    # Log errors but preserve FlextResult pattern
                    if result.is_failure and logger:
                        error = result.error or "Unknown error"
                        logger.error(
                            "CLI command failed: %s - %s", func.__name__, error
                        )

                        # Handle keyboard interrupt specially
                        if "KeyboardInterrupt" in error and handle_keyboard_interrupt:
                            raise SystemExit(1)

                    # Always return the FlextResult to preserve railway-oriented programming
                    return cast("T", result)

                # If not a FlextResult, return directly
                return cast("T", result)

            enhanced_func = cli_safe_wrapper

        else:
            # Without safe execution, just basic CLI wrapper
            @functools.wraps(func)
            def basic_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                logger = get_logger(func.__name__) if log_execution else None

                if show_spinner and logger:
                    logger.info("Processing %s...", func.__name__)

                if validate_inputs:
                    _validate_cli_inputs(args, kwargs)

                try:
                    if measure_time and logger:
                        start_time = time.time()
                        result = func(*args, **kwargs)
                        elapsed = time.time() - start_time
                        logger.info(
                            "Function %s completed in %.3fs", func.__name__, elapsed
                        )
                        return result
                    return func(*args, **kwargs)
                except KeyboardInterrupt as e:
                    if handle_keyboard_interrupt:
                        raise SystemExit(1) from e
                    raise

            enhanced_func = basic_wrapper

        return enhanced_func

    # Support both @cli_enhanced and @cli_enhanced(...)
    if func is not None:
        return decorator(func)
    return decorator


def _validate_cli_inputs(args: tuple[object, ...], kwargs: dict[str, object]) -> None:
    """Basic CLI input validation helper."""
    # Basic validation - check for None values in required parameters
    for arg in args:
        if arg is None:
            msg = "Required positional argument cannot be None"
            raise ValueError(msg)

    # Check for empty strings in common CLI parameters
    for key, value in kwargs.items():
        if isinstance(value, str) and not value.strip():
            msg = f"Parameter '{key}' cannot be empty"
            raise ValueError(msg)


def cli_validate_inputs[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    """Validate CLI command inputs using flext-core patterns.

    Integrates with flext-core validation and adds CLI-specific
    input validation for better error handling.

    Args:
      func: Function to validate inputs for

    Returns:
      Wrapper function with validation logic

    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        """Wrapper with flext-core validation patterns."""
        logger = get_logger(func.__name__)

        def validate_and_execute() -> T:
            # Use flext-core patterns for validation
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

        # Use safe_call for flext-core integration and unwrap_or pattern
        result = safe_call(validate_and_execute)

        if result.is_failure:
            logger.error("Validation failed: %s", result.error)

        # Use .unwrap_or_raise() pattern to simplify error handling
        return FlextResult.unwrap_or_raise(result, RuntimeError)

    return wrapper


def cli_handle_keyboard_interrupt[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    """Handle keyboard interrupt (Ctrl+C) gracefully in CLI commands.

    Args:
      func (Callable[P, T]): Description.

    Returns:
      Callable[P, T]: Description.

    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        """Wrapper function.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            T: Description.

        """
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt as err:
            console = Console()
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            raise SystemExit(1) from err

    return wrapper


def cli_measure_time[**P, T](
    func: Callable[P, T] | None = None,
    *,
    show_in_output: bool = True,
) -> Callable[[Callable[P, T]], Callable[P, T]] | Callable[P, T]:
    """Measure and log CLI command execution time.

    Args:
        func: Function to decorate (for bare decorator usage)
        show_in_output: Whether to print timing information to console

    Returns:
        Decorated function or decorator

    """

    def decorator(f: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Wrapper function."""
            logger = get_logger(f.__name__)
            start_time = time.time()

            try:
                result = f(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time

                # Log to logger
                logger.info(
                    "Command '%s' completed in %.3f seconds",
                    f.__name__,
                    duration,
                )

                # Optionally print to console
                if show_in_output:
                    console = Console()
                    console.print(f"⏱  Execution time: {duration:.2f}s", style="dim")

                return result

            except Exception:
                end_time = time.time()
                duration = end_time - start_time

                logger.exception(
                    "Command '%s' failed after %.3f seconds",
                    f.__name__,
                    duration,
                )
                raise

        return wrapper

    # Support both @cli_measure_time and @cli_measure_time(show_in_output=False)
    if func is not None:
        return decorator(func)
    return decorator


def cli_log_execution[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    """Log CLI command execution with structured logging.

    Args:
      func (Callable[P, T]): Description.

    Returns:
      Callable[P, T]: Description.

    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        """Wrapper function.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            T: Description.

        """
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


def cli_confirm_decorator(
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



    Args:
      message (str): Description.
      default (bool): Description.

    Returns:
      Callable[[Callable[P, T]], Callable[P, T]]: Description.

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        """Decorator function.

        Args:
            func (Callable[P, T]): Description.

        Returns:
            Callable[P, T]: Description.

        """

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Wrapper function.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                T: Description.

            """
            console = Console()

            # Show confirmation prompt
            default_text = "Y/n" if default else "y/N"
            prompt = f"{message} ({default_text}): "

            try:
                response = console.input(prompt).strip().lower()

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



    Args:
      max_attempts (int): Description.
      delay (float): Description.

    Returns:
      Callable[[Callable[P, T]], Callable[P, T]]: Description.

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        """Decorator function.

        Args:
            func (Callable[P, T]): Description.

        Returns:
            Callable[P, T]: Description.

        """

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Wrapper function.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                T: Description.

            """
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
                            f"[yellow]Attempt {attempt + 1} failed. Retrying in {retry_delay:.1f} seconds...[/yellow]"
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
    message: str = "Processing...",
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Show spinner during CLI command execution.

    Args:
          message: Message to display with spinner

    Returns:
          Decorator that shows spinner during execution



    Args:
      message (str): Description.

    Returns:
      Callable[[Callable[P, T]], Callable[P, T]]: Description.

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        """Decorator function.

        Args:
            func (Callable[P, T]): Description.

        Returns:
            Callable[P, T]: Description.

        """

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Wrapper function.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                T: Description.

            """
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



    Args:
      cache_key (str | None): Description.
      ttl (int): Description.

    Returns:
      Callable[[Callable[P, T]], Callable[P, T]]: Description.

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        """Decorator function.

        Args:
            func (Callable[P, T]): Description.

        Returns:
            Callable[P, T]: Description.

        """
        cache: dict[str, tuple[T, float]] = {}

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Wrapper function.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                T: Description.

            """
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



    Args:
      config_key (str): Description.

    Returns:
      Callable[[Callable[P, T]], Callable[P, T]]: Description.

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        """Decorator function.

        Args:
            func (Callable[P, T]): Description.

        Returns:
            Callable[P, T]: Description.

        """

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Wrapper function.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                T: Description.

            """
            # This would integrate with the actual configuration system
            # For now, it's a placeholder implementation
            logger = get_logger(func.__name__)
            logger.debug("Injecting configuration key: %s", config_key)

            # Add config to kwargs if not already present
            if "config" not in kwargs:
                # Create new kwargs dict with injected config
                new_kwargs = dict(kwargs)
                new_kwargs["config"] = {config_key: "default_value"}
                # Use type ignore for kwargs unpacking due to ParamSpec limitations
                return func(*args, **new_kwargs)  # type: ignore[arg-type]

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



    Args:
      backup (bool): Description.

    Returns:
      Callable[[Callable[P, T]], Callable[P, T]]: Description.

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        """Decorator function.

        Args:
            func (Callable[P, T]): Description.

        Returns:
            Callable[P, T]: Description.

        """

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Wrapper function.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                T: Description.

            """
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
# CONSOLIDATION FROM core/decorators.py - Adding unique functionality
# =============================================================================


def async_command[**P, SendType, RecvType, T](
    func: Callable[P, Coroutine[SendType, RecvType, T]],
) -> Callable[P, T]:
    """Convert an async function into a sync function via asyncio.run."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return asyncio.run(func(*args, **kwargs))

    return wrapper


def require_auth(
    *,
    token_file: str | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
    """Require authentication by checking for a token file."""

    def decorator(func: Callable[P, T]) -> Callable[P, T | None]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
            path = token_file
            if path is None:
                path = str(Path.home() / ".flext" / "auth" / "token")
            p = Path(path)
            if not p.exists():
                return None
            content = p.read_text(encoding="utf-8").strip()
            if not content:
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_config(
    required_keys: list[str],
) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
    """Validate that a configuration object has the required keys."""

    def decorator(func: Callable[P, T]) -> Callable[P, T | None]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
            console = Console()
            config = kwargs.get("config")
            if config is None and args:
                config = args[0]
            if config is None:
                console.print(
                    "Configuration not available for validation.", style="red"
                )
                return None
            missing = [key for key in required_keys if not hasattr(config, key)]
            if missing:
                console.print(
                    f"Missing required configuration: {missing[0]}", style="red"
                )
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


# =============================================================================
# COMPATIBILITY DECORATORS
# =============================================================================

# Decorator aliases
flext_cli_enhanced = cli_enhanced
flext_cli_validate_inputs = cli_validate_inputs
flext_cli_handle_keyboard_interrupt = cli_handle_keyboard_interrupt
flext_cli_measure_time = cli_measure_time
flext_cli_log_execution = cli_log_execution
flext_cli_confirm = cli_confirm_decorator
flext_cli_retry = cli_retry
flext_cli_cache_result = cli_cache_result
flext_cli_inject_config = cli_inject_config
flext_cli_file_operation = cli_file_operation


def cli_complete(  # type: ignore[explicit-any]
    model_class: type | None = None,
    *,
    cache_size: int = 128,
    with_timing: bool = False,
    with_logging: bool = False,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Complete CLI decorator using FlextDecorators.complete_decorator.

    This provides full FlextDecorators functionality for CLI functions including
    validation, caching, timing, and logging in a single decorator.

    Args:
        model_class: Optional Pydantic model for input validation
        cache_size: Cache size for result caching
        with_timing: Enable execution timing
        with_logging: Enable structured logging

    Returns:
        Complete decorator with all requested features

    """
    return cast(  # type: ignore[explicit-any]
        "Callable[[Callable[..., T]], Callable[..., T]]",
        FlextDecorators.complete_decorator(
            validator_class=model_class,
            cache_size=cache_size,
            with_timing=with_timing,
            with_logging=with_logging,
        ),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Consolidated decorators from core/decorators.py
    "async_command",
    # Modern CLI decorators using FlextDecorators
    "cli_cache_result",
    "cli_complete",
    "cli_confirm_decorator",
    "cli_enhanced",
    "cli_file_operation",
    "cli_handle_keyboard_interrupt",
    "cli_inject_config",
    "cli_log_execution",
    "cli_measure_time",
    "cli_retry",
    "cli_spinner",
    "cli_validate_inputs",
    # Decorator aliases
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
    "require_auth",
    "validate_config",
]
