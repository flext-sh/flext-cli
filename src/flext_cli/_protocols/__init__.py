# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Protocols package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._protocols.atomic_file import FlextCliProtocolsAtomicFile
    from flext_cli._protocols.atomic_publication import (
        FlextCliProtocolsAtomicPublication,
    )
    from flext_cli._protocols.atomic_queries import FlextCliProtocolsAtomicQueries
    from flext_cli._protocols.atomic_symlink import FlextCliProtocolsAtomicSymlink
    from flext_cli._protocols.base import FlextCliProtocolsBase
    from flext_cli._protocols.color import FlextCliProtocolsColor
    from flext_cli._protocols.config import FlextCliProtocolsConfig
    from flext_cli._protocols.docx import FlextCliProtocolsDocx
    from flext_cli._protocols.docx_document import FlextCliProtocolsDocxDocument
    from flext_cli._protocols.docx_styles import FlextCliProtocolsDocxStyles
    from flext_cli._protocols.domain import FlextCliProtocolsDomain
    from flext_cli._protocols.file_change import FlextCliProtocolsFileChange
    from flext_cli._protocols.files import FlextCliProtocolsFiles
    from flext_cli._protocols.framework import FlextCliProtocolsFramework
    from flext_cli._protocols.markdown import FlextCliProtocolsMarkdown
    from flext_cli._protocols.pipeline import FlextCliProtocolsPipeline
    from flext_cli._protocols.pptx_presentation import FlextCliProtocolsPptxPresentation
    from flext_cli._protocols.process import FlextCliProtocolsProcess
    from flext_cli._protocols.process_runtime import FlextCliProtocolsProcessRuntime
    from flext_cli._protocols.rules import FlextCliProtocolsRules
    from flext_cli._protocols.table_render import FlextCliProtocolsTableRender
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
    "FlextCliProtocolsAtomicPublication",
    "FlextCliProtocolsAtomicQueries",
    "FlextCliProtocolsAtomicSymlink",
    "FlextCliProtocolsBase",
    "FlextCliProtocolsColor",
    "FlextCliProtocolsConfig",
    "FlextCliProtocolsDocx",
    "FlextCliProtocolsDocxDocument",
    "FlextCliProtocolsDocxStyles",
    "FlextCliProtocolsDomain",
    "FlextCliProtocolsFileChange",
    "FlextCliProtocolsFiles",
    "FlextCliProtocolsFramework",
    "FlextCliProtocolsMarkdown",
    "FlextCliProtocolsPipeline",
    "FlextCliProtocolsPptxPresentation",
    "FlextCliProtocolsProcess",
    "FlextCliProtocolsProcessRuntime",
    "FlextCliProtocolsRules",
    "FlextCliProtocolsTableRender",
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
    {
        "FlextCliProtocolsAtomicFile": ".atomic_file",
        "FlextCliProtocolsAtomicPublication": ".atomic_publication",
        "FlextCliProtocolsAtomicQueries": ".atomic_queries",
        "FlextCliProtocolsAtomicSymlink": ".atomic_symlink",
        "FlextCliProtocolsBase": ".base",
        "FlextCliProtocolsColor": ".color",
        "FlextCliProtocolsConfig": ".config",
        "FlextCliProtocolsDocx": ".docx",
        "FlextCliProtocolsDocxDocument": ".docx_document",
        "FlextCliProtocolsDocxStyles": ".docx_styles",
        "FlextCliProtocolsDomain": ".domain",
        "FlextCliProtocolsFileChange": ".file_change",
        "FlextCliProtocolsFiles": ".files",
        "FlextCliProtocolsFramework": ".framework",
        "FlextCliProtocolsMarkdown": ".markdown",
        "FlextCliProtocolsPipeline": ".pipeline",
        "FlextCliProtocolsPptxPresentation": ".pptx_presentation",
        "FlextCliProtocolsProcess": ".process",
        "FlextCliProtocolsProcessRuntime": ".process_runtime",
        "FlextCliProtocolsRules": ".rules",
        "FlextCliProtocolsTableRender": ".table_render",
        "FlextCliProtocolsTemplate": ".template",
        "FlextCliProtocolsXlsx": ".xlsx",
        "FlextCliProtocolsXlsxArchive": ".xlsx_archive",
        "FlextCliProtocolsXlsxRules": ".xlsx_rules",
        "FlextCliProtocolsXlsxSnapshot": ".xlsx_snapshot",
        "FlextCliProtocolsXlsxSnapshotStructure": ".xlsx_snapshot_structure",
        "FlextCliProtocolsXlsxWorkbook": ".xlsx_workbook",
    },
    public_exports=__all__,
)
