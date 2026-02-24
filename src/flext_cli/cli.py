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
        default: bool | None = None,
    ) -> bool | None: ...

    def _extract_typed_value(
        self,
        val: t.JsonValue | None,
        type_name: Literal["str", "bool"],
        default: t.JsonValue | None = None,
    ) -> t.JsonValue | None:
        if val is None:
            return default
        if type_name == "str":
            default_value = u.Parser.convert(default, str, "")
            converted = u.Parser.convert(val, str, default_value)
            return (
                converted if converted else (default if default is not None else None)
            )
        default_value = u.Parser.convert(default, bool, False)
        return u.Parser.convert(val, bool, default_value)

    def _get_log_level_value(self, config: FlextCliSettings) -> int:
        if config.debug or config.trace:
            return logging.DEBUG
        log_level_attr = getattr(config, "cli_log_level", None) or getattr(
            config, "log_level", None
        )
        return getattr(
            logging,
            str(
                u.Parser.convert(
                    log_level_attr.value if log_level_attr else None, str, "INFO"
                )
                or "INFO"
            ),
            logging.INFO,
        )

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
        active_params = u.mapper().filter_dict(
            common_params, lambda _k, v: v is not None and v is not False
        )
        if not active_params:
            return
        config_fields = set(type(config).model_fields.keys())
        filtered_params = u.mapper().filter_dict(
            active_params, lambda k, _v: k in config_fields
        )
        if not filtered_params:
            return

        def get_bool(k: str) -> bool | None:
            value = u.mapper().get(filtered_params, k)
            if value is None or value == "":
                return None
            return self._extract_typed_value(value, "bool")

        def get_str(k: str) -> str | None:
            value = u.mapper().get(filtered_params, k)
            if value is None or value == "":
                return None
            return self._extract_typed_value(value, "str")

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
    ) -> Callable[[p.Cli.CliCommandFunction], click.Group]:
        """Create a group decorator."""
        return self._create_group_cli_decorator(name, help_text)

    def _build_bool_value(
        self, kwargs: Mapping[str, t.JsonValue], key: str, *, default: bool = False
    ) -> bool:
        val = u.mapper().get(kwargs, key)
        if val is None or val == "":
            return default
        return u.Parser.convert(val, bool, default)

    def _build_str_value(
        self, kwargs: Mapping[str, t.JsonValue], key: str, default: str = ""
    ) -> str:
        val = u.mapper().get(kwargs, key)
        if val is None or val == "":
            return default
        return u.Parser.convert(val, str, default)

    def _build_typed_value(
        self,
        kwargs: Mapping[str, t.JsonValue],
        key: str,
        type_name: Literal["bool", "str"],
        default: t.JsonValue,
    ) -> t.JsonValue:
        if type_name == "bool":
            return self._build_bool_value(
                kwargs, key, default=u.Parser.convert(default, bool, False)
            )
        return self._build_str_value(
            kwargs, key, default=u.Parser.convert(default, str, "")
        )

    @classmethod
    def _to_json_value(cls, value: object) -> t.JsonValue:
        try:
            return cls._json_value_adapter.validate_python(value)
        except ValidationError:
            return str(value)

    def _normalize_type_hint(
        self, type_hint_val: t.JsonValue | None
    ) -> t.JsonValue | None:
        type_hint_build = u.build(type_hint_val, ops={"ensure_default": None})
        if type_hint_build is None or type_hint_build == "":
            return None
        return self._to_json_value(type_hint_build)

    def _build_option_config_from_kwargs(
        self, kwargs: Mapping[str, t.JsonValue]
    ) -> m.Cli.OptionConfig:
        return m.Cli.OptionConfig(
            default=u.mapper().get(kwargs, "default"),
            type_hint=self._normalize_type_hint(u.mapper().get(kwargs, "type_hint")),
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
        config: object | None = None,
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
        return cls._datetime_type(formats)

    @classmethod
    def get_uuid_type(cls) -> click.ParamType:
        """Get UUID type."""
        return click.UUID

    @classmethod
    def get_tuple_type(
        cls, types: Sequence[type[t.JsonValue] | click.ParamType]
    ) -> click.Tuple:
        """Get tuple type."""
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
    ) -> tuple[Callable[[str, bool], bool], Callable[[str, str], str]]:
        def get_bool_val(k: str, default: bool = False) -> bool:  # noqa: FBT001, FBT002
            val = u.mapper().get(kwargs, k)
            if val is None or val == "":
                return default
            return u.Parser.convert(val, bool, default)

        def get_str_val(k: str, default: str = "") -> str:
            val = u.mapper().get(kwargs, k)
            if val is None or val == "":
                return default
            return u.Parser.convert(val, str, default)

        return (get_bool_val, get_str_val)

    @staticmethod
    def _build_confirm_config(kwargs: Mapping[str, t.JsonValue]) -> m.Cli.ConfirmConfig:
        get_bool_val, get_str_val = FlextCliCli._build_config_getters(kwargs)
        return m.Cli.ConfirmConfig(
            default=get_bool_val("default", False),
            abort=get_bool_val("abort", False),
            prompt_suffix=get_str_val(
                "prompt_suffix", c.Cli.UIDefaults.DEFAULT_PROMPT_SUFFIX
            ),
            show_default=get_bool_val("show_default", True),
            err=get_bool_val("err", False),
        )

    @staticmethod
    def _build_prompt_config(kwargs: Mapping[str, t.JsonValue]) -> m.Cli.PromptConfig:
        get_bool_val, get_str_val = FlextCliCli._build_config_getters(kwargs)
        value_proc_val = u.mapper().get(kwargs, "value_proc")
        return m.Cli.PromptConfig(
            default=u.mapper().get(kwargs, "default"),
            type_hint=u.mapper().get(kwargs, "type_hint"),
            value_proc=value_proc_val if callable(value_proc_val) else None,
            prompt_suffix=get_str_val(
                "prompt_suffix", c.Cli.UIDefaults.DEFAULT_PROMPT_SUFFIX
            ),
            hide_input=get_bool_val("hide_input", False),
            confirmation_prompt=get_bool_val("confirmation_prompt", False),
            show_default=get_bool_val("show_default", True),
            err=get_bool_val("err", False),
            show_choices=get_bool_val("show_choices", True),
        )

    @staticmethod
    def _build_confirm_config_from_kwargs(
        kwargs: Mapping[str, t.JsonValue],
    ) -> m.Cli.ConfirmConfig:
        return FlextCliCli._build_confirm_config(kwargs)

    @staticmethod
    def confirm(
        text: str,
        config: p.Cli.ConfirmConfigProtocol | None = None,
        **kwargs: bool | str,
    ) -> r[bool]:
        """Confirm action with user."""
        if config is None:
            kwargs_typed: dict[str, t.JsonValue] = dict(kwargs)
            config_instance = FlextCliCli._build_confirm_config_from_kwargs(
                kwargs_typed,
            )
            config = config_instance
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
        return FlextCliCli._build_prompt_config(kwargs)

    @staticmethod
    def prompt(
        text: str,
        config: p.Cli.PromptConfigProtocol | None = None,
        **kwargs: t.JsonValue,
    ) -> r[t.JsonValue]:
        """Prompt user for input."""
        if config is None:
            config_instance = FlextCliCli._build_prompt_config_from_kwargs(kwargs)
            config = config_instance
        try:
            prompt_result = typer.prompt(
                text=text,
                default=config.default,
                hide_input=config.hide_input,
                confirmation_prompt=config.confirmation_prompt,
                type=config.type_hint,
                value_proc=config.value_proc,
                prompt_suffix=config.prompt_suffix,
                show_default=config.show_default,
                err=config.err,
                show_choices=config.show_choices,
            )
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

        def normalized_handler(model: BaseModel) -> t.JsonValue:
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
Typer = typer.Typer
