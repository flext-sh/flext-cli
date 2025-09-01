"""FLEXT CLI Decorators - Thin CLI wrappers over flext-core decorators.

Only provides small convenience decorators and compatibility shims used by CLI/tests.
Prefer using flext_core.FlextDecorators directly when possible.
"""

from __future__ import annotations

import asyncio
import functools
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, ParamSpec, TypeVar, cast

from flext_core import FlextDecorators, FlextResult
from rich.console import Console

P = ParamSpec("P")
T = TypeVar("T")


class FlextCliDecorators(FlextDecorators):
    """CLI-specific decorators extending flext-core FlextDecorators."""


__all__ = [
    "FlextCliDecorators",
    # CLI convenience decorators
    "async_command",
    "confirm_action",
    "require_auth",
    "measure_time",
    "retry",
    "validate_config",
    "with_spinner",
    # Compatibility wrappers used by tests
    "flext_cli_auto_validate",
    "flext_cli_handle_exceptions",
    "flext_cli_require_confirmation",
]


def async_command(func: Callable[P, T]) -> Callable[P, T]:
    """Wrap an async function to run synchronously using asyncio.run.

    If the target is already sync, returns it unchanged.
    """
    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        def _wrapper(*args: P.args, **kwargs: P.kwargs) -> T:  # type: ignore[override]
            return cast("T", asyncio.run(func(*args, **kwargs)))

        return _wrapper
    return func


def confirm_action(message: str) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
    """Ask for user confirmation before executing the function."""

    def _decorator(func: Callable[P, T]) -> Callable[P, T | None]:
        @functools.wraps(func)
        def _wrapped(*args: P.args, **kwargs: P.kwargs) -> T | None:
            console = Console()
            try:
                answer = console.input(f"{message} (y/N): ").strip().lower()
                if answer in ("y", "yes"):
                    return func(*args, **kwargs)
                return None
            except Exception:
                # Non-interactive environments: return None without raising
                return None

        return _wrapped

    return _decorator


def require_auth(
    token_file: str | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
    """Require a non-empty token file before executing the function."""

    def _decorator(func: Callable[P, T]) -> Callable[P, T | None]:
        @functools.wraps(func)
        def _wrapped(*args: P.args, **kwargs: P.kwargs) -> T | None:
            try:
                path = (
                    Path(token_file)
                    if token_file
                    else Path.home() / ".flext" / "auth" / "token.json"
                )
                if not path.exists():
                    return None
                content = path.read_text(encoding="utf-8").strip()
                if not content:
                    return None
                return func(*args, **kwargs)
            except Exception:
                return None

        return _wrapped

    return _decorator


def measure_time(
    *, show_in_output: bool = False
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Measure execution time and optionally print it with dim style."""

    def _decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def _wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = time.time() - start
                if show_in_output:
                    Console().print(f"⏱  Execution time: {elapsed:.2f}s", style="dim")

        return _wrapped

    return _decorator


def retry(
    *, max_attempts: int = 3, delay: float = 0.0
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Retry decorator with constant delay (simple wrapper)."""

    def _decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def _wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exc: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:  # noqa: BLE001
                    last_exc = e
                    if attempt < max_attempts - 1 and delay > 0:
                        time.sleep(delay)
            assert last_exc is not None
            raise last_exc

        return _wrapped

    return _decorator


def validate_config(
    required_keys: list[str],
) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
    """Validate required config keys passed to the function.

    Tries kwargs (config|cfg|settings|mock_config) or first arg as config source.
    Prints a message and returns None if not available or missing keys.
    """

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

            def _get(c: Any, k: str) -> Any:
                if isinstance(c, dict):
                    return c.get(k)
                return getattr(c, k, None)

            for key in required_keys:
                if _get(candidate, key) is None:
                    console.print(f"Missing required configuration: {key}", style="red")
                    return None

            return func(*args, **kwargs)

        return _wrapped

    return _decorator


def with_spinner(
    message: str = "Processing...",
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Show a spinner while executing the function."""

    def _decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def _wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
            console = Console()
            with console.status(message, spinner="dots"):
                return func(*args, **kwargs)

        return _wrapped

    return _decorator


def flext_cli_auto_validate(
    _validators: list[str],
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Compatibility no-op validator decorator (preserves metadata)."""

    def _decorator(func: Callable[P, T]) -> Callable[P, T]:
        return functools.wraps(func)(func)

    return _decorator


def flext_cli_handle_exceptions(
    message: str,
) -> Callable[[Callable[P, T]], Callable[P, FlextResult[T]]]:
    """Wrap exceptions into FlextResult failures; pass-through successes."""

    def _decorator(func: Callable[P, T]) -> Callable[P, FlextResult[T]]:
        @functools.wraps(func)
        def _wrapped(*args: P.args, **kwargs: P.kwargs) -> FlextResult[T]:
            try:
                result = func(*args, **kwargs)
                if isinstance(result, FlextResult):
                    return result
                return FlextResult[T].ok(cast("T", result))
            except Exception as e:  # noqa: BLE001
                return FlextResult[T].fail(f"{message}: {e}")

        return _wrapped

    return _decorator


def flext_cli_require_confirmation(
    _action: str,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Compatibility no-op confirmation decorator (non-interactive)."""

    def _decorator(func: Callable[P, T]) -> Callable[P, T]:
        return functools.wraps(func)(func)

    return _decorator
