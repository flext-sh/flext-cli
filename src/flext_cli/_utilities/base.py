"""Aggregate for generic CLI utility helpers."""

from __future__ import annotations

from flext_cli._utilities.auth import FlextCliUtilitiesAuth
from flext_cli._utilities.cmd import FlextCliUtilitiesCmd
from flext_cli._utilities.commands import FlextCliUtilitiesCommands
from flext_cli._utilities.conversion import FlextCliUtilitiesConversion
from flext_cli._utilities.files import FlextCliUtilitiesFiles
from flext_cli._utilities.formatters import FlextCliUtilitiesFormatters
from flext_cli._utilities.matching import FlextCliUtilitiesMatching
from flext_cli._utilities.model_commands import FlextCliUtilitiesModelCommands
from flext_cli._utilities.options import FlextCliUtilitiesOptions
from flext_cli._utilities.output import FlextCliUtilitiesOutput
from flext_cli._utilities.params import FlextCliUtilitiesParams
from flext_cli._utilities.prompts import FlextCliUtilitiesPrompts
from flext_cli._utilities.runtime import FlextCliUtilitiesRuntime
from flext_cli._utilities.settings import FlextCliUtilitiesSettings
from flext_cli._utilities.tables import FlextCliUtilitiesTables
from flext_cli._utilities.validation import FlextCliUtilitiesValidation


class FlextCliUtilitiesBase(
    FlextCliUtilitiesAuth,
    FlextCliUtilitiesCmd,
    FlextCliUtilitiesSettings,
    FlextCliUtilitiesCommands,
    FlextCliUtilitiesConversion,
    FlextCliUtilitiesFiles,
    FlextCliUtilitiesFormatters,
    FlextCliUtilitiesMatching,
    FlextCliUtilitiesModelCommands,
    FlextCliUtilitiesOptions,
    FlextCliUtilitiesOutput,
    FlextCliUtilitiesParams,
    FlextCliUtilitiesPrompts,
    FlextCliUtilitiesRuntime,
    FlextCliUtilitiesTables,
    FlextCliUtilitiesValidation,
):
    """Thin aggregate for the public direct ``u.Cli`` MRO surface."""


__all__ = ["FlextCliUtilitiesBase"]
