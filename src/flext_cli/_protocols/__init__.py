# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Protocols package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import flext_cli._protocols.base as _flext_cli__protocols_base

    base = _flext_cli__protocols_base
    from flext_cli._protocols.base import FlextCliProtocolsBase
_LAZY_IMPORTS = {
    "FlextCliProtocolsBase": "flext_cli._protocols.base",
    "base": "flext_cli._protocols.base",
}

__all__ = [
    "FlextCliProtocolsBase",
    "base",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
