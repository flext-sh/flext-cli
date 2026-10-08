"""CLI protocol facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._protocols import (
    FlextCliProtocolsBase,
    FlextCliProtocolsConfig,
    FlextCliProtocolsDomain,
    FlextCliProtocolsFramework,
    FlextCliProtocolsPipeline,
    FlextCliProtocolsXlsx,
)
from flext_cli._protocols.docx import FlextCliProtocolsDocx
from flext_cli._protocols.process import FlextCliProtocolsProcess
from flext_core import FlextProtocols


class FlextCliProtocols(FlextProtocols):
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
        FlextCliProtocolsProcess,
        FlextCliProtocolsDocx,
    ):
        """Unified CLI protocol namespace."""


p = FlextCliProtocols

__all__: list[str] = ["FlextCliProtocols", "p"]
