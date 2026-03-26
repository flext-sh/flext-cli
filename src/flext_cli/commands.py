"""FLEXT CLI Commands - Command registration and execution service.

Command creation and management using flext-core patterns.
Provides command registration, execution, grouping, and lifecycle management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping, MutableMapping
from typing import Self, override

from flext_core import r
from pydantic import PrivateAttr
from rich.errors import ConsoleError, LiveError, StyleError

from flext_cli import FlextCliServiceBase, c, m, t


class FlextCliCommands(FlextCliServiceBase):
    """CLI commands service for command registration and execution."""

    _name: str = PrivateAttr(default=c.Cli.CommandsDefaults.DEFAULT_NAME)
    _description: str = PrivateAttr(default=c.Cli.CommandsDefaults.DEFAULT_DESCRIPTION)
    _commands: MutableMapping[str, m.Cli.CommandEntryModel] = PrivateAttr(
        default_factory=dict,
    )

    @classmethod
    def create(cls, *, name: str, description: str = "") -> Self:
        """Create a named FlextCliCommands instance."""
        instance = cls()
        instance._name = name
        instance._description = description or name
        return instance

    @staticmethod
    def _normalize_handler_result(
        result: r[t.Cli.JsonValue] | None,
        command_name: str,
    ) -> r[t.Cli.JsonValue]:
        if result is None:
            return r[t.Cli.JsonValue].ok({"status": "success", "command": command_name})
        if result.is_success:
            return r[t.Cli.JsonValue].ok(result.value)
        error_value = result.error
        return r[t.Cli.JsonValue].fail(
            str(error_value) if error_value else "Command failed",
        )

    @override
    def execute(self) -> r[Mapping[str, t.Cli.JsonValue]]:
        """Execute commands service - returns service status.

        Returns:
            r[dict]: Service status with commands count.

        """
        return r[Mapping[str, t.Cli.JsonValue]].ok({
            "app_name": c.Cli.FLEXT_CLI,
            "is_initialized": True,
            "commands_count": len(self._commands),
        })

    def execute_command(
        self,
        name: str,
        args: t.StrSequence | None = None,
        **kwargs: t.Scalar,
    ) -> r[t.Cli.JsonValue]:
        """Execute a registered CLI command.

        Args:
            name: Command name to execute.
            args: Positional arguments for the command.
            **kwargs: Keyword arguments for the command.

        Returns:
            r: Command execution result.

        """
        if not name.strip():
            return r[t.Cli.JsonValue].fail(
                c.Cli.CommandsErrorMessages.INVALID_COMMAND_NAME
            )
        if name not in self._commands:
            return r[t.Cli.JsonValue].fail(
                c.Cli.CommandsErrorMessages.COMMAND_NOT_FOUND.format(name=name),
            )
        cmd_info = self._commands[name]
        handler = cmd_info.handler
        if not callable(handler):
            return r[t.Cli.JsonValue].fail(
                c.Cli.CommandsErrorMessages.HANDLER_NOT_CALLABLE.format(name=name),
            )
        try:
            result: r[t.Cli.JsonValue] | None = None
            execution_attempted = False
            if args or kwargs:
                try:
                    result = handler(*args, **kwargs) if args else handler(**kwargs)
                    execution_attempted = True
                except TypeError as exc:
                    logging.getLogger(__name__).debug(
                        "Handler signature mismatch for %s, trying no-args: %s",
                        name,
                        exc,
                        exc_info=False,
                    )
            if not execution_attempted:
                result = handler()
            return self._normalize_handler_result(result, name)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            return r[t.Cli.JsonValue].fail(
                c.Cli.CommandsErrorMessages.COMMAND_EXECUTION_FAILED.format(error=e),
            )

    def list_commands(self) -> r[t.StrSequence]:
        """List all registered command names.

        Returns:
            r[t.StrSequence]: List of command names.

        """
        return r[t.StrSequence].ok(list(self._commands.keys()))

    def register_command(
        self,
        name: str,
        handler: Callable[..., r[t.Cli.JsonValue]],
    ) -> r[bool]:
        """Register a CLI command.

        Args:
            name: Command name.
            handler: Command handler callable.

        Returns:
            r[bool]: Success if registered, failure otherwise.

        """
        if not name.strip():
            return r[bool].fail(c.Cli.CommandsErrorMessages.COMMAND_NAME_EMPTY)
        self._commands[name] = m.Cli.CommandEntryModel(name=name, handler=handler)
        return r[bool].ok(value=True)

    def run_cli(self, args: t.StrSequence | None = None) -> r[t.Cli.JsonValue]:
        """Run CLI with given arguments.

        Args:
            args: CLI arguments to process.

        Returns:
            r: Execution result.

        """
        if not args:
            return r[t.Cli.JsonValue].ok({"status": "success", "message": "No args"})
        cmd_name = args[0] if args else ""
        cmd_args = list(args[1:]) if len(args) > 1 else []
        if cmd_name in {"--help", "-h"}:
            return r[t.Cli.JsonValue].ok({
                "status": "help",
                "commands": list(self._commands.keys()),
            })
        if cmd_name in {"--version", "-v"}:
            return r[t.Cli.JsonValue].ok({"status": "version", "name": self._name})
        if cmd_name not in self._commands:
            return r[t.Cli.JsonValue].fail(
                c.Cli.CommandsErrorMessages.COMMAND_NOT_FOUND.format(name=cmd_name),
            )
        return self.execute_command(cmd_name, args=cmd_args)


__all__ = ["FlextCliCommands"]
