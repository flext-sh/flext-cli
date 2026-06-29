"""CLI type facade."""

from __future__ import annotations

from flext_cli._typings.base import FlextCliTypesBase
from flext_cli._typings.domain import FlextCliTypesDomain
from flext_cli._typings.pipeline import FlextCliTypesPipeline
from flext_core import FlextTypes


class FlextCliTypes(FlextTypes):
    """CLI type definitions extending flext-core FlextTypes via inheritance."""

    class Cli(FlextCliTypesPipeline, FlextCliTypesDomain, FlextCliTypesBase):
        """CLI types namespace for cross-project access."""


t: type[FlextCliTypes] = FlextCliTypes

__all__: list[str] = ["FlextCliTypes", "t"]
