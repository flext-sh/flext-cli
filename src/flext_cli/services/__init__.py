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
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
