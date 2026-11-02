# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Protocols package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._protocols.atomic_file import FlextCliProtocolsAtomicFile
    from flext_cli._protocols.base import FlextCliProtocolsBase
    from flext_cli._protocols.config import FlextCliProtocolsConfig
    from flext_cli._protocols.docx import FlextCliProtocolsDocx
    from flext_cli._protocols.domain import FlextCliProtocolsDomain
    from flext_cli._protocols.file_change import FlextCliProtocolsFileChange
    from flext_cli._protocols.framework import FlextCliProtocolsFramework
    from flext_cli._protocols.pipeline import FlextCliProtocolsPipeline
    from flext_cli._protocols.process import FlextCliProtocolsProcess
    from flext_cli._protocols.template import FlextCliProtocolsTemplate
    from flext_cli._protocols.xlsx import FlextCliProtocolsXlsx
    from flext_cli._protocols.xlsx_archive import FlextCliProtocolsXlsxArchive
    from flext_cli._protocols.xlsx_rules import FlextCliProtocolsXlsxRules
    from flext_cli._protocols.xlsx_snapshot import FlextCliProtocolsXlsxSnapshot
    from flext_cli._protocols.xlsx_snapshot_structure import (
        FlextCliProtocolsXlsxSnapshotStructure,
    )
    from flext_cli._protocols.xlsx_workbook import FlextCliProtocolsXlsxWorkbook


__all__: tuple[str, ...] = (
    "FlextCliProtocolsAtomicFile",
    "FlextCliProtocolsBase",
    "FlextCliProtocolsConfig",
    "FlextCliProtocolsDocx",
    "FlextCliProtocolsDomain",
    "FlextCliProtocolsFileChange",
    "FlextCliProtocolsFramework",
    "FlextCliProtocolsPipeline",
    "FlextCliProtocolsProcess",
    "FlextCliProtocolsTemplate",
    "FlextCliProtocolsXlsx",
    "FlextCliProtocolsXlsxArchive",
    "FlextCliProtocolsXlsxRules",
    "FlextCliProtocolsXlsxSnapshot",
    "FlextCliProtocolsXlsxSnapshotStructure",
    "FlextCliProtocolsXlsxWorkbook",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliProtocolsAtomicFile": ".atomic_file",
        "FlextCliProtocolsBase": ".base",
        "FlextCliProtocolsConfig": ".config",
        "FlextCliProtocolsDocx": ".docx",
        "FlextCliProtocolsDomain": ".domain",
        "FlextCliProtocolsFileChange": ".file_change",
        "FlextCliProtocolsFramework": ".framework",
        "FlextCliProtocolsPipeline": ".pipeline",
        "FlextCliProtocolsProcess": ".process",
        "FlextCliProtocolsTemplate": ".template",
        "FlextCliProtocolsXlsx": ".xlsx",
        "FlextCliProtocolsXlsxArchive": ".xlsx_archive",
        "FlextCliProtocolsXlsxRules": ".xlsx_rules",
        "FlextCliProtocolsXlsxSnapshot": ".xlsx_snapshot",
        "FlextCliProtocolsXlsxSnapshotStructure": ".xlsx_snapshot_structure",
        "FlextCliProtocolsXlsxWorkbook": ".xlsx_workbook",
    }),
    public_exports=__all__,
)
