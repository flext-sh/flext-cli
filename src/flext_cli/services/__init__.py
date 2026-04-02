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
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
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
    from flext_core import FlextTypes

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "FlextCliAuth": "flext_cli.services.auth",
    "FlextCliCli": "flext_cli.services.cli",
    "FlextCliCmd": "flext_cli.services.cmd",
    "FlextCliCommands": "flext_cli.services.commands",
    "FlextCliCommonParams": "flext_cli.services.cli_params",
    "FlextCliFileTools": "flext_cli.services.file_tools",
    "FlextCliFormatters": "flext_cli.services.formatters",
    "FlextCliOutput": "flext_cli.services.output",
    "FlextCliPrompts": "flext_cli.services.prompts",
    "FlextCliTables": "flext_cli.services.tables",
    "auth": "flext_cli.services.auth",
    "cli": "flext_cli.services.cli",
    "cli_params": "flext_cli.services.cli_params",
    "cmd": "flext_cli.services.cmd",
    "commands": "flext_cli.services.commands",
    "file_tools": "flext_cli.services.file_tools",
    "formatters": "flext_cli.services.formatters",
    "output": "flext_cli.services.output",
    "prompts": "flext_cli.services.prompts",
    "tables": "flext_cli.services.tables",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
