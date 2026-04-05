"""Compatibility aggregate for generic CLI utility helpers."""

from __future__ import annotations

from flext_cli._utilities.configuration import FlextCliUtilitiesConfiguration
from flext_cli._utilities.conversion import FlextCliUtilitiesConversion
from flext_cli._utilities.matching import FlextCliUtilitiesMatching
from flext_cli._utilities.model_commands import FlextCliUtilitiesModelCommands
from flext_cli._utilities.options import FlextCliUtilitiesOptions
from flext_cli._utilities.validation import FlextCliUtilitiesValidation


class FlextCliUtilitiesBase(
    FlextCliUtilitiesConfiguration,
    FlextCliUtilitiesConversion,
    FlextCliUtilitiesMatching,
    FlextCliUtilitiesModelCommands,
    FlextCliUtilitiesOptions,
    FlextCliUtilitiesValidation,
):
    """Thin aggregate for the public direct ``u.Cli`` MRO surface."""


__all__ = ["FlextCliUtilitiesBase"]
