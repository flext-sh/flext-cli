"""FLEXT CLI Decorators - Class-only decorator utilities (no free helpers)."""

from __future__ import annotations

import asyncio
import functools
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import ParamSpec, TypeVar, cast

from flext_core import FlextDecorators, FlextResult, FlextTypes
from rich.console import Console

from flext_cli.constants import FlextCliConstants

P = ParamSpec("P")
T = TypeVar("T")


def handle_service_result[**P, T](func: Callable[P, T]) -> Callable[P, T | None]:
    """Decorator for handling FlextResult values - extracts success data or returns None on failure."""
    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def _async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
            result = await func(*args, **kwargs)

            # Check if result is FlextResult
            if isinstance(result, FlextResult):
                if result.is_success:
                    return cast("T | None", result.data)
                # For failures, print error and return None
                console = Console()
                console.print(f"[red]Error: {result.error}[/red]")
                return None

            # Pass through non-FlextResult values
            return cast("T | None", result)

        return cast("Callable[P, T | None]", _async_wrapper)

    @functools.wraps(func)
    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
        result = func(*args, **kwargs)

        # Check if result is FlextResult
        if isinstance(result, FlextResult):
            if result.is_success:
                return cast("T | None", result.data)
            # For failures, print error and return None
            console = Console()
            console.print(f"[red]Error: {result.error}[/red]")
            return None

        # Pass through non-FlextResult values
        return cast("T | None", result)

    return _wrapper


class FlextCliDecorators(FlextDecorators):
    """CLI-specific decorators extending flext-core FlextDecorators.

    All decorators are exposed as class methods to avoid module-level helpers.
    """

    @staticmethod
    def async_command(func: Callable[P, T]) -> Callable[P, T]:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            def _wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                return cast("T", asyncio.run(func(*args, **kwargs)))

            return _wrapper
        return func

    @staticmethod
    def confirm_action(
        message: str,
    ) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
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
        *, show_in_output: bool = False
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
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
                            f"⏱  Execution time: {elapsed:.2f}s", style="dim"
                        )

            return _wrapped

        return _decorator

    @staticmethod
    def validate_config(
        required_keys: FlextTypes.Core.StringList,
    ) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
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
                        "Configuration not available for validation.", style="red"
                    )
                    return None

                def _get(c: object, k: str) -> object | None:
                    if isinstance(c, Mapping):
                        m = cast("Mapping[str, object]", c)
                        return m.get(k)
                    return getattr(c, k, None)

                for key in required_keys:
                    if _get(candidate, key) is None:
                        console.print(
                            f"Missing required configuration: {key}", style="red"
                        )
                        return None

                return func(*args, **kwargs)

            return _wrapped

        return _decorator

    @staticmethod
    def with_spinner(
        message: str = "Processing...",
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
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
                    f"[red]Retry failed after {max_attempts} attempts: {last_exception}[/red]"
                )
                return None

            return _wrapped

        return _decorator


# Backward compatibility - expose static methods as module functions
flext_cli_require_confirmation = FlextCliDecorators.require_confirmation


__all__ = [
    "FlextCliDecorators",
    "flext_cli_require_confirmation",
]
