# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Services package."""

from __future__ import annotations

from flext_core.lazy import install_lazy_exports

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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
