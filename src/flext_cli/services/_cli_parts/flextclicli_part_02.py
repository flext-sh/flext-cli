"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from inspect import Parameter
from typing import get_origin

from flext_cli import c, m, p, r, settings, t, u
from flext_cli.services._cli_parts.flextclicli_part_01 import FlextCliCliPart01
from flext_cli.services.cli_params import FlextCliCommonParams


class FlextCliCliPart02(FlextCliCliPart01):
    """Implementation part for FlextCliCliPart02."""

    @classmethod
    def parse_model_options(
        cls,
        model_cls: t.ModelClass[t.Cli.ModelLike],
        arguments: t.StrSequence,
        *,
        field_names: t.StrSequence | None = None,
        stop_at_positional: bool = False,
    ) -> p.Cli.ParsedOptionTokens:
        """Parse route options from the same declarations used to build Typer.

        Classification propagates TypeError for required excluded fields or
        invalid repeated values. Token consumption propagates ValueError for
        undeclared or duplicated options and invalid flag/value arity.

        Returns:
            The resulting ``p.Cli.ParsedOptionTokens``.

        """
        selected = (
            field_names if field_names is not None else tuple(model_cls.model_fields)
        )
        options = cls._model_option_routes(model_cls, selected)
        values: dict[str, t.JsonValue] = {}
        index = 0
        while index < len(arguments):
            argument = arguments[index]
            if argument == "--" and stop_at_positional:
                return m.Cli.ParsedOptionTokens(
                    values=values,
                    remaining=tuple(arguments[index + 1 :]),
                    help_requested=False,
                )
            if argument == "--help":
                return m.Cli.ParsedOptionTokens(
                    values=values,
                    remaining=(),
                    help_requested=True,
                )
            if stop_at_positional and not argument.startswith("-"):
                return m.Cli.ParsedOptionTokens(
                    values=values,
                    remaining=tuple(arguments[index:]),
                    help_requested=False,
                )
            index = cls._consume_model_option(
                arguments,
                index=index,
                options=options,
                values=values,
            )
        return m.Cli.ParsedOptionTokens(
            values=values,
            remaining=(),
            help_requested=False,
        )

    @classmethod
    def _model_option_routes(
        cls,
        model_cls: t.ModelClass[t.Cli.ModelLike],
        selected: t.StrSequence,
    ) -> dict[str, tuple[str, bool, bool, bool]]:
        """Classify declarations using the same option specification as Typer.

        Returns:
            Canonical field, flag status, polarity and repetition for each name.

        Raises:
            TypeError: If a required field is excluded from the CLI.

        """
        options: dict[str, tuple[str, bool, bool, bool]] = {}
        for field_name in selected:
            field = model_cls.model_fields[field_name]
            if field.exclude is True:
                if field.is_required():
                    msg = c.Cli.ERR_REQUIRED_EXCLUDED_FIELD_FMT.format(
                        model=model_cls.__name__,
                        field_name=field_name,
                    )
                    raise TypeError(msg)
                continue
            spec, annotation = cls.model_option_spec(field_name, field, None)
            for declaration in spec.declarations:
                for position, name in enumerate(declaration.split("/")):
                    options[name] = (
                        field_name,
                        annotation is bool,
                        position == 0,
                        get_origin(annotation) is list,
                    )
        return options

    @classmethod
    def _consume_model_option(
        cls,
        arguments: t.StrSequence,
        *,
        index: int,
        options: t.MappingKV[str, tuple[str, bool, bool, bool]],
        values: dict[str, t.JsonValue],
    ) -> int:
        """Consume one declared option and its value before inspecting more tokens.

        Returns:
            The index of the next unconsumed token.

        Raises:
            ValueError: If the option is undeclared, duplicated or has invalid arity.

        """
        argument = arguments[index]
        option, separator, inline = argument.partition("=")
        route = options.get(option)
        if route is None:
            msg = f"CLI option is not declared for this route: {argument}"
            raise ValueError(msg)
        field_name, is_flag, flag_value, is_repeated = route
        if field_name in values and not is_repeated:
            msg = f"CLI option is duplicated: {field_name}"
            raise ValueError(msg)
        if is_flag:
            if separator:
                msg = f"CLI flag cannot take a value: {option}"
                raise ValueError(msg)
            values[field_name] = flag_value
        else:
            if not separator:
                index += 1
                if index >= len(arguments):
                    msg = f"CLI option requires a value: {option}"
                    raise ValueError(msg)
                inline = arguments[index]
            if not inline:
                msg = f"CLI option requires a value: {option}"
                raise ValueError(msg)
            cls._store_model_option_value(
                values,
                field_name=field_name,
                value=inline,
                repeated=is_repeated,
            )
        return index + 1

    @staticmethod
    def _store_model_option_value(
        values: dict[str, t.JsonValue],
        *,
        field_name: str,
        value: str,
        repeated: bool,
    ) -> None:
        """Store scalar or repeated values without changing insertion order.

        Raises:
            TypeError: If a repeated option already holds a non-list value.

        """
        if not repeated:
            values[field_name] = value
            return
        existing = values.get(field_name)
        if existing is None:
            values[field_name] = [value]
        elif isinstance(existing, list):
            existing.append(value)
        else:
            msg = f"CLI repeated option has an invalid value: {field_name}"
            raise TypeError(msg)

    def _apply_common_params_to_config(self, *, params: m.Cli.CliParamsConfig) -> None:
        """Apply global CLI flags to the shared settings singleton."""
        resolved_log_level: str = (
            params.log_level if params.log_level is not None else settings.cli_log_level
        )
        next_params = m.Cli.CliParamsConfig.model_validate({
            **params.model_dump(),
            "log_level": resolved_log_level,
        })
        applied = FlextCliCommonParams.apply_to_config(settings, params=next_params)
        if applied.failure:
            self._exit_failure(r[bool].from_failure(applied))
        self._apply_updated_settings(applied.value)
        if any(
            flag is not None for flag in (params.log_level, params.debug, params.trace)
        ):
            # Explicit operator flags win over the application settings the
            # process entry applied before options were parsed.
            u.apply_log_level(
                log_level=applied.value.cli_log_level,
                debug=applied.value.debug,
                trace=applied.value.trace,
            )

    @staticmethod
    def _apply_updated_settings(updated_settings: p.Cli.Settings) -> None:
        """Diff resolved settings against the singleton and update overrides."""
        # NOTE (multi-agent): the ``settings`` singleton is always the
        # concrete FlextCliSettings, which provably satisfies the Settings
        # protocol — the old isinstance guard was dead code (pyright
        # reportUnnecessaryIsInstance). Settings are flat scalars (§2.6):
        # field-level diff drives ``update_global`` directly.
        if updated_settings is settings:
            return
        overrides: dict[str, t.SettingsOverride | None] = {}
        if updated_settings.debug != settings.debug:
            overrides["debug"] = updated_settings.debug
        if updated_settings.trace != settings.trace:
            overrides["trace"] = updated_settings.trace
        for field in (
            "cli_verbose",
            "cli_quiet",
            "cli_no_color",
            "cli_log_level",
            "cli_log_verbosity",
            "cli_output_format",
        ):
            updated_value = getattr(updated_settings, field)
            if updated_value != getattr(settings, field):
                overrides[field] = updated_value
        if overrides:
            settings.update_global(**overrides)

    def create_app_with_common_params(
        self,
        *,
        name: str,
        help_text: str,
        add_completion: bool = True,
    ) -> p.Cli.Application:
        """Create a Typer app with the shared global FLEXT CLI parameters.

        Returns:
            The resulting ``p.Cli.Application``.

        """
        app = u.Cli.framework_create_app(
            name=name,
            help_text=help_text,
            add_completion=add_completion,
        )

        def apply_common_params(params: m.Cli.CliParamsConfig) -> bool:
            self._apply_common_params_to_config(params=params)
            return True

        parameters: t.MutableSequenceOf[Parameter] = []
        annotations: t.Cli.CliAnnotations = {"return": bool}
        for field_name in c.Cli.CLI_GLOBAL_PARAM_FIELDS:
            parameter, annotation = self._build_model_parameter(
                field_name,
                m.Cli.CliParamsConfig.model_fields[field_name],
                None,
            )
            parameters.append(parameter)
            annotations[field_name] = annotation
        global_callback: FlextCliCliPart02._ModelCommand[m.Cli.CliParamsConfig] = (
            self._ModelCommand(
                handler=apply_common_params,
                model_cls=m.Cli.CliParamsConfig,
                parameters=parameters,
                result_border=True,
            )
        )
        global_callback.__annotations__ = dict(annotations)
        u.Cli.framework_register_callback(app, global_callback)
        return app

    @staticmethod
    def add_group(
        app: p.Cli.Application,
        *,
        name: str,
        group: p.Cli.Application,
    ) -> None:
        """Attach a subcommand group to an application."""
        u.Cli.framework_add_group(app, name=name, group=group)

    @staticmethod
    def create_group(*, help_text: str, name: str | None = None) -> p.Cli.Application:
        """Create a Typer command group without re-registering global params.

        Returns:
            The resulting ``p.Cli.Application``.

        """
        return u.Cli.framework_create_app(
            name=name,
            help_text=help_text,
            add_completion=True,
        )


__all__: list[str] = ["FlextCliCliPart02"]
