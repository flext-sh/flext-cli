"""CLI dependency injection container.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

This module provides a simple DI container specifically for CLI components,
implementing proper Clean Architecture patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, cast

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")


class _Container:
    """Simple DI container for CLI services."""

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}
        self._singletons: dict[str, Any] = {}

    def register(self, service_type: type[T], instance: T) -> None:
        """Register a service instance.

        Args:
            service_type: Service type/interface
            instance: Service instance

        """
        key = service_type.__name__
        self._services[key] = instance

    def register_singleton(self, service_type: type[T], factory: Callable[[], T]) -> None:
        """Register a singleton service.

        Args:
            service_type: Service type/interface
            factory: Factory function to create the service

        """
        key = service_type.__name__
        self._singletons[key] = factory

    def get(self, service_type: type[T]) -> T | None:
        """Get a service instance.

        Args:
            service_type: Service type to retrieve

        Returns:
            Service instance or None if not found

        """
        key = service_type.__name__

        # Check singletons first
        if key in self._singletons:
            if key not in self._services:
                # Create instance and store it
                instance = self._singletons[key]()
                self._services[key] = instance
            # Return the stored service with proper type casting
            return cast("T", self._services[key])

        service = self._services.get(key)
        if service is not None:
            # Type-cast to expected type
            return cast("T", service)
        return None


# Global container instance
_container = _Container()


def get_container() -> _Container:
    """Get the global DI container.

    Returns:
        Global container instance

    """
    return _container


def register_service(service_type: type[T], instance: T) -> None:
    """Register a service instance in the global container.

    Args:
        service_type: Service type/interface
        instance: Service instance

    """
    _container.register(service_type, instance)


def register_singleton(service_type: type[T], factory: Callable[[], T]) -> None:
    """Register a singleton service in the global container.

    Args:
        service_type: Service type/interface
        factory: Factory function to create the service

    """
    _container.register_singleton(service_type, factory)


def get_service[T](service_type: type[T]) -> T | None:
    """Get a service from the global container.

    Args:
        service_type: Service type to retrieve

    Returns:
        Service instance or None if not found

    """
    return _container.get(service_type)


__all__ = [
    "get_container",
    "get_service",
    "register_service",
    "register_singleton",
]
