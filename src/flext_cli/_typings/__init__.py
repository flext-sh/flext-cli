# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Typings package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import flext_cli._typings.base as _flext_cli__typings_base

    base = _flext_cli__typings_base
    import flext_cli._typings.domain as _flext_cli__typings_domain
    from flext_cli._typings.base import FlextCliTypesBase

    domain = _flext_cli__typings_domain
    import flext_cli._typings.pipeline as _flext_cli__typings_pipeline
    from flext_cli._typings.domain import FlextCliTypesDomain

    pipeline = _flext_cli__typings_pipeline
    from flext_cli._typings.pipeline import FlextCliTypesPipeline
_LAZY_IMPORTS = {
    "FlextCliTypesBase": ("flext_cli._typings.base", "FlextCliTypesBase"),
    "FlextCliTypesDomain": ("flext_cli._typings.domain", "FlextCliTypesDomain"),
    "FlextCliTypesPipeline": ("flext_cli._typings.pipeline", "FlextCliTypesPipeline"),
    "base": "flext_cli._typings.base",
    "domain": "flext_cli._typings.domain",
    "pipeline": "flext_cli._typings.pipeline",
}

__all__ = [
    "FlextCliTypesBase",
    "FlextCliTypesDomain",
    "FlextCliTypesPipeline",
    "base",
    "domain",
    "pipeline",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
