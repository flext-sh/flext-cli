# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

import typing as _t

from flext_core.constants import FlextConstants as c
from flext_core.decorators import FlextDecorators as d
from flext_core.exceptions import FlextExceptions as e
from flext_core.handlers import FlextHandlers as h
from flext_core.lazy import install_lazy_exports
from flext_core.mixins import FlextMixins as x
from flext_core.models import FlextModels as m
from flext_core.protocols import FlextProtocols as p
from flext_core.result import FlextResult as r
from flext_core.service import FlextService as s
from flext_core.typings import FlextTypes as t
from flext_core.utilities import FlextUtilities as u
from tests.unit.conftest import reset_config_singleton
from tests.unit.test_base import TestsCliServiceBase
from tests.unit.test_cli_params import (
    ConfigParam,
    TestsCliCommonParams,
    create_cli_app,
    create_decorated_command,
    create_test_config,
)
from tests.unit.test_cli_service import TestsCliService
from tests.unit.test_cmd import TestsCliCmd
from tests.unit.test_cmd_cov import (
    test_get_config_info_failure_on_exception,
    test_show_config_failure_when_info_result_is_failure,
    test_show_config_outer_exception_path,
    test_show_config_paths_failure_on_exception,
    test_validate_config_failure_on_exception,
)
from tests.unit.test_commands import TestsCliCommands
from tests.unit.test_config import (
    ConfigTestFactory,
    ConfigTestScenario,
    ConfigTestType,
    TestsCliConfigBasics,
    TestsCliConfigEdgeCases,
    TestsCliConfigIntegration,
    TestsCliConfigService,
    TestsCliConfigValidation,
    TestsCliLoggingConfig,
)
from tests.unit.test_constants import TestsCliConstants
from tests.unit.test_examples_smoke import TestFlextCliExamplesSmoke
from tests.unit.test_prompts import TestsCliPrompts
from tests.unit.test_prompts_cov import (
    test_prompt_logs_input_when_not_test_env,
    test_read_confirmation_input_paths,
)
from tests.unit.test_protocols import TestsCliProtocols
from tests.unit.test_tables import TestsCliTables
from tests.unit.test_typings import TestsCliTypings
from tests.unit.test_utilities_cov import (
    test_process_fail_and_collect_paths,
    test_process_mapping_fail_and_collect_paths,
    test_validation_v_uses_custom_message_on_empty_failure,
)
from tests.unit.test_version import T, TestsCliVersion

if _t.TYPE_CHECKING:
    import tests.unit.conftest as _tests_unit_conftest

    conftest = _tests_unit_conftest
    import tests.unit.test_base as _tests_unit_test_base

    test_base = _tests_unit_test_base
    import tests.unit.test_cli_params as _tests_unit_test_cli_params

    test_cli_params = _tests_unit_test_cli_params
    import tests.unit.test_cli_service as _tests_unit_test_cli_service

    test_cli_service = _tests_unit_test_cli_service
    import tests.unit.test_cmd as _tests_unit_test_cmd

    test_cmd = _tests_unit_test_cmd
    import tests.unit.test_cmd_cov as _tests_unit_test_cmd_cov

    test_cmd_cov = _tests_unit_test_cmd_cov
    import tests.unit.test_commands as _tests_unit_test_commands

    test_commands = _tests_unit_test_commands
    import tests.unit.test_config as _tests_unit_test_config

    test_config = _tests_unit_test_config
    import tests.unit.test_constants as _tests_unit_test_constants

    test_constants = _tests_unit_test_constants
    import tests.unit.test_examples_smoke as _tests_unit_test_examples_smoke

    test_examples_smoke = _tests_unit_test_examples_smoke
    import tests.unit.test_prompts as _tests_unit_test_prompts

    test_prompts = _tests_unit_test_prompts
    import tests.unit.test_prompts_cov as _tests_unit_test_prompts_cov

    test_prompts_cov = _tests_unit_test_prompts_cov
    import tests.unit.test_protocols as _tests_unit_test_protocols

    test_protocols = _tests_unit_test_protocols
    import tests.unit.test_tables as _tests_unit_test_tables

    test_tables = _tests_unit_test_tables
    import tests.unit.test_typings as _tests_unit_test_typings

    test_typings = _tests_unit_test_typings
    import tests.unit.test_utilities_cov as _tests_unit_test_utilities_cov

    test_utilities_cov = _tests_unit_test_utilities_cov
    import tests.unit.test_version as _tests_unit_test_version

    test_version = _tests_unit_test_version

    _ = (
        ConfigParam,
        ConfigTestFactory,
        ConfigTestScenario,
        ConfigTestType,
        T,
        TestFlextCliExamplesSmoke,
        TestsCliCmd,
        TestsCliCommands,
        TestsCliCommonParams,
        TestsCliConfigBasics,
        TestsCliConfigEdgeCases,
        TestsCliConfigIntegration,
        TestsCliConfigService,
        TestsCliConfigValidation,
        TestsCliConstants,
        TestsCliLoggingConfig,
        TestsCliPrompts,
        TestsCliProtocols,
        TestsCliService,
        TestsCliServiceBase,
        TestsCliTables,
        TestsCliTypings,
        TestsCliVersion,
        c,
        conftest,
        create_cli_app,
        create_decorated_command,
        create_test_config,
        d,
        e,
        h,
        m,
        p,
        r,
        reset_config_singleton,
        s,
        t,
        test_base,
        test_cli_params,
        test_cli_service,
        test_cmd,
        test_cmd_cov,
        test_commands,
        test_config,
        test_constants,
        test_examples_smoke,
        test_get_config_info_failure_on_exception,
        test_process_fail_and_collect_paths,
        test_process_mapping_fail_and_collect_paths,
        test_prompt_logs_input_when_not_test_env,
        test_prompts,
        test_prompts_cov,
        test_protocols,
        test_read_confirmation_input_paths,
        test_show_config_failure_when_info_result_is_failure,
        test_show_config_outer_exception_path,
        test_show_config_paths_failure_on_exception,
        test_tables,
        test_typings,
        test_utilities_cov,
        test_validate_config_failure_on_exception,
        test_validation_v_uses_custom_message_on_empty_failure,
        test_version,
        u,
        x,
    )
_LAZY_IMPORTS = {
    "ConfigParam": "tests.unit.test_cli_params",
    "ConfigTestFactory": "tests.unit.test_config",
    "ConfigTestScenario": "tests.unit.test_config",
    "ConfigTestType": "tests.unit.test_config",
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
    "c": ("flext_core.constants", "FlextConstants"),
    "conftest": "tests.unit.conftest",
    "create_cli_app": "tests.unit.test_cli_params",
    "create_decorated_command": "tests.unit.test_cli_params",
    "create_test_config": "tests.unit.test_cli_params",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "reset_config_singleton": "tests.unit.conftest",
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
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
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "ConfigParam",
    "ConfigTestFactory",
    "ConfigTestScenario",
    "ConfigTestType",
    "T",
    "TestFlextCliExamplesSmoke",
    "TestsCliCmd",
    "TestsCliCommands",
    "TestsCliCommonParams",
    "TestsCliConfigBasics",
    "TestsCliConfigEdgeCases",
    "TestsCliConfigIntegration",
    "TestsCliConfigService",
    "TestsCliConfigValidation",
    "TestsCliConstants",
    "TestsCliLoggingConfig",
    "TestsCliPrompts",
    "TestsCliProtocols",
    "TestsCliService",
    "TestsCliServiceBase",
    "TestsCliTables",
    "TestsCliTypings",
    "TestsCliVersion",
    "c",
    "conftest",
    "create_cli_app",
    "create_decorated_command",
    "create_test_config",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "reset_config_singleton",
    "s",
    "t",
    "test_base",
    "test_cli_params",
    "test_cli_service",
    "test_cmd",
    "test_cmd_cov",
    "test_commands",
    "test_config",
    "test_constants",
    "test_examples_smoke",
    "test_get_config_info_failure_on_exception",
    "test_process_fail_and_collect_paths",
    "test_process_mapping_fail_and_collect_paths",
    "test_prompt_logs_input_when_not_test_env",
    "test_prompts",
    "test_prompts_cov",
    "test_protocols",
    "test_read_confirmation_input_paths",
    "test_show_config_failure_when_info_result_is_failure",
    "test_show_config_outer_exception_path",
    "test_show_config_paths_failure_on_exception",
    "test_tables",
    "test_typings",
    "test_utilities_cov",
    "test_validate_config_failure_on_exception",
    "test_validation_v_uses_custom_message_on_empty_failure",
    "test_version",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
