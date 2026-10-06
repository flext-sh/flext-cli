"""CLI option helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from functools import cache

from flext_cli import c, t
from flext_cli._utilities._options_parts.flextcliutilitiesoptionbuilder_part_01 import (
    FlextCliUtilitiesOptionBuilder,
)
from flext_cli._utilities._options_parts.flextcliutilitiesoptions_part_01 import (
    FlextCliUtilitiesOptionsPart01,
)
from flext_cli.models import m
from flext_core import u


class FlextCliUtilitiesOptionsPart02(FlextCliUtilitiesOptionsPart01):
    """Implementation part for FlextCliUtilitiesOptionsPart02."""

    @classmethod
    @cache
    def cli_default_source_adapter(cls) -> t.ValueAdapter[t.Cli.CliDefaultSource]:
        """Build the CLI default adapter once at the utility boundary.

        Returns:
            The resulting ``t.ValueAdapter[t.Cli.CliDefaultSource]``.

        """
        return u.type_adapter(t.Cli.CliDefaultSource)

    @staticmethod
    def field_annotation(
        field_name: str,
        field_info: m.FieldInfo,
    ) -> t.Cli.RuntimeAnnotation:
        """Return the declared annotation of a CLI field or fail naming the field.

        Returns:
            The declared annotation of a CLI field or fail naming the field.

        Raises:
            TypeError: If ``annotation is None``.

        """
        annotation = field_info.annotation
        if annotation is None:
            raise TypeError(
                c.Cli.ERR_FIELD_WITHOUT_ANNOTATION_FMT.format(field_name=field_name),
            )
        return annotation

    @classmethod
    def field_default(
        cls,
        field_name: str,
        field_info: m.FieldInfo,
        settings: t.Cli.ModelLike | None,
    ) -> t.Cli.CliValue | None:
        """Resolve CLI default from settings first, then from model field metadata.

        ``None`` is the typed absence of a default. Any other default without a
        CLI form fails at command build with its cause: the default-source
        validation error escapes unchanged, and a validated default that no
        Typer option carries raises ``TypeError``. Structured defaults travel
        through the JSON-option path.

        Returns:
            The resulting ``t.Cli.CliValue | None``.

        Raises:
            TypeError: If ``normalized_atom is None``.

        """
        source_value = (
            getattr(settings, field_name)
            if settings is not None and field_name in type(settings).model_fields
            else field_info.get_default(call_default_factory=True, validated_data={})
        )
        if source_value is None:
            return None
        if cls.json_option(cls.field_annotation(field_name, field_info)):
            # A JSON option's default is the JSON text its parser validates.
            adapter = u.type_adapter(field_info.rebuild_annotation())
            validated = adapter.validate_python(source_value)
            return adapter.dump_json(validated, warnings="error").decode(
                c.Cli.ENCODING_DEFAULT,
            )
        normalized_atom = cls.normalize_cli_atom(
            cls.cli_default_source_adapter().validate_python(source_value),
        )
        if normalized_atom is None:
            raise TypeError(
                c.Cli.ERR_FIELD_DEFAULT_NOT_CLI_VALUE_FMT.format(
                    field_name=field_name,
                    value=source_value,
                ),
            )
        return normalized_atom

    @staticmethod
    def build_option(
        field_name: str,
        registry: t.Cli.OptionRegistry,
    ) -> m.Cli.OptionSpec:
        """Build one CLI option spec from the canonical registry.

        Returns:
            The resulting ``m.Cli.OptionSpec``.

        """
        return FlextCliUtilitiesOptionBuilder.build(field_name, registry)

    @staticmethod
    def reorder_prefixed_options(
        args: t.StrSequence,
        *,
        bool_options: t.StrSequence,
        value_options: t.StrSequence,
    ) -> list[str]:
        """Move shared options before subcommand to right after the subcommand.

        Returns:
            The resulting ``list[str]``.

        """
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


__all__: list[str] = ["FlextCliUtilitiesOptionsPart02"]
