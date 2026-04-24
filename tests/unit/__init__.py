# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".conftest": (
            "FlextCliCaptureLogPrompts",
            "FlextCliFailingLogPrompts",
            "FlextCliScriptedPrompts",
            "make_prompts",
        ),
        ".test_base": ("TestsFlextCliServiceBase",),
        ".test_cli_params": ("TestsFlextCliCommonParams",),
        ".test_cli_service": ("TestsFlextCliService",),
        ".test_cmd": ("TestsFlextCliCmd",),
        ".test_cmd_cov": ("TestsFlextCliCmdCov",),
        ".test_commands": ("TestsFlextCliCommands",),
        ".test_constants": ("TestsFlextCliConstantsUnit",),
        ".test_examples_smoke": ("TestsFlextCliExamplesSmoke",),
        ".test_pipeline": ("TestsFlextCliPipeline",),
        ".test_prompts": ("TestsFlextCliPrompts",),
        ".test_prompts_cov": ("TestsFlextCliPromptsCov",),
        ".test_protocols": ("TestsFlextCliProtocolsUnit",),
        ".test_runtime_utilities_core": ("test_runtime_utilities_core",),
        ".test_runtime_utilities_extra": ("TestsFlextCliRuntimeUtilitiesExtra",),
        ".test_settings": ("TestsFlextCliSettings",),
        ".test_tables": ("TestsFlextCliTables",),
        ".test_toml_utilities": ("TestsFlextCliTomlUtilities",),
        ".test_typings": ("TestsFlextCliTypesUnit",),
        ".test_utilities_cov": ("TestsFlextCliUtilitiesCov",),
        ".test_version": ("TestsFlextCliVersion",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
