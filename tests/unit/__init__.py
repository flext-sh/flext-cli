# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import (
        c as c,
        d as d,
        e as e,
        h as h,
        m as m,
        p as p,
        r as r,
        s as s,
        t as t,
        td as td,
        tf as tf,
        tk as tk,
        tm as tm,
        tv as tv,
        u as u,
        x as x,
    )

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
        ".test_formatters_cov": (
            "TestsFlextCliFormattersCov",
            "TestsFlextCliServicesFormattersCov",
        ),
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
        ".test_services_auth_branch_cov": ("TestsFlextCliServicesAuthBranchCov",),
        ".test_services_auth_cov": ("TestsFlextCliServicesAuthCov",),
        ".test_services_output_cov": ("TestsFlextCliServicesOutputCov",),
        ".test_services_tables_branch_cov": ("TestsFlextCliServicesTablesBranchCov",),
        ".test_services_tables_cov": ("TestsFlextCliServicesTablesCov",),
        ".test_settings": ("TestsFlextCliSettingsUnit",),
        ".test_tables": ("TestsFlextCliTables",),
        ".test_tables_branch_cov": ("TestsFlextCliTablesBranchCov",),
        ".test_tables_cov": ("TestsFlextCliTableUtilsCov",),
        ".test_toml_cov": ("TestsFlextCliTomlUtilsCov",),
        ".test_toml_sync_cov": ("TestsFlextCliTomlSyncCoverage",),
        ".test_toml_utilities": ("TestsFlextCliTomlUtilities",),
        ".test_typings": ("TestsFlextCliTypesUnit",),
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
