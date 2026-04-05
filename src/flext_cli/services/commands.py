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

    _name: str = PrivateAttr(default=c.Cli.CommandsDefaults.DEFAULT_NAME)
    _description: str = PrivateAttr(default=c.Cli.CommandsDefaults.DEFAULT_DESCRIPTION)
    _commands: MutableMapping[str, p.Cli.CommandEntry] = PrivateAttr(
        default_factory=lambda: dict[str, p.Cli.CommandEntry](),
    )

    @staticmethod
    def _empty_command_registry() -> MutableMapping[str, p.Cli.CommandEntry]:
        """Create an empty typed command registry for PrivateAttr initialization."""
        return {}

    @classmethod
    def create(cls, *, name: str, description: str = "") -> Self:
        """Create a named FlextCliCommands instance."""
        instance = cls()
        instance._name = name
        instance._description = description or name
        return instance

    @staticmethod
    def _normalize_handler_result(
        result: r[t.RecursiveValue] | None,
        command_name: str,
    ) -> r[t.Cli.JsonValue]:
        if result is None:
            payload: t.Cli.JsonValue = {
                "status": "success",
                "command": command_name,
            }
            return r[t.Cli.JsonValue].ok(payload)
        if result.is_success:
            result_value: t.Cli.JsonValue = u.Cli.normalize_json_value(result.value)
            return r[t.Cli.JsonValue].ok(result_value)
        error_value = result.error
        return r[t.Cli.JsonValue].fail(
            str(error_value) if error_value else "Command failed",
        )

    @override
    def execute(self) -> r[t.Cli.JsonMapping]:
        """Execute commands service - returns service status.

        Returns:
            r[dict]: Service status with commands count.

        """
        status: t.Cli.JsonMapping = {
            "app_name": c.Cli.FLEXT_CLI,
            "is_initialized": True,
            "commands_count": len(self._commands),
        }
        return r[t.Cli.JsonMapping].ok(status)

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
        handler: t.Cli.JsonCommandFn = cmd_info.handler
        if not callable(handler):
            return r[t.Cli.JsonValue].fail(
                c.Cli.CommandsErrorMessages.HANDLER_NOT_CALLABLE.format(name=name),
            )
        try:
            result: r[t.RecursiveValue] | None = None
            execution_attempted = False
            if args or kwargs:
                try:
                    result = handler(*args, **kwargs) if args else handler(**kwargs)
                    execution_attempted = True
                except TypeError as exc:
                    self.logger.debug(
                        "Handler signature mismatch; retrying without args",
                        command_name=name,
                        error=str(exc),
                    )
            if not execution_attempted:
                result = handler()
            return self._normalize_handler_result(result, name)
        except c.Cli.CLI_SAFE_EXCEPTIONS as e:
            return r[t.Cli.JsonValue].fail(
                c.Cli.CommandsErrorMessages.COMMAND_EXECUTION_FAILED.format(error=e),
            )

    def list_commands(self) -> r[t.StrSequence]:
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
    ) -> r[bool]:
        """Register a handler in the lightweight command registry.

        Args:
            name: Command name.
            handler: Command handler callable.

        Returns:
            r[bool]: Success if registered, failure otherwise.

        """
        if not name.strip():
            return r[bool].fail(c.Cli.CommandsErrorMessages.COMMAND_NAME_EMPTY)
        self._commands[name] = m.Cli.CommandEntryModel(name=name, handler=handler)
        return r[bool].ok(True)

    def run_cli(self, args: t.StrSequence | None = None) -> r[t.Cli.JsonValue]:
        """Run CLI with given arguments.

        Args:
            args: CLI arguments to process.

        Returns:
            r: Execution result.

        """
        if not args:
            empty_args_payload: t.Cli.JsonValue = {
                "status": "success",
                "message": "No args",
            }
            return r[t.Cli.JsonValue].ok(empty_args_payload)
        cmd_name = args[0] if args else ""
        cmd_args = list(args[1:]) if len(args) > 1 else []
        if cmd_name in {"--help", "-h"}:
            help_payload: t.Cli.JsonValue = {
                "status": "help",
                "commands": list(self._commands.keys()),
            }
            return r[t.Cli.JsonValue].ok(help_payload)
        if cmd_name in {"--version", "-v"}:
            version_payload: t.Cli.JsonValue = {
                "status": "version",
                "name": self._name,
            }
            return r[t.Cli.JsonValue].ok(version_payload)
        if cmd_name not in self._commands:
            return r[t.Cli.JsonValue].fail(
                c.Cli.CommandsErrorMessages.COMMAND_NOT_FOUND.format(name=cmd_name),
            )
        return self.execute_command(cmd_name, args=cmd_args)


__all__ = ["FlextCliCommands"]
