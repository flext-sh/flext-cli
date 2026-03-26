# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
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
    from tests.unit.test_prompts import TestsCliPrompts
    from tests.unit.test_prompts_cov import (
        test_prompt_logs_input_when_not_test_env,
        test_read_confirmation_input_paths,
    )
    from tests.unit.test_protocols import TestsCliProtocols
    from tests.unit.test_typings import TestsCliTypings
    from tests.unit.test_utilities_cov import (
        test_process_fail_and_collect_paths,
        test_process_mapping_fail_and_collect_paths,
        test_validation_v_uses_custom_message_on_empty_failure,
    )
    from tests.unit.test_version import T, TestsCliVersion

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "ConfigParam": ["tests.unit.test_cli_params", "ConfigParam"],
    "ConfigTestFactory": ["tests.unit.test_config", "ConfigTestFactory"],
    "ConfigTestScenario": ["tests.unit.test_config", "ConfigTestScenario"],
    "ConfigTestType": ["tests.unit.test_config", "ConfigTestType"],
    "T": ["tests.unit.test_version", "T"],
    "TestsCliCmd": ["tests.unit.test_cmd", "TestsCliCmd"],
    "TestsCliCommands": ["tests.unit.test_commands", "TestsCliCommands"],
    "TestsCliCommonParams": ["tests.unit.test_cli_params", "TestsCliCommonParams"],
    "TestsCliConfigBasics": ["tests.unit.test_config", "TestsCliConfigBasics"],
    "TestsCliConfigEdgeCases": ["tests.unit.test_config", "TestsCliConfigEdgeCases"],
    "TestsCliConfigIntegration": [
        "tests.unit.test_config",
        "TestsCliConfigIntegration",
    ],
    "TestsCliConfigService": ["tests.unit.test_config", "TestsCliConfigService"],
    "TestsCliConfigValidation": ["tests.unit.test_config", "TestsCliConfigValidation"],
    "TestsCliConstants": ["tests.unit.test_constants", "TestsCliConstants"],
    "TestsCliLoggingConfig": ["tests.unit.test_config", "TestsCliLoggingConfig"],
    "TestsCliPrompts": ["tests.unit.test_prompts", "TestsCliPrompts"],
    "TestsCliProtocols": ["tests.unit.test_protocols", "TestsCliProtocols"],
    "TestsCliServiceBase": ["tests.unit.test_base", "TestsCliServiceBase"],
    "TestsCliTypings": ["tests.unit.test_typings", "TestsCliTypings"],
    "TestsCliVersion": ["tests.unit.test_version", "TestsCliVersion"],
    "create_cli_app": ["tests.unit.test_cli_params", "create_cli_app"],
    "create_decorated_command": [
        "tests.unit.test_cli_params",
        "create_decorated_command",
    ],
    "create_test_config": ["tests.unit.test_cli_params", "create_test_config"],
    "reset_config_singleton": ["tests.unit.conftest", "reset_config_singleton"],
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
    "test_validation_v_uses_custom_message_on_empty_failure": [
        "tests.unit.test_utilities_cov",
        "test_validation_v_uses_custom_message_on_empty_failure",
    ],
}

__all__ = [
    "ConfigParam",
    "ConfigTestFactory",
    "ConfigTestScenario",
    "ConfigTestType",
    "T",
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
    "TestsCliServiceBase",
    "TestsCliTypings",
    "TestsCliVersion",
    "create_cli_app",
    "create_decorated_command",
    "create_test_config",
    "reset_config_singleton",
    "test_get_config_info_failure_on_exception",
    "test_process_fail_and_collect_paths",
    "test_process_mapping_fail_and_collect_paths",
    "test_prompt_logs_input_when_not_test_env",
    "test_read_confirmation_input_paths",
    "test_show_config_failure_when_info_result_is_failure",
    "test_show_config_outer_exception_path",
    "test_show_config_paths_failure_on_exception",
    "test_validate_config_failure_on_exception",
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
