# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import *

    from tests import conftest, constants, models, typings, unit
    from tests.conftest import *
    from tests.constants import *
    from tests.helpers._impl import *
    from tests.models import *
    from tests.typings import *
    from tests.unit import (
        test_base,
        test_cli_params,
        test_cli_service,
        test_cmd,
        test_cmd_cov,
        test_commands,
        test_config,
        test_constants,
        test_examples_smoke,
        test_prompts,
        test_prompts_cov,
        test_protocols,
        test_tables,
        test_typings,
        test_utilities_cov,
        test_version,
    )
    from tests.unit.conftest import *
    from tests.unit.test_base import *
    from tests.unit.test_cli_params import *
    from tests.unit.test_cli_service import *
    from tests.unit.test_cmd import *
    from tests.unit.test_cmd_cov import *
    from tests.unit.test_commands import *
    from tests.unit.test_config import *
    from tests.unit.test_constants import *
    from tests.unit.test_examples_smoke import *
    from tests.unit.test_prompts import *
    from tests.unit.test_prompts_cov import *
    from tests.unit.test_protocols import *
    from tests.unit.test_tables import *
    from tests.unit.test_typings import *
    from tests.unit.test_utilities_cov import *
    from tests.unit.test_version import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "ConfigParam": "tests.unit.test_cli_params",
    "ConfigTestFactory": "tests.unit.test_config",
    "ConfigTestScenario": "tests.unit.test_config",
    "ConfigTestType": "tests.unit.test_config",
    "Examples": "tests.conftest",
    "FlextCliTestConstants": "tests.constants",
    "FlextCliTestHelpers": "tests.helpers._impl",
    "FlextCliTestModels": "tests.models",
    "FlextCliTestTypes": "tests.typings",
    "InfoTuples": "tests.conftest",
    "T": "tests.unit.test_version",
    "TestFlextCliExamplesSmoke": "tests.unit.test_examples_smoke",
    "TestsCliCmd": "tests.unit.test_cmd",
    "TestsCliCommands": "tests.unit.test_commands",
    "TestsCliCommonParams": "tests.unit.test_cli_params",
    "TestsCliConfigBasics": "tests.unit.test_config",
    "TestsCliConfigEdgeCases": "tests.unit.test_config",
    "TestsCliConfigIntegration": "tests.unit.test_config",
    "TestsCliConfigService": "tests.unit.test_config",
    "TestsCliConfigValidation": "tests.unit.test_config",
    "TestsCliConstants": "tests.unit.test_constants",
    "TestsCliLoggingConfig": "tests.unit.test_config",
    "TestsCliPrompts": "tests.unit.test_prompts",
    "TestsCliProtocols": "tests.unit.test_protocols",
    "TestsCliService": "tests.unit.test_cli_service",
    "TestsCliServiceBase": "tests.unit.test_base",
    "TestsCliTables": "tests.unit.test_tables",
    "TestsCliTypings": "tests.unit.test_typings",
    "TestsCliVersion": "tests.unit.test_version",
    "c": ["tests.constants", "FlextCliTestConstants"],
    "conftest": "tests.conftest",
    "constants": "tests.constants",
    "create_cli_app": "tests.unit.test_cli_params",
    "create_decorated_command": "tests.unit.test_cli_params",
    "create_test_config": "tests.unit.test_cli_params",
    "d": "flext_tests",
    "e": "flext_tests",
    "h": "flext_tests",
    "m": ["tests.models", "FlextCliTestModels"],
    "models": "tests.models",
    "p": "flext_tests",
    "pytest_collection_modifyitems": "tests.conftest",
    "pytest_configure": "tests.conftest",
    "r": "flext_tests",
    "reset_config_singleton": "tests.unit.conftest",
    "s": "flext_tests",
    "t": ["tests.typings", "FlextCliTestTypes"],
    "test_base": "tests.unit.test_base",
    "test_cli_params": "tests.unit.test_cli_params",
    "test_cli_service": "tests.unit.test_cli_service",
    "test_cmd": "tests.unit.test_cmd",
    "test_cmd_cov": "tests.unit.test_cmd_cov",
    "test_commands": "tests.unit.test_commands",
    "test_config": "tests.unit.test_config",
    "test_constants": "tests.unit.test_constants",
    "test_examples_smoke": "tests.unit.test_examples_smoke",
    "test_get_config_info_failure_on_exception": "tests.unit.test_cmd_cov",
    "test_process_fail_and_collect_paths": "tests.unit.test_utilities_cov",
    "test_process_mapping_fail_and_collect_paths": "tests.unit.test_utilities_cov",
    "test_prompt_logs_input_when_not_test_env": "tests.unit.test_prompts_cov",
    "test_prompts": "tests.unit.test_prompts",
    "test_prompts_cov": "tests.unit.test_prompts_cov",
    "test_protocols": "tests.unit.test_protocols",
    "test_read_confirmation_input_paths": "tests.unit.test_prompts_cov",
    "test_show_config_failure_when_info_result_is_failure": "tests.unit.test_cmd_cov",
    "test_show_config_outer_exception_path": "tests.unit.test_cmd_cov",
    "test_show_config_paths_failure_on_exception": "tests.unit.test_cmd_cov",
    "test_tables": "tests.unit.test_tables",
    "test_typings": "tests.unit.test_typings",
    "test_utilities_cov": "tests.unit.test_utilities_cov",
    "test_validate_config_failure_on_exception": "tests.unit.test_cmd_cov",
    "test_validation_v_uses_custom_message_on_empty_failure": "tests.unit.test_utilities_cov",
    "test_version": "tests.unit.test_version",
    "typings": "tests.typings",
    "u": "flext_tests",
    "unit": "tests.unit",
    "x": "flext_tests",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))
