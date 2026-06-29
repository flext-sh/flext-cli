# AUTO-GENERATED FILE — Regenerate with: make gen
"""Test Output Cov package."""

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
    from tests.unit._cases.test_output_cov.testsflextclioutputcov_part_02 import (
        TestsFlextCliOutputCov as TestsFlextCliOutputCov,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".testsflextclioutputcov_part_02": ("TestsFlextCliOutputCov",),
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
