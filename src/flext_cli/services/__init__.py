# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Services package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import flext_cli.services.auth as _flext_cli_services_auth

    auth = _flext_cli_services_auth
    import flext_cli.services.cli as _flext_cli_services_cli
    from flext_cli.services.auth import FlextCliAuth

    cli = _flext_cli_services_cli
    import flext_cli.services.cli_params as _flext_cli_services_cli_params
    from flext_cli.services.cli import FlextCliCli

    cli_params = _flext_cli_services_cli_params
    import flext_cli.services.cmd as _flext_cli_services_cmd
    from flext_cli.services.cli_params import FlextCliCommonParams

    cmd = _flext_cli_services_cmd
    import flext_cli.services.commands as _flext_cli_services_commands
    from flext_cli.services.cmd import FlextCliCmd

    commands = _flext_cli_services_commands
    import flext_cli.services.file_tools as _flext_cli_services_file_tools
    from flext_cli.services.commands import FlextCliCommands

    file_tools = _flext_cli_services_file_tools
    import flext_cli.services.formatters as _flext_cli_services_formatters
    from flext_cli.services.file_tools import FlextCliFileTools

    formatters = _flext_cli_services_formatters
    import flext_cli.services.output as _flext_cli_services_output
    from flext_cli.services.formatters import FlextCliFormatters

    output = _flext_cli_services_output
    import flext_cli.services.prompts as _flext_cli_services_prompts
    from flext_cli.services.output import FlextCliOutput

    prompts = _flext_cli_services_prompts
    import flext_cli.services.tables as _flext_cli_services_tables
    from flext_cli.services.prompts import FlextCliPrompts

    tables = _flext_cli_services_tables
    from flext_cli.services.tables import FlextCliTables
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
_LAZY_IMPORTS = {
    "FlextCliAuth": ("flext_cli.services.auth", "FlextCliAuth"),
    "FlextCliCli": ("flext_cli.services.cli", "FlextCliCli"),
    "FlextCliCmd": ("flext_cli.services.cmd", "FlextCliCmd"),
    "FlextCliCommands": ("flext_cli.services.commands", "FlextCliCommands"),
    "FlextCliCommonParams": ("flext_cli.services.cli_params", "FlextCliCommonParams"),
    "FlextCliFileTools": ("flext_cli.services.file_tools", "FlextCliFileTools"),
    "FlextCliFormatters": ("flext_cli.services.formatters", "FlextCliFormatters"),
    "FlextCliOutput": ("flext_cli.services.output", "FlextCliOutput"),
    "FlextCliPrompts": ("flext_cli.services.prompts", "FlextCliPrompts"),
    "FlextCliTables": ("flext_cli.services.tables", "FlextCliTables"),
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
    "c",
    "cli",
    "cli_params",
    "cmd",
    "commands",
    "d",
    "e",
    "file_tools",
    "formatters",
    "h",
    "m",
    "output",
    "p",
    "prompts",
    "r",
    "s",
    "t",
    "tables",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
