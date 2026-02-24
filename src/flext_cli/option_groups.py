"""Reusable option group definitions for flext-cli.

FlextCliOptionGroup provides pre-defined option groups for common CLI patterns
(connection, authentication, output formatting) that can be reused across
multiple commands.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typer.models import OptionInfo


class FlextCliOptionGroup:
    """Reusable option group definitions.

    Provides static methods that return lists of typer.Option objects for
    common CLI patterns. These can be used with command decorators or
    FlextCliCommandBuilder to reduce boilerplate.

    Example:
        >>> @command("sync")
        >>> @with_options(FlextOptionGroup.connection_options())
        >>> @with_options(FlextOptionGroup.auth_options())
        >>> def sync_command(host: str, port: int, username: str, **kwargs) -> None: ...

    """

    @staticmethod
    def connection_options() -> list[OptionInfo]:
        """Common connection options for any service.

        Returns:
            List of typer.Option objects for connection parameters:
            - --host, -h: Hostname or IP address (default: localhost)
            - --port, -p: Port number (default: 8080)
            - --timeout, -t: Timeout in seconds (default: 30)
            - --ssl/--no-ssl: Enable/disable SSL (default: False)

        """
        return [
            OptionInfo(
                default="localhost",
                param_decls=["--host", "-h"],
                help="Hostname or IP address",
            ),
            OptionInfo(
                default=8080,
                param_decls=["--port", "-p"],
                help="Port number",
            ),
            OptionInfo(
                default=30,
                param_decls=["--timeout", "-t"],
                help="Timeout in seconds",
            ),
            OptionInfo(
                default=False,
                param_decls=["--ssl/--no-ssl"],
                help="Enable SSL/TLS",
            ),
        ]

    @staticmethod
    def auth_options() -> list[OptionInfo]:
        """Common authentication options.

        Returns:
            List of typer.Option objects for authentication parameters:
            - --username, -u: Username (from FLEXT_USERNAME env var)
            - --password: Password (from FLEXT_PASSWORD env var, hidden input)
            - --token: Authentication token (from FLEXT_TOKEN env var)

        """
        return [
            OptionInfo(
                default=None,
                param_decls=["--username", "-u"],
                envvar="FLEXT_USERNAME",
                help="Username for authentication",
            ),
            OptionInfo(
                default=None,
                param_decls=["--password"],
                envvar="FLEXT_PASSWORD",
                help="Password for authentication (hidden input)",
            ),
            OptionInfo(
                default=None,
                param_decls=["--token"],
                envvar="FLEXT_TOKEN",
                help="Authentication token",
            ),
        ]

    @staticmethod
    def output_options() -> list[OptionInfo]:
        """Common output format options.

        Returns:
            List of typer.Option objects for output formatting:
            - --format, -f: Output format (json, yaml, table) (default: table)
            - --output, -o: Output file path
            - --quiet/--verbose: Quiet or verbose output (default: False)

        """
        return [
            OptionInfo(
                default="table",
                param_decls=["--format", "-f"],
                help="Output format (json, yaml, table)",
            ),
            OptionInfo(
                default=None,
                param_decls=["--output", "-o"],
                help="Output file path",
            ),
            OptionInfo(
                default=False,
                param_decls=["--quiet/--verbose"],
                help="Quiet or verbose output",
            ),
        ]
