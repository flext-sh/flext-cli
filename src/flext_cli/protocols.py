"""CLI protocol facade."""

from __future__ import annotations

from flext_core import p as _core_p

from ._protocols.base import FlextCliProtocolsBase
from ._protocols.config import FlextCliProtocolsConfig
from ._protocols.domain import FlextCliProtocolsDomain
from ._protocols.framework import FlextCliProtocolsFramework
from ._protocols.pipeline import FlextCliProtocolsPipeline
from ._protocols.xlsx import FlextCliProtocolsXlsx


class FlextCliProtocols(_core_p):
    """CLI protocol definitions extending FlextProtocols.

    CLI protocol refinements take precedence in MRO while ``Result`` and the
    other core protocol members remain inherited from ``FlextProtocols``.
    """

    class Cli(
        FlextCliProtocolsPipeline,
        FlextCliProtocolsDomain,
        FlextCliProtocolsFramework,
        FlextCliProtocolsBase,
        FlextCliProtocolsConfig,
        FlextCliProtocolsXlsx,
    ):
        """Unified CLI protocol namespace."""


# mro-j47u (codex): canonical facade rebinding must stay type-annotated — an
# unannotated alias makes Mypy treat the facade as the class itself, turning
# class-subscript annotations such as `p.Result[str]` into Any downstream.
p: type[FlextCliProtocols] = FlextCliProtocols  # canonical facade alias (annotated)

__all__: list[str] = ["FlextCliProtocols", "p"]
