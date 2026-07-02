"""FLEXT CLI utility facade."""

from __future__ import annotations

from flext_cli._utilities.auth import FlextCliUtilitiesAuth
from flext_cli._utilities.cmd import FlextCliUtilitiesCmd
from flext_cli._utilities.commands import FlextCliUtilitiesCommands
from flext_cli._utilities.conversion import FlextCliUtilitiesConversion
from flext_cli._utilities.file_test_helpers import FlextCliUtilitiesFileTestHelpersMixin
from flext_cli._utilities.files import FlextCliUtilitiesFiles
from flext_cli._utilities.formatters import FlextCliUtilitiesFormatters
from flext_cli._utilities.json import FlextCliUtilitiesJson
from flext_cli._utilities.matching import FlextCliUtilitiesMatching
from flext_cli._utilities.model_commands import FlextCliUtilitiesModelCommands
from flext_cli._utilities.options import FlextCliUtilitiesOptions
from flext_cli._utilities.output import FlextCliUtilitiesOutput
from flext_cli._utilities.params import FlextCliUtilitiesParams
from flext_cli._utilities.pipeline import FlextCliUtilitiesPipeline
from flext_cli._utilities.processes import FlextCliUtilitiesProcesses
from flext_cli._utilities.prompts import FlextCliUtilitiesPrompts
from flext_cli._utilities.rules import FlextCliUtilitiesRules
from flext_cli._utilities.runtime import FlextCliUtilitiesRuntime
from flext_cli._utilities.settings import FlextCliUtilitiesSettings
from flext_cli._utilities.tables import FlextCliUtilitiesTables
from flext_cli._utilities.toml import FlextCliUtilitiesToml
from flext_cli._utilities.validation import FlextCliUtilitiesValidation
from flext_cli._utilities.yaml import FlextCliUtilitiesYaml
from flext_core import u


class FlextCliUtilities(
    u,
    FlextCliUtilitiesAuth,
    FlextCliUtilitiesCmd,
    FlextCliUtilitiesCommands,
    FlextCliUtilitiesConversion,
    FlextCliUtilitiesFileTestHelpersMixin,
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
    FlextCliUtilitiesProcesses,
    FlextCliUtilitiesRules,
    FlextCliUtilitiesRuntime,
    FlextCliUtilitiesSettings,
    FlextCliUtilitiesTables,
    FlextCliUtilitiesToml,
    FlextCliUtilitiesValidation,
    FlextCliUtilitiesYaml,
):
    """CLI utility facade composed from internal utility mixins."""

    class Cli(
        FlextCliUtilitiesAuth,
        FlextCliUtilitiesCmd,
        FlextCliUtilitiesCommands,
        FlextCliUtilitiesConversion,
        FlextCliUtilitiesFileTestHelpersMixin,
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
        FlextCliUtilitiesProcesses,
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
