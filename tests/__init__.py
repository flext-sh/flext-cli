# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if TYPE_CHECKING:
    from flext_tests import d, e, h, r, td, tf, tk, tm, tv, x

    from tests._constants_parts.tests_core import TestsFlextCliConstantsCore
    from tests._constants_parts.tests_rules_options import (
        TestsFlextCliConstantsRulesOptions,
    )
    from tests._constants_parts.tests_yaml_output import (
        TestsFlextCliConstantsYamlOutput,
    )
    from tests._models_parts.tests_cli import TestsFlextCliModelsCli
    from tests._models_parts.tests_runtime import TestsFlextCliModelsRuntime
    from tests._models_parts.tests_version import TestsFlextCliModelsVersion
    from tests.base import TestsFlextCliServiceBase, s
    from tests.constants import TestsFlextCliConstants, c
    from tests.models import TestsFlextCliModels, m
    from tests.protocols import TestsFlextCliProtocols, p
    from tests.settings import TestsFlextCliSettings
    from tests.typings import TestsFlextCliTypes, t
    from tests.unit.conftest import (
        TestsFlextCliCaptureLogPrompts,
        TestsFlextCliFailingLogPrompts,
        TestsFlextCliScriptedPrompts,
    )
    from tests.unit.test_auth_utils_cov import TestsFlextCliAuthUtilsCov
    from tests.unit.test_base import TestsFlextCliBase
    from tests.unit.test_cli_params import TestsFlextCliCliParams
    from tests.unit.test_cli_service import TestsFlextCliService
    from tests.unit.test_cmd import TestsFlextCliCmd
    from tests.unit.test_cmd_cov import TestsFlextCliCmdCov
    from tests.unit.test_cmd_runtime_validation_branch_cov import (
        TestsFlextCliCmdRuntimeValidationBranchCov,
    )
    from tests.unit.test_commands_utils_cov import TestsFlextCliCommands
    from tests.unit.test_conversion_cov import TestsFlextCliConversion
    from tests.unit.test_examples_models_utilities_cov import (
        TestsFlextCliExampleModelsUtilitiesCov,
    )
    from tests.unit.test_examples_smoke import TestsFlextCliExamplesSmoke
    from tests.unit.test_files_cov import TestsFlextCliFilesCov
    from tests.unit.test_formatters_cov import TestsFlextCliFormattersCov
    from tests.unit.test_json_cov import TestsFlextCliJsonCov
    from tests.unit.test_matching_cov import TestsFlextCliMatchingCov
    from tests.unit.test_model_commands_cov import TestsFlextCliModelCommandsCov
    from tests.unit.test_options_cov import TestsFlextCliOptionsUtilsCov
    from tests.unit.test_options_public_cov import TestsFlextCliOptions
    from tests.unit.test_output_cov import TestsFlextCliOutputCov
    from tests.unit.test_params_branch_cov import TestsFlextCliParams
    from tests.unit.test_pipeline import TestsFlextCliPipeline
    from tests.unit.test_prompts import TestsFlextCliPrompts
    from tests.unit.test_prompts_cov import TestsFlextCliPromptsCov
    from tests.unit.test_public_contracts_cov import (
        TestsFlextCliPublicContractsCoverage,
    )
    from tests.unit.test_rules_cov import TestsFlextCliRulesCov
    from tests.unit.test_runtime_utilities_core import TestsFlextCliRuntimeUtilitiesCore
    from tests.unit.test_runtime_utilities_extra import (
        TestsFlextCliRuntimeUtilitiesExtra,
    )
    from tests.unit.test_services_auth_branch_cov import TestsFlextCliServicesAuth
    from tests.unit.test_services_auth_cov import TestsFlextCliServicesAuthCov
    from tests.unit.test_services_output_cov import TestsFlextCliServicesOutputCov
    from tests.unit.test_services_tables_branch_cov import (
        TestsFlextCliServicesTablesBranchCov,
    )
    from tests.unit.test_services_tables_cov import TestsFlextCliServicesTablesCov
    from tests.unit.test_settings import TestsFlextCliSettingsUnit
    from tests.unit.test_tables import TestsFlextCliTables
    from tests.unit.test_tables_branch_cov import TestsFlextCliTablesBranchCov
    from tests.unit.test_toml_cov import TestsFlextCliTomlCov
    from tests.unit.test_toml_sync_cov import TestsFlextCliTomlSyncCoverage
    from tests.unit.test_toml_utilities import TestsFlextCliTomlUtilities
    from tests.unit.test_typings import TestsFlextCliTypings
    from tests.unit.test_utilities_cov import TestsFlextCliUtilitiesCov
    from tests.unit.test_version import TestsFlextCliVersion
    from tests.unit.test_yaml_cov import TestsFlextCliYamlCov
    from tests.utilities import TestsFlextCliUtilities, u
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "._constants_parts",
        "._models_parts",
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
            ".unit.test_base": ("TestsFlextCliBase",),
            ".unit.test_cli_params": ("TestsFlextCliCliParams",),
            ".unit.test_cli_service": ("TestsFlextCliService",),
            ".unit.test_cmd": ("TestsFlextCliCmd",),
            ".unit.test_cmd_cov": ("TestsFlextCliCmdCov",),
            ".unit.test_cmd_runtime_validation_branch_cov": (
                "TestsFlextCliCmdRuntimeValidationBranchCov",
            ),
            ".unit.test_commands_utils_cov": ("TestsFlextCliCommands",),
            ".unit.test_conversion_cov": ("TestsFlextCliConversion",),
            ".unit.test_examples_models_utilities_cov": (
                "TestsFlextCliExampleModelsUtilitiesCov",
            ),
            ".unit.test_examples_smoke": ("TestsFlextCliExamplesSmoke",),
            ".unit.test_files_cov": ("TestsFlextCliFilesCov",),
            ".unit.test_formatters_cov": ("TestsFlextCliFormattersCov",),
            ".unit.test_json_cov": ("TestsFlextCliJsonCov",),
            ".unit.test_matching_cov": ("TestsFlextCliMatchingCov",),
            ".unit.test_model_commands_cov": ("TestsFlextCliModelCommandsCov",),
            ".unit.test_options_cov": ("TestsFlextCliOptionsUtilsCov",),
            ".unit.test_options_public_cov": ("TestsFlextCliOptions",),
            ".unit.test_output_cov": ("TestsFlextCliOutputCov",),
            ".unit.test_params_branch_cov": ("TestsFlextCliParams",),
            ".unit.test_pipeline": ("TestsFlextCliPipeline",),
            ".unit.test_prompts": ("TestsFlextCliPrompts",),
            ".unit.test_prompts_cov": ("TestsFlextCliPromptsCov",),
            ".unit.test_public_contracts_cov": (
                "TestsFlextCliPublicContractsCoverage",
            ),
            ".unit.test_rules_cov": ("TestsFlextCliRulesCov",),
            ".unit.test_runtime_utilities_core": ("TestsFlextCliRuntimeUtilitiesCore",),
            ".unit.test_runtime_utilities_extra": (
                "TestsFlextCliRuntimeUtilitiesExtra",
            ),
            ".unit.test_services_auth_branch_cov": ("TestsFlextCliServicesAuth",),
            ".unit.test_services_auth_cov": ("TestsFlextCliServicesAuthCov",),
            ".unit.test_services_output_cov": ("TestsFlextCliServicesOutputCov",),
            ".unit.test_services_tables_branch_cov": (
                "TestsFlextCliServicesTablesBranchCov",
            ),
            ".unit.test_services_tables_cov": ("TestsFlextCliServicesTablesCov",),
            ".unit.test_settings": ("TestsFlextCliSettingsUnit",),
            ".unit.test_tables": ("TestsFlextCliTables",),
            ".unit.test_tables_branch_cov": ("TestsFlextCliTablesBranchCov",),
            ".unit.test_toml_cov": ("TestsFlextCliTomlCov",),
            ".unit.test_toml_sync_cov": ("TestsFlextCliTomlSyncCoverage",),
            ".unit.test_toml_utilities": ("TestsFlextCliTomlUtilities",),
            ".unit.test_typings": ("TestsFlextCliTypings",),
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
