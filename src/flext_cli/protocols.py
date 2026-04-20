"""CLI protocol facade."""

from __future__ import annotations

from flext_core import p

from flext_cli import (
    FlextCliProtocolsBase,
    FlextCliProtocolsDomain,
    FlextCliProtocolsPipeline,
)


class FlextCliProtocols(p):
    """CLI protocol definitions extending FlextProtocols."""

    class Cli(
        FlextCliProtocolsPipeline, FlextCliProtocolsDomain, FlextCliProtocolsBase
    ):
        """Unified CLI protocol namespace."""


p = FlextCliProtocols

__all__: list[str] = ["FlextCliProtocols", "p"]
