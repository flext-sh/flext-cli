# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Models package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import flext_cli._models.base as _flext_cli__models_base

    base = _flext_cli__models_base
    import flext_cli._models.pipeline as _flext_cli__models_pipeline
    from flext_cli._models.base import FlextCliModelsBase

    pipeline = _flext_cli__models_pipeline
    from flext_cli._models.pipeline import FlextCliModelsPipeline
_LAZY_IMPORTS = {
    "FlextCliModelsBase": ("flext_cli._models.base", "FlextCliModelsBase"),
    "FlextCliModelsPipeline": ("flext_cli._models.pipeline", "FlextCliModelsPipeline"),
    "base": "flext_cli._models.base",
    "pipeline": "flext_cli._models.pipeline",
}

__all__ = [
    "FlextCliModelsBase",
    "FlextCliModelsPipeline",
    "base",
    "pipeline",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
