"""CLI option helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from types import GenericAlias, NoneType, UnionType
from typing import Annotated, TypeAliasType, get_args, get_origin

from flext_cli import c, m, t


class FlextCliUtilitiesOptionsPart01:
    """Implementation part for FlextCliUtilitiesOptionsPart01."""

    @staticmethod
    def unwrap_annotation(
        annotation: t.Cli.RuntimeAnnotation,
    ) -> t.Cli.RuntimeAnnotation:
        """Strip type aliases and ``Annotated`` metadata down to the carried type.

        Returns:
            The resulting ``t.Cli.RuntimeAnnotation``.

        """
        annotated_origin = get_origin(Annotated[str, "meta"])
        resolved = annotation
        while (
            isinstance(resolved, TypeAliasType)
            or get_origin(resolved) == annotated_origin
        ):
            resolved = (
                resolved.__value__
                if isinstance(resolved, TypeAliasType)
                else get_args(resolved)[0]
            )
        return resolved

    @classmethod
    def json_option(cls, annotation: t.Cli.RuntimeAnnotation) -> bool:
        """Return True when a field has no native CLI form and travels as JSON.

        Mappings, nested models, and the collections or unions that carry them
        are exposed as one JSON option that Pydantic validates into the
        field's declared type.

        Returns:
            True when a field has no native CLI form and travels as JSON.

        """
        resolved = cls.unwrap_annotation(annotation)
        origin = get_origin(resolved)
        if origin is UnionType:
            return any(cls.json_option(arg) for arg in get_args(resolved))
        while isinstance(origin, TypeAliasType):
            origin = get_origin(origin.__value__)
        carrier = resolved if origin is None else origin
        if isinstance(carrier, type) and (
            issubclass(carrier, m.BaseModel) or issubclass(carrier, Mapping)
        ):
            return True
        return origin is not None and any(
            cls.json_option(arg) for arg in get_args(resolved)
        )

    @classmethod
    def resolve_typer_annotation(
        cls,
        annotation: t.Cli.RuntimeAnnotation,
    ) -> type | GenericAlias:
        """Resolve runtime annotations to concrete types accepted by Typer.

        A field without a native CLI form (see ``json_option``) resolves to
        ``str``: its option carries JSON that Pydantic validates on parse.

        Returns:
            The resulting ``type | GenericAlias``.

        """
        if cls.json_option(annotation):
            return str
        sequence_origins: frozenset[object] = frozenset(
            filter(
                None,
                [
                    get_origin(Sequence[str]),
                    get_origin(list[str]),
                    # mro-j2yt (codex): Typer repeats canonical tuple model fields.
                    get_origin(t.VariadicTuple[str]),
                    get_origin(t.StrSequence),
                    t.SequenceOf,
                    t.MutableSequenceOf,
                    # Typer has no set type: sets are repeated options whose
                    # list the request model validates into set/frozenset.
                    get_origin(set[str]),
                    get_origin(frozenset[str]),
                ],
            ),
        )
        resolved_annotation_input = cls.unwrap_annotation(annotation)
        origin = get_origin(resolved_annotation_input)

        # ``X | None`` is a runtime ``UnionType`` the static ``TypeForm``
        # contract cannot narrow to: an optional field resolves to its single
        # carried type, so ``t.StrSequence | None`` stays a repeated option.
        if origin is UnionType:
            resolved_args = tuple(
                cls.resolve_typer_annotation(arg)
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
            resolved_inner = cls.resolve_typer_annotation(inner_annotation)
            sequence_item = resolved_inner if isinstance(resolved_inner, type) else str
            return GenericAlias(list, (sequence_item,))

        return (
            resolved_annotation_input
            if isinstance(resolved_annotation_input, GenericAlias | type)
            else str
        )

    @staticmethod
    def string_sequence(value: t.Cli.CliDefaultSource) -> bool:
        """Return True for concrete string sequences accepted by repeated CLI options.

        Returns:
            True for concrete string sequences accepted by repeated CLI options.

        """
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
        """Normalize one runtime value into an allowed Typer scalar or string sequence.

        Returns:
            The resulting ``t.Cli.DefaultAtom | None``.

        """
        if isinstance(value, c.Cli.CLI_SCALAR_TYPES_TUPLE):
            return value
        if isinstance(value, Path):
            return str(value)
        if cls.string_sequence(value):
            normalized_sequence = t.Cli.STR_SEQUENCE_ADAPTER.validate_python(value)
            return tuple(normalized_sequence)
        return None


__all__: list[str] = ["FlextCliUtilitiesOptionsPart01"]
