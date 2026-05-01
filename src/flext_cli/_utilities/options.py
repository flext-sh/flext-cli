"""CLI option helpers shared through ``u.Cli``."""

from __future__ import annotations

from collections.abc import (
    Mapping,
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

        option_args: t.MutableSequenceOf[str] = [
            f"--{cli_param_name.replace('_', '-')}"
        ]
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
        resolved_annotation_input = annotation
        origin = get_origin(resolved_annotation_input)
        while (
            isinstance(resolved_annotation_input, TypeAliasType)
            or origin == annotated_origin
        ):
            resolved_annotation_input = (
                resolved_annotation_input.__value__
                if isinstance(resolved_annotation_input, TypeAliasType)
                else get_args(resolved_annotation_input)[0]
            )
            origin = get_origin(resolved_annotation_input)

        if isinstance(resolved_annotation_input, UnionType) or origin in union_origins:
            resolved_args = tuple(
                FlextCliUtilitiesOptions.resolve_typer_annotation(arg)
                for arg in get_args(resolved_annotation_input)
            )
            non_none_args = tuple(arg for arg in resolved_args if arg is not NoneType)
            if (
                len(resolved_args) == c.Cli.OPTIONAL_UNION_ARG_COUNT
                and len(non_none_args) == 1
            ):
                return non_none_args[0]
            return str

        if origin in sequence_origins:
            inner_annotation = next(iter(get_args(resolved_annotation_input)), str)
            resolved_inner = FlextCliUtilitiesOptions.resolve_typer_annotation(
                inner_annotation
            )
            sequence_item = resolved_inner if isinstance(resolved_inner, type) else str
            return GenericAlias(list, (sequence_item,))

        set_annotation = set_origins.get(origin)
        if set_annotation is not None:
            return set_annotation

        return (
            resolved_annotation_input
            if isinstance(resolved_annotation_input, GenericAlias | type)
            else str
        )

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
        if normalized_source is None:
            return None
        match normalized_source:
            case _ if (
                normalized_atom := cls.normalize_cli_atom(normalized_source)
            ) is not None:
                normalized_default: t.Cli.CliValue | None = normalized_atom
            case Mapping() as normalized_source_mapping:
                normalized_mapping: t.Cli.MutableDefaultMapping = {}
                for key, item_value in normalized_source_mapping.items():
                    normalized_item = cls.normalize_cli_atom(item_value)
                    if normalized_item is not None:
                        normalized_mapping[key] = normalized_item
                normalized_default = normalized_mapping or None
            case _ if cls.is_string_sequence(normalized_source):
                normalized_default = t.Cli.STR_SEQUENCE_ADAPTER.validate_python(
                    normalized_source
                )
            case _:
                normalized_default = None
        return normalized_default

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
