# AUTO-GENERATED FILE — Regenerate with: make gen
"""Constants Parts package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from flext_tests import (
        c as c,
        d as d,
        e as e,
        h as h,
        m as m,
        p as p,
        r as r,
        s as s,
        t as t,
        td as td,
        tf as tf,
        tk as tk,
        tm as tm,
        tv as tv,
        u as u,
        x as x,
    )

    from tests._constants_parts.tests_core import (
        TestsFlextCliConstantsCore as TestsFlextCliConstantsCore,
    )
    from tests._constants_parts.tests_rules_options import (
        TestsFlextCliConstantsRulesOptions as TestsFlextCliConstantsRulesOptions,
    )
    from tests._constants_parts.tests_yaml_output import (
        TestsFlextCliConstantsYamlOutput as TestsFlextCliConstantsYamlOutput,
    )
    from tests._constants_parts.testsflextcliconstants_part_01 import (
        TestsFlextCliConstants as TestsFlextCliConstants,
    )
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
