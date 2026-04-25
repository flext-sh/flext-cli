"""CLI type facade."""

from __future__ import annotations

from flext_core import FlextTypes
from yaml import YAMLError

from flext_cli import FlextCliTypesDomain, FlextCliTypesPipeline
from flext_cli._typings.base import FlextCliTypesBase


class FlextCliTypes(FlextTypes):
    """CLI type definitions extending flext-core FlextTypes via inheritance."""

    class Cli(FlextCliTypesPipeline, FlextCliTypesDomain, FlextCliTypesBase):
        """CLI types namespace for cross-project access."""

        YAMLError: type[Exception] = YAMLError


t: type[FlextCliTypes] = FlextCliTypes

__all__: list[str] = ["FlextCliTypes", "t"]
