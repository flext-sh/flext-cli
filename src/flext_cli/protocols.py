"""CLI protocol facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._protocols import FlextCliProtocolsBase
from flext_cli._protocols import FlextCliProtocolsConfig
from flext_cli._protocols import FlextCliProtocolsDomain
from flext_cli._protocols import FlextCliProtocolsFramework
from flext_cli._protocols import FlextCliProtocolsPipeline
from flext_cli._protocols import FlextCliProtocolsXlsx
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
    ):
        """Unified CLI protocol namespace."""


# mro-j47u (codex): canonical facade rebinding must stay type-annotated — an
# unannotated alias makes Mypy treat the facade as the class itself, turning
# class-subscript annotations such as `p.Result[str]` into Any downstream.
p = FlextCliProtocols  # canonical facade alias (annotated)

__all__: list[str] = ["FlextCliProtocols", "p"]
