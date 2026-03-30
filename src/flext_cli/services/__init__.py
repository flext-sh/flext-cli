# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
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

    from flext_cli.services import (
        auth,
        cli,
        cli_params,
        cmd,
        commands,
        file_tools,
        formatters,
        output,
        prompts,
        tables,
    )
    from flext_cli.services.auth import FlextCliAuth
    from flext_cli.services.cli import FlextCliCli
    from flext_cli.services.cli_params import FlextCliCommonParams
    from flext_cli.services.cmd import FlextCliCmd
    from flext_cli.services.commands import FlextCliCommands
    from flext_cli.services.file_tools import FlextCliFileTools
    from flext_cli.services.formatters import FlextCliFormatters
    from flext_cli.services.output import FlextCliOutput
    from flext_cli.services.prompts import FlextCliPrompts
    from flext_cli.services.tables import FlextCliTables

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextCliAuth": ["flext_cli.services.auth", "FlextCliAuth"],
    "FlextCliCli": ["flext_cli.services.cli", "FlextCliCli"],
    "FlextCliCmd": ["flext_cli.services.cmd", "FlextCliCmd"],
    "FlextCliCommands": ["flext_cli.services.commands", "FlextCliCommands"],
    "FlextCliCommonParams": ["flext_cli.services.cli_params", "FlextCliCommonParams"],
    "FlextCliFileTools": ["flext_cli.services.file_tools", "FlextCliFileTools"],
    "FlextCliFormatters": ["flext_cli.services.formatters", "FlextCliFormatters"],
    "FlextCliOutput": ["flext_cli.services.output", "FlextCliOutput"],
    "FlextCliPrompts": ["flext_cli.services.prompts", "FlextCliPrompts"],
    "FlextCliTables": ["flext_cli.services.tables", "FlextCliTables"],
    "auth": ["flext_cli.services.auth", ""],
    "cli": ["flext_cli.services.cli", ""],
    "cli_params": ["flext_cli.services.cli_params", ""],
    "cmd": ["flext_cli.services.cmd", ""],
    "commands": ["flext_cli.services.commands", ""],
    "file_tools": ["flext_cli.services.file_tools", ""],
    "formatters": ["flext_cli.services.formatters", ""],
    "output": ["flext_cli.services.output", ""],
    "prompts": ["flext_cli.services.prompts", ""],
    "tables": ["flext_cli.services.tables", ""],
}

__all__ = [
    "FlextCliAuth",
    "FlextCliCli",
    "FlextCliCmd",
    "FlextCliCommands",
    "FlextCliCommonParams",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliOutput",
    "FlextCliPrompts",
    "FlextCliTables",
    "auth",
    "cli",
    "cli_params",
    "cmd",
    "commands",
    "file_tools",
    "formatters",
    "output",
    "prompts",
    "tables",
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
