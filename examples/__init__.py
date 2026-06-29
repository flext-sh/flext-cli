# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

_LAZY_IMPORTS = merge_lazy_imports(
    ("._models_parts",),
    build_lazy_import_map(
        {
            "._models_parts": ("_models_parts",),
            "._models_parts.examples_advanced": (
                "ExamplesFlextCliModelsExamplesAdvanced",
            ),
            "._models_parts.examples_common": ("ExamplesFlextCliModelsExamplesCommon",),
            "._models_parts.examples_database": (
                "ExamplesFlextCliModelsExamplesDatabase",
            ),
            ".constants": (
                "ExamplesFlextCliConstants",
                "c",
            ),
            ".ex_01_getting_started": ("ExamplesFlextCliGettingStarted",),
            ".ex_02_output_formatting": ("ex_02_output_formatting",),
            ".ex_04_file_operations": ("ex_04_file_operations",),
            ".ex_05_authentication": ("Ex05Authentication",),
            ".ex_06_settings": ("Ex06Settings",),
            ".ex_11_complete_integration": ("DataManagerCLI",),
            ".ex_12_pydantic_driven_cli": ("ex_12_pydantic_driven_cli",),
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
    ),
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
        "pytest_addoption",
        "pytest_collect_file",
        "pytest_collection_modifyitems",
        "pytest_configure",
        "pytest_runtest_setup",
        "pytest_runtest_teardown",
        "pytest_sessionfinish",
        "pytest_sessionstart",
        "pytest_terminal_summary",
        "pytest_warning_recorded",
    ),
    module_name=__name__,
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
