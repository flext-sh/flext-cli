"""CLI option helpers shared through ``u.Cli``."""

from __future__ import annotations

from collections.abc import MutableSequence

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
            c.Cli.CliParamsRegistry.KEY_FIELD_NAME_OVERRIDE,
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


__all__ = ["FlextCliUtilitiesOptionBuilder", "FlextCliUtilitiesOptions"]
