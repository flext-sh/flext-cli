# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Services package."""

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
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u

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
    "c": ("flext_core.constants", "FlextConstants"),
    "cli": "flext_cli.services.cli",
    "cli_params": "flext_cli.services.cli_params",
    "cmd": "flext_cli.services.cmd",
    "commands": "flext_cli.services.commands",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "file_tools": "flext_cli.services.file_tools",
    "formatters": "flext_cli.services.formatters",
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_core.models", "FlextModels"),
    "output": "flext_cli.services.output",
    "p": ("flext_core.protocols", "FlextProtocols"),
    "prompts": "flext_cli.services.prompts",
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "tables": "flext_cli.services.tables",
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
