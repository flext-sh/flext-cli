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
    from flext_cli._models.base import FlextCliModelsBase
_LAZY_IMPORTS = {
    "FlextCliModelsBase": "flext_cli._models.base",
    "base": "flext_cli._models.base",
}

__all__ = [
    "FlextCliModelsBase",
    "base",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
