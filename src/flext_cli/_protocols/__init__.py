# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Protocols package."""

from __future__ import annotations

from flext_core.lazy import install_lazy_exports

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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
