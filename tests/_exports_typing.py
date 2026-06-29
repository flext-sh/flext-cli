"""Type-checking imports for the tests lazy namespace."""

from __future__ import annotations

from flext_tests import d, e, h, r, td, tf, tk, tm, tv, x

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
    make_capture_prompts,
    make_failing_prompts,
    make_prompts,
    reset_settings,
)
from tests.unit.test_auth_utils_cov import TestsFlextCliAuthUtilsCov
from tests.unit.test_base import TestsFlextCliServiceBaseBehavior
from tests.unit.test_cli_params import TestsFlextCliCommonParams
from tests.unit.test_cli_service import TestsFlextCliService
from tests.unit.test_cmd import TestsFlextCliCmd
from tests.unit.test_cmd_cov import TestsFlextCliCmdCov
from tests.unit.test_cmd_runtime_validation_branch_cov import (
    TestsFlextCliCmdRuntimeValidationBranchCov,
)
from tests.unit.test_commands_utils_cov import TestsFlextCliCommandsUtilsCov
from tests.unit.test_constants import TestsFlextCliConstantsUnit
from tests.unit.test_conversion_cov import TestsFlextCliConversionCov
from tests.unit.test_examples_models_utilities_cov import (
    TestsFlextCliExampleModelsUtilitiesCov,
)
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
from tests.unit.test_options_public_cov import TestsFlextCliOptionsPublicCoverage
from tests.unit.test_output_cov import TestsFlextCliOutputCov
from tests.unit.test_params_branch_cov import TestsFlextCliParamsBranchCov
from tests.unit.test_pipeline import TestsFlextCliPipeline
from tests.unit.test_prompts import TestsFlextCliPrompts
from tests.unit.test_prompts_cov import TestsFlextCliPromptsCov
from tests.unit.test_protocols import TestsFlextCliProtocolsUnit
from tests.unit.test_public_contracts_cov import TestsFlextCliPublicContractsCoverage
from tests.unit.test_rules_cov import TestsFlextCliRulesCov
from tests.unit.test_runtime_utilities_core import TestsFlextCliRuntimeUtilitiesCore
from tests.unit.test_runtime_utilities_extra import TestsFlextCliRuntimeUtilitiesExtra
from tests.unit.test_services_auth_branch_cov import TestsFlextCliServicesAuthBranchCov
from tests.unit.test_services_auth_cov import TestsFlextCliServicesAuthCov
from tests.unit.test_services_output_cov import TestsFlextCliServicesOutputCov
from tests.unit.test_services_tables_branch_cov import (
    TestsFlextCliServicesTablesBranchCov,
)
from tests.unit.test_services_tables_cov import TestsFlextCliServicesTablesCov
from tests.unit.test_settings import TestsFlextCliSettingsUnit
from tests.unit.test_tables import TestsFlextCliTables
from tests.unit.test_tables_branch_cov import TestsFlextCliTablesBranchCov
from tests.unit.test_tables_cov import TestsFlextCliTableUtilsCov
from tests.unit.test_toml_cov import TestsFlextCliTomlUtilsCov
from tests.unit.test_toml_sync_cov import TestsFlextCliTomlSyncCoverage
from tests.unit.test_toml_utilities import TestsFlextCliTomlUtilities
from tests.unit.test_typings import TestsFlextCliTypesUnit
from tests.unit.test_utilities_cov import TestsFlextCliUtilitiesCov
from tests.unit.test_version import TestsFlextCliVersion
from tests.unit.test_yaml_cov import TestsFlextCliYamlCov
from tests.utilities import TestsFlextCliUtilities, u

__all__: list[str] = [
    "TestsFlextCliAuthUtilsCov",
    "TestsFlextCliCaptureLogPrompts",
    "TestsFlextCliCmd",
    "TestsFlextCliCmdCov",
    "TestsFlextCliCmdRuntimeValidationBranchCov",
    "TestsFlextCliCommandsUtilsCov",
    "TestsFlextCliCommonParams",
    "TestsFlextCliConstants",
    "TestsFlextCliConstantsUnit",
    "TestsFlextCliConversionCov",
    "TestsFlextCliExampleModelsUtilitiesCov",
    "TestsFlextCliExamplesSmoke",
    "TestsFlextCliFailingLogPrompts",
    "TestsFlextCliFilesCov",
    "TestsFlextCliFormattersCov",
    "TestsFlextCliJsonCov",
    "TestsFlextCliMatchingCov",
    "TestsFlextCliModelCommandsCov",
    "TestsFlextCliModels",
    "TestsFlextCliOptionsPublicCoverage",
    "TestsFlextCliOptionsUtilsCov",
    "TestsFlextCliOutputCov",
    "TestsFlextCliParamsBranchCov",
    "TestsFlextCliPipeline",
    "TestsFlextCliPrompts",
    "TestsFlextCliPromptsCov",
    "TestsFlextCliProtocols",
    "TestsFlextCliProtocolsUnit",
    "TestsFlextCliPublicContractsCoverage",
    "TestsFlextCliRulesCov",
    "TestsFlextCliRuntimeUtilitiesCore",
    "TestsFlextCliRuntimeUtilitiesExtra",
    "TestsFlextCliScriptedPrompts",
    "TestsFlextCliService",
    "TestsFlextCliServiceBase",
    "TestsFlextCliServiceBaseBehavior",
    "TestsFlextCliServicesAuthBranchCov",
    "TestsFlextCliServicesAuthCov",
    "TestsFlextCliServicesFormattersCov",
    "TestsFlextCliServicesOutputCov",
    "TestsFlextCliServicesTablesBranchCov",
    "TestsFlextCliServicesTablesCov",
    "TestsFlextCliSettings",
    "TestsFlextCliSettingsUnit",
    "TestsFlextCliTableUtilsCov",
    "TestsFlextCliTables",
    "TestsFlextCliTablesBranchCov",
    "TestsFlextCliTomlSyncCoverage",
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
    "make_capture_prompts",
    "make_failing_prompts",
    "make_prompts",
    "p",
    "r",
    "reset_settings",
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
