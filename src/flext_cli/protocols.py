"""CLI protocol facade."""

from __future__ import annotations

from flext_cli._protocols.base import FlextCliProtocolsBase
from flext_cli._protocols.config import FlextCliProtocolsConfig
from flext_cli._protocols.domain import FlextCliProtocolsDomain
from flext_cli._protocols.framework import FlextCliProtocolsFramework
from flext_cli._protocols.pipeline import FlextCliProtocolsPipeline
from flext_cli._protocols.settings import FlextCliProtocolsSettings
from flext_cli._protocols.toml import FlextCliProtocolsToml
from flext_cli._protocols.xlsx import FlextCliProtocolsXlsx
from flext_core import p


class FlextCliProtocols(p):
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
        FlextCliProtocolsSettings,
        FlextCliProtocolsXlsx,
        FlextCliProtocolsToml,
    ):
        """Unified CLI protocol namespace."""


# mro-j47u (codex): canonical facade rebinding is intentionally unannotated.
p = FlextCliProtocols

__all__: list[str] = ["FlextCliProtocols", "p"]
