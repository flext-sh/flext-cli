# AUTO-GENERATED FILE — Regenerate with: make gen
"""Utilities package."""

from __future__ import annotations

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

_LAZY_IMPORTS = merge_lazy_imports(
    (
        "._file_test_helper_parts",
        "._files_parts",
        "._json_parts",
        "._options_parts",
        "._output_parts",
        "._rules_parts",
        "._toml_parts",
    ),
    build_lazy_import_map(
        {
            "._file_test_helper_parts": ("_file_test_helper_parts",),
            "._file_test_helper_parts.flextcliutilitiesfiletesthelpersmixin_part_04": (
                "FlextCliUtilitiesFileTestHelpersMixin",
            ),
            "._files_parts": ("_files_parts",),
            "._files_parts.flextcliutilitiesfiles_part_04": ("FlextCliUtilitiesFiles",),
            "._json_parts": ("_json_parts",),
            "._json_parts.flextcliutilitiesjson_part_03": ("FlextCliUtilitiesJson",),
            "._options_parts": ("_options_parts",),
            "._options_parts.flextcliutilitiesoptionbuilder_part_01": (
                "FlextCliUtilitiesOptionBuilder",
            ),
            "._options_parts.flextcliutilitiesoptions_part_02": (
                "FlextCliUtilitiesOptions",
            ),
            "._output_parts": ("_output_parts",),
            "._output_parts.flextcliutilitiesoutput_part_02": (
                "FlextCliUtilitiesOutput",
            ),
            "._rules_parts": ("_rules_parts",),
            "._rules_parts.flextcliutilitiesrules_part_03": ("FlextCliUtilitiesRules",),
            "._toml_parts": ("_toml_parts",),
            "._toml_parts.flextcliutilitiestoml_part_07": ("FlextCliUtilitiesToml",),
            ".auth": ("FlextCliUtilitiesAuth",),
            ".cmd": ("FlextCliUtilitiesCmd",),
            ".commands": ("FlextCliUtilitiesCommands",),
            ".conversion": ("FlextCliUtilitiesConversion",),
            ".formatters": ("FlextCliUtilitiesFormatters",),
            ".matching": ("FlextCliUtilitiesMatching",),
            ".model_commands": (
                "FlextCliUtilitiesModelCommandBuilder",
                "FlextCliUtilitiesModelCommands",
            ),
            ".params": ("FlextCliUtilitiesParams",),
            ".pipeline": ("FlextCliUtilitiesPipeline",),
            ".prompts": ("FlextCliUtilitiesPrompts",),
            ".runtime": ("FlextCliUtilitiesRuntime",),
            ".settings": ("FlextCliUtilitiesSettings",),
            ".tables": ("FlextCliUtilitiesTables",),
            ".validation": ("FlextCliUtilitiesValidation",),
            ".yaml": ("FlextCliUtilitiesYaml",),
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
