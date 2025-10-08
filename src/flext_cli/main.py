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

import click
import typer
from flext_core import FlextCore, FlextResult

from flext_cli.cli import FlextCliCli
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels


class FlextCliMain(FlextCore.Service[object]):
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
        This class uses FlextCliCli internally but provides a higher-level
        API for command management. All Click functionality is abstracted.

    """

    def __init__(
        self,
        name: str = "flext",
        version: str = "0.9.0",
        description: str | None = None,
        **kwargs: str | int | bool | None,
    ) -> None:
        """Initialize command registration system with Typer backend.

        Args:
            name: CLI application name
            version: Application version
            description: CLI description
            **kwargs: Additional Typer app options

        """
        super().__init__()
        # Initialize logger (inherited from FlextCore.Service)
        # Logger is automatically provided by FlextMixins.Logging mixin
        self._click = FlextCliCli()

        # CLI metadata
        self._name = name
        self._version = version
        self._description = description or f"{name} CLI"

        # Command registry
        self._commands: FlextCore.Types.Dict = {}
        self._groups: FlextCore.Types.Dict = {}
        self._plugin_commands: FlextCore.Types.Dict = {}

        # Main Typer app (replaces Click group)
        self._app = self._create_typer_app(**kwargs)

        # Get and store the Typer app's Click group (only created once)
        self._main_group = typer.main.get_group(self._app)

        self.logger.debug(
            "Initialized CLI main with Typer backend",
            extra={
                "cli_name": self._name,
                "version": self._version,
            },
        )

    # =========================================================================
    # TYPER APP CREATION
    # =========================================================================

    def _create_typer_app(self, **kwargs: str | int | bool | None) -> typer.Typer:
        """Create main Typer app.

        Args:
            **kwargs: Additional Typer app options

        Returns:
            Typer app instance

        """
        app = typer.Typer(
            name=self._name,
            help=self._description,
            add_completion=bool(kwargs.get("add_completion", True)),
            pretty_exceptions_enable=bool(kwargs.get("pretty_exceptions_enable", True)),
        )

        self.logger.debug(
            "Created Typer app",
            extra={
                "app_name": self._name,
            },
        )

        return app

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
        """Register a command decorator (maintains Click ABI via Typer container).

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
            # Use Click decorator to maintain ABI compatibility
            cmd_decorator = self._click.create_command_decorator(
                name=name,
                **kwargs,
            )
            command_obj = cmd_decorator(func)

            # Register command
            cmd_name = name or func.__name__
            self._commands[cmd_name] = command_obj

            # Add to main group (Typer's Click group)
            if self._main_group is not None:
                self._main_group.add_command(command_obj)

            self.logger.debug(
                "Registered command (Click ABI, Typer container)",
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
        """Register a command programmatically (maintains Click ABI).

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
            # Use Click decorator to maintain ABI compatibility
            cmd_decorator = self._click.create_command_decorator(
                name=name,
                **kwargs,
            )
            command_obj = cmd_decorator(func)

            # Register
            cmd_name = name or func.__name__
            self._commands[cmd_name] = command_obj

            # Add to main group (Typer's Click group)
            if self._main_group is not None:
                self._main_group.add_command(command_obj)

            self.logger.debug(
                "Registered command (Click ABI, Typer container)",
                extra={
                    "command_name": cmd_name,
                },
            )

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to register command: {e}"
            self.logger.exception(error_msg)
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
        """Register a command group decorator (Click groups work with Typer).

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
            # Create group using Click (Typer supports Click groups)
            grp_decorator = self._click.create_group_decorator(
                name=name,
                **kwargs,
            )
            group_obj = grp_decorator(func)

            # Register group
            grp_name = name or func.__name__
            self._groups[grp_name] = group_obj

            # Add to main group (Typer's Click group)
            if self._main_group is not None:
                self._main_group.add_command(group_obj)

            self.logger.debug(
                "Registered group via Typer",
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
            grp_decorator = self._click.create_group_decorator(
                name=name,
                **kwargs,
            )
            group_obj = grp_decorator(func)

            # Register
            grp_name = name or func.__name__
            self._groups[grp_name] = group_obj

            # Add to main group (Typer's Click group)
            if self._main_group is not None:
                self._main_group.add_command(group_obj)

            self.logger.debug(
                "Registered group via Typer",
                extra={
                    "group_name": grp_name,
                },
            )

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to register group: {e}"
            self.logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    def register_model_command(
        self,
        model_class: type,
        handler: Callable[..., FlextResult[object]],
        name: str | None = None,
        help_text: str | None = None,
    ) -> FlextResult[None]:
        """Register a command from a Pydantic model with automatic parameter mapping.

        This method provides automatic CLI generation from Pydantic models:
        1. Extracts all model fields as CLI parameters
        2. Creates Click command with proper types and validation
        3. Automatically converts CLI args to model instance
        4. Calls handler with the validated model instance

        Args:
            model_class: Pydantic model class defining CLI parameters
            handler: Handler function that receives model instance
            name: Command name (defaults to model class name in lowercase)
            help_text: Command help text (defaults to model docstring)

        Returns:
            FlextResult[None]

        Example:
            >>> from pydantic import BaseModel, Field
            >>> from flext_core import FlextResult
            >>>
            >>> class MigrateParams(BaseModel):
            ...     input_dir: str = Field(description="Input directory")
            ...     output_dir: str = Field(description="Output directory")
            ...     sync: bool = Field(default=False, description="Sync mode")
            >>>
            >>> def handle_migrate(params: MigrateParams) -> FlextResult[None]:
            ...     # Use params.input_dir, params.output_dir, params.sync
            ...     return FlextResult[None].ok(None)
            >>>
            >>> main = FlextCliMain()
            >>> result = main.register_model_command(
            ...     model_class=MigrateParams,
            ...     handler=handle_migrate,
            ...     name="migrate",
            ...     help_text="Execute migration",
            ... )

        """
        try:
            # Get command name
            cmd_name = name or model_class.__name__.lower().replace("params", "")

            # Get help text
            cmd_help = help_text or model_class.__doc__ or f"Execute {cmd_name}"

            # Convert model to Click options
            options_result = FlextCliModels.CliModelConverter.model_to_click_options(
                model_class
            )

            if options_result.is_failure:
                return FlextResult[None].fail(
                    f"Failed to convert model to CLI options: {options_result.error}"
                )

            click_options = options_result.unwrap()

            # Create wrapper function that converts CLI args to model
            def command_wrapper(**cli_args: object) -> int:
                """Wrapper that converts CLI args to model and calls handler."""
                # Convert CLI args to model instance
                model_result = FlextCliModels.CliModelConverter.cli_args_to_model(
                    model_class, cli_args
                )

                if model_result.is_failure:
                    error_msg = f"Invalid parameters: {model_result.error}"
                    self.logger.error(error_msg)
                    # Return exit code 1 for validation errors
                    return 1

                # Call handler with validated model
                model_instance = model_result.unwrap()
                handler_result = handler(model_instance)

                if isinstance(handler_result, FlextResult):
                    if handler_result.is_failure:
                        error_msg = f"Command failed: {handler_result.error}"
                        self.logger.error(error_msg)
                        return 1
                    return 0
                # Handler returned non-FlextResult, assume success
                return 0

            # Set function metadata
            command_wrapper.__name__ = cmd_name
            command_wrapper.__doc__ = cmd_help

            # Create Click command manually to avoid **kwargs issues
            # Start with base command
            cmd = click.command(name=cmd_name, help=cmd_help)(command_wrapper)

            # Add all options from model
            for option_spec in reversed(
                click_options
            ):  # Reverse to maintain order after decorating
                option_name = option_spec["option_name"]
                opt_kwargs: FlextCore.Types.Dict = {
                    "type": self._get_click_type(str(option_spec["type"])),
                    "default": option_spec["default"],
                    "help": option_spec["help"],
                    "required": option_spec["required"],
                    "show_default": option_spec.get("show_default", True),
                }

                # Apply click.option decorator
                cmd = click.option(str(option_name), **opt_kwargs)(cmd)

            # Register command
            self._commands[cmd_name] = cmd

            # Add to main group
            if self._main_group is not None:
                self._main_group.add_command(cmd)

            self.logger.debug(
                "Registered model-driven command",
                extra={
                    "command_name": cmd_name,
                    "model_class": model_class.__name__,
                },
            )

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to register model command: {e}"
            self.logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    def _get_click_type(self, click_type_str: str) -> object:
        """Convert Click type string to Click type object.

        Args:
            click_type_str: String representation of Click type

        Returns:
            Click type object

        """
        type_map: FlextCore.Types.Dict = {
            "STRING": click.STRING,
            "INT": click.INT,
            "FLOAT": click.FLOAT,
            "BOOL": click.BOOL,
        }
        return type_map.get(click_type_str, click.STRING)

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

            # Add to main group (Typer's Click group)
            if self._main_group is not None:
                self._main_group.add_command(command_obj)  # type: ignore[arg-type]

            self.logger.debug(
                "Registered plugin command via Typer",
                extra={
                    "command_name": command_name,
                },
            )

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to register plugin command: {e}"
            self.logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    def load_plugin_commands(
        self,
        plugin_package: str,
    ) -> FlextResult[FlextCore.Types.StringList]:
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
            loaded_commands: FlextCore.Types.StringList = []

            # Import plugin package
            try:
                package = importlib.import_module(plugin_package)
            except ImportError as e:
                return FlextResult[FlextCore.Types.StringList].fail(
                    f"Failed to import plugin package: {e}",
                )

            # Discover plugin modules
            if not hasattr(package, "__path__"):
                return FlextResult[FlextCore.Types.StringList].fail(
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
                    self.logger.warning(
                        f"Failed to load plugin module '{full_module}': {e}",
                    )
                    continue

            self.logger.info(
                "Loaded plugin commands",
                extra={
                    "plugin_package": plugin_package,
                    "command_count": len(loaded_commands),
                },
            )

            return FlextResult[FlextCore.Types.StringList].ok(loaded_commands)

        except Exception as e:
            error_msg = f"Failed to load plugin commands: {e}"
            self.logger.exception(error_msg)
            return FlextResult[FlextCore.Types.StringList].fail(error_msg)

    # =========================================================================
    # COMMAND METADATA
    # =========================================================================

    def list_commands(self) -> FlextResult[FlextCore.Types.StringList]:
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
            return FlextResult[FlextCore.Types.StringList].ok(all_commands)

        except Exception as e:
            error_msg = f"Failed to list commands: {e}"
            self.logger.exception(error_msg)
            return FlextResult[FlextCore.Types.StringList].fail(error_msg)

    def list_groups(self) -> FlextResult[FlextCore.Types.StringList]:
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
            return FlextResult[FlextCore.Types.StringList].ok(all_groups)

        except Exception as e:
            error_msg = f"Failed to list groups: {e}"
            self.logger.exception(error_msg)
            return FlextResult[FlextCore.Types.StringList].fail(error_msg)

    def get_command(self, name: str) -> FlextResult[object]:
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
            return FlextResult[object].fail(f"Command '{name}' not found")

        return FlextResult[object].ok(self._commands[name])

    def get_group(self, name: str) -> FlextResult[object]:
        """Get a registered group by name.

        Args:
            name: Group name

        Returns:
            FlextResult containing group object

        Example:
            >>> result = main.get_group(FlextCliConstants.DictKeys.CONFIG)
            >>> if result.is_success:
            ...     grp = result.unwrap()

        """
        if name not in self._groups:
            return FlextResult[object].fail(f"Group '{name}' not found")

        return FlextResult[object].ok(self._groups[name])

    # =========================================================================
    # CLI EXECUTION
    # =========================================================================

    def execute_cli(
        self,
        args: FlextCore.Types.StringList | None = None,
        *,
        standalone_mode: bool = True,
    ) -> FlextResult[object]:
        """Execute the CLI with given arguments using Typer backend.

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
                return FlextResult[object].fail("Main group not initialized")

            # Execute main group (Typer's Click group)
            result = self._main_group.main(
                args=args,
                standalone_mode=standalone_mode,
            )

            return FlextResult[object].ok(result)

        except Exception as e:
            error_msg = FlextCliConstants.ErrorMessages.CLI_EXECUTION_ERROR.format(
                error=e
            )
            self.logger.exception(error_msg)
            return FlextResult[object].fail(error_msg)

    def get_main_group(self) -> FlextResult[object]:
        """Get the main CLI group object (Typer app's Click group).

        Returns:
            FlextResult containing main group

        Example:
            >>> result = main.get_main_group()
            >>> if result.is_success:
            ...     group = result.unwrap()

        """
        if self._main_group is None:
            return FlextResult[object].fail("Main group not initialized")

        return FlextResult[object].ok(self._main_group)

    # =========================================================================
    # FLEXT SERVICE METHODS
    # =========================================================================

    # Note: logger and _container are inherited from FlextCore.Service parent class
    # No need to redeclare them here as Pydantic v2 treats them as fields

    def execute(self) -> FlextResult[object]:
        """Execute CLI main operations.

        Returns:
            FlextResult[None]

        """
        return FlextResult[None].ok(None)


__all__ = [
    "FlextCliMain",
]
