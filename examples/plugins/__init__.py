# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Plugins package."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr


if TYPE_CHECKING:
    from flext_core import FlextTypes
    from examples.plugins.example_plugin import (
        DataProcessorPlugin,
        ExamplePlugin,
        demonstrate_plugin_commands,
    )
    from examples.plugins.protocols import (
        CliMainWithGroups,
        FlextCliProtocols,
        GroupWithCommands,
        p,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "CliMainWithGroups": ["examples.plugins.protocols", "CliMainWithGroups"],
    "DataProcessorPlugin": ["examples.plugins.example_plugin", "DataProcessorPlugin"],
    "ExamplePlugin": ["examples.plugins.example_plugin", "ExamplePlugin"],
    "FlextCliProtocols": ["examples.plugins.protocols", "FlextCliProtocols"],
    "GroupWithCommands": ["examples.plugins.protocols", "GroupWithCommands"],
    "demonstrate_plugin_commands": ["examples.plugins.example_plugin", "demonstrate_plugin_commands"],
    "p": ["examples.plugins.protocols", "p"],
}

__all__ = [
    "CliMainWithGroups",
    "DataProcessorPlugin",
    "ExamplePlugin",
    "FlextCliProtocols",
    "GroupWithCommands",
    "demonstrate_plugin_commands",
    "p",
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