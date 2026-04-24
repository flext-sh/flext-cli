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
    from tests.unit.test_base import TestsCliServiceBase
    from tests.unit.test_cli_params import TestsCliCommonParams
    from tests.unit.test_cli_service import TestsCliService
    from tests.unit.test_cmd import TestsCliCmd
    from tests.unit.test_cmd_cov import TestsCliCmdCov
    from tests.unit.test_commands import TestsCliCommands
    from tests.unit.test_constants import TestsCliConstants
    from tests.unit.test_examples_smoke import TestFlextCliExamplesSmoke
    from tests.unit.test_pipeline import TestPipelineExecute
    from tests.unit.test_prompts import TestsCliPrompts
    from tests.unit.test_prompts_cov import (
        TestsCliPromptsCov,
        TestsFlextCliCaptureLogPromptsCov,
    )
    from tests.unit.test_protocols import TestsCliProtocols
    from tests.unit.test_runtime_utilities_extra import TestCliRuntimeUtilitiesExtra
    from tests.unit.test_settings import (
        TestsCliLoggingSettings,
        TestsCliSettingsBasics,
        TestsCliSettingsEdgeCases,
        TestsCliSettingsIntegration,
        TestsCliSettingsService,
        TestsCliSettingsValidation,
    )
    from tests.unit.test_tables import TestsCliTables
    from tests.unit.test_toml_utilities import (
        TestCliTomlDocument,
        TestCliTomlHelpers,
        TestCliTomlRead,
    )
    from tests.unit.test_typings import TestsCliTypings
    from tests.unit.test_utilities_cov import TestsCliUtilitiesCov
    from tests.unit.test_version import TestsCliVersion
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
            ".unit.test_base": ("TestsCliServiceBase",),
            ".unit.test_cli_params": ("TestsCliCommonParams",),
            ".unit.test_cli_service": ("TestsCliService",),
            ".unit.test_cmd": ("TestsCliCmd",),
            ".unit.test_cmd_cov": ("TestsCliCmdCov",),
            ".unit.test_commands": ("TestsCliCommands",),
            ".unit.test_constants": ("TestsCliConstants",),
            ".unit.test_examples_smoke": ("TestFlextCliExamplesSmoke",),
            ".unit.test_pipeline": ("TestPipelineExecute",),
            ".unit.test_prompts": ("TestsCliPrompts",),
            ".unit.test_prompts_cov": (
                "TestsCliPromptsCov",
                "TestsFlextCliCaptureLogPromptsCov",
            ),
            ".unit.test_protocols": ("TestsCliProtocols",),
            ".unit.test_runtime_utilities_extra": ("TestCliRuntimeUtilitiesExtra",),
            ".unit.test_settings": (
                "TestsCliLoggingSettings",
                "TestsCliSettingsBasics",
                "TestsCliSettingsEdgeCases",
                "TestsCliSettingsIntegration",
                "TestsCliSettingsService",
                "TestsCliSettingsValidation",
            ),
            ".unit.test_tables": ("TestsCliTables",),
            ".unit.test_toml_utilities": (
                "TestCliTomlDocument",
                "TestCliTomlHelpers",
                "TestCliTomlRead",
            ),
            ".unit.test_typings": ("TestsCliTypings",),
            ".unit.test_utilities_cov": ("TestsCliUtilitiesCov",),
            ".unit.test_version": ("TestsCliVersion",),
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
    "TestsCliConstants",
    "TestsCliLoggingSettings",
    "TestsCliPrompts",
    "TestsCliPromptsCov",
    "TestsCliProtocols",
    "TestsCliService",
    "TestsCliServiceBase",
    "TestsCliSettingsBasics",
    "TestsCliSettingsEdgeCases",
    "TestsCliSettingsIntegration",
    "TestsCliSettingsService",
    "TestsCliSettingsValidation",
    "TestsCliTables",
    "TestsCliTypings",
    "TestsCliUtilitiesCov",
    "TestsCliVersion",
    "TestsFlextCliCaptureLogPromptsCov",
    "TestsFlextCliConstants",
    "TestsFlextCliModels",
    "TestsFlextCliProtocols",
    "TestsFlextCliTypes",
    "TestsFlextCliUtilities",
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
