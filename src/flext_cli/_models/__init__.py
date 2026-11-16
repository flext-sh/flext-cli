# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Models package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import defer_lazy_bases, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._models.atomic_publication import FlextCliModelsAtomicPublication
    from flext_cli._models.atomic_queries import FlextCliModelsAtomicQueries
    from flext_cli._models.atomic_state import FlextCliModelsAtomicState
    from flext_cli._models.atomic_symlink import FlextCliModelsAtomicSymlink
    from flext_cli._models.base import FlextCliModelsBase
    from flext_cli._models.color import FlextCliModelsColor
    from flext_cli._models.config import FlextCliModelsConfig
    from flext_cli._models.docx import FlextCliModelsDocx
    from flext_cli._models.docx_document import FlextCliModelsDocxDocument
    from flext_cli._models.docx_styles import FlextCliModelsDocxStyles
    from flext_cli._models.file_change import FlextCliModelsFileChange
    from flext_cli._models.files import FlextCliModelsFiles
    from flext_cli._models.markdown import FlextCliModelsMarkdown
    from flext_cli._models.pipeline import FlextCliModelsPipeline
    from flext_cli._models.pptx import FlextCliModelsPptx
    from flext_cli._models.pptx_presentation import FlextCliModelsPptxPresentation
    from flext_cli._models.process import FlextCliModelsProcess
    from flext_cli._models.process_runtime import FlextCliModelsProcessRuntime
    from flext_cli._models.rules import FlextCliModelsRules
    from flext_cli._models.table_render import FlextCliModelsTableRender
    from flext_cli._models.template import FlextCliModelsTemplate
    from flext_cli._models.xlsx import FlextCliModelsXlsx


__all__: tuple[str, ...] = (
    "FlextCliModelsAtomicPublication",
    "FlextCliModelsAtomicQueries",
    "FlextCliModelsAtomicState",
    "FlextCliModelsAtomicSymlink",
    "FlextCliModelsBase",
    "FlextCliModelsColor",
    "FlextCliModelsConfig",
    "FlextCliModelsDocx",
    "FlextCliModelsDocxDocument",
    "FlextCliModelsDocxStyles",
    "FlextCliModelsFileChange",
    "FlextCliModelsFiles",
    "FlextCliModelsMarkdown",
    "FlextCliModelsPipeline",
    "FlextCliModelsPptx",
    "FlextCliModelsPptxPresentation",
    "FlextCliModelsProcess",
    "FlextCliModelsProcessRuntime",
    "FlextCliModelsRules",
    "FlextCliModelsTableRender",
    "FlextCliModelsTemplate",
    "FlextCliModelsXlsx",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "FlextCliModelsAtomicPublication": ".atomic_publication",
        "FlextCliModelsAtomicQueries": ".atomic_queries",
        "FlextCliModelsAtomicState": ".atomic_state",
        "FlextCliModelsAtomicSymlink": ".atomic_symlink",
        "FlextCliModelsBase": ".base",
        "FlextCliModelsColor": ".color",
        "FlextCliModelsConfig": ".config",
        "FlextCliModelsDocx": ".docx",
        "FlextCliModelsDocxDocument": ".docx_document",
        "FlextCliModelsDocxStyles": ".docx_styles",
        "FlextCliModelsFileChange": ".file_change",
        "FlextCliModelsFiles": ".files",
        "FlextCliModelsMarkdown": ".markdown",
        "FlextCliModelsPipeline": ".pipeline",
        "FlextCliModelsPptx": ".pptx",
        "FlextCliModelsPptxPresentation": ".pptx_presentation",
        "FlextCliModelsProcess": ".process",
        "FlextCliModelsProcessRuntime": ".process_runtime",
        "FlextCliModelsRules": ".rules",
        "FlextCliModelsTableRender": ".table_render",
        "FlextCliModelsTemplate": ".template",
        "FlextCliModelsXlsx": ".xlsx",
    },
    public_exports=__all__,
    deferred_members={
        "FlextCliModelsAtomicPublication": (
            "StagedFile",
            "ObservedFile",
            "AtomicWriteOptions",
            "TreeEntryDetails",
        ),
        "FlextCliModelsAtomicQueries": (
            "AtomicDirectoryWorkingSelectors",
            "AtomicDirectorySelection",
            "AtomicDirectoryObservationRefs",
            "AtomicDirectoryQueryProof",
            "AtomicDirectoryQueryBoundary",
        ),
        "FlextCliModelsAtomicState": (
            "validate_atomic_state_path",
            "validate_parent_identity",
            "validate_non_reparse_state",
        ),
        "FlextCliModelsAtomicSymlink": (
            "AtomicSymlinkIdentity",
            "AtomicSymlinkState",
        ),
        "FlextCliModelsBase": (),
        "FlextCliModelsColor": (
            "RgbColor",
            "ThemeColor",
            "AutomaticColor",
        ),
        "FlextCliModelsConfig": (
            "Cli",
            "ProcessIsolation",
        ),
        "FlextCliModelsDocx": (),
        "FlextCliModelsDocxDocument": (
            "DocxRunPlan",
            "DocxParagraphPlan",
            "DocxTableCellPlan",
            "DocxTableRowPlan",
            "DocxTablePlan",
            "DocxSectionPlan",
            "DocxDocumentPlan",
            "DocxRenderRequest",
            "DocxRenderResult",
        ),
        "FlextCliModelsDocxStyles": (
            "DocxRgbColor",
            "DocxThemeColor",
            "DocxAutomaticColor",
            "DocxColor",
            "DocxFontSpec",
            "DocxParagraphFormatSpec",
            "DocxRunStyleSpec",
            "DocxParagraphStyleSpec",
        ),
        "FlextCliModelsFileChange": ("FileChange",),
        "FlextCliModelsFiles": ("FileAssertionOptions",),
        "FlextCliModelsMarkdown": (
            "MarkdownFence",
            "MarkdownLink",
            "MarkdownHeading",
            "MarkdownCodeSpan",
        ),
        "FlextCliModelsPipeline": (
            "PipelineStageContext",
            "PipelineStageSpec",
            "PipelineStageResult",
            "PipelineResult",
        ),
        "FlextCliModelsPptx": (),
        "FlextCliModelsPptxPresentation": (
            "PptxSlidePlan",
            "PptxPresentationPlan",
            "PptxRenderRequest",
            "PptxRenderResult",
        ),
        "FlextCliModelsProcess": (
            "PythonScriptExecution",
            "ProcessNativePolicyProbe",
            "ProcessNativeToolEvidence",
            "ProcessNativeToolQualification",
            "ProcessNativeQualificationReceipt",
            "ProcessNativeQualificationReport",
            "ProcessReadOnlyIsolation",
            "ProcessOptions",
            "RuntimeProcessRequest",
            "RuntimeProcessState",
            "RuntimeOutputTarget",
            "RuntimeSpawnOptions",
        ),
        "FlextCliModelsProcessRuntime": (
            "ProcessTreeSignal",
            "RuntimeProcessTiming",
            "RuntimeHeartbeat",
            "RuntimeMonitorPhase",
            "RuntimeOutputPlan",
            "RuntimeSpawnCommand",
            "RuntimePipeDrain",
            "ProcessIsolationSeal",
            "NativeElfLayout",
        ),
        "FlextCliModelsRules": ("LocalDefinitionsOptions",),
        "FlextCliModelsTableRender": (
            "TableColumnPolicy",
            "TableLayout",
        ),
        "FlextCliModelsTemplate": (
            "TemplateRenderOptions",
            "TemplateRenderEntry",
            "TemplateRenderReport",
            "AuthenticatedTemplateRender",
        ),
        "FlextCliModelsXlsx": (),
    },
)

defer_lazy_bases(
    __name__,
    {
        "FlextCliModelsBase": (
            (".", "FlextCliModelsAtomicPublication"),
            (".", "FlextCliModelsAtomicSymlink"),
            ("flext_cli._models._base", "FlextCliModelsBasePart01"),
            ("flext_cli._models._base", "FlextCliModelsBasePart02"),
            ("flext_cli._models._base", "FlextCliModelsBasePart03"),
            ("flext_cli._models._base", "FlextCliModelsBasePart04"),
            ("flext_cli._models._base", "FlextCliModelsBasePart05"),
            ("flext_cli._models._base", "FlextCliModelsBasePart06"),
            ("flext_cli._models._base", "FlextCliModelsBasePart07"),
            ("flext_cli._models._base", "FlextCliModelsBasePart08"),
            ("flext_cli._models._base", "FlextCliModelsBasePart09"),
            ("flext_cli._models._base", "FlextCliModelsBasePart10"),
        ),
        "FlextCliModelsDocx": (
            (".", "FlextCliModelsDocxDocument"),
            (".", "FlextCliModelsDocxStyles"),
        ),
        "FlextCliModelsPptx": ((".", "FlextCliModelsPptxPresentation"),),
        "FlextCliModelsXlsx": (
            ("flext_cli._models._xlsx", "FlextCliModelsXlsxSnapshot"),
            ("flext_cli._models._xlsx", "FlextCliModelsXlsxRecalc"),
            ("flext_cli._models._xlsx", "FlextCliModelsXlsxWorkbook"),
            ("flext_cli._models._xlsx", "FlextCliModelsXlsxArchive"),
            ("flext_cli._models._xlsx", "FlextCliModelsXlsxStyleCatalog"),
            ("flext_cli._models._xlsx", "FlextCliModelsXlsxRules"),
            ("flext_cli._models._xlsx", "FlextCliModelsXlsxValidation"),
            ("flext_cli._models._xlsx", "FlextCliModelsXlsxTables"),
            ("flext_cli._models._xlsx", "FlextCliModelsXlsxLayout"),
            ("flext_cli._models._xlsx", "FlextCliModelsXlsxStyles"),
            ("flext_cli._models._xlsx", "FlextCliModelsXlsxCells"),
        ),
    },
)
