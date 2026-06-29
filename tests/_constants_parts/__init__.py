# AUTO-GENERATED FILE — Regenerate with: make gen
"""Constants Parts package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".tests_core": ("TestsFlextCliConstantsCore",),
        ".tests_rules_options": ("TestsFlextCliConstantsRulesOptions",),
        ".tests_yaml_output": ("TestsFlextCliConstantsYamlOutput",),
        ".testsflextcliconstants_part_01": ("TestsFlextCliConstants",),
        "flext_tests": (
            "c",
            "d",
            "e",
            "h",
            "m",
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
        ),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
