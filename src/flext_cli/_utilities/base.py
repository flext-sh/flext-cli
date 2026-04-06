"""Compatibility aggregate for generic CLI utility helpers."""

from __future__ import annotations

from flext_cli import (
    FlextCliUtilitiesConfiguration,
    FlextCliUtilitiesConversion,
    FlextCliUtilitiesFiles,
    FlextCliUtilitiesMatching,
    FlextCliUtilitiesModelCommands,
    FlextCliUtilitiesOptions,
    FlextCliUtilitiesValidation,
)


class FlextCliUtilitiesBase(
    FlextCliUtilitiesConfiguration,
    FlextCliUtilitiesConversion,
    FlextCliUtilitiesFiles,
    FlextCliUtilitiesMatching,
    FlextCliUtilitiesModelCommands,
    FlextCliUtilitiesOptions,
    FlextCliUtilitiesValidation,
):
    """Thin aggregate for the public direct ``u.Cli`` MRO surface."""


__all__ = ["FlextCliUtilitiesBase"]
