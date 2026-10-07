"""Private MRO composition for generic XLSX models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import t
from flext_cli._models import (
    FlextCliModelsXlsxArchive,
    FlextCliModelsXlsxCells,
    FlextCliModelsXlsxLayout,
    FlextCliModelsXlsxRecalc,
    FlextCliModelsXlsxRules,
    FlextCliModelsXlsxSnapshot,
    FlextCliModelsXlsxStyleCatalog,
    FlextCliModelsXlsxStyles,
    FlextCliModelsXlsxTables,
    FlextCliModelsXlsxValidation,
    FlextCliModelsXlsxWorkbook,
)


class FlextCliModelsXlsx(
    FlextCliModelsXlsxSnapshot,
    FlextCliModelsXlsxRecalc,
    FlextCliModelsXlsxWorkbook,
    FlextCliModelsXlsxArchive,
    FlextCliModelsXlsxStyleCatalog,
    FlextCliModelsXlsxRules,
    FlextCliModelsXlsxValidation,
    FlextCliModelsXlsxTables,
    FlextCliModelsXlsxLayout,
    FlextCliModelsXlsxStyles,
    FlextCliModelsXlsxCells,
):
    """Canonical private XLSX model namespace."""

    # NOTE (multi-agent, mro-j2yt.1): snapshot declarations join the existing
    # XLSX namespace without a parallel public model surface.


__all__: t.VariadicTuple[str] = ("FlextCliModelsXlsx",)
