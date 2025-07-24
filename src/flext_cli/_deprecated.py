"""Deprecation warnings and migration helpers for FLEXT CLI refactoring.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This module provides deprecation warnings and migration paths for the CLI refactoring.
All old patterns are maintained for backward compatibility with warnings.
"""

from __future__ import annotations

import warnings
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


class FlextCLIDeprecationWarning(UserWarning):
    """Custom deprecation warning for FLEXT CLI."""


def deprecated(
    *,
    reason: str,
    new_path: str | None = None,
    version: str = "0.8.0",
    category: type[Warning] = FlextCLIDeprecationWarning,
) -> Callable[[F], F]:
    """Mark function or class as deprecated with migration guidance.

    Args:
        reason: Reason for deprecation
        new_path: New import path or class to use
        version: Version when deprecated
        category: Warning category

    Returns:
        Decorated function with deprecation warning

    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            message = f"{func.__module__}.{func.__qualname__} is deprecated: {reason}"
            if new_path:
                message += f" Use {new_path} instead."
            message += f" Will be removed in v{version}."

            warnings.warn(
                message,
                category=category,
                stacklevel=2,
            )
            return func(*args, **kwargs)
        # Cast is necessary because functools.wraps changes the type signature
        return cast("F", wrapper)
    return decorator


def deprecated_module(
    *,
    reason: str,
    new_module: str | None = None,
    version: str = "0.8.0",
) -> None:
    """Mark entire module as deprecated.

    Args:
        reason: Reason for deprecation
        new_module: New module to use
        version: Version when deprecated

    """
    import inspect

    frame = inspect.currentframe()
    if frame and frame.f_back:
        module_name = frame.f_back.f_globals.get("__name__", "unknown")
        message = f"Module {module_name} is deprecated: {reason}"
        if new_module:
            message += f" Use {new_module} instead."
        message += f" Will be removed in v{version}."

        warnings.warn(
            message,
            category=FlextCLIDeprecationWarning,
            stacklevel=2,
        )


def deprecated_import(
    old_name: str,
    new_path: str,
    version: str = "0.8.0",
) -> None:
    """Issue deprecation warning for imports.

    Args:
        old_name: Old import name
        new_path: New import path
        version: Version when deprecated

    """
    message = (
        f"Importing {old_name} is deprecated. "
        f"Use {new_path} instead. Will be removed in v{version}."
    )
    warnings.warn(
        message,
        category=FlextCLIDeprecationWarning,
        stacklevel=3,  # Skip this function and the import
    )


# Migration helpers
def get_new_class_path(old_class: type) -> str:
    """Get new class path for deprecated classes.

    Args:
        old_class: Deprecated class

    Returns:
        New class path

    """
    mapping = {
        # Domain mappings
        "flext_cli.domain.entities.CLICommand": "flext_cli.domain.entities.command.Command",
        "flext_cli.domain.entities.CLIConfig": "flext_cli.domain.entities.config.Configuration",
        "flext_cli.domain.entities.CLISession": "flext_cli.domain.entities.session.Session",
        "flext_cli.domain.entities.CLIPlugin": "flext_cli.domain.entities.plugin.Plugin",

        # Application mappings
        "flext_cli.application.commands": "flext_cli.application.use_cases",
        "flext_cli.domain.cli_services": "flext_cli.application.services",

        # Infrastructure mappings
        "flext_cli.infrastructure.container": "flext_cli.infrastructure.dependency_injection",
    }

    old_path = f"{old_class.__module__}.{old_class.__qualname__}"
    return mapping.get(old_path, "flext_cli.adapters.legacy")


def migration_notice() -> None:
    """Display migration notice for CLI refactoring."""


# Module-level deprecation warnings
DEPRECATED_MODULES = {
    "flext_cli.simple_api": "Use flext_cli.application.services for application logic",
}


def check_deprecated_module(module_name: str) -> None:
    """Check if module is deprecated and issue warning.

    Args:
        module_name: Name of the module being imported

    """
    if module_name in DEPRECATED_MODULES:
        deprecated_import(
            module_name,
            DEPRECATED_MODULES[module_name],
        )
