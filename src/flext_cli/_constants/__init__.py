# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Constants package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import flext_cli._constants.base as _flext_cli__constants_base

    base = _flext_cli__constants_base
    import flext_cli._constants.config as _flext_cli__constants_config
    from flext_cli._constants.base import FlextCliConstantsBase

    config = _flext_cli__constants_config
    import flext_cli._constants.enums as _flext_cli__constants_enums
    from flext_cli._constants.config import FlextCliConstantsConfig

    enums = _flext_cli__constants_enums
    from flext_cli._constants.enums import FlextCliConstantsEnums
_LAZY_IMPORTS = {
    "FlextCliConstantsBase": ("flext_cli._constants.base", "FlextCliConstantsBase"),
    "FlextCliConstantsConfig": (
        "flext_cli._constants.config",
        "FlextCliConstantsConfig",
    ),
    "FlextCliConstantsEnums": ("flext_cli._constants.enums", "FlextCliConstantsEnums"),
    "base": "flext_cli._constants.base",
    "config": "flext_cli._constants.config",
    "enums": "flext_cli._constants.enums",
}

__all__ = [
    "FlextCliConstantsBase",
    "FlextCliConstantsConfig",
    "FlextCliConstantsEnums",
    "base",
    "config",
    "enums",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
