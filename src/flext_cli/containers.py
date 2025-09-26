"""FLEXT CLI Containers - Single unified class following FLEXT standards.

Provides CLI-specific container implementations using flext-core patterns.
Single FlextCliContainers class with nested container subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_core import FlextContainer, FlextResult


class FlextCliContainers:
    """Single unified CLI containers class following FLEXT standards.

    Contains all container implementations for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.

    ARCHITECTURAL COMPLIANCE:
    - Uses composition with FlextContainer to avoid inheritance issues
    - Uses centralized container patterns from FlextContainer
    - Implements CLI-specific extensions while reusing core functionality
    """

    @override
    def __init__(self) -> None:
        """Initialize CLI containers with FlextContainer composition."""
        self._container = FlextContainer.get_global()

    class CommandContainer:
        """CLI command container for managing command instances."""

        @override
        def __init__(self) -> None:
            """Initialize command container."""
            self._commands: dict[str, object] = {}

        def register(self, name: str, command: object) -> FlextResult[None]:
            """Register a command in the container.

            Args:
                name: Command name
                command: Command instance

            Returns:
                FlextResult[None]: Success or error

            """
            try:
                if name in self._commands:
                    return FlextResult[None].fail(
                        f"Command '{name}' already registered"
                    )
                self._commands[name] = command
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Command registration failed: {e}")

        def get(self, name: str) -> FlextResult[object]:
            """Get a command from the container.

            Args:
                name: Command name

            Returns:
                FlextResult[object]: Command instance or error

            """
            try:
                if name not in self._commands:
                    return FlextResult[object].fail(f"Command '{name}' not found")
                return FlextResult[object].ok(self._commands[name])
            except Exception as e:
                return FlextResult[object].fail(f"Command retrieval failed: {e}")

        def list_commands(self) -> FlextResult[list[str]]:
            """List all registered command names.

            Returns:
                FlextResult[list[str]]: List of command names or error

            """
            try:
                return FlextResult[list[str]].ok(list(self._commands.keys()))
            except Exception as e:
                return FlextResult[list[str]].fail(f"Command listing failed: {e}")

        def unregister(self, name: str) -> FlextResult[None]:
            """Unregister a command from the container.

            Args:
                name: Command name

            Returns:
                FlextResult[None]: Success or error

            """
            try:
                if name not in self._commands:
                    return FlextResult[None].fail(f"Command '{name}' not found")
                del self._commands[name]
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Command unregistration failed: {e}")

    class HandlerContainer:
        """CLI handler container for managing handler instances."""

        @override
        def __init__(self) -> None:
            """Initialize handler container."""
            self._handlers: dict[str, object] = {}

        def register(self, name: str, handler: object) -> FlextResult[None]:
            """Register a handler in the container.

            Args:
                name: Handler name
                handler: Handler instance

            Returns:
                FlextResult[None]: Success or error

            """
            try:
                if name in self._handlers:
                    return FlextResult[None].fail(
                        f"Handler '{name}' already registered"
                    )
                self._handlers[name] = handler
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Handler registration failed: {e}")

        def get(self, name: str) -> FlextResult[object]:
            """Get a handler from the container.

            Args:
                name: Handler name

            Returns:
                FlextResult[object]: Handler instance or error

            """
            try:
                if name not in self._handlers:
                    return FlextResult[object].fail(f"Handler '{name}' not found")
                return FlextResult[object].ok(self._handlers[name])
            except Exception as e:
                return FlextResult[object].fail(f"Handler retrieval failed: {e}")

        def list_handlers(self) -> FlextResult[list[str]]:
            """List all registered handler names.

            Returns:
                FlextResult[list[str]]: List of handler names or error

            """
            try:
                return FlextResult[list[str]].ok(list(self._handlers.keys()))
            except Exception as e:
                return FlextResult[list[str]].fail(f"Handler listing failed: {e}")

    class ConfigContainer:
        """CLI configuration container for managing configuration instances."""

        @override
        def __init__(self) -> None:
            """Initialize configuration container."""
            self._configs: dict[str, object] = {}

        def register(self, name: str, config: object) -> FlextResult[None]:
            """Register a configuration in the container.

            Args:
                name: Configuration name
                config: Configuration instance

            Returns:
                FlextResult[None]: Success or error

            """
            try:
                if name in self._configs:
                    return FlextResult[None].fail(f"Config '{name}' already registered")
                self._configs[name] = config
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Config registration failed: {e}")

        def get(self, name: str) -> FlextResult[object]:
            """Get a configuration from the container.

            Args:
                name: Configuration name

            Returns:
                FlextResult[object]: Configuration instance or error

            """
            try:
                if name not in self._configs:
                    return FlextResult[object].fail(f"Config '{name}' not found")
                return FlextResult[object].ok(self._configs[name])
            except Exception as e:
                return FlextResult[object].fail(f"Config retrieval failed: {e}")

        def list_configs(self) -> FlextResult[list[str]]:
            """List all registered configuration names.

            Returns:
                FlextResult[list[str]]: List of configuration names or error

            """
            try:
                return FlextResult[list[str]].ok(list(self._configs.keys()))
            except Exception as e:
                return FlextResult[list[str]].fail(f"Config listing failed: {e}")


__all__ = [
    "FlextCliContainers",
]
