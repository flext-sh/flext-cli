"""FLEXT CLI utility facade."""

from __future__ import annotations

from flext_core import u

from flext_cli import (
    FlextCliUtilitiesBase,
    FlextCliUtilitiesJson,
    FlextCliUtilitiesPipeline,
    FlextCliUtilitiesToml,
    FlextCliUtilitiesYaml,
)


class FlextCliUtilities(u):
    """CLI utility facade composed from internal utility mixins."""

    class Cli(
        FlextCliUtilitiesPipeline,
        FlextCliUtilitiesBase,
        FlextCliUtilitiesJson,
        FlextCliUtilitiesToml,
        FlextCliUtilitiesYaml,
    ):
        """Command line interface specific utilities — all concerns composed via MRO."""


u = FlextCliUtilities

__all__: list[str] = ["FlextCliUtilities", "u"]
