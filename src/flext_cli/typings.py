"""CLI type facade."""

from __future__ import annotations

from flext_core import t
from yaml import YAMLError as _YamlError

from flext_cli import FlextCliTypesBase, FlextCliTypesDomain, FlextCliTypesPipeline


class FlextCliTypes(t):
    """CLI type definitions extending flext-core FlextTypes via inheritance."""

    class Cli(FlextCliTypesPipeline, FlextCliTypesDomain, FlextCliTypesBase):
        """CLI types namespace for cross-project access."""

        YAMLError: type[Exception] = _YamlError


t = FlextCliTypes

__all__: list[str] = ["FlextCliTypes", "t"]
