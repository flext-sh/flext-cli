"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from collections.abc import Callable, Mapping, MutableMapping, MutableSequence, Sequence
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
    FlextCliServiceBase,
    FlextCliSettings,
    c,
    m,
    p,
    t,
)
from flext_core import r


class FlextCliCli(FlextCliServiceBase):
    """Unified Typer abstraction for model-driven CLI applications."""

    class _ModelCommand[M: BaseModel]:
        """Callable wrapper with explicit signature for Typer introspection.

        Note: __annotations__ uses MutableMapping[str, type] because Typer reads
        it via inspect at runtime. __call__ uses t.Scalar kwargs because Typer
        may pass scalar values or repeated option lists.
        """

        __name__: str
        __signature__: Signature
        _config: BaseModel | None
        _handler: Callable[[M], None]
        _model_cls: type[M]

        def __init__(
            self,
            *,
            config: BaseModel | None,
            handler: Callable[[M], None],
            model_cls: type[M],
            parameters: Sequence[Parameter],
        ) -> None:
            self.__name__ = handler.__name__
            self.__signature__ = Signature(parameters)
            self._config = config
            self._handler = handler
            self._model_cls = model_cls

        def __call__(self, **kwargs: t.Cli.CliValue) -> None:
            if self._config is not None:
                for field_name, field_value in kwargs.items():
                    if hasattr(self._config, field_name):
                        setattr(self._config, field_name, field_value)
            model = self._model_cls.model_validate(kwargs)
            self._handler(model)

    @staticmethod
    def _resolve_typer_annotation(annotation: object) -> type | GenericAlias:
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
    def _is_obj_sequence(value: object) -> TypeIs[Sequence[object]]:
        """Safely narrow objects to sequence for iteration without Unknown types."""
        return isinstance(value, (list, tuple))

    @staticmethod
    def _is_obj_mapping(value: object) -> TypeIs[Mapping[object, object]]:
        """Safely narrow objects to mapping for iteration without Unknown types."""
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
    def _normalize_cli_atom(
        cls, value: object
    ) -> t.Cli.Scalar | t.Cli.StrSequence | None:
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
        field_name: str, field_info: FieldInfo, config: BaseModel | None
    ) -> t.Cli.CliValue:
        """Resolve CLI default from config first, then from model field metadata."""
        if config is not None and hasattr(config, field_name):
            configured = getattr(config, field_name)
            return FlextCliCli._normalize_cli_default(configured)
        default_factory = getattr(field_info, "default_factory", None)
        if callable(default_factory):
            factory_result: object = default_factory()
            if factory_result is None:
                return None
            normalized_atom = FlextCliCli._normalize_cli_atom(factory_result)
            if normalized_atom is not None:
                return normalized_atom
            if FlextCliCli._is_obj_mapping(factory_result):
                normalized_mapping: dict[str, t.Cli.Scalar | t.Cli.StrSequence] = {}
                for key, item_value in factory_result.items():
                    if not isinstance(key, str):
                        continue
                    normalized_item = FlextCliCli._normalize_cli_atom(item_value)
                    if normalized_item is not None:
                        normalized_mapping[key] = normalized_item
                if normalized_mapping:
                    return normalized_mapping
                return None
            if FlextCliCli._is_obj_sequence(
                factory_result
            ) and FlextCliCli._is_string_sequence(factory_result):
                normalized_sequence: tuple[str, ...] = tuple(factory_result)
                return normalized_sequence
            return None
        default_value = getattr(field_info, "default", None)
        return FlextCliCli._normalize_cli_default(default_value)

    @classmethod
    def _normalize_cli_default(
        cls,
        value: object | None,
    ) -> t.Cli.CliValue:
        """Normalize field defaults into Typer-compatible scalar/mapping/list values."""
        if value is None:
            return None
        normalized_atom = cls._normalize_cli_atom(value)
        if normalized_atom is not None:
            return normalized_atom
        if cls._is_obj_mapping(value):
            normalized_mapping: dict[str, t.Cli.Scalar | t.Cli.StrSequence] = {}
            for key, item_value in value.items():
                if not isinstance(key, str):
                    continue
                normalized_item = cls._normalize_cli_atom(item_value)
                if normalized_item is not None:
                    normalized_mapping[key] = normalized_item
            if normalized_mapping:
                return normalized_mapping
            return None
        if cls._is_obj_sequence(value) and cls._is_string_sequence(value):
            normalized_sequence: tuple[str, ...] = tuple(value)
            return normalized_sequence
        return None

    @classmethod
    def _build_model_parameter(
        cls,
        field_name: str,
        field_info: FieldInfo,
        config: BaseModel | None,
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
            ... if is_required else cls._field_default(field_name, field_info, config)
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
    ) -> t.Cli.TyperApp:
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
    def add_group(
        app: t.Cli.TyperApp,
        *,
        name: str,
        group: t.Cli.TyperApp,
    ) -> None:
        """Attach a subcommand group to an application."""
        app.add_typer(group, name=name)

    @staticmethod
    def create_group(
        *,
        help_text: str,
        name: str | None = None,
    ) -> t.Cli.TyperApp:
        """Create a Typer command group without re-registering global params."""
        return typer.Typer(name=name, help=help_text)

    @classmethod
    def model_command[M: BaseModel](
        cls,
        model_cls: type[M],
        handler: Callable[[M], None],
        config: BaseModel | None = None,
    ) -> Callable[..., None]:
        """Build a Typer command directly from a Pydantic request model."""
        parameters: MutableSequence[Parameter] = []
        annotations: t.Cli.TyperAnnotations = {"return": type(None)}
        fields: t.Cli.FieldInfoMapping = getattr(model_cls, "model_fields", {})
        for field_name, field_info in fields.items():
            if field_info.exclude is True:
                continue
            parameter, annotation = cls._build_model_parameter(
                field_name,
                field_info,
                config,
            )
            parameters.append(parameter)
            annotations[field_name] = annotation
        command = cls._ModelCommand(
            config=config,
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
        *sources: BaseModel | Mapping[str, t.Cli.Scalar] | None,
        overrides: Mapping[str, t.Cli.Scalar] | None = None,
    ) -> M:
        """Derive a target Pydantic model from ordered model/mapping sources."""
        merged: MutableMapping[str, t.Cli.Scalar] = {}
        for source in sources:
            merged.update(cls._model_source_data(model_cls, source))
        if overrides is not None:
            merged.update(cls._model_source_data(model_cls, overrides))
        return model_cls.model_validate(merged)

    @staticmethod
    def _model_source_data(
        model_cls: type[BaseModel],
        source: BaseModel | Mapping[str, t.Cli.Scalar] | None,
    ) -> Mapping[str, t.Cli.Scalar]:
        """Extract only target-compatible fields from a model or mapping source."""
        if source is None:
            return {}
        raw_source: Mapping[str, t.Cli.Scalar]
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
        charset: str = c.Cli.Encoding.DEFAULT,
        env: Mapping[str, str] | None = None,
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
        app: t.Cli.TyperApp,
        *,
        prog_name: str,
        args: Sequence[str] | None = None,
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
        app: t.Cli.TyperApp,
        *,
        name: str,
        help_text: str,
        command: Callable[..., None],
    ) -> None:
        """Register a command on the given Typer application."""
        _ = app.command(name, help=help_text)(command)

    @classmethod
    def register_result_command[M: BaseModel, TResult: t.Cli.ValueOrModel](
        cls,
        app: t.Cli.TyperApp,
        *,
        failure_message: str,
        handler: p.Cli.ResultCommandHandler[M, TResult],
        help_text: str,
        model_cls: type[M],
        name: str,
        config: BaseModel | None = None,
        remember_failure: p.Cli.FailureMessageRecorder | None = None,
        success_formatter: Callable[..., str] | None = None,
        success_message: str | None = None,
        success_type: str = "success",
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
            command=cls.model_command(model_cls, execute, config=config),
        )

    @classmethod
    def _build_result_executor[M: BaseModel, TResult: t.Cli.ValueOrModel](
        cls,
        *,
        failure_message: str,
        handler: p.Cli.ResultCommandHandler[M, TResult],
        remember_failure: p.Cli.FailureMessageRecorder | None = None,
        success_formatter: Callable[..., str] | None = None,
        success_message: str | None = None,
        success_type: str = "success",
    ) -> Callable[[M], None]:
        """Build the shared executor used by single and batched route registration."""

        def execute(params: M) -> None:
            result: r[TResult] = handler(params)
            if result.is_failure:
                if remember_failure is not None:
                    remember_failure(result.error, failure_message)
                cls.exit(code=1)
            message = success_message
            result_value: TResult = result.value
            if success_formatter is not None:
                message = success_formatter(result_value)
            elif hasattr(result_value, "message"):
                candidate = getattr(result_value, "message")
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
        handler: Callable[..., BaseModel],
        failure_message: str = "",
        remember_failure: p.Cli.FailureMessageRecorder | None = None,
        success_formatter: Callable[..., str] | None = None,
        success_message: str | None = None,
        success_type: str = "success",
    ) -> Callable[[BaseModel], None]:
        """Build a batch executor for type-erased route registration.

        The handler field is typed as ``Callable[..., BaseModel]`` for
        variance compatibility — all ``r[T]`` inherit from ``BaseModel``.
        At runtime, the return is always a ``FlextResult``.
        """

        def execute(params: BaseModel) -> None:
            result_model = handler(params)
            is_failure = getattr(result_model, "is_failure", False)
            if is_failure:
                error_msg = getattr(result_model, "error", None)
                if remember_failure is not None:
                    remember_failure(error_msg, failure_message)
                cls.exit(code=1)
            message = success_message
            result_value = getattr(result_model, "value", None)
            if success_formatter is not None and result_value is not None:
                message = success_formatter(result_value)
            elif hasattr(result_value, "message"):
                candidate = getattr(result_value, "message")
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
        app: t.Cli.TyperApp,
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
        app: t.Cli.TyperApp,
        routes: Sequence[m.Cli.ResultCommandRoute],
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
                        success_formatter=route.success_formatter,
                        success_message=route.success_message,
                        success_type=route.success_type,
                    ),
                ),
            )


__all__ = ["FlextCliCli"]
