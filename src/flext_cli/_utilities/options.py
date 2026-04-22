"""CLI option helpers shared through ``u.Cli``."""

from __future__ import annotations

from collections.abc import (
    MutableSequence,
)

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
