# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Examples package."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes

    from examples import constants, models, protocols, typings, utilities
    from examples.constants import ExamplesConstants, ExamplesConstants as c
    from examples.models import ExamplesModels, ExamplesModels as m
    from examples.protocols import ExamplesProtocols, ExamplesProtocols as p
    from examples.typings import ExamplesTypes, ExamplesTypes as t
    from examples.utilities import ExamplesUtilities, ExamplesUtilities as u
    from flext_cli import d, e, h, r, s, x

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "ExamplesConstants": ["examples.constants", "ExamplesConstants"],
    "ExamplesModels": ["examples.models", "ExamplesModels"],
    "ExamplesProtocols": ["examples.protocols", "ExamplesProtocols"],
    "ExamplesTypes": ["examples.typings", "ExamplesTypes"],
    "ExamplesUtilities": ["examples.utilities", "ExamplesUtilities"],
    "c": ["examples.constants", "ExamplesConstants"],
    "constants": ["examples.constants", ""],
    "d": ["flext_cli", "d"],
    "e": ["flext_cli", "e"],
    "h": ["flext_cli", "h"],
    "m": ["examples.models", "ExamplesModels"],
    "models": ["examples.models", ""],
    "p": ["examples.protocols", "ExamplesProtocols"],
    "protocols": ["examples.protocols", ""],
    "r": ["flext_cli", "r"],
    "s": ["flext_cli", "s"],
    "t": ["examples.typings", "ExamplesTypes"],
    "typings": ["examples.typings", ""],
    "u": ["examples.utilities", "ExamplesUtilities"],
    "utilities": ["examples.utilities", ""],
    "x": ["flext_cli", "x"],
}

__all__ = [
    "ExamplesConstants",
    "ExamplesModels",
    "ExamplesProtocols",
    "ExamplesTypes",
    "ExamplesUtilities",
    "c",
    "constants",
    "d",
    "e",
    "h",
    "m",
    "models",
    "p",
    "protocols",
    "r",
    "s",
    "t",
    "typings",
    "u",
    "utilities",
    "x",
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
