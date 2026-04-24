# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if _t.TYPE_CHECKING:
    from flext_tests import d, e, h, r, s, td, tf, tk, tm, tv, x

    from tests.constants import TestsFlextCliConstants, c
    from tests.models import TestsFlextCliModels, m
    from tests.protocols import TestsFlextCliProtocols, p
    from tests.typings import TestsFlextCliTypes, t
    from tests.unit.conftest import (
        FlextCliCaptureLogPrompts,
        FlextCliFailingLogPrompts,
        FlextCliScriptedPrompts,
        make_prompts,
    )
    from tests.unit.test_base import TestsFlextCliServiceBase
    from tests.unit.test_cli_params import TestsFlextCliCommonParams
    from tests.unit.test_cli_service import TestsFlextCliService
    from tests.unit.test_cmd import TestsFlextCliCmd
    from tests.unit.test_cmd_cov import TestsFlextCliCmdCov
    from tests.unit.test_commands import TestsFlextCliCommands
    from tests.unit.test_constants import TestsFlextCliConstantsUnit
    from tests.unit.test_examples_smoke import TestsFlextCliExamplesSmoke
    from tests.unit.test_pipeline import TestsFlextCliPipeline
    from tests.unit.test_prompts import TestsFlextCliPrompts
    from tests.unit.test_prompts_cov import (
        TestsCliPromptsCov,
        TestsFlextCliCaptureLogPromptsCov,
    )
    from tests.unit.test_protocols import TestsFlextCliProtocolsUnit
    from tests.unit.test_runtime_utilities_extra import (
        TestsFlextCliRuntimeUtilitiesExtra,
    )
    from tests.unit.test_settings import (
        TestsCliLoggingSettings,
        TestsCliSettingsBasics,
        TestsCliSettingsEdgeCases,
        TestsCliSettingsIntegration,
        TestsCliSettingsService,
        TestsCliSettingsValidation,
    )
    from tests.unit.test_tables import TestsFlextCliTables
    from tests.unit.test_toml_utilities import (
        TestCliTomlDocument,
        TestCliTomlHelpers,
        TestCliTomlRead,
    )
    from tests.unit.test_typings import TestsFlextCliTypesUnit
    from tests.unit.test_utilities_cov import TestsFlextCliUtilitiesCov
    from tests.unit.test_version import TestsFlextCliVersion
    from tests.utilities import TestsFlextCliUtilities, u
_LAZY_IMPORTS = merge_lazy_imports(
    (".unit",),
    build_lazy_import_map(
        {
            ".constants": (
                "TestsFlextCliConstants",
                "c",
            ),
            ".models": (
                "TestsFlextCliModels",
                "m",
            ),
            ".protocols": (
                "TestsFlextCliProtocols",
                "p",
            ),
            ".typings": (
                "TestsFlextCliTypes",
                "t",
            ),
            ".unit.conftest": (
                "FlextCliCaptureLogPrompts",
                "FlextCliFailingLogPrompts",
                "FlextCliScriptedPrompts",
                "make_prompts",
            ),
            ".unit.test_base": ("TestsFlextCliServiceBase",),
            ".unit.test_cli_params": ("TestsFlextCliCommonParams",),
            ".unit.test_cli_service": ("TestsFlextCliService",),
            ".unit.test_cmd": ("TestsFlextCliCmd",),
            ".unit.test_cmd_cov": ("TestsFlextCliCmdCov",),
            ".unit.test_commands": ("TestsFlextCliCommands",),
            ".unit.test_constants": ("TestsFlextCliConstantsUnit",),
            ".unit.test_examples_smoke": ("TestsFlextCliExamplesSmoke",),
            ".unit.test_pipeline": ("TestsFlextCliPipeline",),
            ".unit.test_prompts": ("TestsFlextCliPrompts",),
            ".unit.test_prompts_cov": (
                "TestsCliPromptsCov",
                "TestsFlextCliCaptureLogPromptsCov",
            ),
            ".unit.test_protocols": ("TestsFlextCliProtocolsUnit",),
            ".unit.test_runtime_utilities_extra": (
                "TestsFlextCliRuntimeUtilitiesExtra",
            ),
            ".unit.test_settings": (
                "TestsCliLoggingSettings",
                "TestsCliSettingsBasics",
                "TestsCliSettingsEdgeCases",
                "TestsCliSettingsIntegration",
                "TestsCliSettingsService",
                "TestsCliSettingsValidation",
            ),
            ".unit.test_tables": ("TestsFlextCliTables",),
            ".unit.test_toml_utilities": (
                "TestCliTomlDocument",
                "TestCliTomlHelpers",
                "TestCliTomlRead",
            ),
            ".unit.test_typings": ("TestsFlextCliTypesUnit",),
            ".unit.test_utilities_cov": ("TestsFlextCliUtilitiesCov",),
            ".unit.test_version": ("TestsFlextCliVersion",),
            ".utilities": (
                "TestsFlextCliUtilities",
                "u",
            ),
            "flext_tests": (
                "d",
                "e",
                "h",
                "r",
                "s",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "x",
            ),
        },
    ),
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
    ),
    module_name=__name__,
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__: list[str] = [
    "FlextCliCaptureLogPrompts",
    "FlextCliFailingLogPrompts",
    "FlextCliScriptedPrompts",
    "TestCliTomlDocument",
    "TestCliTomlHelpers",
    "TestCliTomlRead",
    "TestsCliLoggingSettings",
    "TestsCliPromptsCov",
    "TestsCliSettingsBasics",
    "TestsCliSettingsEdgeCases",
    "TestsCliSettingsIntegration",
    "TestsCliSettingsService",
    "TestsCliSettingsValidation",
    "TestsFlextCliCaptureLogPromptsCov",
    "TestsFlextCliCmd",
    "TestsFlextCliCmdCov",
    "TestsFlextCliCommands",
    "TestsFlextCliCommonParams",
    "TestsFlextCliConstants",
    "TestsFlextCliExamplesSmoke",
    "TestsFlextCliModels",
    "TestsFlextCliPipeline",
    "TestsFlextCliPrompts",
    "TestsFlextCliProtocols",
    "TestsFlextCliProtocolsUnit",
    "TestsFlextCliRuntimeUtilitiesExtra",
    "TestsFlextCliService",
    "TestsFlextCliServiceBase",
    "TestsFlextCliTables",
    "TestsFlextCliTypes",
    "TestsFlextCliTypesUnit",
    "TestsFlextCliUtilities",
    "TestsFlextCliUtilitiesCov",
    "TestsFlextCliVersion",
    "c",
    "d",
    "e",
    "h",
    "m",
    "make_prompts",
    "p",
    "r",
    "s",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "tv",
    "u",
    "x",
]
