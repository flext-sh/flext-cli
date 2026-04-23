"""CLI protocol facade."""

from __future__ import annotations

from flext_core import FlextProtocols

from flext_cli import (
    FlextCliProtocolsBase,
    FlextCliProtocolsDomain,
    FlextCliProtocolsPipeline,
)


class FlextCliProtocols(FlextProtocols):
    """CLI protocol definitions extending FlextProtocols."""

    class Cli(
        FlextCliProtocolsPipeline, FlextCliProtocolsDomain, FlextCliProtocolsBase
    ):
        """Unified CLI protocol namespace."""


p: type[FlextCliProtocols] = FlextCliProtocols

__all__: list[str] = ["FlextCliProtocols", "p"]
