# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from examples.constants import ExamplesFlextCliConstants, c
    from examples.ex_01_getting_started import FlextCliGettingStarted
    from examples.ex_07_plugin_system import (
        ConfigurablePlugin,
        DataExportPlugin,
        LifecyclePlugin,
        MyAppPluginManager,
        ReportGeneratorPlugin,
    )
    from examples.ex_08_shell_interaction import CommandHistory, InteractiveShell
    from examples.ex_09_performance_optimization import LazyDataLoader
    from examples.ex_11_complete_integration import DataManagerCLI
    from examples.ex_15_plugin import DataProcessorPlugin, ExamplePlugin
    from examples.models import ExamplesFlextCliModels, m
    from examples.protocols import ExamplesFlextCliProtocols, p
    from examples.typings import ExamplesFlextCliTypes, t
    from examples.utilities import ExamplesFlextCliUtilities, u
    from flext_cli import d, e, h, r, s, x
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".constants": (
            "ExamplesFlextCliConstants",
            "c",
        ),
        ".ex_01_getting_started": ("FlextCliGettingStarted",),
        ".ex_07_plugin_system": (
            "ConfigurablePlugin",
            "DataExportPlugin",
            "LifecyclePlugin",
            "MyAppPluginManager",
            "ReportGeneratorPlugin",
        ),
        ".ex_08_shell_interaction": (
            "CommandHistory",
            "InteractiveShell",
        ),
        ".ex_09_performance_optimization": ("LazyDataLoader",),
        ".ex_11_complete_integration": ("DataManagerCLI",),
        ".ex_15_plugin": (
            "DataProcessorPlugin",
            "ExamplePlugin",
        ),
        ".models": (
            "ExamplesFlextCliModels",
            "m",
        ),
        ".protocols": (
            "ExamplesFlextCliProtocols",
            "p",
        ),
        ".typings": (
            "ExamplesFlextCliTypes",
            "t",
        ),
        ".utilities": (
            "ExamplesFlextCliUtilities",
            "u",
        ),
        "flext_cli": (
            "d",
            "e",
            "h",
            "r",
            "s",
            "x",
        ),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__: list[str] = [
    "CommandHistory",
    "ConfigurablePlugin",
    "DataExportPlugin",
    "DataManagerCLI",
    "DataProcessorPlugin",
    "ExamplePlugin",
    "ExamplesFlextCliConstants",
    "ExamplesFlextCliModels",
    "ExamplesFlextCliProtocols",
    "ExamplesFlextCliTypes",
    "ExamplesFlextCliUtilities",
    "FlextCliGettingStarted",
    "InteractiveShell",
    "LazyDataLoader",
    "LifecyclePlugin",
    "MyAppPluginManager",
    "ReportGeneratorPlugin",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
]
