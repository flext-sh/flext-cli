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
    import flext_cli._protocols.domain as _flext_cli__protocols_domain
    from flext_cli._protocols.base import FlextCliProtocolsBase

    domain = _flext_cli__protocols_domain
    import flext_cli._protocols.pipeline as _flext_cli__protocols_pipeline
    from flext_cli._protocols.domain import FlextCliProtocolsDomain

    pipeline = _flext_cli__protocols_pipeline
    from flext_cli._protocols.pipeline import FlextCliProtocolsPipeline
_LAZY_IMPORTS = {
    "FlextCliProtocolsBase": ("flext_cli._protocols.base", "FlextCliProtocolsBase"),
    "FlextCliProtocolsDomain": (
        "flext_cli._protocols.domain",
        "FlextCliProtocolsDomain",
    ),
    "FlextCliProtocolsPipeline": (
        "flext_cli._protocols.pipeline",
        "FlextCliProtocolsPipeline",
    ),
    "base": "flext_cli._protocols.base",
    "domain": "flext_cli._protocols.domain",
    "pipeline": "flext_cli._protocols.pipeline",
}

__all__ = [
    "FlextCliProtocolsBase",
    "FlextCliProtocolsDomain",
    "FlextCliProtocolsPipeline",
    "base",
    "domain",
    "pipeline",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
