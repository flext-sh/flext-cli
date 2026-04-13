"""FLEXT CLI Commands - Command registration and execution service.

Command creation and management using flext-core patterns.
Provides command registration, execution, grouping, and lifecycle management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Self, override

from pydantic import PrivateAttr

from flext_cli import c, m, p, r, s, t, u


class FlextCliCommands(s):
    """CLI commands service for command registration and execution."""

    _name: str = PrivateAttr(default=c.Cli.COMMANDS_DEFAULT_NAME)
    _description: str = PrivateAttr(default=c.Cli.COMMANDS_DEFAULT_DESCRIPTION)
    _commands: MutableMapping[str, p.Cli.CommandEntry] = PrivateAttr(
        default_factory=lambda: dict[str, p.Cli.CommandEntry](),
    )

    @classmethod
    def create(cls, *, name: str, description: str = "") -> Self:
        """Create a named FlextCliCommands instance."""
        instance = cls()
        instance._name = name
        instance._description = description or name
        return instance

    @override
    def execute(self) -> p.Result[t.Cli.JsonMapping]:
        """Execute commands service - returns service status.

        Returns:
            r[dict]: Service status with commands count.

        """
        status: t.Cli.JsonMapping = {
            "app_name": c.Cli.FLEXT_CLI,
            "initialized": True,
            "commands_count": len(self._commands),
        }
        return r[t.Cli.JsonMapping].ok(status)

    def execute_command(
        self,
        name: str,
        args: t.StrSequence | None = None,
        **kwargs: t.Scalar,
    ) -> p.Result[t.Cli.JsonValue]:
        """Execute a registered CLI command.

        Args:
            name: Command name to execute.
            args: Positional arguments for the command.
            **kwargs: Keyword arguments for the command.

        Returns:
            r: Command execution result.

        """
        if not name.strip():
            return r[t.Cli.JsonValue].fail(c.Cli.ERR_INVALID_COMMAND_NAME)
        if name not in self._commands:
            return r[t.Cli.JsonValue].fail(
                c.Cli.ERR_COMMAND_NOT_FOUND.format(name=name),
            )
        cmd_info = self._commands[name]
        handler: t.Cli.JsonCommandFn = cmd_info.handler
        if not callable(handler):
            return r[t.Cli.JsonValue].fail(
                c.Cli.ERR_HANDLER_NOT_CALLABLE.format(name=name),
            )

        def _on_signature_mismatch(error: str) -> None:
            self.logger.debug(
                "Handler signature mismatch; retrying without args",
                command_name=name,
                error=error,
            )

        return u.Cli.commands_execute_handler(
            command_name=name,
            handler=handler,
            args=args,
            kwargs=kwargs,
            on_signature_mismatch=_on_signature_mismatch,
        )

    def list_commands(self) -> p.Result[t.StrSequence]:
        """List all registered command names.

        Returns:
            r[t.StrSequence]: List of command names.

        """
        command_names: t.StrSequence = list(self._commands.keys())
        return r[t.StrSequence].ok(command_names)

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

    def run_cli(self, args: t.StrSequence | None = None) -> p.Result[t.Cli.JsonValue]:
        """Run CLI with given arguments.

        Args:
            args: CLI arguments to process.

        Returns:
            r: Execution result.

        """
        if not args:
            empty_args_payload: t.Cli.JsonValue = {
                "status": c.Cli.CommandStatus.SUCCESS,
                "message": "No args",
            }
            return r[t.Cli.JsonValue].ok(empty_args_payload)
        cmd_name = args[0] if args else ""
        cmd_args = list(args[1:]) if len(args) > 1 else []
        if cmd_name in {"--help", "-h"}:
            help_payload: t.Cli.JsonValue = {
                "status": c.Cli.CommandStatus.HELP,
                "commands": list(self._commands.keys()),
            }
            return r[t.Cli.JsonValue].ok(help_payload)
        if cmd_name in {"--version", "-v"}:
            version_payload: t.Cli.JsonValue = {
                "status": c.Cli.CommandStatus.VERSION,
                "name": self._name,
            }
            return r[t.Cli.JsonValue].ok(version_payload)
        if cmd_name not in self._commands:
            return r[t.Cli.JsonValue].fail(
                c.Cli.ERR_COMMAND_NOT_FOUND.format(name=cmd_name),
            )
        return self.execute_command(cmd_name, args=cmd_args)


__all__: list[str] = ["FlextCliCommands"]
