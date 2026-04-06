# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import tests.unit.conftest as _tests_unit_conftest

    conftest = _tests_unit_conftest
    import tests.unit.test_base as _tests_unit_test_base
    from tests.unit.conftest import reset_config_singleton

    test_base = _tests_unit_test_base
    import tests.unit.test_cli_params as _tests_unit_test_cli_params
    from tests.unit.test_base import TestsCliServiceBase

    test_cli_params = _tests_unit_test_cli_params
    import tests.unit.test_cli_service as _tests_unit_test_cli_service
    from tests.unit.test_cli_params import TestsCliCommonParams

    test_cli_service = _tests_unit_test_cli_service
    import tests.unit.test_cmd as _tests_unit_test_cmd
    from tests.unit.test_cli_service import TestsCliService

    test_cmd = _tests_unit_test_cmd
    import tests.unit.test_cmd_cov as _tests_unit_test_cmd_cov
    from tests.unit.test_cmd import TestsCliCmd

    test_cmd_cov = _tests_unit_test_cmd_cov
    import tests.unit.test_commands as _tests_unit_test_commands
    from tests.unit.test_cmd_cov import TestsCliCmdCov

    test_commands = _tests_unit_test_commands
    import tests.unit.test_config as _tests_unit_test_config
    from tests.unit.test_commands import TestsCliCommands

    test_config = _tests_unit_test_config
    import tests.unit.test_constants as _tests_unit_test_constants
    from tests.unit.test_config import (
        TestsCliConfigBasics,
        TestsCliConfigEdgeCases,
        TestsCliConfigIntegration,
        TestsCliConfigService,
        TestsCliConfigValidation,
        TestsCliLoggingConfig,
    )

    test_constants = _tests_unit_test_constants
    import tests.unit.test_examples_smoke as _tests_unit_test_examples_smoke
    from tests.unit.test_constants import TestsCliConstants

    test_examples_smoke = _tests_unit_test_examples_smoke
    import tests.unit.test_prompts as _tests_unit_test_prompts
    from tests.unit.test_examples_smoke import TestFlextCliExamplesSmoke

    test_prompts = _tests_unit_test_prompts
    import tests.unit.test_prompts_cov as _tests_unit_test_prompts_cov
    from tests.unit.test_prompts import TestsCliPrompts

    test_prompts_cov = _tests_unit_test_prompts_cov
    import tests.unit.test_protocols as _tests_unit_test_protocols
    from tests.unit.test_prompts_cov import TestsCliPromptsCov

    test_protocols = _tests_unit_test_protocols
    import tests.unit.test_runtime_utilities_core as _tests_unit_test_runtime_utilities_core
    from tests.unit.test_protocols import TestsCliProtocols

    test_runtime_utilities_core = _tests_unit_test_runtime_utilities_core
    import tests.unit.test_runtime_utilities_extra as _tests_unit_test_runtime_utilities_extra
    from tests.unit.test_runtime_utilities_core import (
        runner,
        test_capture_cases,
        test_run_cases,
        test_run_raw_cases,
    )

    test_runtime_utilities_extra = _tests_unit_test_runtime_utilities_extra
    import tests.unit.test_tables as _tests_unit_test_tables
    from tests.unit.test_runtime_utilities_extra import TestCliRuntimeUtilitiesExtra

    test_tables = _tests_unit_test_tables
    import tests.unit.test_toml_utilities as _tests_unit_test_toml_utilities
    from tests.unit.test_tables import TestsCliTables

    test_toml_utilities = _tests_unit_test_toml_utilities
    import tests.unit.test_typings as _tests_unit_test_typings
    from tests.unit.test_toml_utilities import (
        TestCliTomlDocument,
        TestCliTomlHelpers,
        TestCliTomlRead,
    )

    test_typings = _tests_unit_test_typings
    import tests.unit.test_utilities_cov as _tests_unit_test_utilities_cov
    from tests.unit.test_typings import TestsCliTypings

    test_utilities_cov = _tests_unit_test_utilities_cov
    import tests.unit.test_version as _tests_unit_test_version
    from tests.unit.test_utilities_cov import TestsCliUtilitiesCov

    test_version = _tests_unit_test_version
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u
    from tests.unit.test_version import TestsCliVersion
_LAZY_IMPORTS = {
    "TestCliRuntimeUtilitiesExtra": (
        "tests.unit.test_runtime_utilities_extra",
        "TestCliRuntimeUtilitiesExtra",
    ),
    "TestCliTomlDocument": ("tests.unit.test_toml_utilities", "TestCliTomlDocument"),
    "TestCliTomlHelpers": ("tests.unit.test_toml_utilities", "TestCliTomlHelpers"),
    "TestCliTomlRead": ("tests.unit.test_toml_utilities", "TestCliTomlRead"),
    "TestFlextCliExamplesSmoke": (
        "tests.unit.test_examples_smoke",
        "TestFlextCliExamplesSmoke",
    ),
    "TestsCliCmd": ("tests.unit.test_cmd", "TestsCliCmd"),
    "TestsCliCmdCov": ("tests.unit.test_cmd_cov", "TestsCliCmdCov"),
    "TestsCliCommands": ("tests.unit.test_commands", "TestsCliCommands"),
    "TestsCliCommonParams": ("tests.unit.test_cli_params", "TestsCliCommonParams"),
    "TestsCliConfigBasics": ("tests.unit.test_config", "TestsCliConfigBasics"),
    "TestsCliConfigEdgeCases": ("tests.unit.test_config", "TestsCliConfigEdgeCases"),
    "TestsCliConfigIntegration": (
        "tests.unit.test_config",
        "TestsCliConfigIntegration",
    ),
    "TestsCliConfigService": ("tests.unit.test_config", "TestsCliConfigService"),
    "TestsCliConfigValidation": ("tests.unit.test_config", "TestsCliConfigValidation"),
    "TestsCliConstants": ("tests.unit.test_constants", "TestsCliConstants"),
    "TestsCliLoggingConfig": ("tests.unit.test_config", "TestsCliLoggingConfig"),
    "TestsCliPrompts": ("tests.unit.test_prompts", "TestsCliPrompts"),
    "TestsCliPromptsCov": ("tests.unit.test_prompts_cov", "TestsCliPromptsCov"),
    "TestsCliProtocols": ("tests.unit.test_protocols", "TestsCliProtocols"),
    "TestsCliService": ("tests.unit.test_cli_service", "TestsCliService"),
    "TestsCliServiceBase": ("tests.unit.test_base", "TestsCliServiceBase"),
    "TestsCliTables": ("tests.unit.test_tables", "TestsCliTables"),
    "TestsCliTypings": ("tests.unit.test_typings", "TestsCliTypings"),
    "TestsCliUtilitiesCov": ("tests.unit.test_utilities_cov", "TestsCliUtilitiesCov"),
    "TestsCliVersion": ("tests.unit.test_version", "TestsCliVersion"),
    "c": ("flext_core.constants", "FlextConstants"),
    "conftest": "tests.unit.conftest",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "reset_config_singleton": ("tests.unit.conftest", "reset_config_singleton"),
    "runner": ("tests.unit.test_runtime_utilities_core", "runner"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "test_base": "tests.unit.test_base",
    "test_capture_cases": (
        "tests.unit.test_runtime_utilities_core",
        "test_capture_cases",
    ),
    "test_cli_params": "tests.unit.test_cli_params",
    "test_cli_service": "tests.unit.test_cli_service",
    "test_cmd": "tests.unit.test_cmd",
    "test_cmd_cov": "tests.unit.test_cmd_cov",
    "test_commands": "tests.unit.test_commands",
    "test_config": "tests.unit.test_config",
    "test_constants": "tests.unit.test_constants",
    "test_examples_smoke": "tests.unit.test_examples_smoke",
    "test_prompts": "tests.unit.test_prompts",
    "test_prompts_cov": "tests.unit.test_prompts_cov",
    "test_protocols": "tests.unit.test_protocols",
    "test_run_cases": ("tests.unit.test_runtime_utilities_core", "test_run_cases"),
    "test_run_raw_cases": (
        "tests.unit.test_runtime_utilities_core",
        "test_run_raw_cases",
    ),
    "test_runtime_utilities_core": "tests.unit.test_runtime_utilities_core",
    "test_runtime_utilities_extra": "tests.unit.test_runtime_utilities_extra",
    "test_tables": "tests.unit.test_tables",
    "test_toml_utilities": "tests.unit.test_toml_utilities",
    "test_typings": "tests.unit.test_typings",
    "test_utilities_cov": "tests.unit.test_utilities_cov",
    "test_version": "tests.unit.test_version",
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "TestCliRuntimeUtilitiesExtra",
    "TestCliTomlDocument",
    "TestCliTomlHelpers",
    "TestCliTomlRead",
    "TestFlextCliExamplesSmoke",
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
    "conftest",
    "d",
    "e",
    "h",
    "m",
    "p",
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
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
