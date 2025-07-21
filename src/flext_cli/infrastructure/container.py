"""Simple dependency injection container for FLEXT CLI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This module provides a basic dependency container without external dependencies.
"""

from __future__ import annotations

import os
from typing import Any, cast

from flext_core.infrastructure.memory import InMemoryRepository


class SimpleDIContainer:
    """Simple dependency injection container."""

    def __init__(self) -> None:
        """Initialize the dependency injection container."""
        self._instances: dict[str, Any] = {}
        self._factories: dict[str, Any] = {}

    def register_factory(self, name: str, factory: Any) -> None:
        """Register a factory function for a dependency.

        Args:
            name: The name of the dependency.
            factory: The factory function to register.

        """
        self._factories[name] = factory

    def register_instance(self, name: str, instance: Any) -> None:
        """Register a concrete instance.

        Args:
            name: The name of the dependency.
            instance: The instance to register.

        """
        self._instances[name] = instance

    def get(self, name: str) -> Any:
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
            instance = self._factories[name]()
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
        def create_config() -> dict[str, Any]:
            """Creates an instance of CLI config with environment defaults.

            This method creates the CLI config with environment defaults.
            It is used to create the CLI config with environment defaults.

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

    def get_config(self) -> dict[str, Any]:
        """Gets an instance of CLI configuration.

        This method gets the CLI configuration from the container.
        It is used to get the CLI configuration from the container.

        Returns:
            The CLI configuration.

        """
        config = self._container.get("config")
        return cast("dict[str, Any]", config)

    def get_command_repository(self) -> InMemoryRepository[Any, Any]:
        """Gets command repository (mock for now).

        This method gets the command repository from the container.
        It is used to get the command repository from the container.

        """
        return InMemoryRepository[Any, Any]()

    def get_config_repository(self) -> InMemoryRepository[Any, Any]:
        """Gets config repository (mock for now).

        This method gets the config repository from the container.
        It is used to get the config repository from the container.

        """
        return InMemoryRepository[Any, Any]()

    def get_session_repository(self) -> InMemoryRepository[Any, Any]:
        """Gets session repository (mock for now).

        This method gets the session repository from the container.
        It is used to get the session repository from the container.

        """
        return InMemoryRepository[Any, Any]()

    def get_plugin_repository(self) -> InMemoryRepository[Any, Any]:
        """Gets plugin repository (mock for now).

        This method gets the plugin repository from the container.
        It is used to get the plugin repository from the container.

        """
        return InMemoryRepository[Any, Any]()


# Global container instance
_container: CLIContainer | None = None


def get_container() -> CLIContainer:
    """Gets the global CLI container.

    This method gets the global CLI container from the container.
    It is used to get the global CLI container from the container.

    """
    global _container
    if _container is None:
        _container = CLIContainer()
    return _container


def create_cli_container() -> CLIContainer:
    """Creates a new CLI container instance.

    This method creates a new CLI container instance.
    It is used to create a new CLI container instance.

    """
    return CLIContainer()
