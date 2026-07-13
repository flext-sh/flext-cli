"""Private Click/Typer adapter behind the public FLEXT CLI facade."""

from __future__ import annotations

import sys
import traceback
from collections.abc import Callable
from contextvars import ContextVar
from inspect import Parameter
from types import EllipsisType, GenericAlias

import click
import typer
from typer.models import OptionInfo
from typer.testing import CliRunner

from flext_cli import c, m, p, t
from flext_core import r


class _TyperApplication:
    """Private application implementation hidden behind ``p.Cli.Application``."""

    __slots__ = ("_app", "_name")

    def __init__(self, app: typer.Typer, *, name: str | None) -> None:
        self._app = app
        self._name = name

    @property
    def name(self) -> str | None:
        """Return the configured application name."""
        return self._name

    @property
    def backend(self) -> typer.Typer:
        """Return the backend object inside this private adapter module."""
        return self._app

    def callback(
        self,
    ) -> Callable[[Callable[..., t.JsonPayload]], Callable[..., t.JsonPayload]]:
        """Return the private framework callback decorator."""
        return self._app.callback()

    def command[TCommand: Callable[..., t.JsonPayload]](
        self, name: str | None = None, *, help: str | None = None
    ) -> Callable[[TCommand], TCommand]:
        """Return a typed command decorator through the neutral contract."""
        return self._app.command(name, help=help)

    def add_typer(self, group: p.Cli.Application, *, name: str) -> None:
        """Attach another adapter-owned application as a child group."""
        if not isinstance(group, _TyperApplication):
            msg = "CLI group was not created by flext_cli"
            raise TypeError(msg)
        self._app.add_typer(group.backend, name=name)


class _ClickCommand:
    """Private command implementation satisfying ``p.Cli.ExternalCommand``."""

    __slots__ = ("_command",)

    def __init__(self, command: click.Command) -> None:
        self._command = command

    def main(
        self,
        args: t.StrSequence | None = None,
        prog_name: str | None = None,
        *,
        standalone_mode: bool = True,
    ) -> t.JsonPayload:
        """Execute and validate the backend command result at the boundary."""
        result = self._command.main(
            args=list(args) if args is not None else None,
            prog_name=prog_name,
            standalone_mode=standalone_mode,
        )
        return t.Cli.JSON_VALUE_ADAPTER.validate_python(result)


class FlextCliUtilitiesFramework:
    """Single adapter owning all Click/Typer runtime interaction."""

    _active_execution: ContextVar[bool] = ContextVar(
        "flext_cli_active_execution", default=False
    )

    @staticmethod
    def _unwrap(application: p.Cli.Application) -> _TyperApplication:
        """Return the private application or fail on a foreign implementation."""
        if not isinstance(application, _TyperApplication):
            msg = "CLI application was not created by flext_cli"
            raise TypeError(msg)
        return application

    @staticmethod
    def _exception_message(exc: BaseException) -> str:
        """Return a non-empty normalized exception message."""
        return str(exc).strip() or exc.__class__.__name__

    @classmethod
    def framework_create_app(
        cls, *, name: str | None, help_text: str, add_completion: bool = True
    ) -> p.Cli.Application:
        """Create one private Typer application behind the neutral protocol."""
        return _TyperApplication(
            typer.Typer(name=name, help=help_text, add_completion=add_completion),
            name=name,
        )

    @classmethod
    def framework_add_group(
        cls, application: p.Cli.Application, *, name: str, group: p.Cli.Application
    ) -> None:
        """Attach one private application group."""
        cls._unwrap(application).add_typer(group, name=name)

    @classmethod
    def framework_register_callback(
        cls, application: p.Cli.Application, callback: t.Cli.CliCommand
    ) -> None:
        """Register one application callback."""
        _ = cls._unwrap(application).callback()(callback)

    @classmethod
    def framework_register_command(
        cls,
        application: p.Cli.Application,
        *,
        name: str,
        help_text: str,
        command: t.Cli.CliCommand,
    ) -> None:
        """Register one named command."""
        _ = cls._unwrap(application).command(name, help=help_text)(command)

    @staticmethod
    def framework_build_parameter(
        field_name: str, annotation: type | GenericAlias, spec: m.Cli.OptionSpec
    ) -> Parameter:
        """Build one inspect parameter with a private Typer option default."""
        option_default: t.Cli.CliValue | EllipsisType | None = (
            ... if spec.required else spec.default
        )
        option = OptionInfo(
            default=option_default,
            param_decls=list(spec.declarations),
            help=spec.help_text or None,
        )
        return Parameter(
            field_name,
            kind=Parameter.KEYWORD_ONLY,
            default=option,
            annotation=annotation,
        )

    @classmethod
    def framework_execute(
        cls,
        application: p.Cli.Application,
        *,
        prog_name: str,
        args: t.StrSequence | None = None,
    ) -> p.Result[bool]:
        """Execute one application and normalize every framework exit path."""
        cli_args = list(args) if args is not None else sys.argv[1:]
        private_application = cls._unwrap(application)
        command = typer.main.get_command(private_application.backend)
        original_argv = sys.argv.copy()
        token = cls._active_execution.set(True)
        try:
            sys.argv = [prog_name, *cli_args]
            exit_result = command.main(
                args=cli_args, prog_name=prog_name, standalone_mode=False
            )
        except click.ClickException as exc:
            return r[bool].fail(exc.format_message().strip())
        except typer.Abort as exc:
            return r[bool].fail(cls._exception_message(exc))
        except typer.Exit as exc:
            return (
                r[bool].ok(True)
                if exc.exit_code == 0
                else r[bool].fail(f"CLI exited with code {exc.exit_code}")
            )
        except SystemExit as exc:
            exit_code = exc.code if isinstance(exc.code, int) else 1
            return (
                r[bool].ok(True)
                if exit_code == 0
                else r[bool].fail(f"CLI exited with code {exit_code}")
            )
        except Exception as exc:
            detail = cls._exception_message(exc)
            return r[bool].fail(f"{detail}\n{traceback.format_exc().strip()}")
        finally:
            sys.argv = original_argv
            cls._active_execution.reset(token)
        if (
            isinstance(exit_result, int)
            and not isinstance(exit_result, bool)
            and exit_result != 0
        ):
            return r[bool].fail(f"CLI exited with code {exit_result}")
        return r[bool].ok(True)

    @classmethod
    def framework_execute_external(
        cls,
        command: p.Cli.ExternalCommand,
        *,
        prog_name: str,
        args: t.StrSequence | None = None,
    ) -> p.Result[bool]:
        """Execute a foreign Click-compatible command inside the boundary."""
        try:
            exit_result = command.main(
                args=args, prog_name=prog_name, standalone_mode=False
            )
        except click.ClickException as exc:
            return r[bool].fail(exc.format_message().strip())
        except click.Abort as exc:
            return r[bool].fail(cls._exception_message(exc))
        except SystemExit as exc:
            exit_code = exc.code if isinstance(exc.code, int) else 1
            return (
                r[bool].ok(True)
                if exit_code == 0
                else r[bool].fail(f"CLI exited with code {exit_code}")
            )
        if (
            isinstance(exit_result, int)
            and not isinstance(exit_result, bool)
            and exit_result != 0
        ):
            return r[bool].fail(f"CLI exited with code {exit_result}")
        return r[bool].ok(True)

    @classmethod
    def framework_external_command(
        cls, application: p.Cli.Application
    ) -> p.Cli.ExternalCommand:
        """Expose an adapter-owned application through the command protocol."""
        return _ClickCommand(typer.main.get_command(cls._unwrap(application).backend))

    @classmethod
    def framework_invoke(
        cls,
        application: p.Cli.Application,
        *,
        args: t.StrSequence | None = None,
        charset: str = c.Cli.ENCODING_DEFAULT,
        env: t.StrMapping | None = None,
    ) -> m.Cli.InvocationResult:
        """Invoke one application through the real framework test runner."""
        runner = CliRunner(charset=charset, env=env)
        private_application = cls._unwrap(application)
        result = runner.invoke(
            private_application.backend, args=list(args) if args is not None else None
        )
        return m.Cli.InvocationResult(
            exit_code=result.exit_code, stdout=result.stdout, stderr=result.stderr
        )

    @classmethod
    def framework_exit(cls, code: int = 0) -> None:
        """Exit through Typer only while an adapter-owned execution is active."""
        if cls._active_execution.get():
            raise typer.Exit(code=code)
        raise SystemExit(code)


__all__: list[str] = ["FlextCliUtilitiesFramework"]
