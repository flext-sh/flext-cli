"""CLI type facade."""

from __future__ import annotations

from flext_core import FlextTypes
from yaml import YAMLError

from flext_cli import FlextCliTypesBase, FlextCliTypesDomain, FlextCliTypesPipeline


class FlextCliTypes(FlextTypes):
    """CLI type definitions extending flext-core FlextTypes via inheritance."""

    class Cli(FlextCliTypesPipeline, FlextCliTypesDomain, FlextCliTypesBase):
        """CLI types namespace for cross-project access."""

        YAMLError: type[Exception] = YAMLError


t: type[FlextCliTypes] = FlextCliTypes

__all__: list[str] = ["FlextCliTypes", "t"]
