"""Private MRO composition for generic XLSX models.

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

from flext_cli._models._xlsx import (
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


__all__: tuple[str, ...] = ("FlextCliModelsXlsx",)
