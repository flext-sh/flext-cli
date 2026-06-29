# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if _t.TYPE_CHECKING:
    from flext_tests import (
        d as d,
        e as e,
        h as h,
        r as r,
        td as td,
        tf as tf,
        tk as tk,
        tm as tm,
        tv as tv,
        x as x,
    )

    from tests._constants_parts.tests_core import (
        TestsFlextCliConstantsCore as TestsFlextCliConstantsCore,
    )
    from tests._constants_parts.tests_rules_options import (
        TestsFlextCliConstantsRulesOptions as TestsFlextCliConstantsRulesOptions,
    )
    from tests._constants_parts.tests_yaml_output import (
        TestsFlextCliConstantsYamlOutput as TestsFlextCliConstantsYamlOutput,
    )
    from tests._models_parts.tests_cli import (
        TestsFlextCliModelsCli as TestsFlextCliModelsCli,
    )
    from tests._models_parts.tests_runtime import (
        TestsFlextCliModelsRuntime as TestsFlextCliModelsRuntime,
    )
    from tests._models_parts.tests_version import (
        TestsFlextCliModelsVersion as TestsFlextCliModelsVersion,
    )
    from tests.base import TestsFlextCliServiceBase as TestsFlextCliServiceBase, s as s
    from tests.constants import TestsFlextCliConstants as TestsFlextCliConstants, c as c
    from tests.models import TestsFlextCliModels as TestsFlextCliModels, m as m
    from tests.protocols import TestsFlextCliProtocols as TestsFlextCliProtocols, p as p
    from tests.settings import TestsFlextCliSettings as TestsFlextCliSettings
    from tests.typings import TestsFlextCliTypes as TestsFlextCliTypes, t as t
    from tests.unit.conftest import (
        TestsFlextCliCaptureLogPrompts as TestsFlextCliCaptureLogPrompts,
        TestsFlextCliFailingLogPrompts as TestsFlextCliFailingLogPrompts,
        TestsFlextCliScriptedPrompts as TestsFlextCliScriptedPrompts,
        make_capture_prompts as make_capture_prompts,
        make_failing_prompts as make_failing_prompts,
        make_prompts as make_prompts,
        reset_settings as reset_settings,
    )
    from tests.unit.test_auth_utils_cov import (
        TestsFlextCliAuthUtilsCov as TestsFlextCliAuthUtilsCov,
    )
    from tests.unit.test_base import (
        TestsFlextCliServiceBaseBehavior as TestsFlextCliServiceBaseBehavior,
    )
    from tests.unit.test_cli_params import (
        TestsFlextCliCommonParams as TestsFlextCliCommonParams,
    )
    from tests.unit.test_cli_service import TestsFlextCliService as TestsFlextCliService
    from tests.unit.test_cmd import TestsFlextCliCmd as TestsFlextCliCmd
    from tests.unit.test_cmd_cov import TestsFlextCliCmdCov as TestsFlextCliCmdCov
    from tests.unit.test_cmd_runtime_validation_branch_cov import (
        TestsFlextCliCmdRuntimeValidationBranchCov as TestsFlextCliCmdRuntimeValidationBranchCov,
    )
    from tests.unit.test_commands_utils_cov import (
        TestsFlextCliCommandsUtilsCov as TestsFlextCliCommandsUtilsCov,
    )
    from tests.unit.test_constants import (
        TestsFlextCliConstantsUnit as TestsFlextCliConstantsUnit,
    )
    from tests.unit.test_conversion_cov import (
        TestsFlextCliConversionCov as TestsFlextCliConversionCov,
    )
    from tests.unit.test_examples_models_utilities_cov import (
        TestsFlextCliExampleModelsUtilitiesCov as TestsFlextCliExampleModelsUtilitiesCov,
    )
    from tests.unit.test_examples_smoke import (
        TestsFlextCliExamplesSmoke as TestsFlextCliExamplesSmoke,
    )
    from tests.unit.test_files_cov import TestsFlextCliFilesCov as TestsFlextCliFilesCov
    from tests.unit.test_formatters_cov import (
        TestsFlextCliFormattersCov as TestsFlextCliFormattersCov,
        TestsFlextCliServicesFormattersCov as TestsFlextCliServicesFormattersCov,
    )
    from tests.unit.test_json_cov import TestsFlextCliJsonCov as TestsFlextCliJsonCov
    from tests.unit.test_matching_cov import (
        TestsFlextCliMatchingCov as TestsFlextCliMatchingCov,
    )
    from tests.unit.test_model_commands_cov import (
        TestsFlextCliModelCommandsCov as TestsFlextCliModelCommandsCov,
    )
    from tests.unit.test_options_cov import (
        TestsFlextCliOptionsUtilsCov as TestsFlextCliOptionsUtilsCov,
    )
    from tests.unit.test_options_public_cov import (
        TestsFlextCliOptionsPublicCoverage as TestsFlextCliOptionsPublicCoverage,
    )
    from tests.unit.test_output_cov import (
        TestsFlextCliOutputCov as TestsFlextCliOutputCov,
    )
    from tests.unit.test_params_branch_cov import (
        TestsFlextCliParamsBranchCov as TestsFlextCliParamsBranchCov,
    )
    from tests.unit.test_pipeline import TestsFlextCliPipeline as TestsFlextCliPipeline
    from tests.unit.test_prompts import TestsFlextCliPrompts as TestsFlextCliPrompts
    from tests.unit.test_prompts_cov import (
        TestsFlextCliPromptsCov as TestsFlextCliPromptsCov,
    )
    from tests.unit.test_protocols import (
        TestsFlextCliProtocolsUnit as TestsFlextCliProtocolsUnit,
    )
    from tests.unit.test_public_contracts_cov import (
        TestsFlextCliPublicContractsCoverage as TestsFlextCliPublicContractsCoverage,
    )
    from tests.unit.test_rules_cov import TestsFlextCliRulesCov as TestsFlextCliRulesCov
    from tests.unit.test_runtime_utilities_core import (
        TestsFlextCliRuntimeUtilitiesCore as TestsFlextCliRuntimeUtilitiesCore,
    )
    from tests.unit.test_runtime_utilities_extra import (
        TestsFlextCliRuntimeUtilitiesExtra as TestsFlextCliRuntimeUtilitiesExtra,
    )
    from tests.unit.test_services_auth_branch_cov import (
        TestsFlextCliServicesAuthBranchCov as TestsFlextCliServicesAuthBranchCov,
    )
    from tests.unit.test_services_auth_cov import (
        TestsFlextCliServicesAuthCov as TestsFlextCliServicesAuthCov,
    )
    from tests.unit.test_services_output_cov import (
        TestsFlextCliServicesOutputCov as TestsFlextCliServicesOutputCov,
    )
    from tests.unit.test_services_tables_branch_cov import (
        TestsFlextCliServicesTablesBranchCov as TestsFlextCliServicesTablesBranchCov,
    )
    from tests.unit.test_services_tables_cov import (
        TestsFlextCliServicesTablesCov as TestsFlextCliServicesTablesCov,
    )
    from tests.unit.test_settings import (
        TestsFlextCliSettingsUnit as TestsFlextCliSettingsUnit,
    )
    from tests.unit.test_tables import TestsFlextCliTables as TestsFlextCliTables
    from tests.unit.test_tables_branch_cov import (
        TestsFlextCliTablesBranchCov as TestsFlextCliTablesBranchCov,
    )
    from tests.unit.test_tables_cov import (
        TestsFlextCliTableUtilsCov as TestsFlextCliTableUtilsCov,
    )
    from tests.unit.test_toml_cov import (
        TestsFlextCliTomlUtilsCov as TestsFlextCliTomlUtilsCov,
    )
    from tests.unit.test_toml_sync_cov import (
        TestsFlextCliTomlSyncCoverage as TestsFlextCliTomlSyncCoverage,
    )
    from tests.unit.test_toml_utilities import (
        TestsFlextCliTomlUtilities as TestsFlextCliTomlUtilities,
    )
    from tests.unit.test_typings import TestsFlextCliTypesUnit as TestsFlextCliTypesUnit
    from tests.unit.test_utilities_cov import (
        TestsFlextCliUtilitiesCov as TestsFlextCliUtilitiesCov,
    )
    from tests.unit.test_version import TestsFlextCliVersion as TestsFlextCliVersion
    from tests.unit.test_yaml_cov import TestsFlextCliYamlCov as TestsFlextCliYamlCov
    from tests.utilities import TestsFlextCliUtilities as TestsFlextCliUtilities, u as u
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
