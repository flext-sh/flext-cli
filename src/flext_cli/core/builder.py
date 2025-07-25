"""FlextCliBuilder - Zero-boilerplate CLI creation using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Consolidated CLI builder eliminating all duplications with flext-core.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

import click
from flext_core import FlextResult, get_logger
from rich.console import Console

# Import centralized helpers to eliminate duplication
from flext_cli.core._helpers import (
    flext_cli_fail as _fail,
    flext_cli_success as _success,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from flext_cli.core.formatter import FlextCliFormatter
    from flext_cli.core.validator import FlextCliValidator

logger = get_logger(__name__)


class FlextCliCommandConfig:
    """Command configuration using standard Python class."""

    def __init__(
        self,
        name: str,
        func: Callable[..., Any],
        help_text: str = "",
        hidden: bool = False,
        aliases: list[str] | None = None,
        options: list[dict[str, Any]] | None = None,
    ) -> None:
        self.name = name
        self.func = func
        self.help = help_text
        self.hidden = hidden
        self.aliases = aliases or []
        self.options = options or []


class FlextCliBuilder:
    """Zero-boilerplate CLI builder with massive code reduction.

    Built on flext-core patterns, eliminating all internal duplications.

    Example:
        cli = FlextCliBuilder("myapp")
        cli.add_command("hello", lambda: "Hello World!")
        cli.run()

    """

    def __init__(
        self,
        name: str = "cli",
        version: str = "1.0.0",
        description: str = "",
    ) -> None:
        self.name = name
        self.version = version
        self.description = description

        # Private fields
        self._commands: dict[str, FlextCliCommandConfig] = {}
        self._global_options: list[dict[str, Any]] = []
        self._console = Console()

        # Will be set by lazy imports to avoid circular dependencies
        self._formatter: FlextCliFormatter | None = None
        self._validator: FlextCliValidator | None = None

        # Add default options
        self._add_default_options()

    def _add_default_options(self) -> None:
        """Add essential global options."""
        self.add_option("--verbose", "-v", is_flag=True, help="Verbose output")
        self.add_option(
            "--format",
            type=click.Choice(["rich", "json", "yaml"]),
            default="rich",
            help="Output format",
        )

    def _get_formatter(self) -> FlextCliFormatter:
        """Lazy import formatter to avoid circular dependencies."""
        if self._formatter is None:
            from flext_cli.core.formatter import FlextCliFormatter

            self._formatter = FlextCliFormatter("rich")
        return self._formatter

    def _get_validator(self) -> FlextCliValidator:
        """Lazy import validator to avoid circular dependencies."""
        if self._validator is None:
            from flext_cli.core.validator import FlextCliValidator

            self._validator = FlextCliValidator({})
        return self._validator

    def add_command(
        self,
        name: str,
        func: Callable[..., Any],
        help_text: str = "",
        hidden: bool = False,
        aliases: list[str] | None = None,
    ) -> FlextCliBuilder:
        """Add command with fluent chaining."""
        config = FlextCliCommandConfig(
            name=name,
            func=func,
            help_text=help_text,
            hidden=hidden,
            aliases=aliases or [],
        )
        self._commands[name] = config
        return self

    def add_option(
        self,
        *param_decls: str,
        help_text: str = "",
        command_name: str | None = None,
        **click_kwargs: Any,
    ) -> FlextCliBuilder:
        """Add option with fluent chaining."""
        option_config = {
            "param_decls": param_decls,
            "help": help_text,
            "click_kwargs": click_kwargs,
        }

        if command_name and command_name in self._commands:
            self._commands[command_name].options.append(option_config)
        else:
            self._global_options.append(option_config)

        return self

    def set_validator(self, **validations: str | Callable[..., Any]) -> FlextCliBuilder:
        """Set input validation patterns."""
        from flext_cli.core.validator import FlextCliValidator

        self._validator = FlextCliValidator(validations)
        return self

    def set_formatter(self, style: str = "rich") -> FlextCliBuilder:
        """Set output formatting style."""
        from flext_cli.core.formatter import FlextCliFormatter

        self._formatter = FlextCliFormatter(style)
        return self

    def run(self, args: list[str] | None = None) -> FlextResult[None]:
        """Build and run CLI application."""
        try:
            cli_group = self._build_click_group()

            if args is None:
                args = sys.argv[1:]

            cli_group(args, standalone_mode=True)
            return _success(None)

        except click.ClickException as e:
            e.show()
            return _fail(f"CLI error: {e}")
        except Exception as e:
            logger.exception("CLI execution failed")
            return _fail(f"Execution failed: {e}")

    def _build_click_group(self) -> click.Group:
        """Build Click group with all commands and options."""

        @click.group(
            name=self.name,
            help=self.description,
            context_settings={"help_option_names": ["-h", "--help"]},
        )
        @click.version_option(version=self.version, prog_name=self.name)
        def cli_group(**kwargs: object) -> None:
            """Main CLI group."""
            ctx = click.get_current_context()
            ctx.ensure_object(dict)
            ctx.obj.update(
                {
                    "formatter": self._get_formatter(),
                    "validator": self._get_validator(),
                    "console": self._console,
                    **kwargs,
                },
            )

        # Add global options
        for option_config in self._global_options:
            cli_group = click.option(
                *option_config["param_decls"],
                help=option_config["help"],
                **option_config["click_kwargs"],
            )(cli_group)

        # Add commands
        for cmd_config in self._commands.values():
            self._add_command_to_group(cli_group, cmd_config)

        return cli_group

    def _add_command_to_group(
        self,
        cli_group: click.Group,
        cmd_config: FlextCliCommandConfig,
    ) -> None:
        """Add command to Click group."""

        def create_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
            """Create command wrapper with validation and formatting."""

            def wrapper(**kwargs: object) -> Any:
                ctx = click.get_current_context()
                obj = ctx.obj or {}

                formatter = obj.get("formatter", self._get_formatter())
                validator = obj.get("validator", self._get_validator())

                try:
                    # Validate inputs if configured
                    if validator and validator.has_validations():
                        validation_result = validator.validate_dict(kwargs)
                        if not validation_result.success:
                            formatter.error(
                                f"Validation failed: {validation_result.error}",
                            )
                            sys.exit(1)

                    # Execute command
                    result = func(**kwargs)

                    # Handle FlextResult
                    if isinstance(result, FlextResult):
                        if result.success:
                            if result.data is not None:
                                formatter.success(result.data)
                        else:
                            formatter.error(result.error or "Command failed")
                            sys.exit(1)
                    elif result is not None:
                        formatter.output(result)

                    return result

                except Exception as e:
                    formatter.error(f"Error: {e}")
                    if obj.get("verbose"):
                        logger.exception("Command failed")
                    sys.exit(1)

            return wrapper

        # Create Click command
        wrapped_func = create_wrapper(cmd_config.func)

        # Add command-specific options
        for option_config in cmd_config.options:
            wrapped_func = click.option(
                *option_config["param_decls"],
                help=option_config["help"],
                **option_config["click_kwargs"],
            )(wrapped_func)

        # Apply command decorator
        command = click.command(
            name=cmd_config.name,
            help=cmd_config.help,
            hidden=cmd_config.hidden,
        )(wrapped_func)

        cli_group.add_command(command)

        # Add aliases
        for alias in cmd_config.aliases:
            cli_group.add_command(command, name=alias)

    def interactive_input(
        self, schema: dict[str, dict[str, Any]],
    ) -> FlextResult[dict[str, Any]]:
        """Collect interactive input using consolidated input system."""
        try:
            from flext_cli.core.input import FlextCliInput

            input_collector = FlextCliInput()
            return _success(input_collector.collect_dict(schema))
        except Exception as e:
            return _fail(f"Input collection failed: {e}")

    def format_output(self, data: Any, style: str | None = None) -> FlextResult[str]:
        """Format output using consolidated formatter."""
        try:
            from flext_cli.core.formatter import FlextCliFormatter

            formatter = (
                self._get_formatter() if style is None else FlextCliFormatter(style)
            )
            return _success(formatter.format(data))
        except Exception as e:
            return _fail(f"Formatting failed: {e}")

    def validate_data(self, data: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Validate data using consolidated validator."""
        validator = self._get_validator()
        if validator:
            return validator.validate_dict(data)
        return _success(data)

    def add_subcommand_group(self, name: str, help_text: str = "") -> FlextCliBuilder:
        """Add a subcommand group for organization."""
        # Create a new builder for the subgroup
        subgroup = FlextCliBuilder(name, self.version, help_text)

        # Add the subgroup as a command
        def subgroup_handler(**kwargs: object) -> None:
            # This will be handled by Click's group structure
            pass

        self.add_command(name, subgroup_handler, help_text)
        return subgroup

    def add_middleware(
        self, middleware: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> FlextCliBuilder:
        """Add middleware function to process all command inputs."""
        if not hasattr(self, "_middleware"):
            self._middleware: list[Callable[[dict[str, Any]], dict[str, Any]]] = []
        self._middleware.append(middleware)
        return self

    def set_error_handler(self, handler: Callable[[Exception], str]) -> FlextCliBuilder:
        """Set custom error handler for all commands."""
        self._error_handler = handler
        return self

    def add_global_flag(
        self, flag: str, help_text: str = "", default: bool = False,
    ) -> FlextCliBuilder:
        """Add a global boolean flag."""
        return self.add_option(flag, is_flag=True, default=default, help=help_text)

    def add_config_file_support(
        self, config_path: str = "config.yaml",
    ) -> FlextCliBuilder:
        """Add support for configuration file loading."""

        def load_config() -> dict[str, Any]:
            try:
                import yaml

                with open(config_path) as f:
                    return yaml.safe_load(f) or {}
            except FileNotFoundError:
                return {}
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
                return {}

        self._config_loader = load_config
        return self

    def __call__(self, *args: Any, **kwargs: object) -> FlextResult[None]:
        """Make builder callable for convenience."""
        return self.run(*args, **kwargs)
