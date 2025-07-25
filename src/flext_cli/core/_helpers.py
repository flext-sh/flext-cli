"""Internal helpers for FlextCli core modules.

Centralized utility functions to eliminate code duplication and massive boilerplate reduction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Any, TypeVar

from flext_core import FlextResult

T = TypeVar("T")


def flext_cli_success(data: Any = None) -> FlextResult[Any]:
    """Create success FlextResult."""
    return FlextResult(success=True, data=data, error=None)


def flext_cli_fail(error: str) -> FlextResult[Any]:
    """Create failure FlextResult."""
    return FlextResult(success=False, data=None, error=error)


# MASSIVE BOILERPLATE REDUCTION HELPERS
def flext_cli_unwrap_or_none[T](result: FlextResult[T]) -> T | None:
    """Unwrap FlextResult or return None if failed. Eliminates if/else boilerplate."""
    return result.data if result.success else None


def flext_cli_unwrap_or_default(result: FlextResult[T], default: T) -> T:
    """Unwrap FlextResult or return default if failed."""
    return result.data if result.success else default


def flext_cli_unwrap_or_raise[T](result: FlextResult[T], exception_class: type[Exception] = RuntimeError) -> T:
    """Unwrap FlextResult or raise exception if failed."""
    if result.success:
        return result.data
    raise exception_class(result.error or "Operation failed")


def flext_cli_execute_if_success[T](result: FlextResult[T], func: callable) -> None:
    """Execute function only if result is successful. Eliminates if boilerplate."""
    if result.success:
        func(result.data)


def flext_cli_silent_execute(func: callable, *args: Any, **kwargs: Any) -> Any:
    """Execute function silently, return None if any error occurs."""
    try:
        result = func(*args, **kwargs)
        return result.data if hasattr(result, "success") and result.success else result
    except Exception:
        return None
