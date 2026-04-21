# AUTO-GENERATED FILE — Regenerate with: make gen
"""Services package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".auth": ("FlextCliAuth",),
        ".cli": ("FlextCliCli",),
        ".cli_params": ("FlextCliCommonParams",),
        ".cmd": ("FlextCliCmd",),
        ".commands": ("FlextCliCommands",),
        ".file_tools": ("FlextCliFileTools",),
        ".formatters": ("FlextCliFormatters",),
        ".output": ("FlextCliOutput",),
        ".prompts": ("FlextCliPrompts",),
        ".rules": ("FlextCliRules",),
        ".tables": ("FlextCliTables",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
