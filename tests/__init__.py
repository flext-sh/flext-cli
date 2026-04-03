# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.decorators import FlextDecorators as d
from flext_core.exceptions import FlextExceptions as e
from flext_core.handlers import FlextHandlers as h
from flext_core.lazy import install_lazy_exports, merge_lazy_imports
from flext_core.mixins import FlextMixins as x
from flext_core.result import FlextResult as r
from flext_core.service import FlextService as s
from tests.conftest import (
    Examples,
    InfoTuples,
    pytest_collection_modifyitems,
    pytest_configure,
)
from tests.constants import FlextCliTestConstants, FlextCliTestConstants as c
from tests.helpers._impl import FlextCliTestHelpers
from tests.models import FlextCliTestModels, FlextCliTestModels as m
from tests.protocols import FlextCliTestProtocols, FlextCliTestProtocols as p
from tests.typings import FlextCliTestTypes, FlextCliTestTypes as t
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
from tests.utilities import FlextCliTestUtilities, FlextCliTestUtilities as u

if _t.TYPE_CHECKING:
    import tests.conftest as _tests_conftest

    conftest = _tests_conftest
    import tests.constants as _tests_constants

    constants = _tests_constants
    import tests.helpers as _tests_helpers

    helpers = _tests_helpers
    import tests.models as _tests_models

    models = _tests_models
    import tests.protocols as _tests_protocols

    protocols = _tests_protocols
    import tests.typings as _tests_typings

    typings = _tests_typings
    import tests.unit as _tests_unit

    unit = _tests_unit
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
    import tests.utilities as _tests_utilities

    utilities = _tests_utilities

    _ = (
        ConfigParam,
        ConfigTestFactory,
        ConfigTestScenario,
        ConfigTestType,
        Examples,
        FlextCliTestConstants,
        FlextCliTestHelpers,
        FlextCliTestModels,
        FlextCliTestProtocols,
        FlextCliTestTypes,
        FlextCliTestUtilities,
        InfoTuples,
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
        constants,
        create_cli_app,
        create_decorated_command,
        create_test_config,
        d,
        e,
        h,
        helpers,
        m,
        models,
        p,
        protocols,
        pytest_collection_modifyitems,
        pytest_configure,
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
        typings,
        u,
        unit,
        utilities,
        x,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "tests.helpers",
        "tests.unit",
    ),
    {
        "Examples": "tests.conftest",
        "FlextCliTestConstants": "tests.constants",
        "FlextCliTestModels": "tests.models",
        "FlextCliTestProtocols": "tests.protocols",
        "FlextCliTestTypes": "tests.typings",
        "FlextCliTestUtilities": "tests.utilities",
        "InfoTuples": "tests.conftest",
        "c": ("tests.constants", "FlextCliTestConstants"),
        "conftest": "tests.conftest",
        "constants": "tests.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "h": ("flext_core.handlers", "FlextHandlers"),
        "helpers": "tests.helpers",
        "m": ("tests.models", "FlextCliTestModels"),
        "models": "tests.models",
        "p": ("tests.protocols", "FlextCliTestProtocols"),
        "protocols": "tests.protocols",
        "pytest_collection_modifyitems": "tests.conftest",
        "pytest_configure": "tests.conftest",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_core.service", "FlextService"),
        "t": ("tests.typings", "FlextCliTestTypes"),
        "typings": "tests.typings",
        "u": ("tests.utilities", "FlextCliTestUtilities"),
        "unit": "tests.unit",
        "utilities": "tests.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)

__all__ = [
    "ConfigParam",
    "ConfigTestFactory",
    "ConfigTestScenario",
    "ConfigTestType",
    "Examples",
    "FlextCliTestConstants",
    "FlextCliTestHelpers",
    "FlextCliTestModels",
    "FlextCliTestProtocols",
    "FlextCliTestTypes",
    "FlextCliTestUtilities",
    "InfoTuples",
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
    "constants",
    "create_cli_app",
    "create_decorated_command",
    "create_test_config",
    "d",
    "e",
    "h",
    "helpers",
    "m",
    "models",
    "p",
    "protocols",
    "pytest_collection_modifyitems",
    "pytest_configure",
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
    "typings",
    "u",
    "unit",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
