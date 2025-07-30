"""Simple dependency injection container for FLEXT CLI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This module provides a basic dependency container without external dependencies.
"""

from __future__ import annotations

import os
from typing import cast

from flext_core import FlextRepository
from flext_core.result import FlextResult


class SimpleDIContainer:
    """Simple dependency injection container."""

    def __init__(self) -> None:
        """Initialize the dependency injection container."""
        self._instances: dict[str, object] = {}
        self._factories: dict[str, object] = {}

    def register_factory(self, name: str, factory: object) -> None:
        """Register a factory function for a dependency.

        Args:
            name: The name of the dependency.
            factory: The factory function to register.

        """
        self._factories[name] = factory

    def register_instance(self, name: str, instance: object) -> None:
        """Register a concrete instance.

        Args:
            name: The name of the dependency.
            instance: The instance to register.

        """
        self._instances[name] = instance

    def get(self, name: str) -> object:
        """Get dependency by name.

        Args:
            name: The name of the dependency.

        Returns:
            The dependency.

        Raises:
            KeyError: If the dependency is not found.

        """
        if name in self._instances:
            return self._instances[name]

        if name in self._factories:
            factory = self._factories[name]
            instance = factory() if callable(factory) else factory
            self._instances[name] = instance
            return instance

        msg = f"Dependency '{name}' not found"
        raise KeyError(msg)


class CLIContainer:
    """CLI dependency container.

    Provides access to CLI dependencies using simple factory pattern.
    """

    def __init__(self) -> None:
        """Initialize the CLI container."""
        self._container = SimpleDIContainer()
        self._setup_dependencies()

    def _setup_dependencies(self) -> None:
        """Setups all CLI dependencies.

        This method sets up the dependencies for the CLI container.
        It is used to create the dependencies for the CLI container.

        """
        # For now, we'll use simple factories that create mock instances
        # This avoids the complex dependency injection issues

        # Configuration
        def create_config() -> dict[str, object]:
            """Create CLI config instance with environment defaults.

            Returns:
                An instance of CLI config.

            """
            return {
                "api_url": os.getenv("FLX_API_URL", "http://localhost:8000"),
                "api_token": os.getenv("FLX_API_TOKEN", ""),
                "debug": os.getenv("FLX_DEBUG", "false").lower() == "true",
                "output_format": os.getenv("FLX_OUTPUT_FORMAT", "table"),
            }

        self._container.register_factory("config", create_config)

    def get_config(self) -> dict[str, object]:
        """Get CLI configuration instance.

        Returns:
            The CLI configuration.

        """
        config = self._container.get("config")
        return cast("dict[str, object]", config)

    def get_command_repository(self) -> FlextRepository:
        """Get command repository (mock for now).

        Returns:
            Command repository instance.

        """

        # Placeholder implementation - concrete repository needed
        class MockRepository(FlextRepository):
            def save(self, _entity: object) -> FlextResult[None]:
                return FlextResult.ok(None)

            def find_by_id(self, entity_id: str) -> FlextResult[object]:
                return FlextResult.fail(f"Entity {entity_id} not found")

            def delete(self, _entity_id: str) -> FlextResult[None]:
                return FlextResult.ok(None)

        return MockRepository()

    def get_config_repository(self) -> FlextRepository:
        """Get config repository (mock for now).

        Returns:
            Config repository instance.

        """

        # Placeholder implementation - concrete repository needed
        class MockRepository(FlextRepository):
            def save(self, _entity: object) -> FlextResult[None]:
                return FlextResult.ok(None)

            def find_by_id(self, entity_id: str) -> FlextResult[object]:
                return FlextResult.fail(f"Entity {entity_id} not found")

            def delete(self, _entity_id: str) -> FlextResult[None]:
                return FlextResult.ok(None)

        return MockRepository()

    def get_session_repository(self) -> FlextRepository:
        """Get session repository (mock for now).

        Returns:
            Session repository instance.

        """

        # Placeholder implementation - concrete repository needed
        class MockRepository(FlextRepository):
            def save(self, _entity: object) -> FlextResult[None]:
                return FlextResult.ok(None)

            def find_by_id(self, entity_id: str) -> FlextResult[object]:
                return FlextResult.fail(f"Entity {entity_id} not found")

            def delete(self, _entity_id: str) -> FlextResult[None]:
                return FlextResult.ok(None)

        return MockRepository()

    def get_plugin_repository(self) -> FlextRepository:
        """Get plugin repository (mock for now).

        Returns:
            Plugin repository instance.

        """

        # Placeholder implementation - concrete repository needed
        class MockRepository(FlextRepository):
            def save(self, _entity: object) -> FlextResult[None]:
                return FlextResult.ok(None)

            def find_by_id(self, entity_id: str) -> FlextResult[object]:
                return FlextResult.fail(f"Entity {entity_id} not found")

            def delete(self, _entity_id: str) -> FlextResult[None]:
                return FlextResult.ok(None)

        return MockRepository()


# Global container instance - using singleton pattern
_container: CLIContainer | None = None


def get_container() -> CLIContainer:
    """Get the global CLI container.

    Returns:
        Global CLI container instance.

    """
    global _container  # noqa: PLW0603
    if _container is None:
        _container = CLIContainer()
    return _container


def create_cli_container() -> CLIContainer:
    """Create new CLI container instance.

    Returns:
        New CLI container instance.

    """
    return CLIContainer()
