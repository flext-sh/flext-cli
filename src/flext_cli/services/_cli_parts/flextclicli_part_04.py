"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys

import click
import typer

from flext_cli import (
    p,
    r,
    t,
    u,
)
from flext_cli.services._cli_parts.flextclicli_part_03 import (
    FlextCliCli as FlextCliCliPart03,
)


class FlextCliCli(FlextCliCliPart03):
    """Implementation part for FlextCliCli."""

    @staticmethod
    def execute_app(
        app: t.Cli.CliApp,
        *,
        prog_name: str,
        args: t.StrSequence | None = None,
    ) -> p.Result[bool]:
        """Execute a Typer app and normalize exit behavior into `r[bool]`."""
        cli_args = list(args) if args is not None else sys.argv[1:]
        command = typer.main.get_command(app)
        original_argv = sys.argv.copy()
        result: p.Result[bool]

        try:
            sys.argv = [prog_name, *cli_args]
            exit_result = command.main(
                args=cli_args,
                prog_name=prog_name,
                standalone_mode=False,
            )
        except click.ClickException as exc:
            result = r[bool].fail(exc.format_message().strip())
        except typer.Abort as exc:
            result = r[bool].fail(
                u.Cli.normalize_required_text(
                    str(exc),
                    default=exc.__class__.__name__,
                ),
            )
        except typer.Exit as exc:
            result = (
                r[bool].ok(True)
                if exc.exit_code == 0
                else r[bool].fail(f"CLI exited with code {exc.exit_code}")
            )
        except Exception as exc:
            result = r[bool].fail(
                u.Cli.normalize_required_text(
                    str(exc),
                    default=exc.__class__.__name__,
                ),
            )
        else:
            if (
                isinstance(exit_result, int)
                and not isinstance(exit_result, bool)
                and exit_result != 0
            ):
                result = r[bool].fail(f"CLI exited with code {exit_result}")
            else:
                result = r[bool].ok(True)
        finally:
            sys.argv = original_argv
        return result

    @staticmethod
    def exit(code: int = 0) -> None:
        """Terminate the CLI flow with the given exit code.

        Context-aware shutdown: inside an active Typer/Click context (a CLI
        callback or subcommand running through ``cli.execute_app``), raises
        ``typer.Exit(code)`` so ``execute_app`` catches it and returns the
        canonical ``r[bool]`` result. Outside any active context (typically
        ``__main__.py`` entry points after ``execute_app`` has returned),
        delegates to ``sys.exit(code)`` for a clean process exit without a
        ``typer.Exit`` traceback.
        """
        try:
            click.get_current_context(silent=False)
        except RuntimeError:
            sys.exit(code)
        raise typer.Exit(code=code)

    @staticmethod
    def register_command(
        app: t.Cli.CliApp,
        *,
        name: str,
        help_text: str,
        command: t.Cli.CliCommand,
    ) -> None:
        """Register a command on the given Typer application."""
        _ = app.command(name, help=help_text)(command)


__all__: list[str] = ["FlextCliCli"]
