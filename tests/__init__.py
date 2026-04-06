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
        cli_settings,
        pytest_collection_modifyitems,
        pytest_configure,
        pytest_plugins,
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
        TestCliRuntimeUtilitiesExtra,
        TestCliTomlDocument,
        TestCliTomlHelpers,
        TestCliTomlRead,
        TestFlextCliExamplesSmoke,
        TestPipelineExecute,
        TestsCliCmd,
        TestsCliCmdCov,
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
        TestsCliPromptsCov,
        TestsCliProtocols,
        TestsCliService,
        TestsCliServiceBase,
        TestsCliTables,
        TestsCliTypings,
        TestsCliUtilitiesCov,
        TestsCliVersion,
        reset_config_singleton,
        runner,
        test_base,
        test_capture_cases,
        test_cli_params,
        test_cli_service,
        test_cmd,
        test_cmd_cov,
        test_commands,
        test_config,
        test_constants,
        test_examples_smoke,
        test_pipeline,
        test_prompts,
        test_prompts_cov,
        test_protocols,
        test_run_cases,
        test_run_raw_cases,
        test_runtime_utilities_core,
        test_runtime_utilities_extra,
        test_tables,
        test_toml_utilities,
        test_typings,
        test_utilities_cov,
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
        "FlextCliTestConstants": ("tests.constants", "FlextCliTestConstants"),
        "FlextCliTestModels": ("tests.models", "FlextCliTestModels"),
        "FlextCliTestProtocols": ("tests.protocols", "FlextCliTestProtocols"),
        "FlextCliTestTypes": ("tests.typings", "FlextCliTestTypes"),
        "FlextCliTestUtilities": ("tests.utilities", "FlextCliTestUtilities"),
        "c": ("tests.constants", "FlextCliTestConstants"),
        "cli_settings": ("tests.conftest", "cli_settings"),
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
        "pytest_collection_modifyitems": (
            "tests.conftest",
            "pytest_collection_modifyitems",
        ),
        "pytest_configure": ("tests.conftest", "pytest_configure"),
        "pytest_plugins": ("tests.conftest", "pytest_plugins"),
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
_ = _LAZY_IMPORTS.pop("cleanup_submodule_namespace", None)
_ = _LAZY_IMPORTS.pop("install_lazy_exports", None)
_ = _LAZY_IMPORTS.pop("lazy_getattr", None)
_ = _LAZY_IMPORTS.pop("merge_lazy_imports", None)
_ = _LAZY_IMPORTS.pop("output", None)
_ = _LAZY_IMPORTS.pop("output_reporting", None)

__all__ = [
    "FlextCliTestConstants",
    "FlextCliTestHelpers",
    "FlextCliTestModels",
    "FlextCliTestProtocols",
    "FlextCliTestTypes",
    "FlextCliTestUtilities",
    "TestCliRuntimeUtilitiesExtra",
    "TestCliTomlDocument",
    "TestCliTomlHelpers",
    "TestCliTomlRead",
    "TestFlextCliExamplesSmoke",
    "TestPipelineExecute",
    "TestsCliCmd",
    "TestsCliCmdCov",
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
    "TestsCliPromptsCov",
    "TestsCliProtocols",
    "TestsCliService",
    "TestsCliServiceBase",
    "TestsCliTables",
    "TestsCliTypings",
    "TestsCliUtilitiesCov",
    "TestsCliVersion",
    "c",
    "cli_settings",
    "conftest",
    "constants",
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
    "pytest_plugins",
    "r",
    "reset_config_singleton",
    "runner",
    "s",
    "t",
    "test_base",
    "test_capture_cases",
    "test_cli_params",
    "test_cli_service",
    "test_cmd",
    "test_cmd_cov",
    "test_commands",
    "test_config",
    "test_constants",
    "test_examples_smoke",
    "test_pipeline",
    "test_prompts",
    "test_prompts_cov",
    "test_protocols",
    "test_run_cases",
    "test_run_raw_cases",
    "test_runtime_utilities_core",
    "test_runtime_utilities_extra",
    "test_tables",
    "test_toml_utilities",
    "test_typings",
    "test_utilities_cov",
    "test_version",
    "typings",
    "u",
    "unit",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
