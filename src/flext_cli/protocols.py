"""CLI protocol facade."""

from __future__ import annotations

from flext_cli import (
    FlextCliProtocolsBase,
    FlextCliProtocolsDomain,
    FlextCliProtocolsPipeline,
)
from flext_core import FlextProtocols


class FlextCliProtocols(
    FlextProtocols,
    FlextCliProtocolsBase,
    FlextCliProtocolsDomain,
    FlextCliProtocolsPipeline,
):
    """CLI protocol definitions extending FlextProtocols."""

    class Cli(
        FlextCliProtocolsPipeline, FlextCliProtocolsDomain, FlextCliProtocolsBase
    ):
        """Unified CLI protocol namespace."""


p: type[FlextCliProtocols] = FlextCliProtocols

__all__: list[str] = ["FlextCliProtocols", "p"]

p = FlextCliProtocols
