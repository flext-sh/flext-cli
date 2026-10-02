# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Protocols package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

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

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._base_parts": ("_base_parts",),
            ".base": ("FlextCliProtocolsBase",),
            ".config": ("FlextCliProtocolsConfig",),
            ".domain": ("FlextCliProtocolsDomain",),
            ".framework": ("FlextCliProtocolsFramework",),
            ".pipeline": ("FlextCliProtocolsPipeline",),
            ".xlsx": ("FlextCliProtocolsXlsx",),
            ".xlsx_archive": ("FlextCliProtocolsXlsxArchive",),
            ".xlsx_rules": ("FlextCliProtocolsXlsxRules",),
            ".xlsx_snapshot": ("FlextCliProtocolsXlsxSnapshot",),
            ".xlsx_snapshot_structure": ("FlextCliProtocolsXlsxSnapshotStructure",),
            ".xlsx_workbook": ("FlextCliProtocolsXlsxWorkbook",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
