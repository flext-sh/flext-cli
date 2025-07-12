"""Decorators for FLEXT CLI framework.

Copyright (c) 2025 FLEXT Team. All rights reserved.
"""

from __future__ import annotations

import asyncio
import functools
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any
from typing import TypeVar

import click

F = TypeVar("F", bound=Callable[..., Any])


def async_command[F: Callable[..., Any]](f: F) -> F:
    @functools.wraps(f)
    def wrapper(*args, **kwargs) -> None:
        return asyncio.run(f(*args, **kwargs))

    return wrapper


def confirm_action(message: str = "Are you sure?", default: bool = False) -> Callable[[F], F]:
    """Decorator to confirm dangerous actions.

    Args:
        message: Confirmation message
        default: Default answer if user just presses Enter

    Example:
        @cli.command()
        @confirm_action("This will delete all data. Continue?")
        def delete_all() -> None:
            # Dangerous operation
            pass

    """

    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args, **kwargs) -> None:
            if not click.confirm(message, default=default):
                click.echo("Operation cancelled.")
                return None
            return f(*args, **kwargs)

        return wrapper

    return decorator


def require_auth(token_file: str = "~/.flext/auth_token") -> Callable[[F], F]:
    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args, **kwargs) -> None:
            token_path = Path(token_file).expanduser()

            if not token_path.exists():
                click.echo(
                    "Authentication required. Please run 'auth login' first.",
                    err=True,
                )
                ctx = click.get_current_context()
                ctx.exit(1)

            # Add token to context
            ctx = click.get_current_context()
            ctx.ensure_object(dict)

            try:
                ctx.obj["auth_token"] = token_path.read_text().strip()
            except (OSError, PermissionError, UnicodeDecodeError) as e:
                click.echo(f"Failed to read auth token: {e}", err=True)
                ctx.exit(1)

            return f(*args, **kwargs)

        return wrapper

    return decorator


def measure_time(show_in_output: bool = True) -> Callable[[F], F]:
    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args, **kwargs) -> None:
            start_time = time.time()

            try:
                return f(*args, **kwargs)
            finally:
                elapsed = time.time() - start_time

                if show_in_output:
                    # Get CLI instance from context
                    ctx = click.get_current_context()
                    cli = ctx.obj.get("cli")

                    if cli and hasattr(cli, "print_info"):
                        cli.print_info(f"Execution time: {elapsed:.2f}s")
                    else:
                        click.echo(f"\nExecution time: {elapsed:.2f}s")

        return wrapper

    return decorator


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Callable[[F], F]:
    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args, **kwargs) -> None:
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return f(*args, **kwargs)
                except (
                    OSError,
                    ValueError,
                    RuntimeError,
                    TypeError,
                    ConnectionError,
                ) as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        click.echo(
                            f"Attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {current_delay:.1f}s...",
                            err=True,
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff

            # All attempts failed
            click.echo(f"All {max_attempts} attempts failed.", err=True)
            if last_exception:
                raise last_exception
            return None

        return wrapper

    return decorator


def validate_config(required_keys: list[str]) -> Callable[[F], F]:
    """Decorator to validate configuration before running command.

    Args:
        required_keys: List of required configuration keys

    Example:
        @cli.command()
        @validate_config(["api_url", "api_token"])
        def api_command() -> None:
            # Command that needs API config
            pass

    """

    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args, **kwargs) -> None:
            ctx = click.get_current_context()
            config = ctx.obj.get("config", {})

            missing_keys = [key for key in required_keys if not config.get(key)]

            if missing_keys:
                click.echo(
                    f"Missing required configuration: {', '.join(missing_keys)}. "
                    f"Please run 'config set' to configure these values.",
                    err=True,
                )
                ctx.exit(1)

            return f(*args, **kwargs)

        return wrapper

    return decorator


def with_spinner(message: str = "Processing...") -> Callable[[F], F]:
    """Decorator to show a spinner during command execution.

    Args:
        message: Message to show with spinner

    Example:
        @cli.command()
        @with_spinner("Loading data...")
        def load_command() -> None:
            # Long-running operation
            pass

    """

    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args, **kwargs) -> None:
            ctx = click.get_current_context()
            cli = ctx.obj.get("cli")

            if cli and hasattr(cli, "create_progress"):
                with cli.create_progress(message) as progress:
                    task = progress.add_task(message, total=None)
                    result = f(*args, **kwargs)
                    progress.update(task, completed=100)
                return result
            # Fallback if no CLI instance
            click.echo(f"{message}")
            return f(*args, **kwargs)

        return wrapper

    return decorator
