# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Protocols package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import flext_cli._protocols.base as _flext_cli__protocols_base
    import flext_cli._protocols.domain as _flext_cli__protocols_domain

    base = _flext_cli__protocols_base
    domain = _flext_cli__protocols_domain
    from flext_cli._protocols.base import FlextCliProtocolsBase
    from flext_cli._protocols.domain import FlextCliProtocolsDomain
_LAZY_IMPORTS = {
    "FlextCliProtocolsBase": "flext_cli._protocols.base",
    "base": "flext_cli._protocols.base",
    "FlextCliProtocolsDomain": "flext_cli._protocols.domain",
    "domain": "flext_cli._protocols.domain",
}

__all__ = [
    "FlextCliProtocolsBase",
    "FlextCliProtocolsDomain",
    "base",
    "domain",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
