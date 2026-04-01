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
    from flext_core import FlextTypes

    from flext_cli.services.auth import *
    from flext_cli.services.cli import *
    from flext_cli.services.cli_params import *
    from flext_cli.services.cmd import *
    from flext_cli.services.commands import *
    from flext_cli.services.file_tools import *
    from flext_cli.services.formatters import *
    from flext_cli.services.output import *
    from flext_cli.services.prompts import *
    from flext_cli.services.tables import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
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
