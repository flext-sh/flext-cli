# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""FLEXT CLI Services - FlextService-based implementations.

This package contains all FlextService-based service classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr


if TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_cli.services.cmd import FlextCliCmd
    from flext_cli.services.core import FlextCliCore
    from flext_cli.services.output import FlextCliOutput
    from flext_cli.services.prompts import FlextCliPrompts
    from flext_cli.services.tables import FlextCliTables

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextCliCmd": ["flext_cli.services.cmd", "FlextCliCmd"],
    "FlextCliCore": ["flext_cli.services.core", "FlextCliCore"],
    "FlextCliOutput": ["flext_cli.services.output", "FlextCliOutput"],
    "FlextCliPrompts": ["flext_cli.services.prompts", "FlextCliPrompts"],
    "FlextCliTables": ["flext_cli.services.tables", "FlextCliTables"],
}

__all__ = [
    "FlextCliCmd",
    "FlextCliCore",
    "FlextCliOutput",
    "FlextCliPrompts",
    "FlextCliTables",
]


_LAZY_CACHE: MutableMapping[str, FlextTypes.ModuleExport] = {}


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562).

    A local cache ``_LAZY_CACHE`` persists resolved objects across repeated
    accesses during process lifetime.

    Args:
        name: Attribute name requested by dir()/import.

    Returns:
        Lazy-loaded module export type.

    Raises:
        AttributeError: If attribute not registered.
    """
    if name in _LAZY_CACHE:
        return _LAZY_CACHE[name]

    value = lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)
    _LAZY_CACHE[name] = value
    return value


def __dir__() -> Sequence[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.
    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)