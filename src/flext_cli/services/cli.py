"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from collections.abc import (
    Mapping,
    MutableSequence,
    Sequence,
)
from inspect import Parameter, Signature
from types import GenericAlias
from typing import (
    Annotated,
)

import click
import typer
from typer.models import OptionInfo
from typer.testing import CliRunner

from flext_cli import (
    FlextCliCommonParams,
    FlextCliSettings,
    c,
    m,
    p,
    r,
    s,
    t,
    u,
)


class FlextCliCli(s):
    """Unified Typer abstraction for model-driven CLI applications."""

    class _ModelCommand[M: m.BaseModel]:
        """Callable wrapper with explicit signature for Typer introspection.

        Note: __annotations__ uses MutableMapping[str, type] because Typer reads
        it via inspect at runtime. __call__ uses t.Scalar kwargs because Typer
        may pass scalar values or repeated option lists.
        """

        __name__: str
        __signature__: Signature
        config: m.BaseModel | None
        _handler: p.Cli.ModelCommandHandler[M]
        _model_cls: type[M]

        def __init__(
            self,
            *,
            settings: m.BaseModel | None,
            handler: p.Cli.ModelCommandHandler[M],
            model_cls: type[M],
            parameters: Sequence[Parameter],
        ) -> None:
            self.__name__ = getattr(handler, "__name__", model_cls.__name__)
            self.__signature__ = Signature(parameters)
            self.config = settings
            self._handler = handler
            self._model_cls = model_cls

        def __call__(self, **kwargs: t.Cli.CliValue) -> t.JsonValue:
            if self.config is not None:
                for field_name, field_value in kwargs.items():
                    if hasattr(self.config, field_name):
                        setattr(self.config, field_name, field_value)
            model = self._model_cls.model_validate(kwargs)
            return self._handler(model)

    @classmethod
    def _build_model_parameter(
        cls,
        field_name: str,
        field_info: m.FieldInfo,
        settings: m.BaseModel | None,
    ) -> tuple[Parameter, type | GenericAlias]:
        """Build a keyword-only Typer option from a Pydantic field."""
        alias = getattr(field_info, "alias", None)
        cli_name = alias or field_name
        option_name = f"--{cli_name.replace('_', '-')}"
        annotation = u.Cli.resolve_typer_annotation(
            getattr(field_info, "annotation", None) or str,
        )
        is_required = bool(getattr(field_info, "is_required")())
        default_value = (
            ...
            if is_required
            else u.Cli.field_default(
                field_name,
                field_info,
                settings,
            )
        )
        option_decls = [option_name]
        extra = getattr(field_info, "json_schema_extra", None)
        custom_param_decls: list[str] | None = None
        if isinstance(extra, Mapping):
            declared = extra.get("typer_param_decls")
            if isinstance(declared, Sequence) and not isinstance(declared, str):
                custom_param_decls = [str(item) for item in declared]
        if annotation is bool and isinstance(default_value, bool):
            dashed_name = cli_name.replace("_", "-")
            option_decls = [f"--{dashed_name}/--no-{dashed_name}"]
        if custom_param_decls is not None:
            option_decls = custom_param_decls
        option = OptionInfo(
            default=default_value,
            param_decls=option_decls,
            help=getattr(field_info, "description", None),
        )
        return (
            Parameter(
                field_name,
                kind=Parameter.KEYWORD_ONLY,
                default=option,
                annotation=annotation,
            ),
            annotation,
        )

    def _apply_common_params_to_config(
        self,
        settings: FlextCliSettings,
        *,
        debug: bool,
        log_level: str | None,
        quiet: bool,
        trace: bool,
        verbose: bool,
    ) -> None:
        """Apply global CLI flags to the shared settings model."""
        resolved_log_level: str = (
            log_level if log_level is not None else settings.cli_log_level
        )
        result = FlextCliCommonParams.apply_to_config(
            settings,
            debug=debug,
            log_level=resolved_log_level,
            quiet=quiet,
            trace=trace,
            verbose=verbose,
        )
        if result.failure:
            self.logger.warning("failed to apply cli params", error=result.error or "")

    def create_app_with_common_params(
        self,
        *,
        name: str,
        help_text: str,
        settings: FlextCliSettings | None = None,
        add_completion: bool = True,
    ) -> t.Cli.CliApp:
        """Create a Typer app with the shared global FLEXT CLI parameters."""
        app = typer.Typer(name=name, help=help_text, add_completion=add_completion)

        @app.callback()
        def global_callback(
            *,
            debug: Annotated[bool, FlextCliCommonParams.create_option("debug")] = False,
            trace: Annotated[bool, FlextCliCommonParams.create_option("trace")] = False,
            verbose: Annotated[
                bool, FlextCliCommonParams.create_option("verbose")
            ] = False,
            quiet: Annotated[bool, FlextCliCommonParams.create_option("quiet")] = False,
            log_level: Annotated[
                str | None,
                FlextCliCommonParams.create_option("cli_log_level"),
            ] = None,
        ) -> None:
            if settings is not None:
                self._apply_common_params_to_config(
                    settings,
                    debug=debug,
                    log_level=log_level,
                    quiet=quiet,
                    trace=trace,
                    verbose=verbose,
                )

        _ = global_callback
        return app

    @staticmethod
    def add_group(
        app: t.Cli.CliApp,
        *,
        name: str,
        group: t.Cli.CliApp,
    ) -> None:
        """Attach a subcommand group to an application."""
        app.add_typer(group, name=name)

    @staticmethod
    def create_group(
        *,
        help_text: str,
        name: str | None = None,
    ) -> t.Cli.CliApp:
        """Create a Typer command group without re-registering global params."""
        return typer.Typer(name=name, help=help_text)

    @classmethod
    def model_command[M: m.BaseModel](
        cls,
        model_cls: type[M],
        handler: p.Cli.ModelCommandHandler[M],
        settings: m.BaseModel | None = None,
    ) -> t.Cli.CliCommand:
        """Build a Typer command directly from a Pydantic request model."""
        parameters: MutableSequence[Parameter] = []
        annotations: t.Cli.CliAnnotations = {"return": type(None)}
        fields = getattr(model_cls, "model_fields", {})
        for field_name, field_info in fields.items():
            if getattr(field_info, "exclude", None) is True:
                continue
            parameter, annotation = cls._build_model_parameter(
                field_name,
                field_info,
                settings,
            )
            parameters.append(parameter)
            annotations[field_name] = annotation
        command = cls._ModelCommand(
            settings=settings,
            handler=handler,
            model_cls=model_cls,
            parameters=parameters,
        )
        command.__annotations__ = dict(annotations)
        return command

    @classmethod
    def derive_model[M: m.BaseModel](
        cls,
        model_cls: type[M],
        *sources: t.Cli.ModelSource,
        overrides: t.ScalarMapping | None = None,
    ) -> M:
        """Derive a target Pydantic model from ordered model/mapping sources."""
        merged: t.MutableScalarMapping = {}
        for source in sources:
            merged.update(u.Cli.model_source_data(model_cls, source))
        if overrides is not None:
            merged.update(u.Cli.model_source_data(model_cls, overrides))
        validated: M = model_cls.model_validate(merged)
        return validated

    @staticmethod
    def create_cli_runner(
        *,
        charset: str = c.Cli.ENCODING_DEFAULT,
        env: t.StrMapping | None = None,
        echo_stdin: bool = False,
    ) -> p.Result[t.Cli.TyperRunner]:
        """Create a Typer/Click test runner for real CLI execution tests."""
        runner = CliRunner(
            charset=charset,
            env=dict(env) if env is not None else None,
            echo_stdin=echo_stdin,
        )
        return r[t.Cli.TyperRunner].ok(runner)

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

        try:
            sys.argv = [prog_name, *cli_args]
            result = command.main(
                args=cli_args,
                prog_name=prog_name,
                standalone_mode=False,
            )
        except click.ClickException as exc:
            message = exc.format_message().strip()
            return r[bool].fail_op(
                "execute cli app",
                message,
            )
        except typer.Abort as exc:
            message = u.Cli.normalize_required_text(
                str(exc),
                default=exc.__class__.__name__,
            )
            return r[bool].fail_op(
                "execute cli app",
                message,
            )
        except typer.Exit as exc:
            if exc.exit_code == 0:
                return r[bool].ok(True)
            return r[bool].fail_op(
                "execute cli app",
                f"CLI exited with code {exc.exit_code}",
            )
        except Exception as exc:
            message = u.Cli.normalize_required_text(
                str(exc),
                default=exc.__class__.__name__,
            )
            return r[bool].fail_op(
                "execute cli app",
                message,
            )
        finally:
            sys.argv = original_argv
        if isinstance(result, int) and not isinstance(result, bool) and result != 0:
            return r[bool].fail_op(
                "execute cli app",
                f"CLI exited with code {result}",
            )
        return r[bool].ok(True)

    @staticmethod
    def exit(*, code: int = 0) -> None:
        """Raise a Typer exit through the public CLI facade."""
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

    @classmethod
    def register_result_command[M: m.BaseModel, TResult: t.Cli.ResultValue](
        cls,
        app: t.Cli.CliApp,
        *,
        handler: p.Cli.ResultCommandHandler[M, TResult],
        help_text: str,
        model_cls: type[M],
        name: str,
        settings: m.BaseModel | None = None,
        success_formatter: p.Cli.SuccessMessageFormatter[TResult] | None = None,
        success_message: str | None = None,
        success_type: c.Cli.MessageTypes = c.Cli.MessageTypes.SUCCESS,
    ) -> None:
        """Register a model command that normalizes `r[...]` CLI handling."""
        execute = cls._build_result_executor(
            handler=handler,
            success_formatter=success_formatter,
            success_message=success_message,
            success_type=success_type,
        )
        cls.register_command(
            app,
            name=name,
            help_text=help_text,
            command=cls.model_command(model_cls, execute, settings=settings),
        )

    @classmethod
    def _build_result_executor[M: m.BaseModel, TResult: t.Cli.ResultValue](
        cls,
        *,
        handler: p.Cli.ResultCommandHandler[M, TResult],
        success_formatter: p.Cli.SuccessMessageFormatter[TResult] | None = None,
        success_message: str | None = None,
        success_type: c.Cli.MessageTypes = c.Cli.MessageTypes.SUCCESS,
    ) -> p.Cli.ModelCommandHandler[M]:
        """Build the shared executor used by single and batched route registration."""

        def _exit_with_failure(error: str | None) -> None:
            if error:
                u.Cli.commands_emit_error_message(error)
            cls.exit(code=1)

        def execute(params: M) -> t.JsonValue:
            result: p.Result[TResult] = handler(params)
            if result.failure:
                _exit_with_failure(result.error)
            result_value: TResult = result.value
            message = u.Cli.commands_resolve_success_message(
                result_value=result_value,
                success_message=success_message,
                success_formatter=success_formatter,
            )
            if message:
                u.Cli.commands_emit_success_message(message, success_type)
            return True

        return execute

    @classmethod
    def register_result_route(
        cls,
        app: t.Cli.CliApp,
        *,
        route: m.Cli.ResultCommandRoute,
    ) -> None:
        """Register a declarative result route on a Typer app."""

        def route_execute(params: m.BaseModel) -> p.Result[t.Cli.ResultValue]:
            result = route.handler(params)
            if result.failure:
                return r[t.Cli.ResultValue].fail(result.error or "")
            return r[t.Cli.ResultValue].ok(result.value)

        cls.register_result_command(
            app,
            name=route.name,
            help_text=route.help_text,
            model_cls=route.model_cls,
            handler=route_execute,
            success_message=route.success_message,
            success_formatter=route.success_formatter,
            success_type=route.success_type,
        )

    @classmethod
    def register_result_routes(
        cls,
        app: t.Cli.CliApp,
        routes: Sequence[m.Cli.ResultCommandRoute],
    ) -> None:
        """Register multiple heterogeneous result routes in one call."""
        for route in routes:
            cls.register_result_route(app, route=route)


__all__: list[str] = ["FlextCliCli"]
