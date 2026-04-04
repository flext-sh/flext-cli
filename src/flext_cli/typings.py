"""CLI type facade."""

from __future__ import annotations

from flext_cli._typings.base import FlextCliTypesBase
from flext_cli._typings.domain import FlextCliTypesDomain
from flext_core import FlextTypes


class FlextCliTypes(FlextTypes):
    """CLI type definitions extending FlextTypes via inheritance."""

    class Cli(FlextCliTypesDomain, FlextCliTypesBase):
        """CLI types namespace for cross-project access."""


t = FlextCliTypes

__all__ = ["FlextCliTypes", "t"]
