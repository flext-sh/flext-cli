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
    from flext_cli._typings.domain import FlextCliTypesDomain
_LAZY_IMPORTS = {
    "FlextCliTypesBase": ("flext_cli._typings.base", "FlextCliTypesBase"),
    "FlextCliTypesDomain": ("flext_cli._typings.domain", "FlextCliTypesDomain"),
    "base": "flext_cli._typings.base",
    "domain": "flext_cli._typings.domain",
}

__all__ = [
    "FlextCliTypesBase",
    "FlextCliTypesDomain",
    "base",
    "domain",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
