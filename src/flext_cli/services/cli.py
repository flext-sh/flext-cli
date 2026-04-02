"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from collections.abc import Callable, Mapping
from inspect import Parameter, Signature
from types import NoneType, UnionType
from typing import Annotated, Literal, TypeAliasType, Union, get_args, get_origin

import typer
from pydantic import BaseModel
from typer.models import OptionInfo
from typer.testing import CliRunner

from flext_cli import (
    FlextCliCommonParams,
    FlextCliOutput,
    FlextCliServiceBase,
    FlextCliSettings,
    m,
    p,
    t,
)
from flext_core import r


class FlextCliCli(FlextCliServiceBase):
    """Unified Typer abstraction for model-driven CLI applications."""

    _OPTIONAL_UNION_ARG_COUNT = 2

    class _ModelCommand:
        """Callable wrapper with explicit signature for Typer introspection."""

        __annotations__: dict[str, object]
        __name__: str
        __signature__: Signature
        _config: BaseModel | None
        _handler: Callable[[BaseModel], object | None]
        _model_cls: type[BaseModel]

        def __init__(
            self,
            *,
            config: BaseModel | None,
            handler: Callable[[BaseModel], object | None],
            model_cls: type[BaseModel],
            parameters: list[Parameter],
        ) -> None:
            self.__name__ = handler.__name__
            self.__signature__ = Signature(parameters)
            self._config = config
            self._handler = handler
            self._model_cls = model_cls

        def __call__(self, **kwargs: object) -> object | None:
            if self._config is not None:
                for field_name, field_value in kwargs.items():
                    if hasattr(self._config, field_name):
                        setattr(self._config, field_name, field_value)
            return self._handler(self._model_cls.model_validate(kwargs))

    @staticmethod
    def _resolve_typer_annotation(annotation: object) -> object:
        """Resolve runtime annotations to concrete types accepted by Typer."""
        if isinstance(annotation, TypeAliasType):
            return FlextCliCli._resolve_typer_annotation(annotation.__value__)
        origin = get_origin(annotation)
        if origin is Annotated:
            value, *_ = get_args(annotation)
            return FlextCliCli._resolve_typer_annotation(value)
        if origin is Literal:
            return str
        if origin in {Union, UnionType}:
            args = tuple(
                FlextCliCli._resolve_typer_annotation(arg)
                for arg in get_args(annotation)
            )
            if len(args) == FlextCliCli._OPTIONAL_UNION_ARG_COUNT and NoneType in args:
                value = args[0] if args[1] is NoneType else args[1]
                return value if isinstance(value, type) else annotation
        if origin in {list, tuple}:
            return annotation
        if origin in {dict, frozenset, set}:
            return origin
        return annotation

    @staticmethod
    def _field_default(
        field_name: str, field_info: object, config: BaseModel | None
    ) -> object:
        """Resolve CLI default from config first, then from model field metadata."""
        if config is not None and hasattr(config, field_name):
            configured = getattr(config, field_name)
            if configured is not None:
                return configured
        default_factory = getattr(field_info, "default_factory", None)
        if callable(default_factory):
            return default_factory()
        default_value = getattr(field_info, "default", ...)
        return default_value if default_value is not None else None

    @classmethod
    def _build_model_parameter(
        cls,
        field_name: str,
        field_info: object,
        config: BaseModel | None,
    ) -> tuple[Parameter, object]:
        """Build a keyword-only Typer option from a Pydantic field."""
        alias = getattr(field_info, "alias", None)
        cli_name = alias if isinstance(alias, str) and alias else field_name
        option_name = f"--{cli_name.replace('_', '-')}"
        annotation = cls._resolve_typer_annotation(
            getattr(field_info, "annotation", None) or str,
        )
        is_required = bool(getattr(field_info, "is_required", lambda: False)())
        default_value = (
            ... if is_required else cls._field_default(field_name, field_info, config)
        )
        option_decls = [option_name]
        if annotation is bool and isinstance(default_value, bool):
            dashed_name = cli_name.replace("_", "-")
            option_decls = [f"--{dashed_name}/--no-{dashed_name}"]
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
        config: FlextCliSettings,
        *,
        debug: bool,
        log_level: str | None,
        quiet: bool,
        trace: bool,
        verbose: bool,
    ) -> None:
        """Apply global CLI flags to the shared settings model."""
        result = FlextCliCommonParams.apply_to_config(
            config,
            debug=debug,
            log_level=log_level,
            quiet=quiet,
            trace=trace,
            verbose=verbose,
        )
        if result.is_failure:
            self.logger.warning("failed to apply cli params", error=result.error or "")

    def create_app_with_common_params(
        self,
        *,
        name: str,
        help_text: str,
        config: FlextCliSettings | None = None,
        add_completion: bool = True,
    ) -> typer.Typer:
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
            if config is not None:
                self._apply_common_params_to_config(
                    config,
                    debug=debug,
                    log_level=log_level,
                    quiet=quiet,
                    trace=trace,
                    verbose=verbose,
                )

        _ = global_callback
        return app

    @staticmethod
    def add_group(app: typer.Typer, *, name: str, group: typer.Typer) -> None:
        """Attach a subcommand group to an application."""
        app.add_typer(group, name=name)

    @staticmethod
    def create_group(*, help_text: str, name: str | None = None) -> typer.Typer:
        """Create a Typer command group without re-registering global params."""
        return typer.Typer(name=name, help=help_text)

    @classmethod
    def model_command[M: BaseModel](
        cls,
        model_cls: type[M],
        handler: Callable[[M], object | None],
        config: BaseModel | None = None,
    ) -> Callable[..., object | None]:
        """Build a Typer command directly from a Pydantic request model."""
        parameters: list[Parameter] = []
        annotations: dict[str, object] = {"return": None}
        for field_name, field_info in model_cls.model_fields.items():
            parameter, annotation = cls._build_model_parameter(
                field_name,
                field_info,
                config,
            )
            parameters.append(parameter)
            annotations[field_name] = annotation
        command = cls._ModelCommand(
            config=config,
            handler=lambda model: handler(model_cls.model_validate(model)),
            model_cls=model_cls,
            parameters=parameters,
        )
        command.__annotations__ = annotations
        return command

    @classmethod
    def derive_model[M: BaseModel](
        cls,
        model_cls: type[M],
        *sources: BaseModel | Mapping[str, object] | None,
        overrides: Mapping[str, object] | None = None,
    ) -> M:
        """Derive a target Pydantic model from ordered model/mapping sources."""
        merged: dict[str, object] = {}
        for source in sources:
            merged.update(cls._model_source_data(model_cls, source))
        if overrides is not None:
            merged.update(cls._model_source_data(model_cls, overrides))
        return model_cls.model_validate(merged)

    @staticmethod
    def _model_source_data(
        model_cls: type[BaseModel],
        source: BaseModel | Mapping[str, object] | None,
    ) -> dict[str, object]:
        """Extract only target-compatible fields from a model or mapping source."""
        if source is None:
            return {}
        raw_source: Mapping[str, object]
        if isinstance(source, BaseModel):
            raw_source = source.model_dump(exclude_none=True)
        else:
            raw_source = source
        return {
            field_name: raw_source[field_name]
            for field_name in model_cls.model_fields
            if field_name in raw_source and raw_source[field_name] is not None
        }

    @staticmethod
    def create_cli_runner(
        *,
        charset: str = "utf-8",
        env: dict[str, str] | None = None,
        echo_stdin: bool = False,
    ) -> r[CliRunner]:
        """Create a Typer/Click test runner for real CLI execution tests."""
        return r[CliRunner].ok(
            CliRunner(charset=charset, env=env, echo_stdin=echo_stdin),
        )

    @staticmethod
    def execute_app(
        app: typer.Typer,
        *,
        prog_name: str,
        args: t.StrSequence | None = None,
        error_message: p.Cli.ErrorMessageProvider | None = None,
    ) -> r[bool]:
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
        except typer.Abort as exc:
            return r[bool].fail(str(exc) or "CLI execution aborted")
        except typer.Exit as exc:
            if exc.exit_code == 0:
                return r[bool].ok(True)
            message = error_message() if error_message is not None else None
            return r[bool].fail(message or f"CLI exited with code {exc.exit_code}")
        except Exception as exc:
            message = error_message() if error_message is not None else None
            return r[bool].fail(message or str(exc))
        finally:
            sys.argv = original_argv
        if isinstance(result, int) and result != 0:
            message = error_message() if error_message is not None else None
            return r[bool].fail(message or f"CLI exited with code {result}")
        return r[bool].ok(True)

    @staticmethod
    def exit(*, code: int = 0) -> None:
        """Raise a Typer exit through the public CLI facade."""
        raise typer.Exit(code=code)

    @staticmethod
    def register_command(
        app: typer.Typer,
        *,
        name: str,
        help_text: str,
        command: Callable[..., object | None],
    ) -> None:
        """Register a command on the given Typer application."""
        _ = app.command(name, help=help_text)(command)

    @classmethod
    def register_result_command[M: BaseModel, TResult: t.ValueOrModel](
        cls,
        app: typer.Typer,
        *,
        failure_message: str,
        handler: p.Cli.ResultCommandHandler[M, TResult],
        help_text: str,
        model_cls: type[M],
        name: str,
        config: BaseModel | None = None,
        remember_failure: p.Cli.FailureMessageRecorder | None = None,
        success_formatter: p.Cli.SuccessMessageFormatter[TResult] | None = None,
        success_message: str | None = None,
        success_type: str = "success",
    ) -> None:
        """Register a model command that normalizes `r[...]` CLI handling."""

        def execute(params: M) -> None:
            result = handler(params)
            if result.is_failure:
                if remember_failure is not None:
                    remember_failure(result.error, failure_message)
                cls.exit(code=1)
            message = success_message
            if success_formatter is not None:
                message = success_formatter(result.value)
            elif hasattr(result.value, "message"):
                candidate = getattr(result.value, "message")
                if isinstance(candidate, str) and candidate:
                    message = candidate
            if message:
                FlextCliOutput.display_message(message, success_type)

        cls.register_command(
            app,
            name=name,
            help_text=help_text,
            command=cls.model_command(model_cls, execute, config=config),
        )

    @classmethod
    def register_result_route[M: BaseModel, TResult: t.ValueOrModel](
        cls,
        app: typer.Typer,
        *,
        route: m.Cli.ResultCommandRouteModel[M, TResult],
        remember_failure: p.Cli.FailureMessageRecorder | None = None,
    ) -> None:
        """Register a declarative result route model on a Typer app."""
        cls.register_result_command(
            app,
            name=route.name,
            help_text=route.help_text,
            model_cls=route.model_cls,
            handler=route.handler,
            failure_message=route.failure_message,
            remember_failure=remember_failure,
            success_formatter=route.success_formatter,
            success_message=route.success_message,
            success_type=route.success_type,
        )


__all__ = ["FlextCliCli"]
