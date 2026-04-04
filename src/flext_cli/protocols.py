"""CLI protocol facade."""

from __future__ import annotations

from flext_cli import FlextCliProtocolsBase, FlextCliProtocolsDomain
from flext_core import FlextProtocols


class FlextCliProtocols(FlextProtocols):
    """CLI protocol definitions extending FlextProtocols."""

    class Cli(FlextCliProtocolsDomain, FlextCliProtocolsBase):
        """Unified CLI protocol namespace."""


p = FlextCliProtocols

__all__ = ["FlextCliProtocols", "p"]
