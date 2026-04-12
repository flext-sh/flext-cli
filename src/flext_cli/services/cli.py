"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from collections.abc import Mapping, MutableSequence, Sequence
from inspect import Parameter, Signature
from pathlib import Path
from types import GenericAlias, NoneType, UnionType
from typing import (
    Annotated,
    Literal,
    TypeAliasType,
    TypeIs,
    Union,
    get_args,
    get_origin,
)

import typer
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from typer.models import OptionInfo
from typer.testing import CliRunner

from flext_cli import (
    FlextCliCommonParams,
    FlextCliOutput,
    FlextCliSettings,
    c,
    m,
    p,
    s,
    t,
)
from flext_core import r


class FlextCliCli(s):
    """Unified Typer abstraction for model-driven CLI applications."""

    class _ModelCommand[M: BaseModel]:
        """Callable wrapper with explicit signature for Typer introspection.

        Note: __annotations__ uses MutableMapping[str, type] because Typer reads
        it via inspect at runtime. __call__ uses t.Scalar kwargs because Typer
        may pass scalar values or repeated option lists.
        """

        __name__: str
        __signature__: Signature
        _config: t.Cli.ConfigModel
        _handler: p.Cli.ModelCommandHandler[M]
        _model_cls: type[M]

        def __init__(
            self,
            *,
            settings: t.Cli.ConfigModel,
            handler: p.Cli.ModelCommandHandler[M],
            model_cls: type[M],
            parameters: Sequence[Parameter],
        ) -> None:
            self.__name__ = getattr(handler, "__name__", model_cls.__name__)
            self.__signature__ = Signature(parameters)
            self._config = settings
            self._handler = handler
            self._model_cls = model_cls

        def __call__(self, **kwargs: t.Cli.CliValue) -> t.Cli.RuntimeValue:
            if self._config is not None:
                for field_name, field_value in kwargs.items():
                    if hasattr(self._config, field_name):
                        setattr(self._config, field_name, field_value)
            model = self._model_cls.model_validate(kwargs)
            return self._handler(model)

    @staticmethod
    def _resolve_typer_annotation(
        annotation: t.Cli.RuntimeAnnotation,
    ) -> type | GenericAlias:
        """Resolve runtime annotations to concrete types accepted by Typer."""
        if isinstance(annotation, TypeAliasType):
            return FlextCliCli._resolve_typer_annotation(annotation.__value__)
        if isinstance(annotation, UnionType):
            args = tuple(
                FlextCliCli._resolve_typer_annotation(arg)
                for arg in get_args(annotation)
            )
            if len(args) == c.Cli.OPTIONAL_UNION_ARG_COUNT and NoneType in args:
                return args[0] if args[1] is NoneType else args[1]
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
            if len(args) == c.Cli.OPTIONAL_UNION_ARG_COUNT and NoneType in args:
                return args[0] if args[1] is NoneType else args[1]
        if origin is Sequence:
            args = get_args(annotation)
            if args:
                value = FlextCliCli._resolve_typer_annotation(args[0])
                if isinstance(value, type):
                    return GenericAlias(list, (value,))
            return list[str]
        if origin in {list, tuple}:
            args = get_args(annotation)
            if args:
                value = FlextCliCli._resolve_typer_annotation(args[0])
                if isinstance(value, type):
                    return GenericAlias(list, (value,))
            return list[str]
        if origin in {dict, frozenset, set}:
            return origin
        if isinstance(annotation, GenericAlias):
            return annotation
        if isinstance(annotation, type):
            return annotation
        return str

    @staticmethod
    def _is_obj_sequence(
        value: object,
    ) -> TypeIs[Sequence[object]]:
        """Safely narrow runtime values to sequence for iteration."""
        return isinstance(value, (list, tuple))

    @staticmethod
    def _is_obj_mapping(
        value: object,
    ) -> TypeIs[Mapping[object, object]]:
        """Safely narrow runtime values to mapping for iteration."""
        return isinstance(value, Mapping)

    @staticmethod
    def _is_string_sequence(value: object) -> TypeIs[t.Cli.StrSequence]:
        """Return True for concrete string sequences accepted by repeated CLI options."""
        if not FlextCliCli._is_obj_sequence(value):
            return False
        return all(isinstance(item, str) for item in value)

    @classmethod
    def _is_cli_default_mapping(
        cls,
        value: Mapping[str, object],
    ) -> TypeIs[t.Cli.DefaultMapping]:
        """Return True when a mapping is a valid Typer default."""
        return all(
            item_value is None
            or isinstance(item_value, c.Cli.CLI_SCALAR_TYPES_TUPLE)
            or cls._is_string_sequence(item_value)
            for item_value in value.values()
        )

    @classmethod
    def _normalize_cli_atom(cls, value: object) -> t.Cli.DefaultAtom:
        """Normalize one runtime value into an allowed Typer scalar or string sequence."""
        if isinstance(value, c.Cli.CLI_SCALAR_TYPES_TUPLE):
            return value
        if isinstance(value, Path):
            return str(value)
        if cls._is_string_sequence(value):
            return tuple(value)
        return None

    @staticmethod
    def _field_default(
        field_name: str,
        field_info: FieldInfo,
        settings: t.Cli.ConfigModel,
    ) -> t.Cli.CliValue:
        """Resolve CLI default from settings first, then from model field metadata."""
        if settings is not None and hasattr(settings, field_name):
            configured = getattr(settings, field_name)
            return FlextCliCli._normalize_cli_default(configured)
        default_factory = getattr(field_info, "default_factory", None)
        if callable(default_factory):
            return FlextCliCli._normalize_cli_default(default_factory())
        default_value = getattr(field_info, "default", None)
        return FlextCliCli._normalize_cli_default(default_value)

    @classmethod
    def _normalize_cli_default(
        cls,
        value: object,
    ) -> t.Cli.CliValue:
        """Normalize field defaults into Typer-compatible scalar/mapping/list values."""
        if value is None:
            return None
        normalized_atom = cls._normalize_cli_atom(value)
        if normalized_atom is not None:
            return normalized_atom
        if cls._is_obj_mapping(value):
            normalized_mapping: t.Cli.MutableDefaultMapping = {}
            for key, item_value in value.items():
                if not isinstance(key, str):
                    continue
                normalized_item = cls._normalize_cli_atom(item_value)
                if normalized_item is not None:
                    normalized_mapping[key] = normalized_item
            if normalized_mapping:
                return normalized_mapping
            return None
        if cls._is_string_sequence(value):
            normalized_sequence: tuple[str, ...] = tuple(value)
            return normalized_sequence
        return None

    @classmethod
    def _build_model_parameter(
        cls,
        field_name: str,
        field_info: FieldInfo,
        settings: t.Cli.ConfigModel,
    ) -> tuple[Parameter, type | GenericAlias]:
        """Build a keyword-only Typer option from a Pydantic field."""
        alias = field_info.alias
        cli_name = alias or field_name
        option_name = f"--{cli_name.replace('_', '-')}"
        annotation = cls._resolve_typer_annotation(
            field_info.annotation or str,
        )
        is_required = bool(field_info.is_required())
        default_value = (
            ... if is_required else cls._field_default(field_name, field_info, settings)
        )
        option_decls = [option_name]
        extra = getattr(field_info, "json_schema_extra", None)
        custom_param_decls: list[str] | None = None
        if cls._is_obj_mapping(extra):
            declared = extra.get("typer_param_decls")
            if cls._is_obj_sequence(declared):
                custom_param_decls = [str(item) for item in declared]
        if annotation is bool and isinstance(default_value, bool):
            dashed_name = cli_name.replace("_", "-")
            option_decls = [f"--{dashed_name}/--no-{dashed_name}"]
        if custom_param_decls is not None:
            option_decls = custom_param_decls
        option = OptionInfo(
            default=default_value,
            param_decls=option_decls,
            help=field_info.description,
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
        result = FlextCliCommonParams.apply_to_config(
            settings,
            debug=debug,
            log_level=log_level,
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
    def model_command[M: BaseModel](
        cls,
        model_cls: type[M],
        handler: p.Cli.ModelCommandHandler[M],
        settings: t.Cli.ConfigModel = None,
    ) -> t.Cli.CliCommand:
        """Build a Typer command directly from a Pydantic request model."""
        parameters: MutableSequence[Parameter] = []
        annotations: t.Cli.CliAnnotations = {"return": type(None)}
        fields: t.Cli.FieldInfoMapping = getattr(model_cls, "model_fields", {})
        for field_name, field_info in fields.items():
            if field_info.exclude is True:
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
    def derive_model[M: BaseModel](
        cls,
        model_cls: type[M],
        *sources: t.Cli.ModelSource,
        overrides: t.Cli.ScalarMapping | None = None,
    ) -> M:
        """Derive a target Pydantic model from ordered model/mapping sources."""
        merged: t.Cli.MutableScalarMapping = {}
        for source in sources:
            merged.update(cls._model_source_data(model_cls, source))
        if overrides is not None:
            merged.update(cls._model_source_data(model_cls, overrides))
        return model_cls.model_validate(merged)

    @staticmethod
    def _model_source_data(
        model_cls: type[BaseModel],
        source: t.Cli.ModelSource,
    ) -> t.Cli.ScalarMapping:
        """Extract only target-compatible fields from a model or mapping source."""
        if source is None:
            return {}
        raw_source: t.Cli.ScalarMapping
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
        charset: str = c.Cli.ENCODING_DEFAULT,
        env: t.Cli.StrEnvMapping | None = None,
        echo_stdin: bool = False,
    ) -> r[t.Cli.TyperRunner]:
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
            return r[bool].fail_op(
                "execute cli app", str(exc) or "CLI execution aborted"
            )
        except typer.Exit as exc:
            if exc.exit_code == 0:
                return r[bool].ok(True)
            message = error_message() if error_message is not None else None
            return r[bool].fail_op(
                "execute cli app",
                message or f"CLI exited with code {exc.exit_code}",
            )
        except Exception as exc:
            message = error_message() if error_message is not None else None
            return r[bool].fail_op("execute cli app", message or str(exc))
        finally:
            sys.argv = original_argv
        if isinstance(result, int) and result != 0:
            message = error_message() if error_message is not None else None
            return r[bool].fail_op(
                "execute cli app",
                message or f"CLI exited with code {result}",
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
    def register_result_command[M: BaseModel, TResult: t.Cli.ResultValue](
        cls,
        app: t.Cli.CliApp,
        *,
        failure_message: str,
        handler: p.Cli.ResultCommandHandler[M, TResult],
        help_text: str,
        model_cls: type[M],
        name: str,
        settings: t.Cli.ConfigModel = None,
        remember_failure: p.Cli.FailureMessageRecorder | None = None,
        success_formatter: p.Cli.SuccessMessageFormatter[TResult] | None = None,
        success_message: str | None = None,
        success_type: c.Cli.MessageTypes | t.Cli.MessageTypeLiteral = (
            c.Cli.MessageTypes.SUCCESS
        ),
    ) -> None:
        """Register a model command that normalizes `r[...]` CLI handling."""
        execute = cls._build_result_executor(
            failure_message=failure_message,
            handler=handler,
            remember_failure=remember_failure,
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
    def _build_result_executor[M: BaseModel, TResult: t.Cli.ResultValue](
        cls,
        *,
        failure_message: str,
        handler: p.Cli.ResultCommandHandler[M, TResult],
        remember_failure: p.Cli.FailureMessageRecorder | None = None,
        success_formatter: p.Cli.SuccessMessageFormatter[TResult] | None = None,
        success_message: str | None = None,
        success_type: c.Cli.MessageTypes | t.Cli.MessageTypeLiteral = (
            c.Cli.MessageTypes.SUCCESS
        ),
    ) -> p.Cli.ModelCommandHandler[M]:
        """Build the shared executor used by single and batched route registration."""

        def _exit_with_failure(error: str | None) -> None:
            if remember_failure is not None:
                remember_failure(error, failure_message)
            FlextCliOutput.display_message(
                error or failure_message,
                c.Cli.MessageTypes.ERROR,
            )
            cls.exit(code=1)

        def execute(params: M) -> None:
            result: r[TResult] = handler(params)
            if result.failure:
                _exit_with_failure(result.error)
            message = success_message
            result_value: TResult = result.value
            if success_formatter is not None:
                message = success_formatter(result_value)
            elif hasattr(result_value, "message"):
                candidate = result_value.message
                if isinstance(candidate, str) and candidate:
                    message = candidate
            elif isinstance(result_value, str) and result_value:
                message = result_value
            if message:
                FlextCliOutput.display_message(message, success_type)

        return execute

    @classmethod
    def _build_result_executor_erased(
        cls,
        *,
        handler: t.Cli.ResultRouteHandler,
        failure_message: str = "",
        remember_failure: p.Cli.FailureMessageRecorder | None = None,
        success_formatter: p.Cli.SuccessMessageFormatter[t.Cli.ResultValue]
        | None = None,
        success_message: str | None = None,
        success_type: c.Cli.MessageTypes | t.Cli.MessageTypeLiteral = (
            c.Cli.MessageTypes.SUCCESS
        ),
    ) -> p.Cli.ModelCommandHandler[BaseModel]:
        """Build a batch executor for type-erased route registration."""

        def _exit_with_failure(error: str | None) -> None:
            if remember_failure is not None:
                remember_failure(error, failure_message)
            FlextCliOutput.display_message(
                error or failure_message,
                c.Cli.MessageTypes.ERROR,
            )
            cls.exit(code=1)

        def execute(params: BaseModel) -> None:
            result_model = handler(params)
            failure = getattr(result_model, "failure", False)
            if failure:
                error_msg = getattr(result_model, "error", None)
                _exit_with_failure(error_msg if isinstance(error_msg, str) else None)
            message = success_message
            result_value = getattr(result_model, "value", None)
            if success_formatter is not None and result_value is not None:
                message = success_formatter(result_value)
            elif hasattr(result_value, "message"):
                candidate = result_value.message
                if isinstance(candidate, str) and candidate:
                    message = candidate
            elif isinstance(result_value, str) and result_value:
                message = result_value
            if message:
                FlextCliOutput.display_message(message, success_type)

        return execute

    @classmethod
    def register_result_route(
        cls,
        app: t.Cli.CliApp,
        *,
        route: m.Cli.ResultCommandRoute,
        remember_failure: p.Cli.FailureMessageRecorder | None = None,
    ) -> None:
        """Register a declarative result route on a Typer app."""
        execute = cls._build_result_executor_erased(
            handler=route.handler,
            remember_failure=remember_failure,
            failure_message=route.failure_message,
            success_formatter=route.success_formatter,
            success_message=route.success_message,
            success_type=route.success_type,
        )
        cls.register_command(
            app,
            name=route.name,
            help_text=route.help_text,
            command=cls.model_command(route.model_cls, execute),
        )

    @classmethod
    def register_result_routes(
        cls,
        app: t.Cli.CliApp,
        routes: Sequence[m.Cli.ResultCommandRoute],
        remember_failure: p.Cli.FailureMessageRecorder | None = None,
    ) -> None:
        """Register multiple heterogeneous result routes in one call."""
        for route in routes:
            cls.register_command(
                app,
                name=route.name,
                help_text=route.help_text,
                command=cls.model_command(
                    route.model_cls,
                    cls._build_result_executor_erased(
                        handler=route.handler,
                        failure_message=route.failure_message,
                        remember_failure=remember_failure,
                        success_formatter=route.success_formatter,
                        success_message=route.success_message,
                        success_type=route.success_type,
                    ),
                ),
            )


__all__: list[str] = ["FlextCliCli"]
