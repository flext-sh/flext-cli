"""FLEXT CLI - Typer/Click Abstraction Layer.

This is the ONLY file in the entire FLEXT ecosystem allowed to import Typer/Click.
All CLI framework functionality is exposed through this unified interface.

Implementation: Uses Typer as the backend framework. Since Typer is built on Click,
it generates Click-compatible commands internally, ensuring backward compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import logging
import shutil
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import IO, Annotated, ClassVar, Literal, overload

import click
import typer
from click.exceptions import UsageError
from flext_core import FlextContainer, FlextLogger, FlextRuntime, r
from pydantic import BaseModel, TypeAdapter, ValidationError
from rich.errors import ConsoleError, LiveError, StyleError
from typer import Typer
from typer.testing import CliRunner

from flext_cli.cli_params import FlextCliCommonParams
from flext_cli.constants import c
from flext_cli.models import m
from flext_cli.protocols import p
from flext_cli.settings import FlextCliSettings
from flext_cli.typings import t
from flext_cli.utilities import u


class FlextCliCli:
    """Unified Typer/Click abstraction used by the FLEXT ecosystem."""

    container: FlextContainer
    logger: FlextLogger
    _json_value_adapter: ClassVar[TypeAdapter[t.JsonValue]] = TypeAdapter(t.JsonValue)

    def __init__(self) -> None:
        """Initialize FlextCliCli."""
        super().__init__()
        self.container = FlextContainer.get_global()
        self.logger = FlextLogger(__name__)

    def _create_command_cli_decorator(
        self, name: str | None, help_text: str | None
    ) -> Callable[[p.Cli.CliCommandFunction], click.Command]:
        decorator = click.command(name=name, help=help_text)
        self.logger.debug(
            "Created command decorator",
            extra={"command_name": name, "help": help_text},
        )
        return decorator

    def _create_group_cli_decorator(
        self, name: str | None, help_text: str | None
    ) -> Callable[[p.Cli.CliCommandFunction], click.Group]:
        decorator = click.group(name=name, help=help_text)
        self.logger.debug(
            "Created group decorator",
            extra={"group_name": name, "help": help_text},
        )
        return decorator

    def _create_cli_decorator(
        self,
        kind: Literal["command", "group"],
        name: str | None,
        help_text: str | None,
    ) -> Callable[[p.Cli.CliCommandFunction], click.Command | click.Group]:
        if kind == "group":
            return self._create_group_cli_decorator(name, help_text)
        return self._create_command_cli_decorator(name, help_text)

    def create_command_decorator(
        self, name: str | None = None, help_text: str | None = None
    ) -> Callable[[p.Cli.CliCommandFunction], click.Command]:
        """Create a command decorator."""
        return self._create_command_cli_decorator(name, help_text)

    @overload
    def _extract_typed_value(
        self,
        val: t.JsonValue | None,
        type_name: Literal["str"],
        default: str | None = None,
    ) -> str | None: ...

    @overload
    def _extract_typed_value(
        self,
        val: t.JsonValue | None,
        type_name: Literal["bool"],
        *,
        default: bool | None = None,
    ) -> bool | None: ...

    @overload
    def _extract_typed_value(
        self,
        val: t.JsonValue | None,
        type_name: Literal["dict"],
        default: t.JsonValue | None = None,
    ) -> t.JsonValue | None: ...

    def _extract_typed_value(
        self,
        val: t.JsonValue | None,
        type_name: str,
        default: t.JsonValue | None = None,
    ) -> t.JsonValue | None:
        if type_name not in {"str", "bool", "dict"}:
            return default
        if type_name == "str":
            return m.Cli.TypedExtract(
                type_kind="str", value=val, default=default
            ).resolve()
        if type_name == "bool":
            return m.Cli.TypedExtract(
                type_kind="bool", value=val, default=default
            ).resolve()
        return m.Cli.TypedExtract(
            type_kind="dict", value=val, default=default
        ).resolve()

    def _get_log_level_value(self, config: FlextCliSettings) -> int:
        if config.debug or config.trace:
            return logging.DEBUG
        log_level_attr = getattr(config, "cli_log_level", None) or getattr(
            config, "log_level", None
        )
        level_str: str = str(
            m.Cli.LogLevelResolved(
                raw=log_level_attr.value
                if log_level_attr and hasattr(log_level_attr, "value")
                else str(log_level_attr)
                if log_level_attr
                else None,
            ).resolve()
        )
        return getattr(logging, level_str, logging.INFO)

    def _get_console_enabled(self, config: FlextCliSettings) -> bool:
        return (
            True
            if getattr(config, "console_enabled", None) is None
            else bool(getattr(config, "console_enabled", None))
        )

    def _apply_common_params_to_config(
        self,
        config: FlextCliSettings,
        *,
        debug: bool = False,
        trace: bool = False,
        verbose: bool = False,
        quiet: bool = False,
        log_level: str | None = None,
    ) -> None:
        common_params: dict[str, t.JsonValue] = {
            "debug": debug,
            "trace": trace,
            "verbose": verbose,
            "quiet": quiet,
            "log_level": log_level,
        }
        active_params = u.filter_dict(
            common_params, lambda _k, v: v is not None and v is not False
        )
        if not active_params:
            return
        config_fields = set(type(config).model_fields.keys())
        filtered_params = u.filter_dict(active_params, lambda k, _v: k in config_fields)
        if not filtered_params:
            return

        def get_bool(k: str) -> bool | None:
            value = u.get(filtered_params, k)
            if value is None or not value:
                return None
            typed_value = self._extract_typed_value(str(value), "bool")
            if typed_value is None:
                return None
            return bool(typed_value)

        def get_str(k: str) -> str | None:
            value = u.get(filtered_params, k)
            if value is None or not value:
                return None
            typed_value = self._extract_typed_value(str(value), "str")
            if typed_value is None:
                return None
            return str(typed_value)

        result = FlextCliCommonParams.apply_to_config(
            config,
            verbose=get_bool("verbose"),
            quiet=get_bool("quiet"),
            debug=get_bool("debug"),
            trace=get_bool("trace"),
            log_level=get_str("log_level"),
        )
        if result.is_failure:
            logger = FlextLogger.create_module_logger("flext_cli.cli")
            logger.warning(f"Failed to apply CLI params: {result.error}")
            return
        reconfigure_method = getattr(FlextRuntime, "reconfigure_structlog", None)
        if reconfigure_method is not None:
            _ = reconfigure_method(
                log_level=self._get_log_level_value(config),
                console_renderer=self._get_console_enabled(config),
            )

    def create_app_with_common_params(
        self,
        name: str,
        help_text: str,
        config: FlextCliSettings | None = None,
        *,
        add_completion: bool = True,
    ) -> typer.Typer:
        """Create a Typer app with common parameters."""
        app = typer.Typer(name=name, help=help_text, add_completion=add_completion)

        @app.callback()
        def global_callback(
            *,
            debug: Annotated[
                bool, typer.Option("--debug/--no-debug", help="Enable debug mode")
            ] = False,
            trace: Annotated[
                bool, typer.Option("--trace/--no-trace", help="Enable trace mode")
            ] = False,
            verbose: Annotated[
                bool, typer.Option("--verbose/--no-verbose", help="Enable verbose mode")
            ] = False,
            quiet: Annotated[
                bool, typer.Option("--quiet/--no-quiet", help="Enable quiet mode")
            ] = False,
            log_level: Annotated[
                str | None,
                typer.Option(
                    "--log-level",
                    "-L",
                    help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
                    case_sensitive=False,
                ),
            ] = None,
        ) -> None:
            if config:
                self._apply_common_params_to_config(
                    config,
                    debug=debug,
                    trace=trace,
                    verbose=verbose,
                    quiet=quiet,
                    log_level=log_level,
                )

        self.logger.debug(
            "Created Typer app with global common params",
            extra={"app_name": name, "has_config": config is not None},
        )
        _ = global_callback
        return app

    def create_group_decorator(
        self, name: str | None = None, help_text: str | None = None
    ) -> Callable[[p.Cli.CliCommandFunction], click.Command | click.Group]:
        """Create a group decorator."""
        raw_decorator = self._create_cli_decorator("group", name, help_text)
        strict_group_decorator = self._create_group_cli_decorator(name, help_text)

        def typed_group_decorator(
            func: p.Cli.CliCommandFunction,
        ) -> click.Command | click.Group:
            command_obj = raw_decorator(func)
            if not isinstance(command_obj, click.Group):
                msg = "Group decorator must return a click.Group"
                raise TypeError(msg)
            return strict_group_decorator(func)

        return typed_group_decorator

    def _build_bool_value(
        self, kwargs: Mapping[str, t.JsonValue], key: str, *, default: bool = False
    ) -> bool:
        result = self._build_typed_value(kwargs, key, "bool", default)
        if not isinstance(result, bool):
            msg = f"{key} must resolve to bool"
            raise TypeError(msg)
        return result

    def _build_str_value(
        self, kwargs: Mapping[str, t.JsonValue], key: str, default: str = ""
    ) -> str:
        result = self._build_typed_value(kwargs, key, "str", default)
        if not isinstance(result, str):
            msg = f"{key} must resolve to str"
            raise TypeError(msg)
        return result

    def _build_typed_value(
        self,
        kwargs: Mapping[str, t.JsonValue],
        key: str,
        type_name: Literal["bool", "str"],
        default: t.JsonValue,
    ) -> t.JsonValue:
        val = u.get(kwargs, key)
        if val is None or not val:
            return default
        if type_name == "bool":
            bool_default = u.Parser.convert(default, bool, False)
            built_bool = u.build(
                val,
                ops={"ensure": "bool", "ensure_default": bool_default},
            )
            if isinstance(built_bool, bool):
                return built_bool
            msg = f"{key} must resolve to bool"
            raise TypeError(msg)
        str_default = u.Parser.convert(default, str, "")
        built_str = u.build(
            val,
            ops={"ensure": "str", "ensure_default": str_default},
        )
        if isinstance(built_str, str):
            return built_str
        msg = f"{key} must resolve to str"
        raise TypeError(msg)

    @classmethod
    def _to_json_value(cls, value: object) -> t.JsonValue:
        try:
            return cls._json_value_adapter.validate_python(value)
        except ValidationError as exc:
            logging.getLogger(__name__).debug(
                "_to_json_value validation fallback: %s",
                exc,
                exc_info=False,
            )
            return str(value)

    def _normalize_type_hint(
        self, type_hint_val: t.JsonValue | None
    ) -> t.JsonValue | None:
        type_hint_build = u.build(type_hint_val, ops={"ensure_default": None})
        match type_hint_build:
            case None | "":
                return None
            case _:
                return self._to_json_value(type_hint_build)

    def _build_option_config_from_kwargs(
        self, kwargs: Mapping[str, t.JsonValue]
    ) -> m.Cli.OptionConfig:
        default_raw = u.get(kwargs, "default")
        default_value = (
            self._to_json_value(default_raw) if default_raw is not None else None
        )
        type_hint_raw = u.get(kwargs, "type_hint")
        type_hint_value = (
            self._to_json_value(type_hint_raw) if type_hint_raw is not None else None
        )
        return m.Cli.OptionConfig(
            default=default_value,
            type_hint=self._normalize_type_hint(type_hint_value),
            required=bool(self._build_typed_value(kwargs, "required", "bool", False)),
            help_text=str(self._build_typed_value(kwargs, "help_text", "str", "")),
            multiple=bool(self._build_typed_value(kwargs, "multiple", "bool", False)),
            count=bool(self._build_typed_value(kwargs, "count", "bool", False)),
            show_default=bool(
                self._build_typed_value(kwargs, "show_default", "bool", False)
            ),
        )

    def create_option_decorator(
        self,
        *param_decls: str,
        config: m.Cli.OptionConfig | None = None,
        **kwargs: t.JsonValue,
    ) -> Callable[[p.Cli.CliCommandFunction], p.Cli.CliCommandFunction]:
        """Create an option decorator."""
        if config is None:
            config_instance = self._build_option_config_from_kwargs(kwargs)
            config = config_instance
        decorator = click.option(
            *param_decls,
            default=getattr(config, "default", None),
            type=getattr(config, "type_hint", None),
            required=getattr(config, "required", False),
            help=getattr(config, "help_text", ""),
            multiple=getattr(config, "multiple", False),
            count=getattr(config, "count", False),
            show_default=getattr(config, "show_default", True),
        )
        self.logger.debug(
            "Created option decorator",
            extra={
                "param_decls": param_decls,
                "required": getattr(config, "required", False),
            },
        )
        return decorator

    def create_argument_decorator(
        self,
        *param_decls: str,
        type_hint: click.ParamType | type | None = None,
        required: bool = True,
        nargs: int = 1,
    ) -> Callable[[p.Cli.CliCommandFunction], p.Cli.CliCommandFunction]:
        """Create an argument decorator."""
        decorator = click.argument(
            *param_decls, type=type_hint, required=required, nargs=nargs
        )
        self.logger.debug(
            "Created argument decorator",
            extra={"param_decls": param_decls, "required": required},
        )
        return decorator

    @staticmethod
    def _datetime_type(formats: Sequence[str] | None = None) -> click.DateTime:
        formats_values = u.build(
            formats,
            ops={
                "ensure": "list",
                "ensure_default": c.Cli.FileDefaults.DEFAULT_DATETIME_FORMATS,
            },
        )
        if not isinstance(formats_values, Sequence) or isinstance(formats_values, str):
            msg = "datetime formats must resolve to a sequence"
            raise TypeError(msg)
        return click.DateTime(formats=[str(fmt) for fmt in formats_values])

    @classmethod
    def _tuple_type(
        cls, tuple_types: Sequence[click.ParamType | type] | None = None
    ) -> click.Tuple:
        if tuple_types is None:
            return click.Tuple([])
        return click.Tuple(list(tuple_types))

    @classmethod
    def type_factory(
        cls,
        type_name: str,
        *,
        formats: Sequence[str] | None = None,
        tuple_types: Sequence[click.ParamType | type] | None = None,
    ) -> (
        type[bool | str | int | float] | click.DateTime | click.ParamType | click.Tuple
    ):
        """Create a click type from a string name."""
        if type_name == "datetime":
            return cls._datetime_type(formats)
        if type_name == "tuple":
            if tuple_types is None:
                return click.Tuple([])
            tuple_values = list(tuple_types)
            return click.Tuple(tuple_values)
        registry: dict[
            str,
            Callable[
                [],
                type[bool | str | int | float] | click.ParamType,
            ],
        ] = {
            "uuid": lambda: click.UUID,
            "bool": lambda: bool,
            "string": lambda: str,
            "int": lambda: int,
            "float": lambda: float,
        }
        factory = registry.get(type_name)
        if factory is None:
            msg = f"Unsupported type factory: {type_name}"
            raise ValueError(msg)
        return factory()

    @classmethod
    def get_datetime_type(cls, formats: Sequence[str] | None = None) -> click.DateTime:
        """Get datetime type."""
        result: (
            type[bool | str | int | float]
            | click.DateTime
            | click.ParamType
            | click.Tuple
        ) = cls.type_factory("datetime", formats=formats)
        if not isinstance(result, click.DateTime):
            msg = "datetime type factory returned invalid type"
            raise TypeError(msg)
        return cls._datetime_type(formats)

    @classmethod
    def get_uuid_type(cls) -> click.ParamType:
        """Get UUID type."""
        result: (
            type[bool | str | int | float]
            | click.DateTime
            | click.ParamType
            | click.Tuple
        ) = cls.type_factory("uuid")
        if not isinstance(result, click.ParamType):
            msg = "uuid type factory returned invalid type"
            raise TypeError(msg)
        return click.UUID

    @classmethod
    def get_tuple_type(
        cls, types: Sequence[type[t.JsonValue] | click.ParamType]
    ) -> click.Tuple:
        """Get tuple type."""
        result: (
            type[bool | str | int | float]
            | click.DateTime
            | click.ParamType
            | click.Tuple
        ) = cls.type_factory("tuple", tuple_types=types)
        if not isinstance(result, click.Tuple):
            msg = "tuple type factory returned invalid type"
            raise TypeError(msg)
        return cls._tuple_type(types)

    @classmethod
    def get_bool_type(cls) -> type[bool]:
        """Get boolean type."""
        return bool

    @classmethod
    def get_string_type(cls) -> type[str]:
        """Get string type."""
        return str

    @classmethod
    def get_int_type(cls) -> type[int]:
        """Get integer type."""
        return int

    @classmethod
    def get_float_type(cls) -> type[float]:
        """Get float type."""
        return float

    @staticmethod
    def get_current_context() -> click.Context | None:
        """Get current click context."""
        return click.get_current_context(silent=True)

    @staticmethod
    def create_pass_context_decorator() -> Callable[
        [Callable[[click.Context], t.JsonValue]],
        Callable[[click.Context], t.JsonValue],
    ]:
        """Create pass context decorator."""

        def pass_context_wrapper(
            func: Callable[[click.Context], t.JsonValue],
        ) -> Callable[[click.Context], t.JsonValue]:
            decorated = click.pass_context(func)

            def typed_decorated(_ctx: click.Context) -> t.JsonValue:
                return decorated()

            return typed_decorated

        return pass_context_wrapper

    @staticmethod
    def echo(
        message: str | None = None,
        file: IO[str] | None = None,
        *,
        nl: bool = True,
        err: bool = False,
        color: bool | None = None,
    ) -> r[bool]:
        """Echo message to stdout or stderr."""
        typer.echo(message=message, file=file, nl=nl, err=err, color=color)
        return r[bool].ok(value=True)

    @staticmethod
    def _build_config_getters(
        kwargs: Mapping[str, t.JsonValue],
    ) -> tuple[Callable[..., bool], Callable[..., str]]:
        def get_bool_val(k: str, *, default: bool = False) -> bool:
            val = u.get(kwargs, k)
            if val is None or not val:
                return default
            built = u.build(
                val,
                ops={"ensure": "bool", "ensure_default": default},
            )
            if not isinstance(built, bool):
                msg = f"{k} must resolve to bool"
                raise TypeError(msg)
            return built

        def get_str_val(k: str, default: str = "") -> str:
            val = u.get(kwargs, k)
            if val is None or not val:
                return default
            built = u.build(
                val,
                ops={"ensure": "str", "ensure_default": default},
            )
            if not isinstance(built, str):
                msg = f"{k} must resolve to str"
                raise TypeError(msg)
            return built

        return (get_bool_val, get_str_val)

    @staticmethod
    def _build_confirm_config(
        kwargs: Mapping[str, t.JsonValue] | m.Cli.ConfirmConfig,
    ) -> m.Cli.ConfirmConfig:
        if isinstance(kwargs, m.Cli.ConfirmConfig):
            return kwargs
        get_bool_val, get_str_val = FlextCliCli._build_config_getters(kwargs)
        return m.Cli.ConfirmConfig(
            default=get_bool_val("default", default=False),
            abort=get_bool_val("abort", default=False),
            prompt_suffix=get_str_val(
                "prompt_suffix", c.Cli.UIDefaults.DEFAULT_PROMPT_SUFFIX
            ),
            show_default=get_bool_val("show_default", default=True),
            err=get_bool_val("err", default=False),
        )

    @staticmethod
    def _build_prompt_config(
        kwargs: Mapping[str, t.JsonValue] | m.Cli.PromptConfig,
    ) -> m.Cli.PromptConfig:
        if isinstance(kwargs, m.Cli.PromptConfig):
            return kwargs
        get_bool_val, get_str_val = FlextCliCli._build_config_getters(kwargs)
        value_proc_val = u.get(kwargs, "value_proc")
        default_raw = u.get(kwargs, "default")
        type_hint_raw = u.get(kwargs, "type_hint")
        default_value = (
            FlextCliCli._to_json_value(default_raw) if default_raw is not None else None
        )
        type_hint_value = (
            FlextCliCli._to_json_value(type_hint_raw)
            if type_hint_raw is not None
            else None
        )
        return m.Cli.PromptConfig(
            default=default_value,
            type_hint=type_hint_value,
            value_proc=value_proc_val if callable(value_proc_val) else None,
            prompt_suffix=get_str_val(
                "prompt_suffix", c.Cli.UIDefaults.DEFAULT_PROMPT_SUFFIX
            ),
            hide_input=get_bool_val("hide_input", default=False),
            confirmation_prompt=get_bool_val("confirmation_prompt", default=False),
            show_default=get_bool_val("show_default", default=True),
            err=get_bool_val("err", default=False),
            show_choices=get_bool_val("show_choices", default=True),
        )

    @staticmethod
    def _build_confirm_config_from_kwargs(
        kwargs: Mapping[str, t.JsonValue],
    ) -> m.Cli.ConfirmConfig:
        config = FlextCliCli._build_prompt_or_confirm_config("confirm", kwargs)
        if not isinstance(config, m.Cli.ConfirmConfig):
            msg = "confirm config builder returned invalid type"
            raise TypeError(msg)
        return config

    @staticmethod
    def _build_prompt_or_confirm_config(
        kind: Literal["confirm", "prompt"],
        kwargs: Mapping[str, t.JsonValue],
    ) -> m.Cli.ConfirmConfig | m.Cli.PromptConfig:
        if kind == "confirm":
            return FlextCliCli._build_confirm_config(kwargs)
        return FlextCliCli._build_prompt_config(kwargs)

    @staticmethod
    def confirm(
        text: str,
        config: p.Cli.ConfirmConfigProtocol | None = None,
        **kwargs: bool | str,
    ) -> r[bool]:
        """Confirm action with user."""
        if config is None:
            kwargs_typed: dict[str, t.JsonValue] = dict(kwargs)
            config = FlextCliCli._build_confirm_config_from_kwargs(kwargs_typed)
        if not hasattr(config, "default"):
            msg = "confirm config must implement ConfirmConfigProtocol"
            raise TypeError(msg)
        try:
            result = typer.confirm(
                text=text,
                default=getattr(config, "default", None),
                abort=getattr(config, "abort", False),
                prompt_suffix=getattr(config, "prompt_suffix", ""),
                show_default=getattr(config, "show_default", True),
                err=getattr(config, "err", False),
            )
            return r[bool].ok(result)
        except typer.Abort as e:
            return r[bool].fail(
                c.Cli.ErrorMessages.USER_ABORTED_CONFIRMATION.format(error=e)
            )

    @staticmethod
    def _build_prompt_config_from_kwargs(
        kwargs: Mapping[str, t.JsonValue],
    ) -> m.Cli.PromptConfig:
        config = FlextCliCli._build_prompt_or_confirm_config("prompt", kwargs)
        if not isinstance(config, m.Cli.PromptConfig):
            msg = "prompt config builder returned invalid type"
            raise TypeError(msg)
        return config

    @staticmethod
    def prompt(
        text: str,
        config: m.Cli.PromptConfig | None = None,
        **kwargs: t.JsonValue,
    ) -> r[t.JsonValue]:
        """Prompt user for input."""
        if config is None:
            config = FlextCliCli._build_prompt_config_from_kwargs(kwargs)
        required_attrs = (
            "default",
            "hide_input",
            "confirmation_prompt",
            "type_hint",
            "value_proc",
            "prompt_suffix",
            "show_default",
            "err",
            "show_choices",
        )
        if any(not hasattr(config, attr) for attr in required_attrs):
            msg = "prompt config must implement PromptConfig"
            raise TypeError(msg)
        try:
            prompt_result = typer.prompt(
                text=text,
                default=config.default,
                hide_input=config.hide_input,
                confirmation_prompt=config.confirmation_prompt,
                type=config.type_hint,
                value_proc=config.value_proc if callable(config.value_proc) else None,
                prompt_suffix=config.prompt_suffix,
                show_default=config.show_default,
                err=config.err,
                show_choices=config.show_choices,
            )
            try:
                prompt_result_map = dict(prompt_result)
            except (
                ValueError,
                TypeError,
                KeyError,
                ConsoleError,
                StyleError,
                LiveError,
            ) as exc:
                logging.getLogger(__name__).debug(
                    "prompt result to dict fallback: %s",
                    exc,
                    exc_info=False,
                )
                prompt_result_map = None
            if prompt_result_map is not None:
                normalized_map: dict[str, t.JsonValue] = {}
                for key, value in prompt_result_map.items():
                    try:
                        normalized_value = (
                            FlextCliCli._json_value_adapter.validate_python(value)
                        )
                        normalized_map[str(key)] = normalized_value
                    except ValidationError as exc:
                        logging.getLogger(__name__).debug(
                            "prompt normalized value skip key %s: %s",
                            key,
                            exc,
                            exc_info=False,
                        )
                        continue
                return r[t.JsonValue].ok(normalized_map)
            json_value = FlextCliCli._to_json_value(prompt_result)
            return r[t.JsonValue].ok(json_value)
        except typer.Abort as e:
            return r[t.JsonValue].fail(
                c.Cli.ErrorMessages.USER_ABORTED_PROMPT.format(error=e)
            )

    def create_cli_runner(
        self,
        charset: str = c.Cli.Utilities.DEFAULT_ENCODING,
        env: Mapping[str, str] | None = None,
        *,
        echo_stdin: bool = False,
    ) -> r[CliRunner]:
        """Create a CLI runner."""
        runner = CliRunner(charset=charset, env=env, echo_stdin=echo_stdin)
        self.logger.debug("Created CliRunner for testing")
        return r[CliRunner].ok(runner)

    @staticmethod
    def format_filename(filename: str | Path, *, shorten: bool = False) -> str:
        """Format filename."""
        return click.format_filename(filename, shorten=shorten)

    @staticmethod
    def get_terminal_size() -> tuple[int, int]:
        """Get terminal size."""
        size = shutil.get_terminal_size()
        return (size.columns, size.lines)

    @staticmethod
    def clear_screen() -> r[bool]:
        """Clear the screen."""
        click.clear()
        return r[bool].ok(value=True)

    @staticmethod
    def pause(info: str = c.Cli.CmdMessages.DEFAULT_PAUSE_MESSAGE) -> r[bool]:
        """Pause execution."""
        click.pause(info=info)
        return r[bool].ok(value=True)

    @staticmethod
    def model_command(
        model_class: type[BaseModel],
        handler: Callable[[BaseModel], t.JsonValue | r[t.JsonValue]],
        config: FlextCliSettings | None = None,
    ) -> p.Cli.CliCommandFunction:
        """Create a command from a Pydantic model."""
        try:
            is_valid_model = issubclass(model_class, BaseModel)
        except TypeError as exc:
            msg = f"model_class must be a BaseModel subclass: {exc}"
            raise TypeError(msg) from exc
        if not is_valid_model:
            msg = "model_class must be a BaseModel subclass"
            raise TypeError(msg)

        def normalized_handler(model: BaseModel) -> t.JsonValue:
            if getattr(model, "__class__", None) is not model_class:
                msg = "model argument must be an instance of the declared model class"
                raise TypeError(msg)
            result = handler(model)
            is_success = getattr(result, "is_success", None)
            if is_success is True:
                return FlextCliCli._to_json_value(getattr(result, "value", None))
            if is_success is False:
                msg = f"Handler failed: {getattr(result, 'error', '')}"
                raise ValueError(msg)
            return FlextCliCli._to_json_value(result)

        return m.Cli.ModelCommandBuilder(
            model_class, normalized_handler, config
        ).build()

    @staticmethod
    def execute() -> r[Mapping[str, t.JsonValue]]:
        """Execute the CLI."""
        return r[Mapping[str, t.JsonValue]].ok({
            c.Cli.DictKeys.SERVICE: c.Cli.FLEXT_CLI,
            c.Cli.DictKeys.STATUS: c.Cli.ServiceStatus.OPERATIONAL.value,
        })


__all__ = ["FlextCliCli", "Typer", "UsageError"]
