"""Decorators for FLEXT CLI framework.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import functools
import time
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import TypeVar

from rich.console import Console

if TYPE_CHECKING:
    from flext_cli.config.cli_config import CLIConfig

# Generic type for decorated functions
F = TypeVar("F", bound=Callable[..., Any])


def async_command[F: Callable[..., Any]](f: F) -> F:
    """Decorator to run async functions in sync context."""

    @functools.wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(f(*args, **kwargs))

    return wrapper  # type: ignore[return-value]


def confirm_action(
    message: str = "Are you sure?",
    default: bool = False,
) -> Callable[[F], F]:
    """Decorator to add confirmation prompt before executing function.

    It is useful for adding a safety check before executing potentially destructive actions.

    Args:
        message: The message to display to the user.
        default: Whether to default to yes or no. If True, the default is yes. If False, the default is no.

    Returns:
        The decorated function.

    """

    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            console = Console()
            if console.input(f"{message} [y/N]: ").lower().startswith("y"):
                return f(*args, **kwargs)
            console.print("Operation cancelled.", style="yellow")
            return None

        return wrapper  # type: ignore[return-value]

    return decorator


def require_auth(token_file: str = "~/.flext/auth_token") -> Callable[[F], F]:
    """Decorator to require authentication before executing function."""

    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            token_path = Path(token_file).expanduser()

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
                    msg = "Empty token"
                    raise ValueError(msg)
            except Exception as e:
                console = Console()
                console.print(f"Invalid token file: {e}", style="red")
                return None

            # Add token to kwargs for the function
            kwargs["auth_token"] = token
            return f(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def measure_time(show_in_output: bool = True) -> Callable[[F], F]:
    """Decorator to measure and optionally display execution time."""

    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                return f(*args, **kwargs)
            finally:
                end_time = time.time()
                duration = end_time - start_time

                if show_in_output:
                    console = Console()
                    console.print(
                        f"⏱️  Execution time: {duration:.2f}s",
                        style="dim",
                    )

        return wrapper  # type: ignore[return-value]

    return decorator


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> Callable[[F], F]:
    """Decorator to retry function calls with exponential backoff."""

    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            console = Console()
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        console.print(
                            f"Failed after {max_attempts} attempts: {e}",
                            style="red",
                        )
                        raise

                    console.print(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay:.1f}s...",
                        style="yellow",
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff

            return None  # Should never reach here

        return wrapper  # type: ignore[return-value]

    return decorator


def validate_config(required_keys: list[str]) -> Callable[[F], F]:
    """Decorator to validate required configuration keys before execution."""

    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Try to get config from context or kwargs
            config: CLIConfig | None = kwargs.get("config")

            if not config:
                # Try to get from args (assuming first arg might be context with config)
                if args and hasattr(args[0], "config"):
                    config = args[0].config

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

        return wrapper  # type: ignore[return-value]

    return decorator


def with_spinner(message: str = "Processing...") -> Callable[[F], F]:
    """Decorator to show a spinner during function execution."""

    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            console = Console()

            with console.status(message, spinner="dots"):
                try:
                    return f(*args, **kwargs)
                except Exception:
                    # Let the exception propagate but ensure spinner stops
                    raise

        return wrapper  # type: ignore[return-value]

    return decorator
