# AUTO-GENERATED FILE — Regenerate with: make gen
"""Lazy export map part."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map

FLEXT_CLI_TESTS_UNIT_LAZY_IMPORTS_PART_01 = build_lazy_import_map(
    {
        ".conftest": (
            "TestsFlextCliCaptureLogPrompts",
            "TestsFlextCliFailingLogPrompts",
            "TestsFlextCliScriptedPrompts",
        ),
        ".test_auth_utils_cov": ("TestsFlextCliAuthUtilsCov",),
        ".test_base": ("TestsFlextCliServiceBaseBehavior",),
        ".test_cli_params": ("TestsFlextCliCommonParams",),
        ".test_cli_service": ("TestsFlextCliService",),
        ".test_cmd": ("TestsFlextCliCmd",),
        ".test_cmd_cov": ("TestsFlextCliCmdCov",),
        ".test_cmd_runtime_validation_branch_cov": (
            "TestsFlextCliCmdRuntimeValidationBranchCov",
        ),
        ".test_commands_utils_cov": ("TestsFlextCliCommandsUtilsCov",),
        ".test_constants": ("TestsFlextCliConstantsUnit",),
        ".test_conversion_cov": ("TestsFlextCliConversionCov",),
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
        ".test_options_public_cov": ("TestsFlextCliOptionsPublicCoverage",),
        ".test_output_cov": ("TestsFlextCliOutputCov",),
        ".test_params_branch_cov": ("TestsFlextCliParamsBranchCov",),
        ".test_pipeline": ("TestsFlextCliPipeline",),
        ".test_prompts": ("TestsFlextCliPrompts",),
        ".test_prompts_cov": ("TestsFlextCliPromptsCov",),
        ".test_protocols": ("TestsFlextCliProtocolsUnit",),
        ".test_public_contracts_cov": ("TestsFlextCliPublicContractsCoverage",),
        ".test_rules_cov": ("TestsFlextCliRulesCov",),
        ".test_runtime_utilities_core": ("TestsFlextCliRuntimeUtilitiesCore",),
        ".test_runtime_utilities_extra": ("TestsFlextCliRuntimeUtilitiesExtra",),
    },
)

__all__: list[str] = ["FLEXT_CLI_TESTS_UNIT_LAZY_IMPORTS_PART_01"]
