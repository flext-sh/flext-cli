"""FLEXT CLI Container - Facade to flext-core centralized container.

This module provides backward compatibility by re-exporting the centralized
FlextContainer from flext-core, eliminating code duplication.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextLogger

# Import centralized container from flext-core
from flext_core.container import FlextContainer

# CLI-specific container instance
_cli_container_initialized = False


def get_flext_container() -> FlextContainer:
    """Get global FLEXT container with CLI-specific services registered."""
    global _cli_container_initialized

    # Create container instance
    container = FlextContainer()

    # Register CLI-specific services if not already done
    if not _cli_container_initialized:
        _register_cli_services(container)
        _cli_container_initialized = True

    return container


def _register_cli_services(container: FlextContainer) -> None:
    """Register CLI-specific services in the centralized container."""
    # Register logger service for CLI
    container.register("cli_logger", lambda: FlextLogger("flext_cli"))

    # Register CLI configuration factories (when available)
    try:
        from flext_cli.models_simple import FlextCliCommand, FlextCliSession

        container.register("command_factory", FlextCliCommand)
        container.register("session_factory", FlextCliSession)
    except ImportError:
        # Graceful degradation if models are not available
        pass


# Service decorator using centralized container
def flext_service(service_name: str, singleton: bool = False):
    """Decorator to register services in centralized container."""

    def decorator(cls):
        container = get_flext_container()
        result = container.register(service_name, cls)
        if result.is_failure:
            FlextLogger(__name__).error(f"Failed to register service: {result.error}")
        return cls

    return decorator


__all__ = [
    "FlextContainer",
    "flext_service",
    "get_flext_container",
]
