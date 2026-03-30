# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""FLEXT CLI Services - FlextService-based implementations.

This package contains all FlextService-based service classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.services import (
        auth as auth,
        cli as cli,
        cli_params as cli_params,
        cmd as cmd,
        commands as commands,
        file_tools as file_tools,
        formatters as formatters,
        output as output,
        prompts as prompts,
        tables as tables,
    )
    from flext_cli.services.auth import FlextCliAuth as FlextCliAuth
    from flext_cli.services.cli import FlextCliCli as FlextCliCli
    from flext_cli.services.cli_params import (
        FlextCliCommonParams as FlextCliCommonParams,
    )
    from flext_cli.services.cmd import FlextCliCmd as FlextCliCmd
    from flext_cli.services.commands import FlextCliCommands as FlextCliCommands
    from flext_cli.services.file_tools import FlextCliFileTools as FlextCliFileTools
    from flext_cli.services.formatters import FlextCliFormatters as FlextCliFormatters
    from flext_cli.services.output import FlextCliOutput as FlextCliOutput
    from flext_cli.services.prompts import FlextCliPrompts as FlextCliPrompts
    from flext_cli.services.tables import FlextCliTables as FlextCliTables

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

_EXPORTS: Sequence[str] = [
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
