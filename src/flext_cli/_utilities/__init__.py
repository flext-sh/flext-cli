# AUTO-GENERATED FILE — Regenerate with: make gen
"""Utilities package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".auth": ("FlextCliUtilitiesAuth",),
        ".base": ("FlextCliUtilitiesBase",),
        ".cmd": ("FlextCliUtilitiesCmd",),
        ".commands": ("FlextCliUtilitiesCommands",),
        ".conversion": ("FlextCliUtilitiesConversion",),
        ".files": ("FlextCliUtilitiesFiles",),
        ".formatters": ("FlextCliUtilitiesFormatters",),
        ".json": ("FlextCliUtilitiesJson",),
        ".matching": ("FlextCliUtilitiesMatching",),
        ".model_commands": (
            "FlextCliUtilitiesModelCommandBuilder",
            "FlextCliUtilitiesModelCommands",
        ),
        ".options": (
            "FlextCliUtilitiesOptionBuilder",
            "FlextCliUtilitiesOptions",
        ),
        ".output": ("FlextCliUtilitiesOutput",),
        ".params": ("FlextCliUtilitiesParams",),
        ".pipeline": ("FlextCliUtilitiesPipeline",),
        ".prompts": ("FlextCliUtilitiesPrompts",),
        ".runtime": ("FlextCliUtilitiesRuntime",),
        ".settings": ("FlextCliUtilitiesSettings",),
        ".tables": ("FlextCliUtilitiesTables",),
        ".toml": ("FlextCliUtilitiesToml",),
        ".validation": ("FlextCliUtilitiesValidation",),
        ".yaml": ("FlextCliUtilitiesYaml",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
