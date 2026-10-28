# AUTO-GENERATED FILE — Regenerate with: make gen
"""CLI protocol facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from flext_core import p as flext_core_p

from flext_cli._protocols import (
    FlextCliProtocolsAtomicFile,
    FlextCliProtocolsBase,
    FlextCliProtocolsConfig,
    FlextCliProtocolsDocx,
    FlextCliProtocolsDomain,
    FlextCliProtocolsFramework,
    FlextCliProtocolsPipeline,
    FlextCliProtocolsProcess,
    FlextCliProtocolsXlsx,
)


class FlextCliProtocols(flext_core_p):
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
        FlextCliProtocolsAtomicFile,
        FlextCliProtocolsDocx,
    ):
        """Unified CLI protocol namespace."""


p = FlextCliProtocols
__all__: list[str] = ["FlextCliProtocols", "p"]
