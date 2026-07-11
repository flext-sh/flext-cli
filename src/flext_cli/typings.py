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


# NOTE (multi-agent): bare assignment, NOT ``t: type[FlextCliTypes] = ...``.
# Pyright cannot resolve nested class-scope PEP 695 aliases through an
# explicitly annotated ``type[X]`` variable (every ``t.Cli.*`` alias became
# Unknown — proven via reveal_type on the pre-existing TomlMappingSource).
# The bare form keeps mypy/pyrefly/pyright resolution correct for all aliases.
t = FlextCliTypes

__all__: list[str] = ["FlextCliTypes", "t"]
