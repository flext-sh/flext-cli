"""FLEXT CLI utility facade."""

from __future__ import annotations

from flext_cli._utilities.base import FlextCliUtilitiesBase
from flext_cli._utilities.json import FlextCliUtilitiesJson
from flext_cli._utilities.toml import FlextCliUtilitiesToml
from flext_cli._utilities.yaml import FlextCliUtilitiesYaml
from flext_core import FlextUtilities


class FlextCliUtilities(FlextUtilities):
    """CLI utility facade composed from internal utility mixins."""

    class Cli(
        FlextCliUtilitiesBase,
        FlextCliUtilitiesJson,
        FlextCliUtilitiesToml,
        FlextCliUtilitiesYaml,
    ):
        """Command line interface specific utilities."""


u = FlextCliUtilities

__all__ = ["FlextCliUtilities", "u"]
