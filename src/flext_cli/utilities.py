"""FLEXT CLI utility facade."""

from __future__ import annotations

from flext_cli import (
    FlextCliUtilitiesBase,
    FlextCliUtilitiesJson,
    FlextCliUtilitiesPipeline,
    FlextCliUtilitiesToml,
    FlextCliUtilitiesYaml,
)
from flext_core import FlextUtilities


class FlextCliUtilities(FlextUtilities):
    """CLI utility facade composed from internal utility mixins."""

    class Cli(
        FlextCliUtilitiesPipeline,
        FlextCliUtilitiesBase,
        FlextCliUtilitiesJson,
        FlextCliUtilitiesToml,
        FlextCliUtilitiesYaml,
    ):
        """Command line interface specific utilities."""


u = FlextCliUtilities

__all__: list[str] = ["FlextCliUtilities", "u"]
