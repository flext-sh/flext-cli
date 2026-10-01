# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Xlxx package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._xlxx.xlsx_addresses import FlextCliUtilitiesXlsxAddresses
    from flext_cli._utilities._xlxx.xlsx_archive import FlextCliUtilitiesXlsxArchive
    from flext_cli._utilities._xlxx.xlsx_archive_checks import (
        FlextCliUtilitiesXlsxArchiveChecks,
    )
    from flext_cli._utilities._xlxx.xlsx_cells import FlextCliUtilitiesXlsxCells
    from flext_cli._utilities._xlxx.xlsx_conditional import (
        FlextCliUtilitiesXlsxConditional,
    )
    from flext_cli._utilities._xlxx.xlsx_defined_name_values import (
        FlextCliUtilitiesXlsxDefinedNameValues,
    )
    from flext_cli._utilities._xlxx.xlsx_formula_codec import (
        FlextCliUtilitiesXlsxFormulaCodec,
    )
    from flext_cli._utilities._xlxx.xlsx_layout import FlextCliUtilitiesXlsxLayout
    from flext_cli._utilities._xlxx.xlsx_protection import (
        FlextCliUtilitiesXlsxProtection,
    )
    from flext_cli._utilities._xlxx.xlsx_recalc import FlextCliUtilitiesXlsxRecalc
    from flext_cli._utilities._xlxx.xlsx_recalc_evidence import (
        FlextCliUtilitiesXlsxRecalcEvidence,
    )
    from flext_cli._utilities._xlxx.xlsx_renderer import FlextCliUtilitiesXlsxRenderer
    from flext_cli._utilities._xlxx.xlsx_rules import FlextCliUtilitiesXlsxRules
    from flext_cli._utilities._xlxx.xlsx_snapshot import FlextCliUtilitiesXlsxSnapshot
    from flext_cli._utilities._xlxx.xlsx_snapshot_sheet import (
        FlextCliUtilitiesXlsxSnapshotSheet,
    )
    from flext_cli._utilities._xlxx.xlsx_snapshot_structure import (
        FlextCliUtilitiesXlsxSnapshotStructure,
    )
    from flext_cli._utilities._xlxx.xlsx_snapshot_values import (
        FlextCliUtilitiesXlsxSnapshotValues,
    )
    from flext_cli._utilities._xlxx.xlsx_style_builders import (
        FlextCliUtilitiesXlsxStyleBuilders,
    )
    from flext_cli._utilities._xlxx.xlsx_style_catalog import (
        FlextCliUtilitiesXlsxStyleCatalog,
    )
    from flext_cli._utilities._xlxx.xlsx_style_codec import (
        FlextCliUtilitiesXlsxStyleCodec,
    )
    from flext_cli._utilities._xlxx.xlsx_style_readers import (
        FlextCliUtilitiesXlsxStyleReaders,
    )
    from flext_cli._utilities._xlxx.xlsx_tables import FlextCliUtilitiesXlsxTables
    from flext_cli._utilities._xlxx.xlsx_validations import (
        FlextCliUtilitiesXlsxValidations,
    )
    from flext_cli._utilities._xlxx.xlsx_workbook_io import (
        FlextCliUtilitiesXlsxWorkbookIo,
    )
    from flext_cli._utilities._xlxx.xlsx_workbook_plan import (
        FlextCliUtilitiesXlsxWorkbookPlan,
    )


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesXlsxAddresses",
    "FlextCliUtilitiesXlsxArchive",
    "FlextCliUtilitiesXlsxArchiveChecks",
    "FlextCliUtilitiesXlsxCells",
    "FlextCliUtilitiesXlsxConditional",
    "FlextCliUtilitiesXlsxDefinedNameValues",
    "FlextCliUtilitiesXlsxFormulaCodec",
    "FlextCliUtilitiesXlsxLayout",
    "FlextCliUtilitiesXlsxProtection",
    "FlextCliUtilitiesXlsxRecalc",
    "FlextCliUtilitiesXlsxRecalcEvidence",
    "FlextCliUtilitiesXlsxRenderer",
    "FlextCliUtilitiesXlsxRules",
    "FlextCliUtilitiesXlsxSnapshot",
    "FlextCliUtilitiesXlsxSnapshotSheet",
    "FlextCliUtilitiesXlsxSnapshotStructure",
    "FlextCliUtilitiesXlsxSnapshotValues",
    "FlextCliUtilitiesXlsxStyleBuilders",
    "FlextCliUtilitiesXlsxStyleCatalog",
    "FlextCliUtilitiesXlsxStyleCodec",
    "FlextCliUtilitiesXlsxStyleReaders",
    "FlextCliUtilitiesXlsxTables",
    "FlextCliUtilitiesXlsxValidations",
    "FlextCliUtilitiesXlsxWorkbookIo",
    "FlextCliUtilitiesXlsxWorkbookPlan",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".xlsx_addresses": ("FlextCliUtilitiesXlsxAddresses",),
            ".xlsx_archive": ("FlextCliUtilitiesXlsxArchive",),
            ".xlsx_archive_checks": ("FlextCliUtilitiesXlsxArchiveChecks",),
            ".xlsx_cells": ("FlextCliUtilitiesXlsxCells",),
            ".xlsx_conditional": ("FlextCliUtilitiesXlsxConditional",),
            ".xlsx_defined_name_values": ("FlextCliUtilitiesXlsxDefinedNameValues",),
            ".xlsx_formula_codec": ("FlextCliUtilitiesXlsxFormulaCodec",),
            ".xlsx_layout": ("FlextCliUtilitiesXlsxLayout",),
            ".xlsx_protection": ("FlextCliUtilitiesXlsxProtection",),
            ".xlsx_recalc": ("FlextCliUtilitiesXlsxRecalc",),
            ".xlsx_recalc_evidence": ("FlextCliUtilitiesXlsxRecalcEvidence",),
            ".xlsx_renderer": ("FlextCliUtilitiesXlsxRenderer",),
            ".xlsx_rules": ("FlextCliUtilitiesXlsxRules",),
            ".xlsx_snapshot": ("FlextCliUtilitiesXlsxSnapshot",),
            ".xlsx_snapshot_sheet": ("FlextCliUtilitiesXlsxSnapshotSheet",),
            ".xlsx_snapshot_structure": ("FlextCliUtilitiesXlsxSnapshotStructure",),
            ".xlsx_snapshot_values": ("FlextCliUtilitiesXlsxSnapshotValues",),
            ".xlsx_style_builders": ("FlextCliUtilitiesXlsxStyleBuilders",),
            ".xlsx_style_catalog": ("FlextCliUtilitiesXlsxStyleCatalog",),
            ".xlsx_style_codec": ("FlextCliUtilitiesXlsxStyleCodec",),
            ".xlsx_style_readers": ("FlextCliUtilitiesXlsxStyleReaders",),
            ".xlsx_tables": ("FlextCliUtilitiesXlsxTables",),
            ".xlsx_validations": ("FlextCliUtilitiesXlsxValidations",),
            ".xlsx_workbook_io": ("FlextCliUtilitiesXlsxWorkbookIo",),
            ".xlsx_workbook_plan": ("FlextCliUtilitiesXlsxWorkbookPlan",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
