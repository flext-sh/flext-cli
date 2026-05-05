"""FLEXT CLI Commands - Command registration and execution service.

Command creation and management using flext-core patterns.
Provides command registration, execution, grouping, and lifecycle management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Annotated, Self, override

from flext_cli import c, m, p, r, s, t, u


class FlextCliCommands(s):
    """CLI commands service for command registration and execution."""

    name: Annotated[
        str,
        m.Field(description="CLI command registry name"),
    ] = c.Cli.COMMANDS_DEFAULT_NAME
    _description: str = m.PrivateAttr(
        default_factory=lambda: c.Cli.COMMANDS_DEFAULT_DESCRIPTION
    )
    _commands: dict[str, p.Cli.CommandEntry] = m.PrivateAttr(default_factory=dict)

    @classmethod
    def create(cls, *, name: str, description: str = "") -> Self:
        """Create a named FlextCliCommands instance."""
        instance = cls(name=name)
        instance._description = description or name
        return instance

    @override
    def execute(self) -> p.Result[t.JsonMapping]:
        """Execute commands service - returns service status.

        Returns:
            r[dict]: Service status with commands count.

        """
        return r[t.JsonMapping].ok({
            c.Cli.DICT_KEY_APP_NAME: c.Cli.FLEXT_CLI,
            c.Cli.DICT_KEY_INITIALIZED: True,
            c.Cli.DICT_KEY_COMMANDS_COUNT: len(self._commands),
        })

    def execute_command(
        self,
        name: str,
        args: t.StrSequence | None = None,
        **kwargs: t.Scalar,
    ) -> p.Result[t.JsonValue]:
        """Execute a registered CLI command.

        Args:
            name: Command name to execute.
            args: Positional arguments for the command.
            **kwargs: Keyword arguments for the command.

        Returns:
            r: Command execution result.

        """
        if not name.strip():
            return r[t.JsonValue].fail(c.Cli.ERR_INVALID_COMMAND_NAME)
        if name not in self._commands:
            return r[t.JsonValue].fail(
                c.Cli.ERR_COMMAND_NOT_FOUND.format(name=name),
            )
        cmd_info = self._commands[name]
        handler: t.Cli.JsonCommandFn = cmd_info.handler
        if not callable(handler):
            return r[t.JsonValue].fail(
                c.Cli.ERR_HANDLER_NOT_CALLABLE.format(name=name),
            )
        command_args: tuple[str, ...] = tuple(args or ())
        try:
            return u.Cli.commands_normalize_handler_result(
                handler(*command_args, **kwargs),
                name,
            )
        except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
            return r[t.JsonValue].fail(
                c.Cli.ERR_COMMAND_EXECUTION_FAILED.format(error=exc),
            )

    def list_commands(self) -> p.Result[t.StrSequence]:
        """List all registered command names.

        Returns:
            r[t.StrSequence]: List of command names.

        """
        return r[t.StrSequence].ok(list(self._commands))

    def register_handler(
        self,
        name: str,
        handler: t.Cli.JsonCommandFn,
    ) -> p.Result[bool]:
        """Register a handler in the lightweight command registry.

        Args:
            name: Command name.
            handler: Command handler callable.

        Returns:
            r[bool]: Success if registered, failure otherwise.

        """
        if not name.strip():
            return r[bool].fail(c.Cli.ERR_COMMAND_NAME_EMPTY)
        self._commands[name] = m.Cli.CommandEntryModel(name=name, handler=handler)
        return r[bool].ok(True)

    def run_cli(self, args: t.StrSequence | None = None) -> p.Result[t.JsonValue]:
        """Run CLI with given arguments.

        Args:
            args: CLI arguments to process.

        Returns:
            r: Execution result.

        """
        if not args:
            return r[t.JsonValue].ok({
                c.Cli.DICT_KEY_STATUS: c.Cli.CommandStatus.SUCCESS,
                c.Cli.DICT_KEY_MESSAGE: c.Cli.MSG_NO_ARGS,
            })
        cmd_name, *cmd_args = args
        match cmd_name:
            case "--help" | "-h":
                return r[t.JsonValue].ok({
                    c.Cli.DICT_KEY_STATUS: c.Cli.CommandStatus.HELP,
                    c.Cli.DICT_KEY_COMMANDS: list(self._commands),
                })
            case "--version" | "-v":
                return r[t.JsonValue].ok({
                    c.Cli.DICT_KEY_STATUS: c.Cli.CommandStatus.VERSION,
                    c.Cli.DICT_KEY_NAME: self.name,
                })
            case _ if cmd_name not in self._commands:
                return r[t.JsonValue].fail(
                    c.Cli.ERR_COMMAND_NOT_FOUND.format(name=cmd_name),
                )
            case _:
                return self.execute_command(cmd_name, args=cmd_args)


__all__: list[str] = ["FlextCliCommands"]
