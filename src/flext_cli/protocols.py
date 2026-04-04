"""CLI protocol facade."""

from __future__ import annotations

from flext_cli._protocols.base import FlextCliProtocolsBase
from flext_cli._protocols.domain import FlextCliProtocolsDomain
from flext_core import FlextProtocols


class FlextCliProtocols(FlextProtocols):
    """CLI protocol definitions extending FlextProtocols."""

    class Cli(FlextCliProtocolsDomain, FlextCliProtocolsBase):
        """Unified CLI protocol namespace."""


p = FlextCliProtocols

__all__ = ["FlextCliProtocols", "p"]
