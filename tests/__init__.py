# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _TYPE_CHECKING:
    from flext_tests import d, e, h, r, s, x

    from flext_core import FlextTypes
    from tests import (
        conftest,
        constants,
        helpers,
        models,
        protocols,
        typings,
        unit,
        utilities,
    )
    from tests.conftest import (
        Examples,
        InfoTuples,
        pytest_collection_modifyitems,
        pytest_configure,
    )
    from tests.constants import FlextCliTestConstants, FlextCliTestConstants as c
    from tests.helpers import FlextCliTestHelpers
    from tests.models import FlextCliTestModels, FlextCliTestModels as m
    from tests.protocols import FlextCliTestProtocols, FlextCliTestProtocols as p
    from tests.typings import FlextCliTestTypes, FlextCliTestTypes as t
    from tests.unit import (
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
    )
    from tests.utilities import FlextCliTestUtilities, FlextCliTestUtilities as u

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = merge_lazy_imports(
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
        "d": "flext_tests",
        "e": "flext_tests",
        "h": "flext_tests",
        "helpers": "tests.helpers",
        "m": ("tests.models", "FlextCliTestModels"),
        "models": "tests.models",
        "p": ("tests.protocols", "FlextCliTestProtocols"),
        "protocols": "tests.protocols",
        "pytest_collection_modifyitems": "tests.conftest",
        "pytest_configure": "tests.conftest",
        "r": "flext_tests",
        "s": "flext_tests",
        "t": ("tests.typings", "FlextCliTestTypes"),
        "typings": "tests.typings",
        "u": ("tests.utilities", "FlextCliTestUtilities"),
        "unit": "tests.unit",
        "utilities": "tests.utilities",
        "x": "flext_tests",
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
