"""CLI protocol facade."""

from __future__ import annotations

from flext_cli._protocols.base import FlextCliProtocolsBase
from flext_cli._protocols.domain import FlextCliProtocolsDomain
from flext_cli._protocols.pipeline import FlextCliProtocolsPipeline
from flext_core import FlextProtocols


class FlextCliProtocols(
    FlextProtocols,
    FlextCliProtocolsBase,
    FlextCliProtocolsDomain,
    FlextCliProtocolsPipeline,
):
    """CLI protocol definitions extending FlextProtocols.

    ``Result`` and the other protocol members are inherited from
    ``FlextProtocols`` via MRO; re-binding them as class variables would
    shadow the nested protocol classes and make them invalid as types.
    """

    class Cli(
        FlextCliProtocolsPipeline,
        FlextCliProtocolsDomain,
        FlextCliProtocolsBase,
    ):
        """Unified CLI protocol namespace."""


p: type[FlextCliProtocols] = FlextCliProtocols

__all__: list[str] = ["FlextCliProtocols", "p"]
