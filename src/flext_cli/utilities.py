"""FLEXT CLI utility facade."""

from __future__ import annotations

from flext_cli import (
    FlextCliUtilitiesAuth,
    FlextCliUtilitiesCmd,
    FlextCliUtilitiesCommands,
    FlextCliUtilitiesConversion,
    FlextCliUtilitiesFiles,
    FlextCliUtilitiesFormatters,
    FlextCliUtilitiesJson,
    FlextCliUtilitiesMatching,
    FlextCliUtilitiesModelCommands,
    FlextCliUtilitiesOptions,
    FlextCliUtilitiesOutput,
    FlextCliUtilitiesParams,
    FlextCliUtilitiesPipeline,
    FlextCliUtilitiesPrompts,
    FlextCliUtilitiesRules,
    FlextCliUtilitiesRuntime,
    FlextCliUtilitiesSettings,
    FlextCliUtilitiesTables,
    FlextCliUtilitiesToml,
    FlextCliUtilitiesValidation,
    FlextCliUtilitiesYaml,
)
from flext_core import u


class FlextCliUtilities(u):
    """CLI utility facade composed from internal utility mixins."""

    class Cli(
        FlextCliUtilitiesAuth,
        FlextCliUtilitiesCmd,
        FlextCliUtilitiesCommands,
        FlextCliUtilitiesConversion,
        FlextCliUtilitiesFiles,
        FlextCliUtilitiesFormatters,
        FlextCliUtilitiesJson,
        FlextCliUtilitiesMatching,
        FlextCliUtilitiesModelCommands,
        FlextCliUtilitiesOptions,
        FlextCliUtilitiesOutput,
        FlextCliUtilitiesParams,
        FlextCliUtilitiesPipeline,
        FlextCliUtilitiesPrompts,
        FlextCliUtilitiesRules,
        FlextCliUtilitiesRuntime,
        FlextCliUtilitiesSettings,
        FlextCliUtilitiesTables,
        FlextCliUtilitiesToml,
        FlextCliUtilitiesValidation,
        FlextCliUtilitiesYaml,
    ):
        """Command line interface specific utilities — all concerns composed via MRO."""


u = FlextCliUtilities

__all__: list[str] = ["FlextCliUtilities", "u"]
