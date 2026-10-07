"""Private MRO composition for generic XLSX models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import t
from flext_cli._models import FlextCliModelsXlsxArchive
from flext_cli._models import FlextCliModelsXlsxCells
from flext_cli._models import FlextCliModelsXlsxLayout
from flext_cli._models import FlextCliModelsXlsxRecalc
from flext_cli._models import FlextCliModelsXlsxRules
from flext_cli._models import FlextCliModelsXlsxSnapshot
from flext_cli._models import FlextCliModelsXlsxStyleCatalog
from flext_cli._models import FlextCliModelsXlsxStyles
from flext_cli._models import FlextCliModelsXlsxTables
from flext_cli._models import FlextCliModelsXlsxValidation
from flext_cli._models import FlextCliModelsXlsxWorkbook


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
