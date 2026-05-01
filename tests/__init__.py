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
    from flext_tests import d, e, h, r, s, td, tf, tk, tm, tv, x

    from tests.constants import TestsFlextCliConstants, c
    from tests.models import TestsFlextCliModels, m
    from tests.protocols import TestsFlextCliProtocols, p
    from tests.typings import TestsFlextCliTypes, t
    from tests.unit.conftest import (
        TestsFlextCliCaptureLogPrompts,
        TestsFlextCliFailingLogPrompts,
        TestsFlextCliScriptedPrompts,
        make_prompts,
    )
    from tests.unit.test_auth_utils_cov import TestsFlextCliAuthUtilsCov
    from tests.unit.test_base import TestsFlextCliServiceBase
    from tests.unit.test_cli_params import TestsFlextCliCommonParams
    from tests.unit.test_cli_service import TestsFlextCliService
    from tests.unit.test_cmd import TestsFlextCliCmd
    from tests.unit.test_cmd_cov import TestsFlextCliCmdCov
    from tests.unit.test_commands import TestsFlextCliCommands
    from tests.unit.test_commands_utils_cov import TestsFlextCliCommandsUtilsCov
    from tests.unit.test_constants import TestsFlextCliConstantsUnit
    from tests.unit.test_conversion_cov import TestsFlextCliConversionCov
    from tests.unit.test_examples_smoke import TestsFlextCliExamplesSmoke
    from tests.unit.test_files_cov import TestsFlextCliFilesCov
    from tests.unit.test_formatters_cov import (
        TestsFlextCliFormattersCov,
        TestsFlextCliServicesFormattersCov,
    )
    from tests.unit.test_json_cov import TestsFlextCliJsonCov
    from tests.unit.test_matching_cov import TestsFlextCliMatchingCov
    from tests.unit.test_model_commands_cov import TestsFlextCliModelCommandsCov
    from tests.unit.test_options_cov import TestsFlextCliOptionsUtilsCov
    from tests.unit.test_output_cov import TestsFlextCliOutputCov
    from tests.unit.test_pipeline import TestsFlextCliPipeline
    from tests.unit.test_prompts import TestsFlextCliPrompts
    from tests.unit.test_prompts_cov import TestsFlextCliPromptsCov
    from tests.unit.test_protocols import TestsFlextCliProtocolsUnit
    from tests.unit.test_rules_cov import (
        TestsFlextCliRulesUtilsCov,
        TestsFlextCliServiceRulesCov,
    )
    from tests.unit.test_runtime_utilities_core import TestsFlextCliRuntimeUtilitiesCore
    from tests.unit.test_runtime_utilities_extra import (
        TestsFlextCliRuntimeUtilitiesExtra,
    )
    from tests.unit.test_services_auth_branch_cov import (
        TestsFlextCliServicesAuthBranchCov,
    )
    from tests.unit.test_services_auth_cov import TestsFlextCliServicesAuthCov
    from tests.unit.test_services_commands_branch_cov import (
        TestsFlextCliServicesCommandsBranchCov,
    )
    from tests.unit.test_services_commands_cov import TestsFlextCliServicesCommandsCov
    from tests.unit.test_services_output_cov import TestsFlextCliServicesOutputCov
    from tests.unit.test_services_tables_branch_cov import (
        TestsFlextCliServicesTablesBranchCov,
    )
    from tests.unit.test_services_tables_cov import TestsFlextCliServicesTablesCov
    from tests.unit.test_settings import TestsFlextCliSettings
    from tests.unit.test_tables import TestsFlextCliTables
    from tests.unit.test_tables_branch_cov import TestsFlextCliTablesBranchCov
    from tests.unit.test_tables_cov import TestsFlextCliTableUtilsCov
    from tests.unit.test_toml_cov import TestsFlextCliTomlUtilsCov
    from tests.unit.test_toml_utilities import TestsFlextCliTomlUtilities
    from tests.unit.test_typings import TestsFlextCliTypesUnit
    from tests.unit.test_utilities_cov import TestsFlextCliUtilitiesCov
    from tests.unit.test_version import TestsFlextCliVersion
    from tests.unit.test_yaml_cov import TestsFlextCliYamlCov
    from tests.utilities import TestsFlextCliUtilities, u
_LAZY_IMPORTS = merge_lazy_imports(
    (".unit",),
    build_lazy_import_map(
        {
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
            ".typings": (
                "TestsFlextCliTypes",
                "t",
            ),
            ".unit.conftest": (
                "TestsFlextCliCaptureLogPrompts",
                "TestsFlextCliFailingLogPrompts",
                "TestsFlextCliScriptedPrompts",
                "make_prompts",
            ),
            ".unit.test_auth_utils_cov": ("TestsFlextCliAuthUtilsCov",),
            ".unit.test_base": ("TestsFlextCliServiceBase",),
            ".unit.test_cli_params": ("TestsFlextCliCommonParams",),
            ".unit.test_cli_service": ("TestsFlextCliService",),
            ".unit.test_cmd": ("TestsFlextCliCmd",),
            ".unit.test_cmd_cov": ("TestsFlextCliCmdCov",),
            ".unit.test_commands": ("TestsFlextCliCommands",),
            ".unit.test_commands_utils_cov": ("TestsFlextCliCommandsUtilsCov",),
            ".unit.test_constants": ("TestsFlextCliConstantsUnit",),
            ".unit.test_conversion_cov": ("TestsFlextCliConversionCov",),
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
            ".unit.test_output_cov": ("TestsFlextCliOutputCov",),
            ".unit.test_pipeline": ("TestsFlextCliPipeline",),
            ".unit.test_prompts": ("TestsFlextCliPrompts",),
            ".unit.test_prompts_cov": ("TestsFlextCliPromptsCov",),
            ".unit.test_protocols": ("TestsFlextCliProtocolsUnit",),
            ".unit.test_rules_cov": (
                "TestsFlextCliRulesUtilsCov",
                "TestsFlextCliServiceRulesCov",
            ),
            ".unit.test_runtime_utilities_core": ("TestsFlextCliRuntimeUtilitiesCore",),
            ".unit.test_runtime_utilities_extra": (
                "TestsFlextCliRuntimeUtilitiesExtra",
            ),
            ".unit.test_services_auth_branch_cov": (
                "TestsFlextCliServicesAuthBranchCov",
            ),
            ".unit.test_services_auth_cov": ("TestsFlextCliServicesAuthCov",),
            ".unit.test_services_commands_branch_cov": (
                "TestsFlextCliServicesCommandsBranchCov",
            ),
            ".unit.test_services_commands_cov": ("TestsFlextCliServicesCommandsCov",),
            ".unit.test_services_output_cov": ("TestsFlextCliServicesOutputCov",),
            ".unit.test_services_tables_branch_cov": (
                "TestsFlextCliServicesTablesBranchCov",
            ),
            ".unit.test_services_tables_cov": ("TestsFlextCliServicesTablesCov",),
            ".unit.test_settings": ("TestsFlextCliSettings",),
            ".unit.test_tables": ("TestsFlextCliTables",),
            ".unit.test_tables_branch_cov": ("TestsFlextCliTablesBranchCov",),
            ".unit.test_tables_cov": ("TestsFlextCliTableUtilsCov",),
            ".unit.test_toml_cov": ("TestsFlextCliTomlUtilsCov",),
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
                "s",
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__: list[str] = [
    "TestsFlextCliAuthUtilsCov",
    "TestsFlextCliCaptureLogPrompts",
    "TestsFlextCliCmd",
    "TestsFlextCliCmdCov",
    "TestsFlextCliCommands",
    "TestsFlextCliCommandsUtilsCov",
    "TestsFlextCliCommonParams",
    "TestsFlextCliConstants",
    "TestsFlextCliConstantsUnit",
    "TestsFlextCliConversionCov",
    "TestsFlextCliExamplesSmoke",
    "TestsFlextCliFailingLogPrompts",
    "TestsFlextCliFilesCov",
    "TestsFlextCliFormattersCov",
    "TestsFlextCliJsonCov",
    "TestsFlextCliMatchingCov",
    "TestsFlextCliModelCommandsCov",
    "TestsFlextCliModels",
    "TestsFlextCliOptionsUtilsCov",
    "TestsFlextCliOutputCov",
    "TestsFlextCliPipeline",
    "TestsFlextCliPrompts",
    "TestsFlextCliPromptsCov",
    "TestsFlextCliProtocols",
    "TestsFlextCliProtocolsUnit",
    "TestsFlextCliRulesUtilsCov",
    "TestsFlextCliRuntimeUtilitiesCore",
    "TestsFlextCliRuntimeUtilitiesExtra",
    "TestsFlextCliScriptedPrompts",
    "TestsFlextCliService",
    "TestsFlextCliServiceBase",
    "TestsFlextCliServiceRulesCov",
    "TestsFlextCliServicesAuthBranchCov",
    "TestsFlextCliServicesAuthCov",
    "TestsFlextCliServicesCommandsBranchCov",
    "TestsFlextCliServicesCommandsCov",
    "TestsFlextCliServicesFormattersCov",
    "TestsFlextCliServicesOutputCov",
    "TestsFlextCliServicesTablesBranchCov",
    "TestsFlextCliServicesTablesCov",
    "TestsFlextCliSettings",
    "TestsFlextCliTableUtilsCov",
    "TestsFlextCliTables",
    "TestsFlextCliTablesBranchCov",
    "TestsFlextCliTomlUtilities",
    "TestsFlextCliTomlUtilsCov",
    "TestsFlextCliTypes",
    "TestsFlextCliTypesUnit",
    "TestsFlextCliUtilities",
    "TestsFlextCliUtilitiesCov",
    "TestsFlextCliVersion",
    "TestsFlextCliYamlCov",
    "c",
    "d",
    "e",
    "h",
    "m",
    "make_prompts",
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
]
