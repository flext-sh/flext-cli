"""Core decorators."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable, Coroutine
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from rich.console import Console

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

P = ParamSpec("P")
T = TypeVar("T")
SendType = TypeVar("SendType")
RecvType = TypeVar("RecvType")


def async_command[**P, SendType, RecvType, T](
    func: Callable[P, Coroutine[SendType, RecvType, T]],
) -> Callable[P, T]:
    """Convert an async function into a sync function via asyncio.run.

    Args:
        func (Callable[P, Coroutine[SendType, RecvType, T]]): Description.

    Returns:
        Callable[P, T]: Description.

    """
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        """Wrapper function.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            T: Description.

        """
        return asyncio.run(func(*args, **kwargs))

    return wrapper


def confirm_action(message: str) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
    """Request confirmation before executing the wrapped function.

    Args:
        message (str): Description.

    Returns:
        Callable[[Callable[P, T]], Callable[P, T | None]]: Description.

    """
    def decorator(func: Callable[P, T]) -> Callable[P, T | None]:
        """Decorator function.

        Args:
            func (Callable[P, T]): Description.

        Returns:
            Callable[P, T | None]: Description.

        """
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
            """Wrapper function.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                T | None: Description.

            """
            console = Console()
            response = console.input(f"{message} [y/N]: ").strip().lower()
            if response in {"y", "yes"}:
                return func(*args, **kwargs)
            return None

        return wrapper

    return decorator


def require_auth(
    *,
    token_file: str | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
    """Require authentication by checking for a token file.

    Args:
        token_file (str | None): Description.

    Returns:
        Callable[[Callable[P, T]], Callable[P, T | None]]: Description.

    """
    def decorator(func: Callable[P, T]) -> Callable[P, T | None]:
        """Decorator function.

        Args:
            func (Callable[P, T]): Description.

        Returns:
            Callable[P, T | None]: Description.

        """
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
            """Wrapper function.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                T | None: Description.

            """
            path = token_file
            if path is None:
                # Default path under ~/.flext/auth/token
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


def measure_time(
    *,
    show_in_output: bool = False,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Measure the execution time of a function.

    Args:
        show_in_output (bool): Description.

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
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Wrapper function.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                T: Description.

            """
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            if show_in_output:
                Console().print(f"⏱  Execution time: {elapsed:.2f}s", style="dim")
            return result

        return wrapper

    return decorator


def retry(
    *,
    max_attempts: int,
    delay: float,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Retry a function call on failure.

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
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Wrapper function.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                T: Description.

            """
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    if attempt < max_attempts:
                        time.sleep(delay)
            if last_exc is not None:
                raise last_exc
            # This line is unreachable, but mypy needs it
            msg = "Retry failed unexpectedly"
            raise RuntimeError(msg)

        return wrapper

    return decorator


def validate_config(
    required_keys: list[str],
) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
    """Validate that a configuration object has the required keys.

    Args:
        required_keys (list[str]): Description.

    Returns:
        Callable[[Callable[P, T]], Callable[P, T | None]]: Description.

    """
    def decorator(func: Callable[P, T]) -> Callable[P, T | None]:
        """Decorator function.

        Args:
            func (Callable[P, T]): Description.

        Returns:
            Callable[P, T | None]: Description.

        """
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
            """Wrapper function.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                T | None: Description.

            """
            console = Console()
            config = kwargs.get("config")
            if config is None and args:
                # fallback: try first positional
                config = args[0]
            if config is None:
                console.print(
                    "Configuration not available for validation.",
                    style="red",
                )
                return None
            missing = [key for key in required_keys if not hasattr(config, key)]
            if missing:
                console.print(
                    f"Missing required configuration: {missing[0]}",
                    style="red",
                )
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def with_spinner(
    message: str = "Processing...",
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Display a spinner while a function is executing.

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
        @wraps(func)
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
