"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from collections.abc import Sequence

from flext_cli import p, t, u
from flext_cli.services._cli import FlextCliCliPart03


class FlextCliCliPart04(FlextCliCliPart03):
    """Implementation part for FlextCliCliPart04."""

    @staticmethod
    def execute_app(
        app: p.Cli.Application,
        *,
        prog_name: str,
        args: Sequence[str] | None = None,
    ) -> p.Result[bool]:
        """Execute an application through the private framework boundary.

        Args:
            app: Application to execute.
            prog_name: Program name shown in help and errors.
            args: Optional command-line tokens passed to the application.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        return u.Cli.framework_execute(app, prog_name=prog_name, args=args)

    @staticmethod
    def execute_external_command(
        command: p.Cli.ExternalCommand,
        *,
        prog_name: str,
        args: Sequence[str] | None = None,
    ) -> p.Result[bool]:
        """Execute a foreign command through the private framework boundary.

        Args:
            command: Foreign command adapter to execute.
            prog_name: Program name shown in help and errors.
            args: Optional command-line tokens passed to the command.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        return u.Cli.framework_execute_external(command, prog_name=prog_name, args=args)

    @staticmethod
    def register_callback(app: p.Cli.Application, *, command: t.Cli.CliCommand) -> None:
        """Register one model-backed root callback.

        Args:
            app: Application receiving the callback.
            command: Callback command to register.

        """
        u.Cli.framework_register_callback(app, command)

    @staticmethod
    def exit(code: int = 0) -> None:
        """Terminate through the adapter-owned execution context.

        Args:
            code: Process exit code; zero when omitted.

        """
        u.Cli.framework_exit(code)

    @staticmethod
    def register_command(
        app: p.Cli.Application,
        *,
        name: str,
        help_text: str,
        command: t.Cli.CliCommand,
    ) -> None:
        """Register a command through the private framework boundary.

        Args:
            app: Application receiving the command.
            name: Name the command registers under.
            help_text: Command help text.
            command: Command callable to register.

        """
        u.Cli.framework_register_command(
            app,
            name=name,
            help_text=help_text,
            command=command,
        )


__all__: list[str] = ["FlextCliCliPart04"]
