# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Protocols package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._protocols import _base_parts
    from flext_cli._protocols.base import FlextCliProtocolsBase
    from flext_cli._protocols.config import FlextCliProtocolsConfig
    from flext_cli._protocols.domain import FlextCliProtocolsDomain
    from flext_cli._protocols.framework import FlextCliProtocolsFramework
    from flext_cli._protocols.pipeline import FlextCliProtocolsPipeline
    from flext_cli._protocols.xlsx import FlextCliProtocolsXlsx
    from flext_cli._protocols.xlsx_archive import FlextCliProtocolsXlsxArchive
    from flext_cli._protocols.xlsx_rules import FlextCliProtocolsXlsxRules
    from flext_cli._protocols.xlsx_snapshot import FlextCliProtocolsXlsxSnapshot
    from flext_cli._protocols.xlsx_snapshot_structure import (
        FlextCliProtocolsXlsxSnapshotStructure,
    )
    from flext_cli._protocols.xlsx_workbook import FlextCliProtocolsXlsxWorkbook


__all__: tuple[str, ...] = (
    "FlextCliProtocolsBase",
    "FlextCliProtocolsConfig",
    "FlextCliProtocolsDomain",
    "FlextCliProtocolsFramework",
    "FlextCliProtocolsPipeline",
    "FlextCliProtocolsXlsx",
    "FlextCliProtocolsXlsxArchive",
    "FlextCliProtocolsXlsxRules",
    "FlextCliProtocolsXlsxSnapshot",
    "FlextCliProtocolsXlsxSnapshotStructure",
    "FlextCliProtocolsXlsxWorkbook",
    "_base_parts",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliProtocolsBase": ".base",
        "FlextCliProtocolsConfig": ".config",
        "FlextCliProtocolsDomain": ".domain",
        "FlextCliProtocolsFramework": ".framework",
        "FlextCliProtocolsPipeline": ".pipeline",
        "FlextCliProtocolsXlsx": ".xlsx",
        "FlextCliProtocolsXlsxArchive": ".xlsx_archive",
        "FlextCliProtocolsXlsxRules": ".xlsx_rules",
        "FlextCliProtocolsXlsxSnapshot": ".xlsx_snapshot",
        "FlextCliProtocolsXlsxSnapshotStructure": ".xlsx_snapshot_structure",
        "FlextCliProtocolsXlsxWorkbook": ".xlsx_workbook",
        "_base_parts": "._base_parts",
    }),
    public_exports=__all__,
)
