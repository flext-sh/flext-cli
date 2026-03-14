# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Plugins package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from examples.plugins.example_plugin import (
        CliMainWithGroups,
        DataProcessorPlugin,
        ExamplePlugin,
        GroupWithCommands,
        demonstrate_plugin_commands,
    )

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "CliMainWithGroups": ("examples.plugins.example_plugin", "CliMainWithGroups"),
    "DataProcessorPlugin": ("examples.plugins.example_plugin", "DataProcessorPlugin"),
    "ExamplePlugin": ("examples.plugins.example_plugin", "ExamplePlugin"),
    "GroupWithCommands": ("examples.plugins.example_plugin", "GroupWithCommands"),
    "demonstrate_plugin_commands": (
        "examples.plugins.example_plugin",
        "demonstrate_plugin_commands",
    ),
}

__all__ = [
    "CliMainWithGroups",
    "DataProcessorPlugin",
    "ExamplePlugin",
    "GroupWithCommands",
    "demonstrate_plugin_commands",
]


def __getattr__(name: str) -> t.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
