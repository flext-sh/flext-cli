# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

_LAZY_IMPORTS = merge_lazy_imports(
    (
        "._constants_parts",
        "._models_parts",
        ".helpers",
        ".unit",
    ),
    build_lazy_import_map(
        {
            "._constants_parts": ("_constants_parts",),
            "._constants_parts.tests_core": ("TestsFlextCliConstantsCore",),
            "._constants_parts.tests_rules_options": (
                "TestsFlextCliConstantsRulesOptions",
            ),
            "._constants_parts.tests_yaml_output": (
                "TestsFlextCliConstantsYamlOutput",
            ),
            "._models_parts": ("_models_parts",),
            "._models_parts.tests_cli": ("TestsFlextCliModelsCli",),
            "._models_parts.tests_runtime": ("TestsFlextCliModelsRuntime",),
            "._models_parts.tests_version": ("TestsFlextCliModelsVersion",),
            ".base": (
                "TestsFlextCliServiceBase",
                "s",
            ),
            ".conftest": ("conftest",),
            ".constants": (
                "TestsFlextCliConstants",
                "c",
            ),
            ".helpers": ("helpers",),
            ".models": (
                "TestsFlextCliModels",
                "m",
            ),
            ".protocols": (
                "TestsFlextCliProtocols",
                "p",
            ),
            ".settings": ("TestsFlextCliSettings",),
            ".typings": (
                "TestsFlextCliTypes",
                "t",
            ),
            ".unit": ("unit",),
            ".unit.conftest": (
                "TestsFlextCliCaptureLogPrompts",
                "TestsFlextCliFailingLogPrompts",
                "TestsFlextCliScriptedPrompts",
                "make_capture_prompts",
                "make_failing_prompts",
                "make_prompts",
                "reset_settings",
            ),
            ".unit.test_auth_utils_cov": ("TestsFlextCliAuthUtilsCov",),
            ".unit.test_base": ("TestsFlextCliServiceBaseBehavior",),
            ".unit.test_cli_params": ("TestsFlextCliCommonParams",),
            ".unit.test_cli_service": ("TestsFlextCliService",),
            ".unit.test_cmd": ("TestsFlextCliCmd",),
            ".unit.test_cmd_cov": ("TestsFlextCliCmdCov",),
            ".unit.test_cmd_runtime_validation_branch_cov": (
                "TestsFlextCliCmdRuntimeValidationBranchCov",
            ),
            ".unit.test_commands_utils_cov": ("TestsFlextCliCommandsUtilsCov",),
            ".unit.test_constants": ("TestsFlextCliConstantsUnit",),
            ".unit.test_conversion_cov": ("TestsFlextCliConversionCov",),
            ".unit.test_examples_models_utilities_cov": (
                "TestsFlextCliExampleModelsUtilitiesCov",
            ),
            ".unit.test_examples_smoke": ("TestsFlextCliExamplesSmoke",),
            ".unit.test_files_cov": ("TestsFlextCliFilesCov",),
            ".unit.test_formatters_cov": (
                "TestsFlextCliFormattersCov",
                "TestsFlextCliServicesFormattersCov",
            ),
            ".unit.test_json_cov": ("TestsFlextCliJsonCov",),
            ".unit.test_matching_cov": ("TestsFlextCliMatchingCov",),
            ".unit.test_model_commands_cov": ("TestsFlextCliModelCommandsCov",),
            ".unit.test_options_cov": ("TestsFlextCliOptionsUtilsCov",),
            ".unit.test_options_public_cov": ("TestsFlextCliOptionsPublicCoverage",),
            ".unit.test_output_cov": ("TestsFlextCliOutputCov",),
            ".unit.test_params_branch_cov": ("TestsFlextCliParamsBranchCov",),
            ".unit.test_pipeline": ("TestsFlextCliPipeline",),
            ".unit.test_prompts": ("TestsFlextCliPrompts",),
            ".unit.test_prompts_cov": ("TestsFlextCliPromptsCov",),
            ".unit.test_protocols": ("TestsFlextCliProtocolsUnit",),
            ".unit.test_public_contracts_cov": (
                "TestsFlextCliPublicContractsCoverage",
            ),
            ".unit.test_rules_cov": ("TestsFlextCliRulesCov",),
            ".unit.test_runtime_utilities_core": ("TestsFlextCliRuntimeUtilitiesCore",),
            ".unit.test_runtime_utilities_extra": (
                "TestsFlextCliRuntimeUtilitiesExtra",
            ),
            ".unit.test_services_auth_branch_cov": (
                "TestsFlextCliServicesAuthBranchCov",
            ),
            ".unit.test_services_auth_cov": ("TestsFlextCliServicesAuthCov",),
            ".unit.test_services_output_cov": ("TestsFlextCliServicesOutputCov",),
            ".unit.test_services_tables_branch_cov": (
                "TestsFlextCliServicesTablesBranchCov",
            ),
            ".unit.test_services_tables_cov": ("TestsFlextCliServicesTablesCov",),
            ".unit.test_settings": ("TestsFlextCliSettingsUnit",),
            ".unit.test_tables": ("TestsFlextCliTables",),
            ".unit.test_tables_branch_cov": ("TestsFlextCliTablesBranchCov",),
            ".unit.test_tables_cov": ("TestsFlextCliTableUtilsCov",),
            ".unit.test_toml_cov": ("TestsFlextCliTomlUtilsCov",),
            ".unit.test_toml_sync_cov": ("TestsFlextCliTomlSyncCoverage",),
            ".unit.test_toml_utilities": ("TestsFlextCliTomlUtilities",),
            ".unit.test_typings": ("TestsFlextCliTypesUnit",),
            ".unit.test_utilities_cov": ("TestsFlextCliUtilitiesCov",),
            ".unit.test_version": ("TestsFlextCliVersion",),
            ".unit.test_yaml_cov": ("TestsFlextCliYamlCov",),
            ".utilities": (
                "TestsFlextCliUtilities",
                "u",
            ),
            "flext_tests": (
                "d",
                "e",
                "h",
                "r",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "x",
            ),
        },
    ),
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
        "pytest_addoption",
        "pytest_collect_file",
        "pytest_collection_modifyitems",
        "pytest_configure",
        "pytest_runtest_setup",
        "pytest_runtest_teardown",
        "pytest_sessionfinish",
        "pytest_sessionstart",
        "pytest_terminal_summary",
        "pytest_warning_recorded",
    ),
    module_name=__name__,
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
