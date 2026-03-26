# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_tests import d, e, h, r, s, x

    from tests import integration, unit
    from tests.conftest import (
        CliCommandFactory,
        CliSessionFactory,
        Examples,
        InfoTuples,
        LoggingConfigFactory,
        clean_flext_container,
        cli_command_factory,
        cli_runner,
        cli_session_factory,
        fixture_config_file,
        fixture_data_csv,
        fixture_data_json,
        flext_cli_api,
        flext_cli_cmd,
        flext_cli_commands,
        flext_cli_config,
        flext_cli_constants,
        flext_cli_context,
        flext_cli_debug,
        flext_cli_file_tools,
        flext_cli_models,
        flext_cli_output,
        flext_cli_prompts,
        flext_cli_protocols,
        flext_cli_utilities,
        flext_test_docker,
        input_exception_simulator,
        input_simulator,
        load_fixture_config,
        load_fixture_data,
        logging_config_factory,
        mock_env_vars,
        password_simulator,
        pytest_collection_modifyitems,
        pytest_configure,
        reset_singletons,
        sample_command_data,
        sample_config_data,
        sample_file_data,
        temp_csv_file,
        temp_dir,
        temp_file,
        temp_json_file,
        temp_yaml_file,
    )
    from tests.constants import FlextCliTestConstants, FlextCliTestConstants as c
    from tests.helpers._impl import (
        ConfigFactory,
        FlextCliTestHelpers,
        ParamsFactory,
        TestScenario,
        ValidationHelper,
        _is_json_dict,
        _is_json_list,
    )
    from tests.integration.test_cli_workflow import TestsCliWorkflowIntegration
    from tests.models import FlextCliTestModels, FlextCliTestModels as m
    from tests.protocols import FlextCliTestProtocols, FlextCliTestProtocols as p
    from tests.typings import FlextCliTestTypes, FlextCliTestTypes as t
    from tests.unit.conftest import reset_config_singleton
    from tests.unit.test_base import TestsCliServiceBase
    from tests.unit.test_cli import TestsCliCli
    from tests.unit.test_cli_extended import TestsCliCliExtended
    from tests.unit.test_cli_params import (
        ConfigParam,
        TestsCliCommonParams,
        create_cli_app,
        create_decorated_command,
        create_test_config,
    )
    from tests.unit.test_cmd import TestsCliCmd
    from tests.unit.test_cmd_cov import (
        test_get_config_info_failure_on_exception,
        test_show_config_failure_when_info_result_is_failure,
        test_show_config_outer_exception_path,
        test_show_config_paths_failure_on_exception,
        test_validate_config_failure_on_exception,
    )
    from tests.unit.test_commands import TestsCliCommands
    from tests.unit.test_comprehensive_models import (
        TestsCliComprehensiveModels,
        TestsCliModelSerialization,
        TestsCliModelValidation,
    )
    from tests.unit.test_config import (
        ConfigTestFactory,
        ConfigTestScenario,
        ConfigTestType,
        TestsCliConfigBasics,
        TestsCliConfigConcurrency,
        TestsCliConfigEdgeCases,
        TestsCliConfigIntegration,
        TestsCliConfigLogging,
        TestsCliConfigMemory,
        TestsCliConfigService,
        TestsCliConfigValidation,
        TestsCliLoggingConfig,
    )
    from tests.unit.test_config_model_integration import TestsCliConfigModelIntegration
    from tests.unit.test_constants import TestsCliConstants
    from tests.unit.test_debug import TestsCliDebug
    from tests.unit.test_model_command_comprehensive import (
        TestsCliModelCommandComprehensive,
    )
    from tests.unit.test_model_factories import TestsCliModelFactories
    from tests.unit.test_performance_automated import TestsCliPerformanceAutomated
    from tests.unit.test_prompts import TestsCliPrompts
    from tests.unit.test_prompts_cov import (
        test_prompt_logs_input_when_not_test_env,
        test_read_confirmation_input_paths,
    )
    from tests.unit.test_protocols import TestsCliProtocols
    from tests.unit.test_railway_pattern_example import TestsCliRailwayPatternExample
    from tests.unit.test_typings import TestsCliTypings, TypingTestCase, TypingTestType
    from tests.unit.test_utilities_cov import (
        test_process_fail_and_collect_paths,
        test_process_mapping_fail_and_collect_paths,
        test_validate_required_string_raises_value_error,
        test_validation_state_requires_criteria,
        test_validation_v_uses_custom_message_on_empty_failure,
    )
    from tests.unit.test_version import T, TestsCliVersion
    from tests.utilities import FlextCliTestUtilities, FlextCliTestUtilities as u

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "CliCommandFactory": ["tests.conftest", "CliCommandFactory"],
    "CliSessionFactory": ["tests.conftest", "CliSessionFactory"],
    "ConfigFactory": ["tests.helpers._impl", "ConfigFactory"],
    "ConfigParam": ["tests.unit.test_cli_params", "ConfigParam"],
    "ConfigTestFactory": ["tests.unit.test_config", "ConfigTestFactory"],
    "ConfigTestScenario": ["tests.unit.test_config", "ConfigTestScenario"],
    "ConfigTestType": ["tests.unit.test_config", "ConfigTestType"],
    "Examples": ["tests.conftest", "Examples"],
    "FlextCliTestConstants": ["tests.constants", "FlextCliTestConstants"],
    "FlextCliTestHelpers": ["tests.helpers._impl", "FlextCliTestHelpers"],
    "FlextCliTestModels": ["tests.models", "FlextCliTestModels"],
    "FlextCliTestProtocols": ["tests.protocols", "FlextCliTestProtocols"],
    "FlextCliTestTypes": ["tests.typings", "FlextCliTestTypes"],
    "FlextCliTestUtilities": ["tests.utilities", "FlextCliTestUtilities"],
    "InfoTuples": ["tests.conftest", "InfoTuples"],
    "LoggingConfigFactory": ["tests.conftest", "LoggingConfigFactory"],
    "ParamsFactory": ["tests.helpers._impl", "ParamsFactory"],
    "T": ["tests.unit.test_version", "T"],
    "TestScenario": ["tests.helpers._impl", "TestScenario"],
    "TestsCliCli": ["tests.unit.test_cli", "TestsCliCli"],
    "TestsCliCliExtended": ["tests.unit.test_cli_extended", "TestsCliCliExtended"],
    "TestsCliCmd": ["tests.unit.test_cmd", "TestsCliCmd"],
    "TestsCliCommands": ["tests.unit.test_commands", "TestsCliCommands"],
    "TestsCliCommonParams": ["tests.unit.test_cli_params", "TestsCliCommonParams"],
    "TestsCliComprehensiveModels": [
        "tests.unit.test_comprehensive_models",
        "TestsCliComprehensiveModels",
    ],
    "TestsCliConfigBasics": ["tests.unit.test_config", "TestsCliConfigBasics"],
    "TestsCliConfigConcurrency": [
        "tests.unit.test_config",
        "TestsCliConfigConcurrency",
    ],
    "TestsCliConfigEdgeCases": ["tests.unit.test_config", "TestsCliConfigEdgeCases"],
    "TestsCliConfigIntegration": [
        "tests.unit.test_config",
        "TestsCliConfigIntegration",
    ],
    "TestsCliConfigLogging": ["tests.unit.test_config", "TestsCliConfigLogging"],
    "TestsCliConfigMemory": ["tests.unit.test_config", "TestsCliConfigMemory"],
    "TestsCliConfigModelIntegration": [
        "tests.unit.test_config_model_integration",
        "TestsCliConfigModelIntegration",
    ],
    "TestsCliConfigService": ["tests.unit.test_config", "TestsCliConfigService"],
    "TestsCliConfigValidation": ["tests.unit.test_config", "TestsCliConfigValidation"],
    "TestsCliConstants": ["tests.unit.test_constants", "TestsCliConstants"],
    "TestsCliDebug": ["tests.unit.test_debug", "TestsCliDebug"],
    "TestsCliLoggingConfig": ["tests.unit.test_config", "TestsCliLoggingConfig"],
    "TestsCliModelCommandComprehensive": [
        "tests.unit.test_model_command_comprehensive",
        "TestsCliModelCommandComprehensive",
    ],
    "TestsCliModelFactories": [
        "tests.unit.test_model_factories",
        "TestsCliModelFactories",
    ],
    "TestsCliModelSerialization": [
        "tests.unit.test_comprehensive_models",
        "TestsCliModelSerialization",
    ],
    "TestsCliModelValidation": [
        "tests.unit.test_comprehensive_models",
        "TestsCliModelValidation",
    ],
    "TestsCliPerformanceAutomated": [
        "tests.unit.test_performance_automated",
        "TestsCliPerformanceAutomated",
    ],
    "TestsCliPrompts": ["tests.unit.test_prompts", "TestsCliPrompts"],
    "TestsCliProtocols": ["tests.unit.test_protocols", "TestsCliProtocols"],
    "TestsCliRailwayPatternExample": [
        "tests.unit.test_railway_pattern_example",
        "TestsCliRailwayPatternExample",
    ],
    "TestsCliServiceBase": ["tests.unit.test_base", "TestsCliServiceBase"],
    "TestsCliTypings": ["tests.unit.test_typings", "TestsCliTypings"],
    "TestsCliVersion": ["tests.unit.test_version", "TestsCliVersion"],
    "TestsCliWorkflowIntegration": [
        "tests.integration.test_cli_workflow",
        "TestsCliWorkflowIntegration",
    ],
    "TypingTestCase": ["tests.unit.test_typings", "TypingTestCase"],
    "TypingTestType": ["tests.unit.test_typings", "TypingTestType"],
    "ValidationHelper": ["tests.helpers._impl", "ValidationHelper"],
    "_is_json_dict": ["tests.helpers._impl", "_is_json_dict"],
    "_is_json_list": ["tests.helpers._impl", "_is_json_list"],
    "c": ["tests.constants", "FlextCliTestConstants"],
    "clean_flext_container": ["tests.conftest", "clean_flext_container"],
    "cli_command_factory": ["tests.conftest", "cli_command_factory"],
    "cli_runner": ["tests.conftest", "cli_runner"],
    "cli_session_factory": ["tests.conftest", "cli_session_factory"],
    "create_cli_app": ["tests.unit.test_cli_params", "create_cli_app"],
    "create_decorated_command": [
        "tests.unit.test_cli_params",
        "create_decorated_command",
    ],
    "create_test_config": ["tests.unit.test_cli_params", "create_test_config"],
    "d": ["flext_tests", "d"],
    "e": ["flext_tests", "e"],
    "fixture_config_file": ["tests.conftest", "fixture_config_file"],
    "fixture_data_csv": ["tests.conftest", "fixture_data_csv"],
    "fixture_data_json": ["tests.conftest", "fixture_data_json"],
    "flext_cli_api": ["tests.conftest", "flext_cli_api"],
    "flext_cli_cmd": ["tests.conftest", "flext_cli_cmd"],
    "flext_cli_commands": ["tests.conftest", "flext_cli_commands"],
    "flext_cli_config": ["tests.conftest", "flext_cli_config"],
    "flext_cli_constants": ["tests.conftest", "flext_cli_constants"],
    "flext_cli_context": ["tests.conftest", "flext_cli_context"],
    "flext_cli_debug": ["tests.conftest", "flext_cli_debug"],
    "flext_cli_file_tools": ["tests.conftest", "flext_cli_file_tools"],
    "flext_cli_models": ["tests.conftest", "flext_cli_models"],
    "flext_cli_output": ["tests.conftest", "flext_cli_output"],
    "flext_cli_prompts": ["tests.conftest", "flext_cli_prompts"],
    "flext_cli_protocols": ["tests.conftest", "flext_cli_protocols"],
    "flext_cli_utilities": ["tests.conftest", "flext_cli_utilities"],
    "flext_test_docker": ["tests.conftest", "flext_test_docker"],
    "h": ["flext_tests", "h"],
    "input_exception_simulator": ["tests.conftest", "input_exception_simulator"],
    "input_simulator": ["tests.conftest", "input_simulator"],
    "integration": ["tests.integration", ""],
    "load_fixture_config": ["tests.conftest", "load_fixture_config"],
    "load_fixture_data": ["tests.conftest", "load_fixture_data"],
    "logging_config_factory": ["tests.conftest", "logging_config_factory"],
    "m": ["tests.models", "FlextCliTestModels"],
    "mock_env_vars": ["tests.conftest", "mock_env_vars"],
    "p": ["tests.protocols", "FlextCliTestProtocols"],
    "password_simulator": ["tests.conftest", "password_simulator"],
    "pytest_collection_modifyitems": [
        "tests.conftest",
        "pytest_collection_modifyitems",
    ],
    "pytest_configure": ["tests.conftest", "pytest_configure"],
    "r": ["flext_tests", "r"],
    "reset_config_singleton": ["tests.unit.conftest", "reset_config_singleton"],
    "reset_singletons": ["tests.conftest", "reset_singletons"],
    "s": ["flext_tests", "s"],
    "sample_command_data": ["tests.conftest", "sample_command_data"],
    "sample_config_data": ["tests.conftest", "sample_config_data"],
    "sample_file_data": ["tests.conftest", "sample_file_data"],
    "t": ["tests.typings", "FlextCliTestTypes"],
    "temp_csv_file": ["tests.conftest", "temp_csv_file"],
    "temp_dir": ["tests.conftest", "temp_dir"],
    "temp_file": ["tests.conftest", "temp_file"],
    "temp_json_file": ["tests.conftest", "temp_json_file"],
    "temp_yaml_file": ["tests.conftest", "temp_yaml_file"],
    "test_get_config_info_failure_on_exception": [
        "tests.unit.test_cmd_cov",
        "test_get_config_info_failure_on_exception",
    ],
    "test_process_fail_and_collect_paths": [
        "tests.unit.test_utilities_cov",
        "test_process_fail_and_collect_paths",
    ],
    "test_process_mapping_fail_and_collect_paths": [
        "tests.unit.test_utilities_cov",
        "test_process_mapping_fail_and_collect_paths",
    ],
    "test_prompt_logs_input_when_not_test_env": [
        "tests.unit.test_prompts_cov",
        "test_prompt_logs_input_when_not_test_env",
    ],
    "test_read_confirmation_input_paths": [
        "tests.unit.test_prompts_cov",
        "test_read_confirmation_input_paths",
    ],
    "test_show_config_failure_when_info_result_is_failure": [
        "tests.unit.test_cmd_cov",
        "test_show_config_failure_when_info_result_is_failure",
    ],
    "test_show_config_outer_exception_path": [
        "tests.unit.test_cmd_cov",
        "test_show_config_outer_exception_path",
    ],
    "test_show_config_paths_failure_on_exception": [
        "tests.unit.test_cmd_cov",
        "test_show_config_paths_failure_on_exception",
    ],
    "test_validate_config_failure_on_exception": [
        "tests.unit.test_cmd_cov",
        "test_validate_config_failure_on_exception",
    ],
    "test_validate_required_string_raises_value_error": [
        "tests.unit.test_utilities_cov",
        "test_validate_required_string_raises_value_error",
    ],
    "test_validation_state_requires_criteria": [
        "tests.unit.test_utilities_cov",
        "test_validation_state_requires_criteria",
    ],
    "test_validation_v_uses_custom_message_on_empty_failure": [
        "tests.unit.test_utilities_cov",
        "test_validation_v_uses_custom_message_on_empty_failure",
    ],
    "u": ["tests.utilities", "FlextCliTestUtilities"],
    "unit": ["tests.unit", ""],
    "x": ["flext_tests", "x"],
}

__all__ = [
    "CliCommandFactory",
    "CliSessionFactory",
    "ConfigFactory",
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
    "LoggingConfigFactory",
    "ParamsFactory",
    "T",
    "TestScenario",
    "TestsCliCli",
    "TestsCliCliExtended",
    "TestsCliCmd",
    "TestsCliCommands",
    "TestsCliCommonParams",
    "TestsCliComprehensiveModels",
    "TestsCliConfigBasics",
    "TestsCliConfigConcurrency",
    "TestsCliConfigEdgeCases",
    "TestsCliConfigIntegration",
    "TestsCliConfigLogging",
    "TestsCliConfigMemory",
    "TestsCliConfigModelIntegration",
    "TestsCliConfigService",
    "TestsCliConfigValidation",
    "TestsCliConstants",
    "TestsCliDebug",
    "TestsCliLoggingConfig",
    "TestsCliModelCommandComprehensive",
    "TestsCliModelFactories",
    "TestsCliModelSerialization",
    "TestsCliModelValidation",
    "TestsCliPerformanceAutomated",
    "TestsCliPrompts",
    "TestsCliProtocols",
    "TestsCliRailwayPatternExample",
    "TestsCliServiceBase",
    "TestsCliTypings",
    "TestsCliVersion",
    "TestsCliWorkflowIntegration",
    "TypingTestCase",
    "TypingTestType",
    "ValidationHelper",
    "_is_json_dict",
    "_is_json_list",
    "c",
    "clean_flext_container",
    "cli_command_factory",
    "cli_runner",
    "cli_session_factory",
    "create_cli_app",
    "create_decorated_command",
    "create_test_config",
    "d",
    "e",
    "fixture_config_file",
    "fixture_data_csv",
    "fixture_data_json",
    "flext_cli_api",
    "flext_cli_cmd",
    "flext_cli_commands",
    "flext_cli_config",
    "flext_cli_constants",
    "flext_cli_context",
    "flext_cli_debug",
    "flext_cli_file_tools",
    "flext_cli_models",
    "flext_cli_output",
    "flext_cli_prompts",
    "flext_cli_protocols",
    "flext_cli_utilities",
    "flext_test_docker",
    "h",
    "input_exception_simulator",
    "input_simulator",
    "integration",
    "load_fixture_config",
    "load_fixture_data",
    "logging_config_factory",
    "m",
    "mock_env_vars",
    "p",
    "password_simulator",
    "pytest_collection_modifyitems",
    "pytest_configure",
    "r",
    "reset_config_singleton",
    "reset_singletons",
    "s",
    "sample_command_data",
    "sample_config_data",
    "sample_file_data",
    "t",
    "temp_csv_file",
    "temp_dir",
    "temp_file",
    "temp_json_file",
    "temp_yaml_file",
    "test_get_config_info_failure_on_exception",
    "test_process_fail_and_collect_paths",
    "test_process_mapping_fail_and_collect_paths",
    "test_prompt_logs_input_when_not_test_env",
    "test_read_confirmation_input_paths",
    "test_show_config_failure_when_info_result_is_failure",
    "test_show_config_outer_exception_path",
    "test_show_config_paths_failure_on_exception",
    "test_validate_config_failure_on_exception",
    "test_validate_required_string_raises_value_error",
    "test_validation_state_requires_criteria",
    "test_validation_v_uses_custom_message_on_empty_failure",
    "u",
    "unit",
    "x",
]


_LAZY_CACHE: MutableMapping[str, FlextTypes.ModuleExport] = {}


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562).

    A local cache ``_LAZY_CACHE`` persists resolved objects across repeated
    accesses during process lifetime.

    Args:
        name: Attribute name requested by dir()/import.

    Returns:
        Lazy-loaded module export type.

    Raises:
        AttributeError: If attribute not registered.

    """
    if name in _LAZY_CACHE:
        return _LAZY_CACHE[name]

    value = lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)
    _LAZY_CACHE[name] = value
    return value


def __dir__() -> Sequence[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
