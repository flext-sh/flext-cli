"""CLI protocol facade."""

from __future__ import annotations

from flext_cli._protocols.base import FlextCliProtocolsBase
from flext_cli._protocols.config import FlextCliProtocolsConfig
from flext_cli._protocols.domain import FlextCliProtocolsDomain
from flext_cli._protocols.pipeline import FlextCliProtocolsPipeline
from flext_core import FlextProtocols


class FlextCliProtocols(
    FlextCliProtocolsBase,
    FlextProtocols,
    FlextCliProtocolsConfig,
    FlextCliProtocolsDomain,
    FlextCliProtocolsPipeline,
):
    """CLI protocol definitions extending FlextProtocols.

    CLI protocol refinements take precedence in MRO while ``Result`` and the
    other core protocol members remain inherited from ``FlextProtocols``.
    """

    class Cli(
        FlextCliProtocolsPipeline,
        FlextCliProtocolsDomain,
        FlextCliProtocolsBase,
        FlextCliProtocolsConfig,
    ):
        """Unified CLI protocol namespace."""


p: type[FlextCliProtocols] = FlextCliProtocols

__all__: list[str] = ["FlextCliProtocols", "p"]
