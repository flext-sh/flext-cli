# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Test units for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes

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
    from tests.unit.test_cmd import (
        CONFIG_FILE_NAME,
        CONFIG_OPERATION_METHODS,
        ERROR_SCENARIO_DATA,
        VALID_CONFIG_DATA,
        ConfigErrorScenario,
        ConfigOperation,
        TestsCliCmd,
    )
    from tests.unit.test_cmd_cov import (
        test_edit_config_outer_exception_path,
        test_edit_config_success_logs_and_returns_ok,
        test_get_config_info_failure_on_exception,
        test_get_config_value_outer_exception_path,
        test_set_config_value_outer_exception_path,
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
        TestsCliConfigComputedFields,
        TestsCliConfigConcurrency,
        TestsCliConfigEdgeCases,
        TestsCliConfigFilesOperations,
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
    from tests.unit.test_option_groups_cov import (
        test_auth_options_include_expected_env_vars,
        test_connection_options_defaults_are_exposed,
        test_output_options_expose_format_output_and_verbosity,
    )
    from tests.unit.test_performance_automated import TestsCliPerformanceAutomated
    from tests.unit.test_prompts import TestsCliPrompts
    from tests.unit.test_prompts_cov import (
        test_print_status_exception_path,
        test_prompt_choice_covers_required_default_and_exception,
        test_prompt_confirmation_handles_exception_from_record,
        test_prompt_logs_input_when_not_test_env,
        test_read_confirmation_input_paths,
        test_read_selection_paths,
        test_select_from_options_logs_successful_selection,
    )
    from tests.unit.test_protocols import TestsCliProtocols
    from tests.unit.test_railway_pattern_example import TestsCliRailwayPatternExample
    from tests.unit.test_typings import TestsCliTypings, TypingTestCase, TypingTestType
    from tests.unit.test_utilities_cov import (
        test_normalize_union_type_returns_annotation_for_none_only_args,
        test_normalize_union_type_returns_none_for_empty_normalized_list,
        test_normalize_union_type_returns_none_when_inner_is_none,
        test_parse_kwargs_skips_missing_enum_field_key,
        test_process_fail_and_collect_paths,
        test_process_mapping_fail_and_collect_paths,
        test_validate_required_string_raises_value_error,
        test_validated_with_result_returns_failure_on_validation_error,
        test_validation_state_requires_criteria,
        test_validation_v_uses_custom_message_on_empty_failure,
    )
    from tests.unit.test_version import T, TestsCliVersion

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "CONFIG_FILE_NAME": ["tests.unit.test_cmd", "CONFIG_FILE_NAME"],
    "CONFIG_OPERATION_METHODS": ["tests.unit.test_cmd", "CONFIG_OPERATION_METHODS"],
    "ConfigErrorScenario": ["tests.unit.test_cmd", "ConfigErrorScenario"],
    "ConfigOperation": ["tests.unit.test_cmd", "ConfigOperation"],
    "ConfigParam": ["tests.unit.test_cli_params", "ConfigParam"],
    "ConfigTestFactory": ["tests.unit.test_config", "ConfigTestFactory"],
    "ConfigTestScenario": ["tests.unit.test_config", "ConfigTestScenario"],
    "ConfigTestType": ["tests.unit.test_config", "ConfigTestType"],
    "ERROR_SCENARIO_DATA": ["tests.unit.test_cmd", "ERROR_SCENARIO_DATA"],
    "T": ["tests.unit.test_version", "T"],
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
    "TestsCliConfigComputedFields": [
        "tests.unit.test_config",
        "TestsCliConfigComputedFields",
    ],
    "TestsCliConfigConcurrency": [
        "tests.unit.test_config",
        "TestsCliConfigConcurrency",
    ],
    "TestsCliConfigEdgeCases": ["tests.unit.test_config", "TestsCliConfigEdgeCases"],
    "TestsCliConfigFilesOperations": [
        "tests.unit.test_config",
        "TestsCliConfigFilesOperations",
    ],
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
    "TypingTestCase": ["tests.unit.test_typings", "TypingTestCase"],
    "TypingTestType": ["tests.unit.test_typings", "TypingTestType"],
    "VALID_CONFIG_DATA": ["tests.unit.test_cmd", "VALID_CONFIG_DATA"],
    "create_cli_app": ["tests.unit.test_cli_params", "create_cli_app"],
    "create_decorated_command": [
        "tests.unit.test_cli_params",
        "create_decorated_command",
    ],
    "create_test_config": ["tests.unit.test_cli_params", "create_test_config"],
    "reset_config_singleton": ["tests.unit.conftest", "reset_config_singleton"],
    "test_auth_options_include_expected_env_vars": [
        "tests.unit.test_option_groups_cov",
        "test_auth_options_include_expected_env_vars",
    ],
    "test_connection_options_defaults_are_exposed": [
        "tests.unit.test_option_groups_cov",
        "test_connection_options_defaults_are_exposed",
    ],
    "test_edit_config_outer_exception_path": [
        "tests.unit.test_cmd_cov",
        "test_edit_config_outer_exception_path",
    ],
    "test_edit_config_success_logs_and_returns_ok": [
        "tests.unit.test_cmd_cov",
        "test_edit_config_success_logs_and_returns_ok",
    ],
    "test_get_config_info_failure_on_exception": [
        "tests.unit.test_cmd_cov",
        "test_get_config_info_failure_on_exception",
    ],
    "test_get_config_value_outer_exception_path": [
        "tests.unit.test_cmd_cov",
        "test_get_config_value_outer_exception_path",
    ],
    "test_normalize_union_type_returns_annotation_for_none_only_args": [
        "tests.unit.test_utilities_cov",
        "test_normalize_union_type_returns_annotation_for_none_only_args",
    ],
    "test_normalize_union_type_returns_none_for_empty_normalized_list": [
        "tests.unit.test_utilities_cov",
        "test_normalize_union_type_returns_none_for_empty_normalized_list",
    ],
    "test_normalize_union_type_returns_none_when_inner_is_none": [
        "tests.unit.test_utilities_cov",
        "test_normalize_union_type_returns_none_when_inner_is_none",
    ],
    "test_output_options_expose_format_output_and_verbosity": [
        "tests.unit.test_option_groups_cov",
        "test_output_options_expose_format_output_and_verbosity",
    ],
    "test_parse_kwargs_skips_missing_enum_field_key": [
        "tests.unit.test_utilities_cov",
        "test_parse_kwargs_skips_missing_enum_field_key",
    ],
    "test_print_status_exception_path": [
        "tests.unit.test_prompts_cov",
        "test_print_status_exception_path",
    ],
    "test_process_fail_and_collect_paths": [
        "tests.unit.test_utilities_cov",
        "test_process_fail_and_collect_paths",
    ],
    "test_process_mapping_fail_and_collect_paths": [
        "tests.unit.test_utilities_cov",
        "test_process_mapping_fail_and_collect_paths",
    ],
    "test_prompt_choice_covers_required_default_and_exception": [
        "tests.unit.test_prompts_cov",
        "test_prompt_choice_covers_required_default_and_exception",
    ],
    "test_prompt_confirmation_handles_exception_from_record": [
        "tests.unit.test_prompts_cov",
        "test_prompt_confirmation_handles_exception_from_record",
    ],
    "test_prompt_logs_input_when_not_test_env": [
        "tests.unit.test_prompts_cov",
        "test_prompt_logs_input_when_not_test_env",
    ],
    "test_read_confirmation_input_paths": [
        "tests.unit.test_prompts_cov",
        "test_read_confirmation_input_paths",
    ],
    "test_read_selection_paths": [
        "tests.unit.test_prompts_cov",
        "test_read_selection_paths",
    ],
    "test_select_from_options_logs_successful_selection": [
        "tests.unit.test_prompts_cov",
        "test_select_from_options_logs_successful_selection",
    ],
    "test_set_config_value_outer_exception_path": [
        "tests.unit.test_cmd_cov",
        "test_set_config_value_outer_exception_path",
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
    "test_validated_with_result_returns_failure_on_validation_error": [
        "tests.unit.test_utilities_cov",
        "test_validated_with_result_returns_failure_on_validation_error",
    ],
    "test_validation_state_requires_criteria": [
        "tests.unit.test_utilities_cov",
        "test_validation_state_requires_criteria",
    ],
    "test_validation_v_uses_custom_message_on_empty_failure": [
        "tests.unit.test_utilities_cov",
        "test_validation_v_uses_custom_message_on_empty_failure",
    ],
}

__all__ = [
    "CONFIG_FILE_NAME",
    "CONFIG_OPERATION_METHODS",
    "ERROR_SCENARIO_DATA",
    "VALID_CONFIG_DATA",
    "ConfigErrorScenario",
    "ConfigOperation",
    "ConfigParam",
    "ConfigTestFactory",
    "ConfigTestScenario",
    "ConfigTestType",
    "T",
    "TestsCliCli",
    "TestsCliCliExtended",
    "TestsCliCmd",
    "TestsCliCommands",
    "TestsCliCommonParams",
    "TestsCliComprehensiveModels",
    "TestsCliConfigBasics",
    "TestsCliConfigComputedFields",
    "TestsCliConfigConcurrency",
    "TestsCliConfigEdgeCases",
    "TestsCliConfigFilesOperations",
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
    "TypingTestCase",
    "TypingTestType",
    "create_cli_app",
    "create_decorated_command",
    "create_test_config",
    "reset_config_singleton",
    "test_auth_options_include_expected_env_vars",
    "test_connection_options_defaults_are_exposed",
    "test_edit_config_outer_exception_path",
    "test_edit_config_success_logs_and_returns_ok",
    "test_get_config_info_failure_on_exception",
    "test_get_config_value_outer_exception_path",
    "test_normalize_union_type_returns_annotation_for_none_only_args",
    "test_normalize_union_type_returns_none_for_empty_normalized_list",
    "test_normalize_union_type_returns_none_when_inner_is_none",
    "test_output_options_expose_format_output_and_verbosity",
    "test_parse_kwargs_skips_missing_enum_field_key",
    "test_print_status_exception_path",
    "test_process_fail_and_collect_paths",
    "test_process_mapping_fail_and_collect_paths",
    "test_prompt_choice_covers_required_default_and_exception",
    "test_prompt_confirmation_handles_exception_from_record",
    "test_prompt_logs_input_when_not_test_env",
    "test_read_confirmation_input_paths",
    "test_read_selection_paths",
    "test_select_from_options_logs_successful_selection",
    "test_set_config_value_outer_exception_path",
    "test_show_config_failure_when_info_result_is_failure",
    "test_show_config_outer_exception_path",
    "test_show_config_paths_failure_on_exception",
    "test_validate_config_failure_on_exception",
    "test_validate_required_string_raises_value_error",
    "test_validated_with_result_returns_failure_on_validation_error",
    "test_validation_state_requires_criteria",
    "test_validation_v_uses_custom_message_on_empty_failure",
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
