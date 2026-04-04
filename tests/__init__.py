# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _t.TYPE_CHECKING:
    import tests.conftest as _tests_conftest

    conftest = _tests_conftest
    import tests.constants as _tests_constants
    from tests.conftest import (
        Examples,
        InfoTuples,
        pytest_collection_modifyitems,
        pytest_configure,
    )

    constants = _tests_constants
    import tests.helpers as _tests_helpers
    from tests.constants import FlextCliTestConstants, FlextCliTestConstants as c

    helpers = _tests_helpers
    import tests.models as _tests_models
    from tests.helpers import FlextCliTestHelpers

    models = _tests_models
    import tests.protocols as _tests_protocols
    from tests.models import FlextCliTestModels, FlextCliTestModels as m

    protocols = _tests_protocols
    import tests.typings as _tests_typings
    from tests.protocols import FlextCliTestProtocols, FlextCliTestProtocols as p

    typings = _tests_typings
    import tests.unit as _tests_unit
    from tests.typings import FlextCliTestTypes, FlextCliTestTypes as t

    unit = _tests_unit
    import tests.utilities as _tests_utilities
    from tests.unit import (
        ConfigParam,
        ConfigTestFactory,
        ConfigTestScenario,
        ConfigTestType,
        T,
        TestCliTomlDocument,
        TestCliTomlHelpers,
        TestCliTomlRead,
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
        create_cli_app,
        create_decorated_command,
        create_test_config,
        reset_config_singleton,
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
        test_project_names_from_values_normalizes_repeated_cli_selectors,
        test_prompt_logs_input_when_not_test_env,
        test_prompts,
        test_prompts_cov,
        test_protocols,
        test_read_confirmation_input_paths,
        test_show_config_failure_when_info_result_is_failure,
        test_show_config_outer_exception_path,
        test_show_config_paths_failure_on_exception,
        test_tables,
        test_toml_utilities,
        test_typings,
        test_utilities_cov,
        test_validate_config_failure_on_exception,
        test_validation_v_uses_custom_message_on_empty_failure,
        test_version,
    )

    utilities = _tests_utilities
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from tests.utilities import FlextCliTestUtilities, FlextCliTestUtilities as u
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
    "TestCliTomlDocument",
    "TestCliTomlHelpers",
    "TestCliTomlRead",
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
    "test_project_names_from_values_normalizes_repeated_cli_selectors",
    "test_prompt_logs_input_when_not_test_env",
    "test_prompts",
    "test_prompts_cov",
    "test_protocols",
    "test_read_confirmation_input_paths",
    "test_show_config_failure_when_info_result_is_failure",
    "test_show_config_outer_exception_path",
    "test_show_config_paths_failure_on_exception",
    "test_tables",
    "test_toml_utilities",
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
