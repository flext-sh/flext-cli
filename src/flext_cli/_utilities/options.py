"""CLI option helpers shared through ``u.Cli``."""

from __future__ import annotations

from collections.abc import (
    Mapping,
    MutableSequence,
    Sequence,
)
from pathlib import Path
from types import GenericAlias, NoneType, UnionType
from typing import Annotated, TypeAliasType, Union, get_args, get_origin

from typer.models import OptionInfo

from flext_cli import c, m, t


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
    def resolve_typer_annotation(
        annotation: t.Cli.RuntimeAnnotation,
    ) -> type | GenericAlias:
        """Resolve runtime annotations to concrete types accepted by Typer."""
        resolve = FlextCliUtilitiesOptions.resolve_typer_annotation
        annotated_origin = get_origin(Annotated[str, "meta"])
        union_origins: frozenset[object] = frozenset(
            filter(None, [Union, get_origin(str | int)])
        )
        sequence_origins: frozenset[object] = frozenset(
            filter(
                None,
                [
                    get_origin(Sequence[str]),
                    get_origin(list[str]),
                    get_origin(tuple[str, ...]),
                ],
            )
        )
        set_origins: dict[object, type] = {
            o: t_
            for o, t_ in [
                (get_origin(dict[str, t.Scalar]), dict),
                (get_origin(frozenset[str]), frozenset),
                (get_origin(set[str]), set),
            ]
            if o is not None
        }
        resolved_annotation: type | GenericAlias = str
        if isinstance(annotation, TypeAliasType):
            resolved_annotation = resolve(annotation.__value__)
        elif isinstance(annotation, UnionType):
            args = tuple(resolve(arg) for arg in get_args(annotation))
            resolved_annotation = (
                args[0]
                if args[1] is NoneType
                else args[1]
                if len(args) == c.Cli.OPTIONAL_UNION_ARG_COUNT and NoneType in args
                else str
            )
        else:
            origin = get_origin(annotation)
            if origin == annotated_origin:
                first, *_ = get_args(annotation)
                resolved_annotation = resolve(first)
            elif origin in union_origins:
                args = tuple(resolve(arg) for arg in get_args(annotation))
                resolved_annotation = (
                    args[0]
                    if args[1] is NoneType
                    else args[1]
                    if len(args) == c.Cli.OPTIONAL_UNION_ARG_COUNT and NoneType in args
                    else str
                )
            elif origin in sequence_origins:
                resolved_annotation = GenericAlias(list, (str,))
                inner_args = get_args(annotation)
                if inner_args:
                    resolved = resolve(inner_args[0])
                    if isinstance(resolved, type):
                        resolved_annotation = GenericAlias(list, (resolved,))
            elif origin in set_origins:
                resolved_annotation = set_origins[origin]
            elif isinstance(annotation, GenericAlias | type):
                resolved_annotation = annotation
        return resolved_annotation

    @staticmethod
    def is_string_sequence(
        value: t.Cli.CliDefaultSource,
    ) -> bool:
        """Return True for concrete string sequences accepted by repeated CLI options."""
        if isinstance(value, Path) or not isinstance(value, Sequence):
            return False
        if isinstance(value, str | bytes):
            return False
        return all(isinstance(item, str) for item in value)

    @classmethod
    def normalize_cli_atom(
        cls,
        value: t.Cli.CliDefaultSource,
    ) -> t.Cli.DefaultAtom | None:
        """Normalize one runtime value into an allowed Typer scalar or string sequence."""
        if isinstance(value, c.Cli.CLI_SCALAR_TYPES_TUPLE):
            return value
        if isinstance(value, Path):
            return str(value)
        if cls.is_string_sequence(value):
            normalized_sequence = t.Cli.STR_SEQUENCE_ADAPTER.validate_python(value)
            return tuple(normalized_sequence)
        return None

    @classmethod
    def normalize_cli_default(
        cls,
        value: t.Cli.CliDefaultSource,
    ) -> t.Cli.CliValue | None:
        """Normalize field defaults into Typer-compatible scalar/mapping/list values."""
        if value is None:
            return None
        normalized_atom = cls.normalize_cli_atom(value)
        if normalized_atom is not None:
            return normalized_atom
        if isinstance(value, Mapping):
            normalized_mapping: t.Cli.MutableDefaultMapping = {}
            for key, item_value in value.items():
                if not isinstance(key, str):
                    continue
                normalized_item = cls.normalize_cli_atom(item_value)
                if normalized_item is not None:
                    normalized_mapping[key] = normalized_item
            if normalized_mapping:
                return normalized_mapping
            return None
        if cls.is_string_sequence(value):
            return t.Cli.STR_SEQUENCE_ADAPTER.validate_python(value)
        return None

    @classmethod
    def field_default(
        cls,
        field_name: str,
        field_info: m.FieldInfo,
        settings: m.BaseModel | None,
    ) -> t.Cli.CliValue | None:
        """Resolve CLI default from settings first, then from model field metadata."""
        default_factory = getattr(field_info, "default_factory", None)
        source_value = (
            getattr(settings, field_name)
            if settings is not None and hasattr(settings, field_name)
            else default_factory()
            if callable(default_factory)
            else getattr(field_info, "default", None)
        )
        try:
            normalized_source = t.Cli.CLI_DEFAULT_SOURCE_ADAPTER.validate_python(
                source_value,
            )
        except (TypeError, ValueError, c.ValidationError):
            normalized_source = None
        return (
            cls.normalize_cli_default(normalized_source)
            if normalized_source is not None
            else None
        )

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
