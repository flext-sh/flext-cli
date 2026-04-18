# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".conftest": ("conftest",),
        ".test_base": ("TestsCliServiceBase",),
        ".test_cli_params": ("TestsCliCommonParams",),
        ".test_cli_service": ("TestsCliService",),
        ".test_cmd": ("TestsCliCmd",),
        ".test_cmd_cov": ("TestsCliCmdCov",),
        ".test_commands": ("TestsCliCommands",),
        ".test_constants": ("TestsCliConstants",),
        ".test_examples_smoke": ("TestFlextCliExamplesSmoke",),
        ".test_pipeline": ("TestPipelineExecute",),
        ".test_prompts": (
            "CaptureLogPrompts",
            "FailingLogPrompts",
            "ScriptedPrompts",
            "TestsCliPrompts",
        ),
        ".test_prompts_cov": ("TestsCliPromptsCov",),
        ".test_protocols": ("TestsCliProtocols",),
        ".test_runtime_utilities_core": ("test_runtime_utilities_core",),
        ".test_runtime_utilities_extra": ("TestCliRuntimeUtilitiesExtra",),
        ".test_settings": (
            "TestsCliLoggingSettings",
            "TestsCliSettingsBasics",
            "TestsCliSettingsEdgeCases",
            "TestsCliSettingsIntegration",
            "TestsCliSettingsService",
            "TestsCliSettingsValidation",
        ),
        ".test_tables": ("TestsCliTables",),
        ".test_toml_utilities": (
            "TestCliTomlDocument",
            "TestCliTomlHelpers",
            "TestCliTomlRead",
        ),
        ".test_typings": ("TestsCliTypings",),
        ".test_utilities_cov": ("TestsCliUtilitiesCov",),
        ".test_version": ("TestsCliVersion",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
