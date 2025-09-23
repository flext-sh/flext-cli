"""FLEXT CLI Main - Direct Click integration without over-abstraction.

Main CLI entry point that extends FlextService and uses Click directly
for command registration and execution.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import cast

import click

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
)

# Type alias for Click options - can be complex nested structures
ClickOptions = dict[str, str | bool | int | list[str] | None]


class FlextCliMain(FlextService[dict[str, object]]):
    """Main CLI class - direct Click integration without abstraction layers.

    Provides essential Click functionality for the FLEXT ecosystem by directly
    extending FlextService and using Click appropriately.
    """

    def __init__(self, name: str = "flext-cli", description: str = "FLEXT CLI") -> None:
        """Initialize FlextCliMain with direct Click integration."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()

        # Direct Click group creation
        self._cli_group = click.Group(
            name=name,
            help=description,
            context_settings={"help_option_names": ["-h", "--help"]},
        )

        self._logger.info(f"FlextCliMain initialized: {name}")

    def execute(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute the main domain service operation - required by FlextService."""
        return FlextResult[FlextTypes.Core.Dict].ok({
            "status": "operational",
            "service": "flext-cli-main",
            "commands": len(self._cli_group.commands),
            "groups": len([
                cmd
                for cmd in self._cli_group.commands.values()
                if isinstance(cmd, click.Group)
            ]),
        })

    def add_command(
        self,
        name: str,
        callback: object,
        help_text: str = "",
        click_options: ClickOptions | None = None,
    ) -> FlextResult[None]:
        """Add a command to the CLI group.

        Args:
            name: Command name
            callback: Command function
            help_text: Help text for the command
            click_options: Additional Click options

        Returns:
            FlextResult[None]: Success or failure result

        """
        if not callable(callback):
            return FlextResult[None].fail(
                f"Callback for command '{name}' is not callable"
            )

        try:
            # Create Click command directly with explicit parameters
            command = click.Command(
                name=name,
                callback=callback,
                help=help_text,
                params=cast("list[click.Parameter]", click_options.get("params"))
                if click_options and isinstance(click_options.get("params"), list)
                else None,
                short_help=str(click_options.get("short_help"))
                if click_options and click_options.get("short_help")
                else None,
                options_metavar=str(click_options.get("options_metavar")) if (click_options and click_options.get("options_metavar")) else "",
                add_help_option=bool(click_options.get("add_help_option", True))
                if click_options
                else True,
                no_args_is_help=bool(click_options.get("no_args_is_help", True))
                if click_options
                else True,
            )
            self._cli_group.add_command(command)
            self._logger.info(f"Added command: {name}")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to add command '{name}': {e}")

    def add_group(
        self, name: str, help_text: str = "", click_options: ClickOptions | None = None
    ) -> FlextResult[click.Group]:
        """Add a command group to the CLI.

        Args:
            name: Group name
            help_text: Help text for the group
            click_options: Additional Click options

        Returns:
            FlextResult[click.Group]: Created group or error

        """
        try:
            # Create Click group directly with explicit parameters
            group = click.Group(
                name=name,
                help=help_text,
                commands=cast(
                    "dict[str, click.Command]",
                    click_options.get("commands"),
                )
                if click_options
                and isinstance(click_options.get("commands"), dict)
                else None,
                invoke_without_command=bool(
                    click_options.get("invoke_without_command", False)
                )
                if click_options
                else False,
                no_args_is_help=bool(click_options.get("no_args_is_help", True))
                if click_options
                else True,
                add_help_option=bool(click_options.get("add_help_option", True))
                if click_options
                else True,
                chain=bool(click_options.get("chain", False))
                if click_options
                else False,
            )
            self._cli_group.add_command(group)
            self._logger.info(f"Added group: {name}")
            return FlextResult[click.Group].ok(group)
        except Exception as e:
            return FlextResult[click.Group].fail(f"Failed to add group '{name}': {e}")

    def run_cli(
        self, args: list[str] | None = None, *, standalone_mode: bool = True
    ) -> FlextResult[None]:
        """Run the CLI with the given arguments.

        Args:
            args: Command line arguments (None for sys.argv)
            standalone_mode: Whether to run in standalone mode

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            self._cli_group.main(args=args, standalone_mode=standalone_mode)
            return FlextResult[None].ok(None)
        except SystemExit as e:
            # Click raises SystemExit for normal operation
            if e.code == 0:
                return FlextResult[None].ok(None)
            return FlextResult[None].fail(f"CLI exited with code: {e.code}")
        except Exception as e:
            return FlextResult[None].fail(f"CLI execution failed: {e}")

    def get_click_group(self) -> click.Group:
        """Get the underlying Click group for direct access.

        Returns:
            click.Group: The Click group instance

        """
        return self._cli_group

    def execute_command(self, command: str, **kwargs: object) -> FlextResult[str]:
        """Execute a command with the given arguments.

        Args:
            command: Command name to execute
            **kwargs: Command arguments

        Returns:
            FlextResult[str]: Command execution result

        """
        try:
            # Convert kwargs to CLI args
            args = [command]
            for key, value in kwargs.items():
                if isinstance(value, bool) and value:
                    args.append(f"--{key}")
                elif value is not None:
                    args.extend([f"--{key}", str(value)])

            # Execute the command
            result = self._cli_group.main(args=args, standalone_mode=False)
            return FlextResult[str].ok(str(result) if result is not None else "")
        except SystemExit as e:
            if e.code == 0:
                return FlextResult[str].ok("")
            return FlextResult[str].fail(f"Command failed with exit code: {e.code}")
        except Exception as e:
            return FlextResult[str].fail(f"Command execution failed: {e}")

    def list_commands(self) -> FlextResult[list[str]]:
        """List all registered commands.

        Returns:
            FlextResult[list[str]]: List of command names

        """
        try:
            # Create a dummy context for list_commands
            ctx = click.Context(self._cli_group)
            commands = list(self._cli_group.list_commands(ctx))
            return FlextResult[list[str]].ok(commands)
        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to list commands: {e}")

    def register_command_group(
        self,
        name: str,
        commands: dict[str, object],
        description: str = "",
    ) -> FlextResult[None]:
        """Register a group of commands with the CLI.
        
        Args:
            name: Group name
            commands: Dictionary of command definitions
            description: Group description
            
        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            # Create a Click group for the command group
            group = click.Group(
                name=name,
                help=description,
                context_settings={"help_option_names": ["-h", "--help"]},
            )
            
            # Add commands to the group
            for cmd_name, cmd_def in commands.items():
                if isinstance(cmd_def, dict) and "handler" in cmd_def:
                    command = click.Command(
                        name=cmd_name,
                        callback=cmd_def["handler"],
                        help=cmd_def.get("description", ""),
                    )
                    group.add_command(command)
            
            # Add the group to the main CLI
            self._cli_group.add_command(group)
            self._logger.info(f"Registered command group: {name}")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to register command group '{name}': {e}")


def create_main_cli() -> FlextCliMain:
    """Create the main CLI instance.

    Returns:
        FlextCliMain: Main CLI instance

    """
    return FlextCliMain(
        name="flext", description="FLEXT Enterprise Data Integration Platform CLI"
    )


__all__ = [
    "FlextCliMain",
    "create_main_cli",
]
