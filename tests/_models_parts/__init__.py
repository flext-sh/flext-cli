# AUTO-GENERATED FILE — Regenerate with: make gen
"""Models Parts package."""

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

    from tests._models_parts.tests_cli import (
        TestsFlextCliModelsCli as TestsFlextCliModelsCli,
    )
    from tests._models_parts.tests_runtime import (
        TestsFlextCliModelsRuntime as TestsFlextCliModelsRuntime,
    )
    from tests._models_parts.tests_version import (
        TestsFlextCliModelsVersion as TestsFlextCliModelsVersion,
    )
    from tests._models_parts.testsflextclimodels_part_01 import (
        TestsFlextCliModels as TestsFlextCliModels,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".tests_cli": ("TestsFlextCliModelsCli",),
        ".tests_runtime": ("TestsFlextCliModelsRuntime",),
        ".tests_version": ("TestsFlextCliModelsVersion",),
        ".testsflextclimodels_part_01": ("TestsFlextCliModels",),
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
