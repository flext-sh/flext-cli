# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests. Constants Parts package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import c, d, e, h, m, p, r, s, t, td, tf, tk, tm, tv, u, x

    from .tests_core import TestsFlextCliConstantsCore
    from .tests_rules_options import TestsFlextCliConstantsRulesOptions
    from .tests_yaml_output import TestsFlextCliConstantsYamlOutput
    from .testsflextcliconstants_part_01 import TestsFlextCliConstants
__all__: tuple[str, ...] = (
    "TestsFlextCliConstants",
    "TestsFlextCliConstantsCore",
    "TestsFlextCliConstantsRulesOptions",
    "TestsFlextCliConstantsYamlOutput",
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
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
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
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
