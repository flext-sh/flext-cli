"""CLI option helpers shared through ``u.Cli``."""

from __future__ import annotations

from flext_cli import c, t
from flext_cli.models import m
from flext_core import u

from .flextcliutilitiesoptionbuilder_part_01 import FlextCliUtilitiesOptionBuilder
from .flextcliutilitiesoptions_part_01 import (
    FlextCliUtilitiesOptions as FlextCliUtilitiesOptionsPart01,
)


class FlextCliUtilitiesOptions(FlextCliUtilitiesOptionsPart01):
    """Implementation part for FlextCliUtilitiesOptions."""

    @classmethod
    def field_default(
        cls, field_name: str, field_info: m.FieldInfo, settings: t.Cli.ModelLike | None
    ) -> t.Cli.CliValue | None:
        """Resolve CLI default from settings first, then from model field metadata.

        ``None`` is the typed absence of a default. Any other default without a
        CLI form fails at command build with its cause: the default-source
        validation error escapes unchanged, and a validated default that no
        Typer option carries raises ``TypeError``. Structured defaults travel
        through the JSON-option path.
        """
        default_factory = getattr(field_info, "default_factory", None)
        source_value = (
            getattr(settings, field_name)
            if settings is not None and hasattr(settings, field_name)
            else default_factory()
            if callable(default_factory)
            else getattr(field_info, "default", None)
        )
        if source_value is None:
            return None
        if cls.is_json_option(getattr(field_info, "annotation", None) or str):
            # A JSON option's default is the JSON text its parser validates.
            return u.to_json(source_value).decode()
        normalized_atom = cls.normalize_cli_atom(
            t.Cli.CLI_DEFAULT_SOURCE_ADAPTER.validate_python(source_value)
        )
        if normalized_atom is None:
            raise TypeError(
                c.Cli.ERR_FIELD_DEFAULT_NOT_CLI_VALUE_FMT.format(
                    field_name=field_name, value=source_value
                )
            )
        return normalized_atom

    @staticmethod
    def build_option(
        field_name: str, registry: t.Cli.OptionRegistry
    ) -> m.Cli.OptionSpec:
        """Build one CLI option spec from the canonical registry."""
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


__all__: list[str] = ["FlextCliUtilitiesOptions"]
