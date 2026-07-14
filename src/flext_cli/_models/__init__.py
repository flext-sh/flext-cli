# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Models package."""

from __future__ import annotations

from typing import TYPE_CHECKING

# mro-i6nq.10: The package consumes its manifest's public-export contract.
from flext_cli._models.__unit__ import (
    CHILD_MODULE_PATHS as _CHILD_MODULE_PATHS,
    EXCLUDED_LAZY_NAMES as _EXCLUDED_LAZY_NAMES,
    PUBLIC_EXPORTS as _PUBLIC_EXPORTS,
)
from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if TYPE_CHECKING:
    from flext_cli._models import _base_parts as _base_parts
    from flext_cli._models._base_parts.flextclimodelsbase_part_07 import (
        FlextCliModelsBase as FlextCliModelsBase,
    )
    from flext_cli._models._test_tmp import X as X
    from flext_cli._models.config import FlextCliConfigModels as FlextCliConfigModels
    from flext_cli._models.pipeline import (
        FlextCliModelsPipeline as FlextCliModelsPipeline,
    )
    from flext_cli._models.rules import FlextCliModelsRules as FlextCliModelsRules
    from flext_cli._models.template import (
        FlextCliModelsTemplate as FlextCliModelsTemplate,
    )
    from flext_cli._models.xlsx import FlextCliModelsXlsx as FlextCliModelsXlsx
    from flext_cli._models.xlsx_archive import (
        FlextCliModelsXlsxArchive as FlextCliModelsXlsxArchive,
    )
    from flext_cli._models.xlsx_cells import (
        FlextCliModelsXlsxCells as FlextCliModelsXlsxCells,
    )
    from flext_cli._models.xlsx_layout import (
        FlextCliModelsXlsxLayout as FlextCliModelsXlsxLayout,
    )
    from flext_cli._models.xlsx_recalc import (
        FlextCliModelsXlsxRecalc as FlextCliModelsXlsxRecalc,
    )
    from flext_cli._models.xlsx_rules import (
        FlextCliModelsXlsxRules as FlextCliModelsXlsxRules,
    )
    from flext_cli._models.xlsx_snapshot import (
        FlextCliModelsXlsxSnapshot as FlextCliModelsXlsxSnapshot,
    )
    from flext_cli._models.xlsx_style_catalog import (
        FlextCliModelsXlsxStyleCatalog as FlextCliModelsXlsxStyleCatalog,
    )
    from flext_cli._models.xlsx_style_fills import (
        FlextCliModelsXlsxStyleFills as FlextCliModelsXlsxStyleFills,
    )
    from flext_cli._models.xlsx_style_primitives import (
        FlextCliModelsXlsxStylePrimitives as FlextCliModelsXlsxStylePrimitives,
    )
    from flext_cli._models.xlsx_styles import (
        FlextCliModelsXlsxStyles as FlextCliModelsXlsxStyles,
    )
    from flext_cli._models.xlsx_tables import (
        FlextCliModelsXlsxTables as FlextCliModelsXlsxTables,
    )
    from flext_cli._models.xlsx_validation import (
        FlextCliModelsXlsxValidation as FlextCliModelsXlsxValidation,
    )
    from flext_cli._models.xlsx_workbook import (
        FlextCliModelsXlsxWorkbook as FlextCliModelsXlsxWorkbook,
    )

    # mro-i6nq.10: Static declaration mirrors the installer-owned runtime binding.
    __all__: tuple[str, ...]


_LAZY_IMPORTS = merge_lazy_imports(
    _CHILD_MODULE_PATHS,
    build_lazy_import_map(
        _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
    ),
    exclude_names=_EXCLUDED_LAZY_NAMES,
    module_name=__name__,
)


# mro-i6nq.10: The installer publishes __all__ from the manifest's literal ABI.
install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=_PUBLIC_EXPORTS)
