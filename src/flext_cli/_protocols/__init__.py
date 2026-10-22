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
    from flext_cli._protocols import _base as _base
    from flext_cli._protocols._base import (
        FlextCliProtocolsBasePart01,
        FlextCliProtocolsBasePart02,
        FlextCliProtocolsBasePart03,
        FlextCliProtocolsBasePart04,
        FlextCliProtocolsBasePart05,
    )
    from flext_cli._protocols.atomic_file import FlextCliProtocolsAtomicFile
    from flext_cli._protocols.base import FlextCliProtocolsBase
    from flext_cli._protocols.config import FlextCliProtocolsConfig
    from flext_cli._protocols.docx import FlextCliProtocolsDocx
    from flext_cli._protocols.domain import FlextCliProtocolsDomain
    from flext_cli._protocols.framework import FlextCliProtocolsFramework
    from flext_cli._protocols.pipeline import FlextCliProtocolsPipeline
    from flext_cli._protocols.process import FlextCliProtocolsProcess
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
    "FlextCliProtocolsBasePart01",
    "FlextCliProtocolsBasePart02",
    "FlextCliProtocolsBasePart03",
    "FlextCliProtocolsBasePart04",
    "FlextCliProtocolsBasePart05",
    "FlextCliProtocolsConfig",
    "FlextCliProtocolsDocx",
    "FlextCliProtocolsDomain",
    "FlextCliProtocolsFramework",
    "FlextCliProtocolsPipeline",
    "FlextCliProtocolsProcess",
    "FlextCliProtocolsXlsx",
    "FlextCliProtocolsXlsxArchive",
    "FlextCliProtocolsXlsxRules",
    "FlextCliProtocolsXlsxSnapshot",
    "FlextCliProtocolsXlsxSnapshotStructure",
    "FlextCliProtocolsXlsxWorkbook",
    "_base",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliProtocolsAtomicFile": ".atomic_file",
        "FlextCliProtocolsBase": ".base",
        "FlextCliProtocolsBasePart01": "._base.flextcliprotocolsbase_part_01",
        "FlextCliProtocolsBasePart02": "._base.flextcliprotocolsbase_part_02",
        "FlextCliProtocolsBasePart03": "._base.flextcliprotocolsbase_part_03",
        "FlextCliProtocolsBasePart04": "._base.flextcliprotocolsbase_part_04",
        "FlextCliProtocolsBasePart05": "._base.flextcliprotocolsbase_part_05",
        "FlextCliProtocolsConfig": ".config",
        "FlextCliProtocolsDocx": ".docx",
        "FlextCliProtocolsDomain": ".domain",
        "FlextCliProtocolsFramework": ".framework",
        "FlextCliProtocolsPipeline": ".pipeline",
        "FlextCliProtocolsProcess": ".process",
        "FlextCliProtocolsXlsx": ".xlsx",
        "FlextCliProtocolsXlsxArchive": ".xlsx_archive",
        "FlextCliProtocolsXlsxRules": ".xlsx_rules",
        "FlextCliProtocolsXlsxSnapshot": ".xlsx_snapshot",
        "FlextCliProtocolsXlsxSnapshotStructure": ".xlsx_snapshot_structure",
        "FlextCliProtocolsXlsxWorkbook": ".xlsx_workbook",
        "_base": "._base",
    }),
    public_exports=__all__,
)
