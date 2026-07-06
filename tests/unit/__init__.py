# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".conftest": (
            "TestsFlextCliCaptureLogPrompts",
            "TestsFlextCliFailingLogPrompts",
            "TestsFlextCliScriptedPrompts",
            "make_capture_prompts",
            "make_failing_prompts",
            "make_prompts",
            "reset_settings",
        ),
        ".test_auth_utils_cov": ("TestsFlextCliAuthUtilsCov",),
        ".test_base": ("TestsFlextCliBase",),
        ".test_cli_params": ("TestsFlextCliCliParams",),
        ".test_cli_service": ("TestsFlextCliService",),
        ".test_cmd": ("TestsFlextCliCmd",),
        ".test_cmd_cov": ("TestsFlextCliCmdCov",),
        ".test_cmd_runtime_validation_branch_cov": (
            "TestsFlextCliCmdRuntimeValidationBranchCov",
        ),
        ".test_commands_utils_cov": ("TestsFlextCliCommands",),
        ".test_constants": ("TestsFlextCliConstants",),
        ".test_conversion_cov": ("TestsFlextCliConversion",),
        ".test_examples_models_utilities_cov": (
            "TestsFlextCliExampleModelsUtilitiesCov",
        ),
        ".test_examples_smoke": ("TestsFlextCliExamplesSmoke",),
        ".test_files_cov": ("TestsFlextCliFilesCov",),
        ".test_formatters_cov": ("TestsFlextCliFormattersCov",),
        ".test_json_cov": ("TestsFlextCliJsonCov",),
        ".test_matching_cov": ("TestsFlextCliMatchingCov",),
        ".test_model_commands_cov": ("TestsFlextCliModelCommandsCov",),
        ".test_options_cov": ("TestsFlextCliOptionsUtilsCov",),
        ".test_options_public_cov": ("TestsFlextCliOptions",),
        ".test_output_cov": ("TestsFlextCliOutputCov",),
        ".test_params_branch_cov": ("TestsFlextCliParams",),
        ".test_pipeline": ("TestsFlextCliPipeline",),
        ".test_prompts": ("TestsFlextCliPrompts",),
        ".test_prompts_cov": ("TestsFlextCliPromptsCov",),
        ".test_protocols": ("TestsFlextCliProtocols",),
        ".test_public_contracts_cov": ("TestsFlextCliPublicContractsCoverage",),
        ".test_rules_cov": ("TestsFlextCliRulesCov",),
        ".test_runtime_utilities_core": ("TestsFlextCliRuntimeUtilitiesCore",),
        ".test_runtime_utilities_extra": ("TestsFlextCliRuntimeUtilitiesExtra",),
        ".test_services_auth_branch_cov": ("TestsFlextCliServicesAuth",),
        ".test_services_auth_cov": ("TestsFlextCliServicesAuthCov",),
        ".test_services_output_cov": ("TestsFlextCliServicesOutputCov",),
        ".test_services_tables_branch_cov": ("TestsFlextCliServicesTablesBranchCov",),
        ".test_services_tables_cov": ("TestsFlextCliServicesTablesCov",),
        ".test_settings": ("TestsFlextCliSettingsUnit",),
        ".test_tables": ("TestsFlextCliTables",),
        ".test_tables_branch_cov": ("TestsFlextCliTablesBranchCov",),
        ".test_toml_cov": ("TestsFlextCliTomlCov",),
        ".test_toml_sync_cov": ("TestsFlextCliTomlSyncCoverage",),
        ".test_toml_utilities": ("TestsFlextCliTomlUtilities",),
        ".test_typings": ("TestsFlextCliTypings",),
        ".test_utilities_cov": ("TestsFlextCliUtilitiesCov",),
        ".test_version": ("TestsFlextCliVersion",),
        ".test_yaml_cov": ("TestsFlextCliYamlCov",),
        "flext_tests": (
            "c",
            "d",
            "e",
            "h",
            "m",
            "p",
            "r",
            "s",
            "t",
            "td",
            "tf",
            "tk",
            "tm",
            "tv",
            "u",
            "x",
        ),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
