"""CLI option helpers shared through ``u.Cli``."""

from __future__ import annotations

from collections.abc import (
    MutableSequence,
    Sequence,
)
from types import GenericAlias, NoneType, UnionType
from typing import Annotated, TypeAliasType, Union, get_args, get_origin

from typer.models import OptionInfo

from flext_cli import c, t


class FlextCliUtilitiesOptionBuilder:
    """Build Typer options from canonical field metadata."""

    def __init__(
        self,
        field_name: str,
        registry: t.Cli.OptionRegistry,
    ) -> None:
        """Initialize the option builder."""
        super().__init__()
        self.field_name = field_name
        self.registry = registry

    def build(self) -> OptionInfo:
        """Build ``OptionInfo`` from field metadata."""
        field_meta = self.registry.get(self.field_name, {})
        if not field_meta:
            msg = "Option registry metadata must support key lookup"
            raise TypeError(msg)
        help_text = str(field_meta.get("help", ""))
        short_flag = str(field_meta.get("short", ""))
        default_value = field_meta.get("default", ...)

        field_name_override = field_meta.get(
            c.Cli.CLI_PARAM_KEY_FIELD_NAME_OVERRIDE,
        )
        cli_param_name: str = (
            field_name_override
            if isinstance(field_name_override, str)
            else self.field_name
        )

        option_args: MutableSequence[str] = [f"--{cli_param_name.replace('_', '-')}"]
        if cli_param_name == "project":
            option_args.append("--projects")
        if short_flag:
            option_args.append(f"-{short_flag}")

        return OptionInfo(
            default=default_value,
            param_decls=option_args,
            help=help_text,
        )


class FlextCliUtilitiesOptions:
    """Option methods exposed directly on ``u.Cli``."""

    @staticmethod
    def _is_union_origin(
        origin: object | None,
        *,
        typing_union_origin: object,
        runtime_union_origin: object | None,
    ) -> bool:
        """Return True when runtime origin represents a union annotation."""
        return origin is typing_union_origin or origin is runtime_union_origin

    @staticmethod
    def resolve_typer_annotation(
        annotation: t.Cli.RuntimeAnnotation,
    ) -> type | GenericAlias:
        """Resolve runtime annotations to concrete types accepted by Typer."""
        annotated_origin: object | None = get_origin(Annotated[str, "meta"])
        typing_union_origin: object = Union
        runtime_union_origin: object | None = get_origin(str | int)
        sequence_origin: object | None = get_origin(Sequence[str])
        list_origin: object | None = get_origin(list[str])
        tuple_origin: object | None = get_origin(tuple[str, ...])
        dict_origin: object | None = get_origin(dict[str, t.Scalar])
        frozenset_origin: object | None = get_origin(frozenset[str])
        set_origin: object | None = get_origin(set[str])
        if isinstance(annotation, TypeAliasType):
            return FlextCliUtilitiesOptions.resolve_typer_annotation(
                annotation.__value__
            )
        if isinstance(annotation, UnionType):
            args = tuple(
                FlextCliUtilitiesOptions.resolve_typer_annotation(arg)
                for arg in get_args(annotation)
            )
            if len(args) == c.Cli.OPTIONAL_UNION_ARG_COUNT and NoneType in args:
                return args[0] if args[1] is NoneType else args[1]
            return str
        origin: object | None = get_origin(annotation)
        if origin == annotated_origin:
            value, *_ = get_args(annotation)
            return FlextCliUtilitiesOptions.resolve_typer_annotation(value)
        if FlextCliUtilitiesOptions._is_union_origin(
            origin,
            typing_union_origin=typing_union_origin,
            runtime_union_origin=runtime_union_origin,
        ):
            args = tuple(
                FlextCliUtilitiesOptions.resolve_typer_annotation(arg)
                for arg in get_args(annotation)
            )
            if len(args) == c.Cli.OPTIONAL_UNION_ARG_COUNT and NoneType in args:
                return args[0] if args[1] is NoneType else args[1]
            return str
        if origin == sequence_origin:
            args = get_args(annotation)
            if args:
                value = FlextCliUtilitiesOptions.resolve_typer_annotation(args[0])
                if isinstance(value, type):
                    return GenericAlias(list, (value,))
            return list[str]
        if origin in {list_origin, tuple_origin}:
            args = get_args(annotation)
            if args:
                value = FlextCliUtilitiesOptions.resolve_typer_annotation(args[0])
                if isinstance(value, type):
                    return GenericAlias(list, (value,))
            return list[str]
        if origin == dict_origin:
            return dict
        if origin == frozenset_origin:
            return frozenset
        if origin == set_origin:
            return set
        if isinstance(annotation, GenericAlias):
            return annotation
        if isinstance(annotation, type):
            return annotation
        return str

    @staticmethod
    def build_option(
        field_name: str,
        registry: t.Cli.OptionRegistry,
    ) -> OptionInfo:
        """Build one Typer option from the canonical registry."""
        return FlextCliUtilitiesOptionBuilder(field_name, registry).build()

    @staticmethod
    def reorder_prefixed_options(
        args: t.StrSequence,
        *,
        bool_options: t.StrSequence,
        value_options: t.StrSequence,
    ) -> list[str]:
        """Move shared options before subcommand to right after the subcommand."""
        if not args:
            return []
        bool_set = set(bool_options)
        value_set = set(value_options)
        prefix_tokens: list[str] = []
        index = 0
        while index < len(args):
            token = args[index]
            normalized = token.split("=", 1)[0]
            if normalized in bool_set:
                prefix_tokens.append(token)
                index += 1
                continue
            if normalized in value_set:
                prefix_tokens.append(token)
                if "=" not in token and index + 1 < len(args):
                    prefix_tokens.append(args[index + 1])
                    index += 2
                else:
                    index += 1
                continue
            if token.startswith("-"):
                break
            subcommand = token
            suffix_tokens = list(args[index + 1 :])
            return [subcommand, *prefix_tokens, *suffix_tokens]
        return list(args)


__all__: list[str] = ["FlextCliUtilitiesOptionBuilder", "FlextCliUtilitiesOptions"]
