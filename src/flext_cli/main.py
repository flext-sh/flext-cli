"""FLEXT CLI - Command Registration System.

This module provides the central command registration and management system
for the FLEXT CLI ecosystem. It handles command discovery, registration,
grouping, and lifecycle management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Callable
from typing import Any

from click import Group

from flext_cli.cli import FlextCliClick
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
)


class FlextCliMain(FlextService[None]):
    """Command registration and management system.

    Central hub for CLI command registration, discovery, and execution.
    Provides unified interface for:

    - Command registration and discovery
    - Command group management
    - Plugin command loading
    - Command metadata and documentation
    - Command lifecycle management

    Examples:
        >>> main = FlextCliMain(name="myapp", version="1.0.0")
        >>>
        >>> # Register a command
        >>> @main.command()
        >>> def hello(name: str):
        ...     print(f"Hello {name}!")
        >>>
        >>> # Register a command group
        >>> @main.group()
        >>> def config():
        ...     '''Configuration commands.'''
        ...     pass
        >>>
        >>> # Register subcommand
        >>> @config.command()
        >>> def show():
        ...     '''Show configuration.'''
        ...     pass
        >>>
        >>> # Execute CLI
        >>> result = main.execute_cli()

    Note:
        This class uses FlextCliClick internally but provides a higher-level
        API for command management. All Click functionality is abstracted.

    """

    def __init__(
        self,
        name: str = "flext",
        version: str = "0.9.0",
        description: str | None = None,
        **kwargs: str | int | bool | None,
    ) -> None:
        """Initialize command registration system.

        Args:
            name: CLI application name
            version: Application version
            description: CLI description
            **kwargs: Additional Click group options

        """
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()
        self._click = FlextCliClick()

        # CLI metadata
        self._name = name
        self._version = version
        self._description = description or f"{name} CLI"

        # Command registry
        self._commands: dict[str, Any] = {}
        self._groups: dict[str, Any] = {}
        self._plugin_commands: dict[str, Any] = {}

        # Main CLI group
        self._main_group = self._create_main_group(**kwargs)

        self._logger.debug(
            "Initialized CLI main",
            extra={
                "cli_name": self._name,
                "version": self._version,
            },
        )

    # =========================================================================
    # MAIN GROUP CREATION
    # =========================================================================

    def _create_main_group(self, **kwargs: str | int | bool | None) -> Group:
        """Create main CLI group using Click abstraction.

        Args:
            **kwargs: Additional Click group options

        Returns:
            Click group object (internal use only)

        """
        group_result = self._click.create_group_decorator(
            name=self._name,
            help=self._description,
            **kwargs,
        )

        if group_result.is_failure:
            self._logger.error(
                f"Failed to create main group: {group_result.error}",
            )
            return None

        group_decorator = group_result.unwrap()

        # Create empty group function
        def main_cli() -> None:
            """Main CLI entry point."""

        # Apply decorator
        return group_decorator(main_cli)

    # =========================================================================
    # COMMAND REGISTRATION
    # =========================================================================

    def command(
        self,
        name: str | None = None,
        **kwargs: str | int | bool | None,
    ) -> Callable[
        [Callable[..., str | int | bool | None]], Callable[..., str | int | bool | None]
    ]:
        """Register a command decorator.

        Args:
            name: Command name (optional, uses function name if None)
            **kwargs: Click command options

        Returns:
            Command decorator function

        Example:
            >>> main = FlextCliMain()
            >>> @main.command()
            >>> def hello(name: str):
            ...     print(f"Hello {name}!")

        """

        def decorator(
            func: Callable[..., str | int | bool | None],
        ) -> Callable[..., str | int | bool | None]:
            """Command decorator."""
            # Create command using Click abstraction
            cmd_result = self._click.create_command_decorator(
                name=name,
                **kwargs,
            )

            if cmd_result.is_failure:
                self._logger.error(
                    f"Failed to create command: {cmd_result.error}",
                )
                return func

            cmd_decorator = cmd_result.unwrap()
            command_obj = cmd_decorator(func)

            # Register command
            cmd_name = name or func.__name__
            self._commands[cmd_name] = command_obj

            # Add to main group
            if self._main_group is not None:
                self._main_group.add_command(command_obj)

            self._logger.debug(
                "Registered command",
                extra={
                    "command_name": cmd_name,
                },
            )

            return command_obj

        return decorator

    def register_command(
        self,
        func: Callable[..., str | int | bool | None],
        name: str | None = None,
        **kwargs: str | int | bool | None,
    ) -> FlextResult[None]:
        """Register a command programmatically.

        Args:
            func: Command function
            name: Command name (optional)
            **kwargs: Click command options

        Returns:
            FlextResult[None]

        Example:
            >>> def my_command(arg: str):
            ...     print(arg)
            >>> result = main.register_command(my_command, name="mycmd")

        """
        try:
            # Create command
            cmd_result = self._click.create_command_decorator(
                name=name,
                **kwargs,
            )

            if cmd_result.is_failure:
                return FlextResult[None].fail(
                    f"Failed to create command: {cmd_result.error}",
                )

            cmd_decorator = cmd_result.unwrap()
            command_obj = cmd_decorator(func)

            # Register
            cmd_name = name or func.__name__
            self._commands[cmd_name] = command_obj

            # Add to main group
            if self._main_group is not None:
                self._main_group.add_command(command_obj)

            self._logger.debug(
                "Registered command",
                extra={
                    "command_name": cmd_name,
                },
            )

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to register command: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    # =========================================================================
    # GROUP REGISTRATION
    # =========================================================================

    def group(
        self,
        name: str | None = None,
        **kwargs: str | int | bool | None,
    ) -> Callable[
        [Callable[..., str | int | bool | None]], Callable[..., str | int | bool | None]
    ]:
        """Register a command group decorator.

        Args:
            name: Group name (optional)
            **kwargs: Click group options

        Returns:
            Group decorator function

        Example:
            >>> main = FlextCliMain()
            >>> @main.group()
            >>> def config():
            ...     '''Configuration commands.'''
            ...     pass
            >>>
            >>> @config.command()
            >>> def show():
            ...     '''Show configuration.'''
            ...     print("Config...")

        """

        def decorator(
            func: Callable[..., str | int | bool | None],
        ) -> Callable[..., str | int | bool | None]:
            """Group decorator."""
            # Create group using Click abstraction
            grp_result = self._click.create_group_decorator(
                name=name,
                **kwargs,
            )

            if grp_result.is_failure:
                self._logger.error(
                    f"Failed to create group: {grp_result.error}",
                )
                return func

            grp_decorator = grp_result.unwrap()
            group_obj = grp_decorator(func)

            # Register group
            grp_name = name or func.__name__
            self._groups[grp_name] = group_obj

            # Add to main group
            if self._main_group is not None:
                self._main_group.add_command(group_obj)

            self._logger.debug(
                "Registered group",
                extra={
                    "group_name": grp_name,
                },
            )

            return group_obj

        return decorator

    def register_group(
        self,
        func: Callable[..., str | int | bool | None],
        name: str | None = None,
        **kwargs: str | int | bool | None,
    ) -> FlextResult[None]:
        """Register a command group programmatically.

        Args:
            func: Group function
            name: Group name (optional)
            **kwargs: Click group options

        Returns:
            FlextResult[None]

        Example:
            >>> def my_group():
            ...     '''My commands.'''
            ...     pass
            >>> result = main.register_group(my_group, name="mygroup")

        """
        try:
            # Create group
            grp_result = self._click.create_group_decorator(
                name=name,
                **kwargs,
            )

            if grp_result.is_failure:
                return FlextResult[None].fail(
                    f"Failed to create group: {grp_result.error}",
                )

            grp_decorator = grp_result.unwrap()
            group_obj = grp_decorator(func)

            # Register
            grp_name = name or func.__name__
            self._groups[grp_name] = group_obj

            # Add to main group
            if self._main_group is not None:
                self._main_group.add_command(group_obj)

            self._logger.debug(
                "Registered group",
                extra={
                    "group_name": grp_name,
                },
            )

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to register group: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    # =========================================================================
    # PLUGIN COMMAND LOADING
    # =========================================================================

    def register_plugin_command(
        self,
        command_name: str,
        command_obj: Callable[..., str | int | bool | None],
    ) -> FlextResult[None]:
        """Register a plugin command.

        Args:
            command_name: Plugin command name
            command_obj: Click command object

        Returns:
            FlextResult[None]

        Example:
            >>> result = main.register_plugin_command("custom", custom_cmd)

        """
        try:
            if command_name in self._plugin_commands:
                return FlextResult[None].fail(
                    f"Plugin command '{command_name}' already registered",
                )

            # Register plugin command
            self._plugin_commands[command_name] = command_obj

            # Add to main group
            if self._main_group is not None:
                self._main_group.add_command(command_obj)

            self._logger.debug(
                "Registered plugin command",
                extra={
                    "command_name": command_name,
                },
            )

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to register plugin command: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    def load_plugin_commands(
        self,
        plugin_package: str,
    ) -> FlextResult[list[str]]:
        """Load commands from a plugin package.

        Args:
            plugin_package: Python package path (e.g., "myapp.plugins")

        Returns:
            FlextResult containing list of loaded command names

        Example:
            >>> result = main.load_plugin_commands("myapp.plugins")
            >>> if result.is_success:
            ...     loaded = result.unwrap()
            ...     print(f"Loaded: {loaded}")

        """
        try:
            loaded_commands: list[str] = []

            # Import plugin package
            try:
                package = importlib.import_module(plugin_package)
            except ImportError as e:
                return FlextResult[list[str]].fail(
                    f"Failed to import plugin package: {e}",
                )

            # Discover plugin modules
            if not hasattr(package, "__path__"):
                return FlextResult[list[str]].fail(
                    f"'{plugin_package}' is not a package",
                )

            for _, module_name, _ in pkgutil.iter_modules(package.__path__):
                full_module = f"{plugin_package}.{module_name}"

                try:
                    module = importlib.import_module(full_module)

                    # Look for commands in module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)

                        # Check if it's a Click command
                        if callable(attr) and hasattr(attr, "__click_params__"):
                            register_result = self.register_plugin_command(
                                attr_name,
                                attr,
                            )

                            if register_result.is_success:
                                loaded_commands.append(attr_name)

                except Exception as e:
                    self._logger.warning(
                        f"Failed to load plugin module '{full_module}': {e}",
                    )
                    continue

            self._logger.info(
                "Loaded plugin commands",
                extra={
                    "plugin_package": plugin_package,
                    "command_count": len(loaded_commands),
                },
            )

            return FlextResult[list[str]].ok(loaded_commands)

        except Exception as e:
            error_msg = f"Failed to load plugin commands: {e}"
            self._logger.exception(error_msg)
            return FlextResult[list[str]].fail(error_msg)

    # =========================================================================
    # COMMAND METADATA
    # =========================================================================

    def list_commands(self) -> FlextResult[list[str]]:
        """List all registered commands.

        Returns:
            FlextResult containing list of command names

        Example:
            >>> result = main.list_commands()
            >>> if result.is_success:
            ...     commands = result.unwrap()
            ...     print(f"Commands: {commands}")

        """
        try:
            all_commands = list(self._commands.keys())
            return FlextResult[list[str]].ok(all_commands)

        except Exception as e:
            error_msg = f"Failed to list commands: {e}"
            self._logger.exception(error_msg)
            return FlextResult[list[str]].fail(error_msg)

    def list_groups(self) -> FlextResult[list[str]]:
        """List all registered command groups.

        Returns:
            FlextResult containing list of group names

        Example:
            >>> result = main.list_groups()
            >>> if result.is_success:
            ...     groups = result.unwrap()
            ...     print(f"Groups: {groups}")

        """
        try:
            all_groups = list(self._groups.keys())
            return FlextResult[list[str]].ok(all_groups)

        except Exception as e:
            error_msg = f"Failed to list groups: {e}"
            self._logger.exception(error_msg)
            return FlextResult[list[str]].fail(error_msg)

    def get_command(self, name: str) -> FlextResult[Any]:
        """Get a registered command by name.

        Args:
            name: Command name

        Returns:
            FlextResult containing command object

        Example:
            >>> result = main.get_command("hello")
            >>> if result.is_success:
            ...     cmd = result.unwrap()

        """
        if name not in self._commands:
            return FlextResult[Any].fail(f"Command '{name}' not found")

        return FlextResult[Any].ok(self._commands[name])

    def get_group(self, name: str) -> FlextResult[Any]:
        """Get a registered group by name.

        Args:
            name: Group name

        Returns:
            FlextResult containing group object

        Example:
            >>> result = main.get_group("config")
            >>> if result.is_success:
            ...     grp = result.unwrap()

        """
        if name not in self._groups:
            return FlextResult[Any].fail(f"Group '{name}' not found")

        return FlextResult[Any].ok(self._groups[name])

    # =========================================================================
    # CLI EXECUTION
    # =========================================================================

    def execute_cli(
        self,
        args: list[str] | None = None,
        *,
        standalone_mode: bool = True,
    ) -> FlextResult[Any]:
        """Execute the CLI with given arguments.

        Args:
            args: CLI arguments (None = sys.argv)
            standalone_mode: Exit on error if True

        Returns:
            FlextResult containing execution result

        Example:
            >>> main = FlextCliMain()
            >>> result = main.execute_cli(["--help"])

        """
        try:
            if self._main_group is None:
                return FlextResult[Any].fail("Main group not initialized")

            # Execute main group
            result = self._main_group(
                args=args,
                standalone_mode=standalone_mode,
            )

            return FlextResult[Any].ok(result)

        except Exception as e:
            error_msg = f"CLI execution failed: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Any].fail(error_msg)

    def get_main_group(self) -> FlextResult[Any]:
        """Get the main CLI group object.

        Returns:
            FlextResult containing main group

        Example:
            >>> result = main.get_main_group()
            >>> if result.is_success:
            ...     group = result.unwrap()

        """
        if self._main_group is None:
            return FlextResult[Any].fail("Main group not initialized")

        return FlextResult[Any].ok(self._main_group)

    # =========================================================================
    # FLEXT SERVICE METHODS
    # =========================================================================

    def execute(self) -> FlextResult[None]:
        """Execute CLI main operations.

        Returns:
            FlextResult[None]

        """
        return FlextResult[None].ok(None)


__all__ = [
    "FlextCliMain",
]
