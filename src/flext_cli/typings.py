"""CLI type facade."""

from __future__ import annotations

from flext_core import t

from ._typings.base import FlextCliTypesBase
from ._typings.domain import FlextCliTypesDomain
from ._typings.pipeline import FlextCliTypesPipeline
from ._typings.xlsx import FlextCliTypesXlsx


class FlextCliTypes(t):
    """CLI type definitions extending flext-core FlextTypes via inheritance."""

    class Cli(
        FlextCliTypesPipeline, FlextCliTypesDomain, FlextCliTypesBase, FlextCliTypesXlsx
    ):
        """CLI types namespace for cross-project access."""


t = FlextCliTypes

__all__: list[str] = ["FlextCliTypes", "t"]
