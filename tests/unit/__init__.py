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
            "make_prompts",
        ),
        ".test_auth_utils_cov": ("TestsFlextCliAuthUtilsCov",),
        ".test_base": ("TestsFlextCliServiceBase",),
        ".test_cli_params": ("TestsFlextCliCommonParams",),
        ".test_cli_service": ("TestsFlextCliService",),
        ".test_cmd": ("TestsFlextCliCmd",),
        ".test_cmd_cov": ("TestsFlextCliCmdCov",),
        ".test_cmd_runtime_validation_branch_cov": (
            "TestsFlextCliCmdRuntimeValidationBranchCov",
        ),
        ".test_commands": ("TestsFlextCliCommands",),
        ".test_commands_utils_cov": ("TestsFlextCliCommandsUtilsCov",),
        ".test_constants": ("TestsFlextCliConstantsUnit",),
        ".test_conversion_cov": ("TestsFlextCliConversionCov",),
        ".test_examples_smoke": ("TestsFlextCliExamplesSmoke",),
        ".test_files_cov": ("TestsFlextCliFilesCov",),
        ".test_formatters_cov": (
            "TestsFlextCliFormattersCov",
            "TestsFlextCliServicesFormattersCov",
        ),
        ".test_json_cov": ("TestsFlextCliJsonCov",),
        ".test_matching_cov": ("TestsFlextCliMatchingCov",),
        ".test_model_commands_cov": ("TestsFlextCliModelCommandsCov",),
        ".test_options_cov": ("TestsFlextCliOptionsUtilsCov",),
        ".test_output_cov": ("TestsFlextCliOutputCov",),
        ".test_params_branch_cov": ("TestsFlextCliParamsBranchCov",),
        ".test_pipeline": ("TestsFlextCliPipeline",),
        ".test_prompts": ("TestsFlextCliPrompts",),
        ".test_prompts_cov": ("TestsFlextCliPromptsCov",),
        ".test_protocols": ("TestsFlextCliProtocolsUnit",),
        ".test_rules_cov": (
            "TestsFlextCliRulesUtilsCov",
            "TestsFlextCliServiceRulesCov",
        ),
        ".test_runtime_utilities_core": ("TestsFlextCliRuntimeUtilitiesCore",),
        ".test_runtime_utilities_extra": ("TestsFlextCliRuntimeUtilitiesExtra",),
        ".test_services_auth_branch_cov": ("TestsFlextCliServicesAuthBranchCov",),
        ".test_services_auth_cov": ("TestsFlextCliServicesAuthCov",),
        ".test_services_commands_branch_cov": (
            "TestsFlextCliServicesCommandsBranchCov",
        ),
        ".test_services_commands_cov": ("TestsFlextCliServicesCommandsCov",),
        ".test_services_output_cov": ("TestsFlextCliServicesOutputCov",),
        ".test_services_tables_branch_cov": ("TestsFlextCliServicesTablesBranchCov",),
        ".test_services_tables_cov": ("TestsFlextCliServicesTablesCov",),
        ".test_settings": ("TestsFlextCliSettings",),
        ".test_tables": ("TestsFlextCliTables",),
        ".test_tables_branch_cov": ("TestsFlextCliTablesBranchCov",),
        ".test_tables_cov": ("TestsFlextCliTableUtilsCov",),
        ".test_toml_cov": ("TestsFlextCliTomlUtilsCov",),
        ".test_toml_utilities": ("TestsFlextCliTomlUtilities",),
        ".test_typings": ("TestsFlextCliTypesUnit",),
        ".test_utilities_cov": ("TestsFlextCliUtilitiesCov",),
        ".test_version": ("TestsFlextCliVersion",),
        ".test_yaml_cov": ("TestsFlextCliYamlCov",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
