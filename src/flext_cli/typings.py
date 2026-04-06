"""CLI type facade."""

from __future__ import annotations

from yaml import YAMLError as _YamlError

from flext_cli import FlextCliTypesBase, FlextCliTypesDomain, FlextCliTypesPipeline
from flext_core import FlextTypes


class FlextCliTypes(FlextTypes):
    """CLI type definitions extending FlextTypes via inheritance."""

    class Cli(FlextCliTypesPipeline, FlextCliTypesDomain, FlextCliTypesBase):
        """CLI types namespace for cross-project access."""

        YAMLError: type[Exception] = _YamlError


t = FlextCliTypes

__all__ = ["FlextCliTypes", "t"]
