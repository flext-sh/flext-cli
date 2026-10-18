"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import get_origin

from flext_cli import c, m, p, t, u
from flext_cli.services._cli_parts import FlextCliCliPart01


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

        Args:
            model_cls: Request model whose fields declare the options.
            arguments: Raw command-line tokens to parse.
            field_names: Optional subset of fields to parse; all fields apply
                when omitted.
            stop_at_positional: Whether to stop at the first positional token.

        Returns:
            The resulting ``p.Cli.ParsedOptionTokens``.

        """
        selected = (
            field_names if field_names is not None else tuple(model_cls.model_fields)
        )
        options = cls._model_option_routes(model_cls, selected)
        values: t.JsonDict = {}
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
    ) -> t.MappingKV[str, tuple[str, bool, bool, bool]]:
        """Classify declarations using the same option specification as Typer.

        Returns:
            Canonical field, flag status, polarity and repetition for each name.

        Raises:
            TypeError: If a required field is excluded from the CLI.

        """
        options: t.MutableMappingKV[str, tuple[str, bool, bool, bool]] = {}
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
        values: t.JsonDict,
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
        values: t.JsonDict,
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

    @staticmethod
    def add_group(
        app: p.Cli.Application,
        *,
        name: str,
        group: p.Cli.Application,
    ) -> None:
        """Attach a subcommand group to an application.

        Args:
            app: Application receiving the group.
            name: Name the group registers under.
            group: Group application to attach.

        """
        u.Cli.framework_add_group(app, name=name, group=group)

    @staticmethod
    def create_group(*, help_text: str, name: str | None = None) -> p.Cli.Application:
        """Create a Typer command group without re-registering global params.

        Args:
            help_text: Group help text.
            name: Optional group name.

        Returns:
            The resulting ``p.Cli.Application``.

        """
        return u.Cli.framework_create_app(
            name=name,
            help_text=help_text,
            add_completion=True,
        )


__all__: list[str] = ["FlextCliCliPart02"]
