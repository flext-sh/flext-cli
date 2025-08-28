"""FLEXT CLI Container - Dependency injection following FLEXT patterns.

Simple dependency container implementing flext-core patterns without complex dependencies.
Follows FLEXT_REFACTORING_PROMPT.md container patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import logging
from typing import Any, TypeVar

from flext_cli.models_simple import FlextResult

T = TypeVar("T")


class FlextContainer:
    """Simple dependency container following FLEXT patterns."""

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}
        self._singletons: dict[str, Any] = {}
        self._logger = logging.getLogger(__name__)

    def register(self, service_name: str, service_factory: Any, singleton: bool = False) -> FlextResult[None]:
        """Register a service in the container - FLEXT pattern."""
        try:
            if singleton:
                self._singletons[service_name] = service_factory
            else:
                self._services[service_name] = service_factory
            return FlextResult.ok(None)
        except Exception as e:
            return FlextResult.fail(f"Failed to register service {service_name}: {e}")

    def resolve(self, service_name: str) -> FlextResult[Any]:
        """Resolve a service from the container - FLEXT pattern."""
        try:
            # Check singletons first
            if service_name in self._singletons:
                service = self._singletons[service_name]
                if callable(service):
                    # Create singleton instance if not already created
                    instance_key = f"_instance_{service_name}"
                    if instance_key not in self._singletons:
                        self._singletons[instance_key] = service()
                    return FlextResult.ok(self._singletons[instance_key])
                return FlextResult.ok(service)

            # Check regular services
            if service_name in self._services:
                service = self._services[service_name]
                if callable(service):
                    return FlextResult.ok(service())
                return FlextResult.ok(service)

            return FlextResult.fail(f"Service not found: {service_name}")

        except Exception as e:
            return FlextResult.fail(f"Failed to resolve service {service_name}: {e}")

    def has_service(self, service_name: str) -> bool:
        """Check if service is registered."""
        return service_name in self._services or service_name in self._singletons


# Global container instance - FLEXT pattern
_global_container: FlextContainer | None = None


def get_flext_container() -> FlextContainer:
    """Get global FLEXT container - following flext-core patterns."""
    global _global_container
    if _global_container is None:
        _global_container = FlextContainer()
        _register_default_services(_global_container)
    return _global_container


def _register_default_services(container: FlextContainer) -> None:
    """Register default CLI services."""
    # Logger service
    container.register("logger", lambda: logging.getLogger("flext_cli"), singleton=True)

    # CLI configuration (when available)
    try:
        from flext_cli.models_simple import FlextCliCommand, FlextCliSession
        container.register("command_factory", FlextCliCommand, singleton=False)
        container.register("session_factory", FlextCliSession, singleton=False)
    except ImportError:
        pass


# Service decorator following FLEXT patterns
def flext_service(service_name: str, singleton: bool = False):
    """Decorator to register services in container - FLEXT pattern."""
    def decorator(cls):
        container = get_flext_container()
        result = container.register(service_name, cls, singleton=singleton)
        if result.is_failure:
            logging.getLogger(__name__).error(f"Failed to register service: {result.error}")
        return cls
    return decorator


__all__ = [
    "FlextContainer",
    "flext_service",
    "get_flext_container",
]
